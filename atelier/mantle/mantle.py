"""Retained04 Advanced exterior pass. Coordinates are Blender Z-up, forward -Y."""
import math
import re

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

TAU = math.tau
ORIGIN = Vector((0, 0, 0))
MATERIAL_NAMES = ("black-iron", "machined-steel", "worn-bronze", "forged-steel")
COLLECTION = "First Choice | formed metal and shoulder repair"


def bounded(value):
    return min(1.0, max(0.0, value))


def tag(obj, region):
    obj["first_choice_region"] = region
    obj["fc_region"] = "torso" if region in ("wing.L", "wing.R", "torso") else region


class Hardware:
    """Batch the drawn metal details per rigid motion region and finish."""
    def __init__(self, region, collection):
        self.region = region
        self.collection = collection
        self.vertices = []
        self.faces = []
        self.face_mats = []
        self.smooth = []

    def surface(self, rings, material, close=True, smooth=True):
        start = len(self.vertices)
        width = len(rings[0])
        for ring in rings:
            self.vertices.extend(ring)
        for i in range(len(rings) - 1):
            for j in range(width):
                a = start + i * width + j
                b = start + i * width + ((j + 1) % width)
                self.faces.append((a, b, b + width, a + width))
                self.face_mats.append(material)
                self.smooth.append(smooth)
        if close:
            first = tuple(start + j for j in reversed(range(width)))
            last = tuple(start + (len(rings) - 1) * width + j for j in range(width))
            self.faces.extend((first, last))
            self.face_mats.extend((material, material))
            self.smooth.extend((False, False))

    def tube(self, points, up, radius, material, edges=5):
        rings = []
        for i, p in enumerate(points):
            tangent = (points[min(i + 1, len(points)-1)] - points[max(i - 1, 0)]).normalized()
            sideways = tangent.cross(up).normalized()
            outward = tangent.cross(sideways).normalized()
            rings.append([p + radius*(sideways*math.cos(TAU*j/edges) + outward*math.sin(TAU*j/edges))
                          for j in range(edges)])
        self.surface(rings, material)

    def turned(self, pos, normal, profile, material, sides=10, smooth=True):
        tangent = normal.cross(Vector((0, 0, 1)))
        if tangent.length_squared < 1e-6:
            tangent = normal.cross(Vector((0, 1, 0)))
        tangent.normalize()
        bitangent = normal.cross(tangent)
        rings = [[pos + normal*h + radius*(tangent*math.cos(TAU*j/sides) + bitangent*math.sin(TAU*j/sides))
                  for j in range(sides)] for h, radius in profile]
        self.surface(rings, material, smooth=smooth)

    def rivet(self, pos, normal, radius, material=2, socket=False):
        # A narrow dark annulus remains between the lip and the inset, peened crown.
        self.turned(pos, normal, [(-radius*.18, radius), (radius*.09, radius), (radius*.22, radius*.88)], 0)
        self.turned(pos, normal, [(radius*.13, radius*.72), (radius*.28, radius*.70),
                                  (radius*.44, radius*.47), (radius*.45, radius*.26)],
                    material, sides=10)
        if socket:
            self.turned(pos, normal, [(radius*.446, radius*.27), (radius*.455, radius*.23)], 0, 6, False)

    def finish(self):
        if not self.faces:
            return None
        name = "FC " + self.region + " | plate lips, rivets and fittings"
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(self.vertices, [], self.faces)
        for material_name in MATERIAL_NAMES:
            mesh.materials.append(bpy.data.materials[f"CG metal05 / {material_name} / builder / retained-uv"])
        for polygon, index, smooth in zip(mesh.polygons, self.face_mats, self.smooth):
            polygon.material_index = index
            polygon.use_smooth = smooth
        # Small turned parts need UVs too; stable triplanar projections retain a visible grain.
        uv = mesh.uv_layers.new(name="formed-metal")
        for poly in mesh.polygons:
            normal = poly.normal
            axis = max(range(3), key=lambda i: abs(normal[i]))
            u, v = ((1, 2), (0, 2), (0, 1))[axis]
            for idx in poly.loop_indices:
                p = mesh.vertices[mesh.loops[idx].vertex_index].co
                uv.data[idx].uv = (p[u]*6.0, p[v]*6.0)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        self.collection.objects.link(obj)
        tag(obj, self.region)
        return obj


def top_sample(obj, across, along, cols, rows):
    """Bilinear point and exterior normal of a formed plate's existing face grid."""
    x = bounded(across) * (cols - 1)
    y = bounded(along) * (rows - 1)
    i, j = min(int(x), cols-2), min(int(y), rows-2)
    vertices = obj.data.vertices
    p = [obj.matrix_world @ vertices[(j+b)*cols+i+a].co for a,b in ((0,0),(1,0),(0,1),(1,1))]
    a, b = x-i, y-j
    du = (p[1] - p[0]).lerp(p[3] - p[2], b)
    dv = (p[2] - p[0]).lerp(p[3] - p[1], a)
    position = p[0].lerp(p[1], a).lerp(p[2].lerp(p[3], a), b)
    normal = du.cross(dv).normalized()
    # Align to the actual mesh normal. Some mirrored panels have reversed grid winding.
    source_normal = (obj.matrix_world.to_3x3() @ vertices[j*cols+i].normal).normalized()
    if source_normal.dot(normal) < 0:
        normal.negate()
    return position, normal


def pressed_edge(batch, obj, grid, trim, radius, mat):
    # One short returning swage follows both flanks around the scalloped end.
    points, normals = [], []
    for u,v in trim:
        pos, normal = top_sample(obj, u, v, *grid)
        points.append(pos + normal*(radius*.22))
        normals.append(normal)
    batch.tube(points, sum(normals, ORIGIN.copy()).normalized(), radius, mat)


def fan(point):
    """Keep the shoulder root seated; pull the distal shield into a compact rear sweep."""
    x, y, z = point
    t = bounded((1.39-z)/.447)
    s = -1 if x<0 else 1
    x += s * .013 * math.sin(math.pi*t)
    y += .147*t**1.35 + .038*t*bounded((y+.20)/.45)
    z -= .057*t**1.45
    return Vector((x, y, z))


def breast(point):
    x,y,z = point
    w = bounded(1 - abs(z-1.06)/.33)
    low = bounded((1.36-z)/.59)
    return Vector((x*(1+.048*w), y-.021*w, z-.024*low))


def shift_grid(obj, transformer):
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        vertex.co = inverse @ transformer(obj.matrix_world @ vertex.co)
    obj.data.update()


def shape_shield(obj, row, col, side, batch):
    shift_grid(obj, fan)
    # Give the lanceolate ends a rounded shoulder and an individually cast camber.
    mesh = obj.data
    rows, cols = 17, 9
    for layer in (0, rows*cols):
        for j in range(10, rows):
            t=(j-10)/6
            taper=(1-(1-t)**2)
            center=mesh.vertices[layer + j*cols + 4].co.copy()
            wide_center=mesh.vertices[layer+9*cols+4].co
            for i in range(cols):
                v=mesh.vertices[layer+j*cols+i]
                width=mesh.vertices[layer+9*cols+i].co-wide_center
                # A softened free tip remains distinct from the one below it.
                v.co += width*(.40*taper*t) + Vector((side*.0012*taper*(1-abs(i-4)/4), 0,
                                                        -.0021*taper*math.sin(math.pi*i/8)))
    mesh.update()
    for i in (.25,.75) if row>4 and (row+col)%3==0 else (.48,):
        pos, normal = top_sample(obj,i,.76,cols,rows)
        batch.rivet(pos, normal, .00245 + .00048*bounded(row/7), material=3 if col%3 else 2)
    if row >= 2:
        trim = [(u,.48+.40*t) for t,u in ((0,.107),(.35,.11),(.70,.13),(1,.20))]
        trim += [(.32,.913),(.50,.932),(.68,.913),(.80,.88),(.86,.79),(.88,.66),(.89,.52)]
        pressed_edge(batch,obj,(cols,rows),trim,.00062 if row<5 else .00079,3)


def body_detail(obj, batch, col, row):
    shift_grid(obj, breast)
    cols, rows=9, 11
    # Restrained rolled termination and uneven peening give the broad breast quiet areas.
    for a in (.19,.79):
        p,n=top_sample(obj,a,.79,cols,rows)
        batch.rivet(p,n,.00315 + .00040*(1 if row in (2,3) else 0), 2 if (row+col)%3 else 3)
    trim=[(.082,.42),(.09,.58),(.10,.73),(.13,.83),(.19,.88),
          (.32,.925),(.5,.940),(.68,.925),(.81,.88),(.87,.83),(.9,.70),(.91,.56)]
    pressed_edge(batch,obj,(cols,rows),trim,.0010 if row in (2,3,4) else .00082,3)


def wing_accelerator(panels):
    vertices, faces=[],[]
    for obj in panels:
        off=len(vertices)
        vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(off+i for i in face.vertices) for face in obj.data.polygons)
    return BVHTree.FromPolygons(vertices, faces)


def place_repair(collection, left_panels, batch):
    tree=wing_accelerator(left_panels)
    def surface(y,z):
        hit,n,_,_=tree.ray_cast(Vector((-.7,y,z)),Vector((1,0,0)),.60)
        if hit is None: return None
        if n.x>0: n.negate()
        return hit,n
    def strap(centerline,half_width,metal,bulge):
        spans=[]
        upper=[]
        for i,(y,z) in enumerate(centerline):
            samples=[]
            width=half_width*(.68 if i in (0,len(centerline)-1) else 1.0)
            for off in (-width,0,width):
                sample=surface(y+off,z)
                if not sample:return []
                pos,normal=sample
                samples.append((pos,normal))
            spans.append([samples[j][0]+Vector((-bulge-(.0018 if j==1 else 0),0,0)) for j in range(3)])
            upper.append(samples[1])
        # A closed section forms an inset iron strap whose crown catches grazing light.
        rings=[]
        for s in spans:
            rings.append([s[0],s[1],s[2],s[2]+Vector((.003,0,0)),s[0]+Vector((.003,0,0))])
        batch.surface(rings,metal, smooth=False)
        return [(s[1],n) for s,(_,n) in zip(spans,upper)]
    # Old fitted keeper under a shorter iron splice. Unused plugged holes remain at its ends.
    path=[(-.052,1.362),(-.060,1.351),(-.067,1.340),(-.077,1.326),
          (-.087,1.312),(-.101,1.296),(-.112,1.282),(-.122,1.266),(-.131,1.248)]
    old=strap(path,.014,2,.0036)
    newer=strap([(y-.005,z-.005) for y,z in path[1:-1]],.009,3,.008)
    if old and newer:
        for i in (0,-1):
            p,n=old[i];batch.rivet(p,n,.0041,1)
        for i in (1,-2):
            p,n=newer[i];batch.rivet(p,n,.0063,1,True)
    return bool(old and newer)


def close_lower_breast(collection, fittings):
    """Nest a compact, lengthwise-plated keel between the two native belly courses."""
    # (fore-aft station, half-width, lower edge, upper edge). The fore end goes
    # beneath the lowest pectoral plates; the after end returns under the pelvis.
    sections = [
        (-.353, .084, .935, .990), (-.327, .122, .890, .987),
        (-.291, .151, .840, .986), (-.255, .171, .802, .978),
        (-.216, .184, .762, .967), (-.174, .193, .719, .954),
        (-.129, .196, .681, .937), (-.081, .189, .653, .920),
        (-.032, .171, .626, .904), (.015, .144, .614, .882),
        (.061, .117, .608, .857), (.108, .094, .620, .843),
        (.152, .073, .653, .830), (.183, .049, .701, .821)
    ]
    section_steps = 3
    def interpolate(t):
        loc=bounded(t)*(len(sections)-1)
        k=min(int(loc),len(sections)-2)
        f=loc-k
        # Cardinal interpolation uses the neighboring stations' tangents.
        a,b,c,d=[sections[max(0,min(len(sections)-1,k+i))] for i in (-1,0,1,2)]
        return [.5*((2*v)+(-u+w)*f+(2*u-5*v+4*w-q)*f*f+
                    (-u+3*v-3*w+q)*f*f*f) for u,v,w,q in zip(a,b,c,d)]

    def point(t,angle,lift=0):
        y,rx,low,high=interpolate(t)
        rz=(high-low)/2
        return Vector(((rx+lift)*math.sin(angle),y,low+rz-(rz+lift)*math.cos(angle)))

    def normal(t,a):
        tangent=(point(min(1,t+.001),a)-point(max(0,t-.001),a)).normalized()
        cross=(point(t,a+.001)-point(t,a-.001)).normalized()
        return tangent.cross(cross).normalized()

    class Shell:
        def __init__(self):
            self.verts=[]
            self.faces=[]
            self.mat=[]
        def add_face(self,idx,mat):
            self.faces.append(tuple(idx))
            self.mat.append(mat)

    shell=Shell()
    n=(len(sections)-1)*section_steps+1
    width=32
    for i in range(n):
        for j in range(width):shell.verts.append(point(i/(n-1),TAU*j/width,-.001))
    # Cosine-arched dark undertray sits below the formed strips.
    for i in range(n-1):
        for j in range(width):
            a=i*width+j
            b=i*width+(j+1)%width
            shell.add_face([a,a+width,b+width,b],0)
    shell.add_face(range(width),0)
    shell.add_face(range((n-1)*width,n*width)[::-1],0)
    # Each strake travels from the lower chest into the existing compact rear.
    # Broad quiet metal, short returned seams and no dangling tips.
    edges=(-2.80,-2.21,-1.64,-1.04,-.43,.43,1.04,1.64,2.21,2.80)
    w=7
    for k,(a0,a1) in enumerate(zip(edges,edges[1:])):
        start=len(shell.verts)
        for i in range(n):
            t=i/(n-1)
            for j in range(w):
                u=j/(w-1)
                angle=a0+(a1-a0)*(.018+.964*u)
                angle+=.11*math.sin(math.pi*t)*math.sin(angle)
                rolled=math.sin(math.pi*u)**.6
                lift=.0015+.0028*rolled+.0007*math.sin(t*math.pi*2+k*.8)
                shell.verts.append(point(t,angle,lift))
        for i in range(n-1):
            for j in range(w-1):
                a=start+i*w+j
                shell.add_face((a,a+w,a+w+1,a+1),1 if k%3 else 2)
        if k not in (0,len(edges)-2):
            for t in (.28,.58):
                ang=a0+(a1-a0)*.86
                ang+=.11*math.sin(math.pi*t)*math.sin(ang)
                p=point(t,ang,.0035)
                fittings.rivet(p,normal(t,ang),.003,3)
    mesh=bpy.data.meshes.new("FC short formed ventral keel")
    mesh.from_pydata(shell.verts,[],shell.faces)
    cat=("black-iron","forged-steel","breast-armor")
    for name in cat:
        mesh.materials.append(bpy.data.materials[f"CG metal05 / {name} / builder / retained-uv"])
    uv=mesh.uv_layers.new(name="wrapped-ventral-metal")
    for f,index in zip(mesh.polygons,shell.mat):
        f.material_index=index
        f.use_smooth=True
        for li in f.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(p.y*4.5,p.z*3+p.x*1.5)
    mesh.update()
    obj=bpy.data.objects.new("FC torso | nested ventral keel",mesh)
    collection.objects.link(obj)
    tag(obj,"torso")
    return obj


def apply_mantle():
    """Apply the authored pass to a freshly opened retained04 Builder scene."""
    if bpy.data.collections.get(COLLECTION):
        raise RuntimeError("The First Choice formed-metal pass is already present")
    collection=bpy.data.collections.new(COLLECTION)
    bpy.context.scene.collection.children.link(collection)
    buckets={r:Hardware(r,collection) for r in ("wing.L","wing.R","torso","neck")}
    left_panels=[]
    changed=[]
    wing_pattern=re.compile(r"CGB05 (-?1) shield curved feather (\d+)-(\d+)$")
    body_pattern=re.compile(r"CGRB01 rounded course (\d+)-(\d+)$")
    for obj in list(bpy.context.scene.objects):
        if obj.type!="MESH" or obj.hide_render:continue
        name=obj.name
        wing_match=wing_pattern.fullmatch(name)
        body_match=body_pattern.fullmatch(name)
        if wing_match:
            sign,row,col=map(int,wing_match.groups())
            region="wing.L" if sign==-1 else "wing.R"
            shape_shield(obj,row,col,sign,buckets[region])
            if sign==-1:left_panels.append(obj)
        elif "small shoulder covert" in name or name in ("CG supervised left compact shield recess",
                                                        "CG supervised right compact shield recess"):
            region="wing.L" if "left" in name or "-1 " in name else "wing.R"
            shift_grid(obj,fan)
            if region=="wing.L":left_panels.append(obj)
        elif body_match:
            col,row=map(int,body_match.groups())
            region="torso"
            body_detail(obj,buckets[region],col,row)
        elif name.startswith("CGRB03 "):
            region="torso"
            shift_grid(obj,breast)
        elif name.startswith("CGB12 longitudinal formed panel "):
            # The neck has an open mechanical flank and plates sweep gently over the upper breast.
            # Retain the native collar/range here; only add its seated surface detail.
            if len(obj.data.vertices)!=325:continue
            region="neck" if max(v.co.z for v in obj.data.vertices)>1.49 else "torso"
            for a in (.23,.77):
                p,n=top_sample(obj,a,.82,13,25)
                buckets[region].rivet(p,n,.0026,3)
            trim=[(.10,.65),(.12,.80),(.16,.88),(.30,.925),(.53,.936),(.75,.919),(.87,.86),(.89,.68)]
            pressed_edge(buckets[region],obj,(13,25),trim,.00070,3)
        else:
            continue
        tag(obj,region)
        changed.append(name)
    repaired=place_repair(collection,left_panels,buckets["wing.L"])
    if not repaired:
        raise ValueError("Repaired shoulder strap missed the retained shield")
    close_lower_breast(collection,buckets["torso"])
    for batch in buckets.values():batch.finish()
    bpy.context.view_layer.update()
    print("First Choice formed metal:",len(changed),"retained surfaces and",len(collection.objects),"regional fittings")
    return {"changed_retained":len(changed),"new_groups":len(collection.objects),"left_keeper_seated":repaired}
