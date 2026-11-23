"""Fit a grounded, flared pedal silhouette to the retained04 Advanced native scene.

World space uses Blender Z up; the retained beak faces -Y. The ankle bearings and
their original pivot centers stay in place. These are picture-led CG surfaces.
"""
from math import cos, sin, pi, exp
import re

import bpy
from mathutils import Vector

FLOOR = .0005
GROUP = "FC | Grounded digits"
ANKLE_X = .218
ANGLES = 32
MATERIALS = (
    ("dark graphite", (.040, .045, .043), .61, .50),
    ("hammered gunmetal", (.110, .120, .106), .85, .37),
    ("oxide bronze", (.156, .110, .064), .77, .46),
    ("worn rim", (.227, .204, .157), .86, .35),
    ("blackened claw", (.072, .079, .075), .91, .30),
    ("claw bevel", (.136, .140, .126), .88, .30),
)


def _materials():
    result = []
    for title, color, metallic, roughness in MATERIALS:
        name = "FC pedal / " + title
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        m.use_nodes = True
        shader = m.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = (*color, 1)
        shader.inputs["Metallic"].default_value = metallic
        shader.inputs["Roughness"].default_value = roughness
        m.diffuse_color = (*color, 1)
        m.metallic = metallic
        m.roughness = roughness
        m["fc_surface"] = title
        result.append(m)
    return result


def _lerp_profile(t, keys):
    for (ta, va), (tb, vb) in zip(keys, keys[1:]):
        if t <= tb:
            u = min(1, max(0, (t - ta) / (tb - ta)))
            u = u * u * (3 - 2 * u)
            return va * (1 - u) + vb * u
    return keys[-1][1]


def _bezier(controls, u):
    a, b, c, d = controls
    v = 1 - u
    return v**3*a + 3*v*v*u*b + 3*v*u*u*c + u**3*d


def _direction(controls, u):
    a, b, c, d = controls
    v = 1 - u
    return (v*v*(b-a) + 2*v*u*(c-b) + u*u*(d-c)).normalized()


class Surface:
    def __init__(self):
        self.verts = []
        self.faces = []
        self.indices = []

    def rows(self, rings, material, close=True):
        """Join cross-sections, preserving independent closed plate islands."""
        first = len(self.verts)
        count = len(rings[0])
        for ring in rings:
            self.verts.extend(tuple(v) for v in ring)
        for i in range(len(rings) - 1):
            a = first + i * count
            b = a + count
            for j in range(count):
                j2 = (j + 1) % count
                self.faces.append((a+j, a+j2, b+j2, b+j))
                self.indices.append(material(i,j) if callable(material) else material)
        if close:
            last = first + count * (len(rings)-1)
            self.faces.extend((tuple(reversed(range(first, first+count))), tuple(range(last,last+count))))
            self.indices.extend((0,0))

    def object(self, collection, name, role, mats, region="foot"):
        data = bpy.data.meshes.new(name)
        data.from_pydata(self.verts, [], self.faces)
        data.materials.clear()
        for m in mats:
            data.materials.append(m)
        for p, mi in zip(data.polygons, self.indices):
            p.material_index = mi
            p.use_smooth = len(p.vertices) == 4
        data.update()
        ob = bpy.data.objects.new(name, data)
        collection.objects.link(ob)
        ob["cg1cRegion"] = region
        ob["cg2bRegion"] = region
        ob["surfaceRole"] = role
        ob["fc_region"] = region
        ob["fc_rigid"] = "fixed"
        ob["fc_surface"] = role
        return ob


class Digit:
    def __init__(self, side, digit):
        # Each digit departs the shared metatarsal outlet at its own angle.
        # Positions are measured relative to the retained ankle's centerline.
        digit_specs = {
            "outer": ((.030,-.044),(.046,-.111),(.082,-.168),(.118,-.215),(.170,-.278),1.01),
            "central": ((.002,-.050),(.006,-.122),(.012,-.216),(.018,-.268),(.024,-.357),1.09),
            "inner": ((-.032,-.046),(-.048,-.113),(-.071,-.164),(-.103,-.211),(-.141,-.282),.96),
            "hallux": ((-.005,.008),(-.008,.067),(-.024,.081),(-.040,.128),(-.059,.199),.86),
        }
        root, near, middle, socket, tip, self.width = digit_specs[digit]
        self.rear = digit == "hallux"

        def point(coords, z):
            return Vector((side * (ANKLE_X + coords[0]), coords[1], z))

        self.path = tuple(point(x,0) for x in (root,near,middle,socket))
        start, end = self.path[-1], point(tip,0)
        delta = end - start
        self.blade = (
            Vector((start.x, start.y, .050 if not self.rear else .046)),
            start + .47*delta + Vector((0,0,.076 if not self.rear else .065)),
            start + .84*delta + Vector((0,0,.047 if not self.rear else .037)),
            end + Vector((0,0,FLOOR)),
        )

    def frame(self,u):
        origin = _bezier(self.path,u)
        t = _direction(self.path,u)
        side = Vector((-t.y,t.x,0))
        return origin, side

    def profile(self,u):
        # Pads contact at two locations, with a shallow arch between them.
        bottom = _lerp_profile(u, [(0,.032),(.18,.011),(.26,FLOOR),(.45,FLOOR),
                                   (.55,.010),(.65,.003),(.69,FLOOR),(.84,FLOOR),(1,.019)])
        top = _lerp_profile(u, [(0,.089),(.21,.074),(.33,.068),(.52,.073),
                                 (.70,.056),(.83,.063),(1,.067)])
        halfwidth = self.width * _lerp_profile(u, [(0,.024),(.25,.030),(.43,.025),
                                                    (.53,.028),(.72,.023),(.82,.027),(1,.022)])
        return bottom, top, halfwidth

    def underpad(self, surface):
        rings = []
        for i in range(41):
            u = i/40
            origin, across = self.frame(u)
            bottom, top, hw = self.profile(u)
            ring = []
            for j in range(ANGLES):
                a = 2*pi*j/ANGLES
                # A broad sole and tight heel radius give discernible contact.
                h = sin(a)
                if h < 0:
                    h = max(-1,1.47*h)
                z = bottom + (h + 1) * .5 * (top - bottom)
                ring.append(origin + across*hw*cos(a) + Vector((0,0,z)))
            rings.append(ring)
        surface.rows(rings,0)

    def plates(self, surface):
        # Overlapping dorsal shoes have a turned-under medial edge. Each
        # shell wraps around a dark core, leaving the planted tread visible.
        cuts = [(.005,.29),(.262,.555),(.530,.803),(.772,1.008)]
        for idx, (lo,hi) in enumerate(cuts):
            rings = []
            samples = (0,.024,.060,.17,.35,.55,.74,.87,.96,1)
            for v in samples:
                center = lo+(hi-lo)*v
                ring = []
                for k in range(2):
                    angles = [pi * (-.09 + 1.18*j/24) for j in range(25)]
                    if k:
                        angles.reverse()
                    for a in angles:
                        # The free lip extends farther over the dorsal center.
                        u = min(1.0,max(0,center + .018*sin(a)**2*v))
                        p, across = self.frame(u)
                        bottom, top, hw = self.profile(u)
                        taper = _lerp_profile(v,[(0,.74),(.07,.97),(.24,1.06),(.72,1),(.94,.97),(1,.91)])
                        flare = 1 + .08*exp(-((v-.89)/.10)**2)
                        rz = .5*(top-bottom) + .0045
                        mid = bottom + .5*(top-bottom) - .001
                        width = (hw+.003)*taper*flare - .0024*k
                        height = rz*taper + .004*sin(pi*v) - .0026*k
                        # subtle longitudinal ridge along each convex dorsal plate.
                        z = mid + height*sin(a) + .0018*max(0,sin(a))**6
                        ring.append(p + across*width*cos(a) + Vector((0,0,z)))
                rings.append(ring)
            def finish(i,j):
                if j in (24,49) or i == 8:
                    return 3
                if j > 24:
                    return 0
                return 2 if idx == 0 or (self.rear and idx==2) else 1
            surface.rows(rings,finish)

    def claw(self, surface):
        rings = []
        sections = 30
        for i in range(sections):
            # Last section is very small. The separate apex is the actual point.
            u = .996*i/(sections-1)
            origin = _bezier(self.blade,u)
            t = _direction(self.blade,u)
            side = Vector((-t.y,t.x,0)).normalized()
            up = t.cross(side).normalized()
            # Width closes earlier than the dorsal ridge, giving a blade edge
            # visible in plan and a convex profile in the lateral view.
            w = self.width*.0230*(1-u)**.90*(1-.12*u)
            h = self.width*.0232*(1-u)**.78
            rings.append([
                origin + side*(w*cos(a)) + up*((h if sin(a)>=0 else .71*h)*sin(a)
                         + .22*h*max(0,sin(a))**7)
                for a in (2*pi*j/ANGLES for j in range(ANGLES))
            ])
        surface.rows(rings, lambda i,j: 5 if j in (5,6,25,26) and i>3 else 4, close=False)
        first=len(surface.verts)-ANGLES*sections
        surface.faces.append(tuple(reversed(range(first,first+ANGLES))))
        surface.indices.append(4)
        last = len(surface.verts)-ANGLES
        apex = len(surface.verts)
        surface.verts.append(tuple(self.blade[-1]))
        for j in range(ANGLES):
            surface.faces.append((last+j,last+(j+1)%ANGLES,apex))
            surface.indices.append(4)


def _turned(surface, a, b, profile, material, radial=24):
    """Turn a compact stepped ferrule around the native terminal direction."""
    axis = (b - a).normalized()
    side = axis.cross(Vector((0, 0, 1)))
    if side.length < .01:
        side = axis.cross(Vector((0, 1, 0)))
    side.normalize()
    up = axis.cross(side)
    rings = []
    for u, radius in profile:
        center = a.lerp(b, u)
        rings.append([center + radius*(side*cos(2*pi*j/radial) + up*sin(2*pi*j/radial))
                      for j in range(radial)])
    surface.rows(rings, material)


def _seat_terminals(collection, mats, sign, side):
    """Fit the twelve visible medial rod ends to their existing round races."""
    out = []
    for leg, joint in (("upper","knee"),("shank","hock"),("tarsus","ankle")):
        race = bpy.data.objects[f"CG2b {side} {joint} medial steel lip"]
        bbox = [race.matrix_world @ Vector(c) for c in race.bound_box]
        center = sum(bbox,Vector((0,0,0)))/len(bbox)
        surface = Surface()
        rods = []
        for index in (0,1):
            rod = bpy.data.objects[f"CG2b {side} {leg} medial exposed rod {index}"]
            caps = sorted((rod.matrix_world @ p.center for p in rod.data.polygons
                           if len(p.vertices) > 6), key=lambda v:v.z)
            if len(caps) != 2:
                raise ValueError(f"Unrecognized native end faces on {rod.name}")
            low, high = caps
            shaft = (high-low).normalized()
            eye = low - .009*shaft
            # The cuff swallows the original cap and shoulders into the eye.
            _turned(surface,eye,low+.014*shaft,
                    [(0,.0073),(.15,.0100),(.62,.0101),(.73,.0121),(.91,.0121),(1,.0090)],
                    lambda i,j:3 if i==4 else (2 if i==3 else 1))
            # Pick up the existing face just inside its rim. Keep the old
            # center bolt clear rather than capping the face of the hinge.
            pickup = center + .53*(eye-center)
            pickup.x = center.x - sign*.003
            arm = (pickup-eye).normalized()
            width = arm.cross(Vector((1,0,0))).normalized()
            thickness = arm.cross(width)
            rings = []
            for u, w, h in ((0,.008,.004),(.12,.011,.0045),(.48,.009,.0045),
                             (.80,.012,.005),(.98,.012,.005),(1,.010,.004)):
                p = eye.lerp(pickup,u)
                rings.append([p+w*width*cos(2*pi*j/16)+h*thickness*sin(2*pi*j/16)
                              for j in range(16)])
            surface.rows(rings,1)
            # A low pin head on each side of the cheek keeps the small joint
            # legible from either orbit direction.
            inward = Vector((-sign,0,0))
            for pivot,radius in ((eye,.0125),(pickup,.0105)):
                _turned(surface,pivot-inward*.006,pivot+inward*.009,
                        [(0,.84*radius),(.12,radius),(.59,radius),(.68,.91*radius),
                         (.82,.91*radius),(.84,.68*radius),(.96,.68*radius),(1,.54*radius)],
                        lambda i,j:3 if i in (2,4) else (2 if i in (3,5) else 1))
            rods.append(rod.name)
        ob = surface.object(collection,f"FC {side} {joint} medial rod seats","bearing",mats,"leg")
        ob["fc_registers"] = "; ".join(rods + [race.name])
        out.append(ob)
    return out


def _supersede(obj):
    obj.hide_render = True
    obj.hide_set(True)
    obj["fc_superseded"] = True


def apply_pedal():
    """Apply once after loading retained04; return the new, fixed render meshes."""
    if bpy.data.collections.get(GROUP):
        raise ValueError("Pedal surfaces already present")
    if "CG1c left ankle concentric hinge" not in bpy.data.objects:
        raise ValueError("Missing retained04 ankle registration")
    for o in list(bpy.context.scene.objects):
        if o.hide_render:
            continue
        n = o.name
        if o.get("cg1cRegion") in {"leg","foot"}:
            if "forward toe" in n or "rear toe" in n:
                _supersede(o)
            if "embedded thigh plate" in n:
                # Reveal the existing upper-leg mechanisms and knee under the
                # mantle. Short upper courses remain around the hip.
                match = re.search(r"embedded thigh plate (\d+) (\d+)", n)
                if match and (int(match[1])>=1 or int(match[2]) in (4,5,6)):
                    _supersede(o)
    collection = bpy.data.collections.new(GROUP)
    bpy.context.scene.collection.children.link(collection)
    mats = _materials()
    objects = []
    for sign,name in [(-1,"left"),(1,"right")]:
        objects.extend(_seat_terminals(collection,mats,sign,name))
        for digit_name in ("outer","central","inner","hallux"):
            toe = Digit(sign,digit_name)
            for label, fn, role in (("plantar pad",toe.underpad,"sole"),
                                    ("articulated covers",toe.plates,"armor"),
                                    ("keeled talon",toe.claw,"talon")):
                s = Surface()
                fn(s)
                o = s.object(collection,f"FC {name} {digit_name} {label}", role, mats)
                o["fc_digit"] = digit_name
                o["fc_side"] = name
                objects.append(o)
    bpy.context.view_layer.update()
    return objects
