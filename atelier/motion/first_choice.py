"""Rigid visual staging and keyframes for the Advanced First Choice encounter.

Apply to the retained Blender source after the regional artists finish their
mesh edits. All distances and pivot choices are in that source's coordinates.
"""
from math import cos, pi, radians, sin
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

FPS = 24
LAST_FRAME = 252
TRACK = "First Choice"
HIP = (0.0, 0.105, 0.865)
CERVICAL_BASE = (0.0, -0.105, 1.300)
ATLANTO = (0.0, -0.11437, 1.56159)
SADDLE_AXIS = (0.025, -0.438, 0.808)

# Rotations in local anatomical axes, from the stable rest pose. Negative X
# on the saddle lets the rearward arm drop while the centre of its pin stays
# seated. Negative X at the hips brings the bird's breast off the shoe.
POSE_KEYS = {
    "saddle": [
        (0, 0, 0, 0), (36, 0, 0, 0), (40, -.35, 0, 0),
        (46, -3.8, 0, 0), (54, -6.8, 0, 0), (61, -6.15, 0, 0),
        (76, -6.35, 0, 0), (158, -6.35, 0, 0), (177, -5.90, 0, 0),
        (207, -2.85, 0, 0), (236, -.12, 0, 0), (244, 0, 0, 0),
        (252, 0, 0, 0)],
    "torso": [
        (0, 0, 0, 0), (44, 0, 0, 0), (49, -.20, -.10, 0),
        (59, -1.25, -.70, -.16), (73, -2.45, -1.70, -.50),
        (81, -2.15, -1.65, -.52), (95, -2.12, -1.61, -.48),
        (129, -2.10, -1.63, -.46), (157, -2.00, -1.59, -.43),
        (182, -2.00, -1.59, -.43), (209, -1.15, -1.10, -.15),
        (237, -.08, -.05, 0), (245, 0, 0, 0), (252, 0, 0, 0)],
    "neck": [
        (0, 0, 0, 0), (48, 0, 0, 0), (72, .82, .35, 0),
        (89, .74, .40, 0), (98, .74, .40, 0), (117, 2.1, .55, -.65),
        (151, 4.7, .27, -2.2), (165, 4.45, .27, -2.15),
        (193, 4.45, .27, -2.15), (226, 1.05, .09, -.45),
        (245, 0, 0, 0), (252, 0, 0, 0)],
    "head": [
        (0, 0, 0, 0), (46, 0, 0, 0), (68, 1.10, .46, .08),
        (84, 1.18, .53, .14), (97, 1.18, .53, .14), (104, 1.68, .55, -.55),
        (117, 5.05, .40, -3.55), (143, 9.05, -.2, -6.75),
        (155, 9.22, -.35, -7.05), (166, 8.85, -.26, -6.85),
        (193, 8.85, -.26, -6.85), (213, 6.15, -.05, -4.95),
        (237, .52, .05, -.58), (247, 0, 0, 0), (252, 0, 0, 0)],
}


def _material(name, rgb, metallic, roughness):
    m = bpy.data.materials.new("FC fixture | " + name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    return m


class Fixture:
    """A compact cast-iron workshop pedestal and the separately rotating shoe."""

    def __init__(self, collection, anchors):
        self.collection = collection
        self.anchors = anchors
        self.iron = _material("blue black cast iron", (.064, .075, .079), .68, .47)
        self.mill = _material("exposed milled steel", (.23, .23, .207), .83, .32)
        self.dark = _material("graphite steel", (.046, .042, .034), .68, .45)
        self.bronze = _material("oiled bronze bush", (.292, .175, .076), .84, .29)
        self.pad = _material("compressed leather liner", (.067, .034, .018), .08, .7)
        self.line = _material("worn enamel witness", (.61, .51, .32), .26, .47)

    def part(self, name, vertices, faces, material, region, bevel=0, smooth=False):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        ob = bpy.data.objects.new("FC fixture | " + name, mesh)
        self.collection.objects.link(ob)
        ob["fc_region"] = region
        ob["first_choice_region"] = "assembly support " + region
        ob.parent = self.anchors[region]
        # Coordinates were authored in the native rest frame.
        ob.matrix_parent_inverse = ob.parent.matrix_world.inverted()
        mesh.materials.append(material)
        for face in mesh.polygons:
            face.use_smooth = smooth
        if bevel:
            bev = ob.modifiers.new("Foundry fillet", "BEVEL")
            bev.width = bevel
            bev.segments = 3
            bev.limit_method = "ANGLE"
            bev.harden_normals = True
            norm = ob.modifiers.new("Face weighted corner normals", "WEIGHTED_NORMAL")
            norm.keep_sharp = True
        return ob

    def prism(self, name, yz, x1, x2, mat, region="stand", bevel=.003):
        # yz is clockwise or counterclockwise as seen along X; orient outward.
        area = sum(y*z2-y2*z for (y,z),(y2,z2) in zip(yz,yz[1:]+yz[:1]))
        if area < 0:
            yz = list(reversed(yz))
        n = len(yz)
        vs = [(x,y,z) for x in (x1,x2) for y,z in yz]
        fs = [tuple(reversed(range(n))),tuple(range(n,2*n))]
        fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        return self.part(name,vs,fs,mat,region,bevel)

    def block(self, name, lo, hi, mat, region="stand", bevel=.003):
        x,y,z=lo
        X,Y,Z=hi
        return self.prism(name,[(y,z),(Y,z),(Y,Z),(y,Z)],x,X,mat,region,bevel)

    def turning(self, name, center, axis, sections, mat, region="stand", sides=48, closed=False):
        # A lathed (radius, axial offset) profile. Closed sections describe
        # genuine annuli for the two ears flanking the saddle and its bush.
        tangent=Vector(axis).normalized()
        basis=Vector((0,1,0)); perpendicular=tangent.cross(basis)
        if perpendicular.length < .1:
            basis=Vector((1,0,0));perpendicular=tangent.cross(basis)
        u=perpendicular.normalized()
        v=tangent.cross(u)
        vs=[]
        for rad, t in sections:
            origin=Vector(center)+tangent*t
            vs += [origin + rad*(u*cos(2*pi*i/sides)+v*sin(2*pi*i/sides)) for i in range(sides)]
        fs=[]
        for row in range(len(sections) if closed else len(sections)-1):
            nxt=(row+1)%len(sections)
            for i in range(sides):
                j=(i+1)%sides
                fs.append((row*sides+i,row*sides+j,nxt*sides+j,nxt*sides+i))
        if not closed:
            fs += [tuple(reversed(range(sides))), tuple(range(len(vs)-sides,len(vs)))]
        ob=self.part(name,vs,fs,mat,region)
        for poly in ob.data.polygons:
            # Smooth across a cylindrical band, preserve changes in the turned profile.
            poly.use_smooth=sides>12 and len(poly.vertices)==4
        ob.data.set_sharp_from_angle(angle=radians(22))
        return ob

    def fastener(self, name, pt, size, direction):
        # Washer and hex fastener share the same axis. Keep the focal bolt unique.
        self.turning(name+" washer",pt,direction,[(size*1.24,-.003),(size*1.24,0),(size*1.17,.001)],self.mill,sides=24)
        self.turning(name,pt,direction,[(size*.91,.001),(size,.0025),(size,size*.51),(size*.84,size*.62)],self.dark,sides=6)

    def build(self, top):
        # Mounted on the workshop floor, ahead of the feet and slightly to the
        # far side from the native comparison camera. Pin axis is lateral.
        self.block("bed sole",(-.162,-.893,.0005),(.261,-.386,.024),self.dark,bevel=.006)
        self.block("bed foot casting",(-.136,-.868,.024),(.235,-.411,.078),self.iron,bevel=.009)
        self.block("bed machined shelf",(-.14,-.862,.078),(.239,-.417,.089),self.mill,bevel=.003)
        for x in (-.125,.224):
            for y in (-.847,-.433):
                self.fastener("bed retaining stud %s %s"%(x,y),(x,y,.089),.017,(0,0,1))
        side=[(-.802,.087),(-.784,.112),(-.705,.119),(-.683,.148),
              (-.656,.205),(-.652,.720),(-.628,.784),(-.593,.801),
              (-.508,.803),(-.493,.764),(-.49,.239),(-.477,.176),(-.448,.121),(-.421,.101),(-.421,.087)]
        self.prism("tapered standard",side,-.027,.092,self.iron,bevel=.007)
        for ix,(a,b) in enumerate(((-.049,-.026),(.093,.116))):
            self.prism("cast foot rib "+str(ix),
                       [(-.788,.089),(-.646,.089),(-.611,.134),(-.610,.52),
                        (-.644,.36),(-.688,.185),(-.735,.125),(-.788,.113)],
                       a,b,self.iron,bevel=.004)
        # The fixed eyes have a clear through bore; an actual cross pin remains
        # seated in them. Clevis webs terminate inside the outline of each eye.
        y,z=SADDLE_AXIS[1:]
        self.block("clevis lower cap",(-.061,-.659,.739),(.129,-.515,.775),self.dark,bevel=.005)
        for side_id,(a,b) in enumerate(((-.066,-.041),(.091,.116))):
            self.prism("offset clevis web "+str(side_id),
                       [(-.645,.757),(-.644,.806),(-.599,.833),(y-.021,.836),
                        (y-.012,.778),(-.508,.757),(-.542,.744)],
                       a,b,self.iron,bevel=.004)
            cx=.5*(a+b)
            half=.5*(b-a)
            self.turning("clevis eye "+str(side_id),(cx,y,z),(1,0,0),
                         [(.026,-half),(.048,-half),(.053,-half+.004),(.053,half-.004),
                          (.048,half),(.026,half)],self.iron,closed=True)
        self.turning("seated cross pin",SADDLE_AXIS,(1,0,0),
                     [(.021,-.130),(.024,-.125),(.024,.105),(.021,.11)],self.mill)
        self.turning("recessed journal thrust washer",SADDLE_AXIS,(1,0,0),
                     [(.026,-.105),(.062,-.105),(.067,-.099),(.067,-.094),(.058,-.09),(.026,-.09)],
                     self.dark,closed=True)
        self.turning("bronze witness ring",SADDLE_AXIS,(1,0,0),
                     [(.024,-.112),(.047,-.112),(.050,-.108),(.050,-.105),(.024,-.105)],
                     self.bronze,closed=True)
        self.turning("seated mounting bolt",SADDLE_AXIS,(1,0,0),
                     [(.026,-.139),(.032,-.134),(.032,-.115),(.028,-.112)],
                     self.mill,sides=6)
        self.turning("captive pin cap reverse",SADDLE_AXIS,(1,0,0),
                     [(.035,.090),(.040,.095),(.040,.100),(.033,.104)],self.mill)
        # A fixed index and an independently rotating bronze nick make the slip
        # readable in motion without enlarging the saddle movement.
        self.prism("stationary index",[(y-.009,z+.055),(y+.001,z+.055),(y-.003,z+.069)],
                   -.073,-.069,self.line,bevel=.0007)
        self.turning("saddle sleeve",SADDLE_AXIS,(1,0,0),
                     [(.025,-.064),(.041,-.064),(.050,-.059),(.050,.060),(.041,.065),(.025,.065)],
                     self.bronze,"saddle",closed=True)
        mid=top[len(top)//2][len(top[0])//2][2]
        for i,(a,b) in enumerate(((-.028,-.006),(.055,.077))):
            self.prism("rocking forged cheek "+str(i),
                       [(y-.011,z-.036),(y+.032,z-.044),(-.277,mid-.071),(-.214,mid-.062),
                        (-.208,mid-.025),(-.268,mid-.035),(y+.046,z+.023),(y+.006,z+.037)],
                       a,b,self.dark,"saddle",.004)
        self.prism("moving saddle index",[(y+.009,z+.034),(y+.024,z+.025),(y+.030,z+.051)],
                   -.037,-.033,self.bronze,"saddle",bevel=.001)
        self.shoe(top,.010,.016,self.iron,"cupped saddle shell")
        self.shoe(top,.0006,.010,self.pad,"shaped leather saddle liner")
        for ix, x in enumerate((-.079,.076)):
            self.turning("saddle end rivet "+str(ix),(x,-.224,mid-.028),(1,0,0),
                         [(.008,-.003),(.009,-.001),(.009,.002),(.007,.004)],self.bronze,"saddle",sides=20)

    def shoe(self, top, clearance, thickness, mat, name):
        width=len(top[0])
        count=len(top)*width
        vs=[(x,y,z-clearance-extra) for extra in (0,thickness)
            for row in top for x,y,z in row]
        fs=[]
        for j in range(len(top)-1):
            for i in range(width-1):
                n=j*width+i
                for face in ((n,n+1,n+width+1),(n,n+width+1,n+width)):
                    fs.extend([face,tuple(k+count for k in reversed(face))])
        border=list(range(width))+[j*width+width-1 for j in range(1,len(top))]
        border+=list(range(count-2,count-width-1,-1))
        border+=[j*width for j in range(len(top)-2,0,-1)]
        fs += [(i,i+count,j+count,j) for i,j in zip(border,border[1:]+border[:1])]
        return self.part(name,vs,fs,mat,"saddle",bevel=.0013)


def _fit_shoe(body):
    """Ray-sample only the visible ventral shell in native rest coordinates."""
    xs=tuple(-.074+.148*i/12 for i in range(13))
    ys=tuple(-.265+.054*j/8 for j in range(9))
    dg=bpy.context.evaluated_depsgraph_get()
    meshes=[]
    for ob in body:
        if ob.type!="MESH":
            continue
        bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
        if (max(p.x for p in bb)<min(xs) or min(p.x for p in bb)>max(xs) or
            max(p.y for p in bb)<min(ys) or min(p.y for p in bb)>max(ys) or
            max(p.z for p in bb)<.56 or min(p.z for p in bb)>.99):
            continue
        meshes.append((BVHTree.FromObject(ob,dg),ob.matrix_world.copy(),ob.matrix_world.inverted()))

    def height(x,y):
        hits=[]
        for tree,world,inv in meshes:
            at,_,_,_=tree.ray_cast(inv@Vector((x,y,.48)),inv.to_3x3()@Vector((0,0,1)))
            if at is not None:
                z=(world@at).z
                if .57<z<1.05:
                    hits.append(z)
        return min(hits) if hits else None

    heights=[[height(x,y) for x in xs] for y in ys]
    known=[(x,y,heights[j][i]) for j,y in enumerate(ys) for i,x in enumerate(xs) if heights[j][i] is not None]
    if not known:
        raise ValueError("No ventral shell under the saddle shoe")
    # A thin seam may be open between adjacent plate edges. Bridge only that
    # cell using its closest seated neighbours, keeping the pad coherent.
    for j,y in enumerate(ys):
        for i,x in enumerate(xs):
            if heights[j][i] is None:
                close=sorted(known,key=lambda p:(p[0]-x)**2+(p[1]-y)**2)[:4]
                heights[j][i]=sum(p[2] for p in close)/len(close)

    # A smooth broad pad alone can penetrate small overlapping armor hems.
    # Relieve each triangle locally wherever it rises above sampled metal.
    # Evaluating the same diagonal used by shoe() preserves its contact line.
    relief=[[0. for x in xs] for y in ys]
    for j in range(len(ys)-1):
        for i in range(len(xs)-1):
            z00,z10=heights[j][i:i+2]
            z01,z11=heights[j+1][i:i+2]
            for su in range(1,8):
                for sv in range(1,8):
                    u,v=su/8,sv/8
                    target=height(xs[i]*(1-u)+xs[i+1]*u,ys[j]*(1-v)+ys[j+1]*v)
                    if target is None:
                        continue
                    if u>=v:
                        predicted=z00*(1-u)+z10*(u-v)+z11*v
                        corners=((j,i),(j,i+1),(j+1,i+1))
                    else:
                        predicted=z00*(1-v)+z01*(v-u)+z11*u
                        corners=((j,i),(j+1,i),(j+1,i+1))
                    for a,b in corners:
                        relief[a][b]=max(relief[a][b],predicted-target)
    rows=[[(x,y,heights[j][i]-relief[j][i]) for i,x in enumerate(xs)] for j,y in enumerate(ys)]
    return rows


def _empty(collection,name,location,parent=None):
    ob=bpy.data.objects.new("FC | "+name,None)
    collection.objects.link(ob)
    ob.empty_display_type="CIRCLE"
    ob.empty_display_size=.045
    ob.location=location
    if parent:
        ob.parent=parent
        ob.matrix_parent_inverse=parent.matrix_world.inverted()
    bpy.context.view_layer.update()
    return ob


def _region(ob):
    tag=str(ob.get("fc_region",ob.get("cg1cRegion",""))).lower()
    if tag in {"head","neck","saddle","stand"}:
        return tag
    if tag in {"foot","leg","feet","talon","ground","fixed"} or ob.get("fc_rigid")=="fixed":
        return "ground"
    if tag in {"wing","shoulder","torso","body","mantle"}:
        return "torso"
    if "ground" in ob.name.lower():
        return "floor"
    raise ValueError(f"Visible mesh lacks First Choice or retained region: {ob.name!r}")


def apply_motion(cranial_pivot=ATLANTO):
    """Set up the rigid assembly, support, NLA strip and timeline on the active scene."""
    scene=bpy.context.scene
    if bpy.data.objects.get("FC | Torso"):
        raise ValueError("First Choice motion already exists in this file")
    scene.render.fps=FPS
    scene.render.fps_base=1
    scene.frame_start=0
    scene.frame_end=LAST_FRAME
    scene.frame_set(0)
    visible=[ob for ob in scene.objects if ob.type=="MESH" and not ob.hide_render and ob.visible_get()]
    grouped={}
    for ob in visible:
        region=_region(ob)
        grouped.setdefault(region,[]).append(ob)
    top=_fit_shoe(grouped["torso"])
    coll=bpy.data.collections.new("First Choice | seated support and motion")
    scene.collection.children.link(coll)
    anchors={}
    anchors["ground"]=_empty(coll,"Ground",(0,0,0))
    anchors["stand"]=_empty(coll,"Stand",(0,0,0))
    anchors["saddle"]=_empty(coll,"Saddle",SADDLE_AXIS,anchors["stand"])
    anchors["torso"]=_empty(coll,"Torso",HIP,anchors["ground"])
    anchors["neck"]=_empty(coll,"Neck",CERVICAL_BASE,anchors["torso"])
    anchors["head"]=_empty(coll,"Head",cranial_pivot,anchors["neck"])
    for region,anchor in anchors.items():
        anchor["fc_region"]=region
    # Parent each mesh once, keeping its exact native rest transform.
    for region,objects in grouped.items():
        if region=="floor":
            continue
        parent=anchors[region]
        for ob in objects:
            ob["fc_region"]=region
            world=ob.matrix_world.copy()
            ob.parent=parent
            ob.matrix_parent_inverse=parent.matrix_world.inverted()
            ob.matrix_basis=world
    Fixture(coll,anchors).build(top)
    for region,keys in POSE_KEYS.items():
        ob=anchors[region]
        ob.rotation_mode="XYZ"
        for frame,rx,ry,rz in keys:
            ob.rotation_euler=tuple(radians(a) for a in (rx,ry,rz))
            ob.keyframe_insert(data_path="rotation_euler",frame=frame,group=TRACK)
        data=ob.animation_data
        action=data.action
        action.name="First Choice | "+region
        slot=data.action_slot
        # Blender defaults to Bezier interpolation. Clamp handles so straight
        # holds stay quiet and the small joint rebounds cannot overshoot.
        for layer in action.layers:
            for strip in layer.strips:
                bag=strip.channelbag(slot)
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.handle_left_type="AUTO_CLAMPED"
                        key.handle_right_type="AUTO_CLAMPED"
        data.action=None
        track=data.nla_tracks.new()
        track.name=TRACK
        strip=track.strips.new(TRACK,0,action)
        strip.action_slot=slot
        strip.extrapolation='HOLD'
    for name,frame in [("Seated",0),("Saddle gives",36),("Weight leaves shoe",44),
                       ("Inspects the bolt",98),("Attention held",159),("Reseats",193),("Rest",247)]:
        scene.timeline_markers.new(name,frame=frame)
    scene.frame_set(0)
    bpy.context.view_layer.update()
    return {"anchors":anchors,"clip":TRACK,"fps":FPS,"last_frame":LAST_FRAME,"shoe_surface":top}
