"""Create a native-only, hash-bound head-construction study from frozen V7."""
from pathlib import Path
import bpy
import bmesh
import hashlib
import json
import math
import os
import statistics
import shutil
import struct
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend"
INVENTORY = ROOT / "assets/models/uncaged-alignment-v7/alignment-inventory.json"
HEAD_RECIPE = ROOT / "scripts/alignment-v6-head.py"
JULY = ROOT / "context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png"
MODEL_DIR = ROOT / "assets/models/uncaged-head-construction-study-v2"
AUDIT_DIR = ROOT / "assets/audit/head-construction-study-v2"
ATTEMPT = "attempt-05"
ATTEMPT_MODEL_DIR = MODEL_DIR / "iterations" / ATTEMPT
ATTEMPT_AUDIT_DIR = AUDIT_DIR / "iterations" / ATTEMPT
CANDIDATE = ATTEMPT_MODEL_DIR / "murderbird-head-construction-study-v2.blend"
PARTIAL_CANDIDATE = ATTEMPT_MODEL_DIR / "murderbird-head-construction-study-v2-partial.blend"
MANIFEST = ATTEMPT_AUDIT_DIR / "head-construction-study-v2.json"
PREMUTATION = ATTEMPT_AUDIT_DIR / "target-contracts-before-mutation.json"
SCRIPT_SNAPSHOT = ATTEMPT_AUDIT_DIR / "study-v7-head-construction.py"
EXPECTED = {
    "source": "a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f",
    "inventory": "9346323a07dd618dcb9680cf5d5d620aef1c6608c986a590a3a9aee90d550c5c",
    "headRecipe": "a921130111ac27f14f1ddda10328f7dd21bf2cffa1d4e34aee8d1756fd738472",
    "july": "47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9",
}
UNUSED_RETAINED_MATERIALS = {"Neutral / edge.001", "Neutral / plate.001"}
TARGETS = {
    "Forged orbital brow -1": "cranial-cover", "Forged orbital brow 1": "cranial-cover",
    "Cere root transition -1": "upper-bill", "Cere root transition 1": "upper-bill",
    "Broad swept cheek band -1": "head", "Broad swept cheek band 1": "head",
    "Overlapping nasal hood": "upper-bill",
    "Profiled upper bill blade 0": "upper-bill", "Profiled upper bill blade 1": "upper-bill",
}
CAMERAS = [
    {"name":"front-bilateral", "position":(0,-6,1.78), "target":(0,-.30,1.78), "ortho":1.05},
    {"name":"anatomical-right-profile", "position":(-6,-.30,1.78), "target":(0,-.30,1.78), "ortho":1.10},
    {"name":"anatomical-left-profile", "position":(6,-.30,1.78), "target":(0,-.30,1.78), "ortho":1.10},
    {"name":"three-quarter-a", "position":(-6,-3,2.4), "target":(0,-.29,1.78), "ortho":.88},
    {"name":"three-quarter-b", "position":(-6,-4.2,2.1), "target":(0,-.29,1.78), "ortho":.88},
]
FINAL_OUTPUTS = [CANDIDATE, PARTIAL_CANDIDATE, MANIFEST, PREMUTATION, SCRIPT_SNAPSHOT] + [
    ATTEMPT_AUDIT_DIR / f"{phase}-{spec['name']}.png" for phase in ("before", "after") for spec in CAMERAS
]
HEAD_SECTIONS = [(1.575,-.15,.065,.10),(1.65,-.20,.123,.185),(1.74,-.25,.149,.22),
                 (1.825,-.265,.153,.20),(1.915,-.24,.119,.175),(1.955,-.17,.025,.075)]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def serial(v):
    if isinstance(v,(str,int,float,bool)) or v is None: return v
    if hasattr(v,"to_list"): return [serial(x) for x in v.to_list()]
    try: return [serial(x) for x in v]
    except TypeError: return str(v)

def mesh_sig(mesh):
    coords=hashlib.sha256(); topo=hashlib.sha256()
    for v in mesh.vertices: coords.update(struct.pack('<3d',*v.co))
    for e in mesh.edges: topo.update(struct.pack('<2I',*e.vertices))
    for p in mesh.polygons:
        topo.update(struct.pack('<I',len(p.vertices))); topo.update(struct.pack('<%dI'%len(p.vertices),*p.vertices))
        topo.update(struct.pack('<i?',p.material_index,p.use_smooth))
    return {"name":mesh.name,"vertices":len(mesh.vertices),"edges":len(mesh.edges),"polygons":len(mesh.polygons),
            "coords":coords.hexdigest(),"topology":topo.hexdigest(),"materials":[m.name if m else None for m in mesh.materials]}

def obj_sig(o):
    if o.type=='MESH': data=mesh_sig(o.data)
    elif o.type=='CURVE':
        splines=[]
        for s in o.data.splines:
            if s.type=='BEZIER': points=[[list(p.co),list(p.handle_left),list(p.handle_right),p.handle_left_type,p.handle_right_type] for p in s.bezier_points]
            else: points=[list(p.co) for p in s.points]
            splines.append({"type":s.type,"cyclic":s.use_cyclic_u,"points":points})
        data={"name":o.data.name,"dimensions":o.data.dimensions,"resolutionU":o.data.resolution_u,
              "bevelDepth":o.data.bevel_depth,"splines":splines}
    else: data=o.data.name if o.data else None
    mods=[]
    for m in o.modifiers:
        props={k:serial(getattr(m,k)) for k in ("levels","render_levels","thickness","offset","width","segments","limit_method","angle_limit","use_clamp_overlap","use_even_offset") if hasattr(m,k)}
        mods.append({"name":m.name,"type":m.type,"properties":props})
    return {"type":o.type,"data":data,
            "parent":o.parent.name if o.parent else None,
            "matrixBasis":[float(x) for row in o.matrix_basis for x in row],
            "matrixParentInverse":[float(x) for row in o.matrix_parent_inverse for x in row],
            "location":list(o.location),"rotation":list(o.rotation_euler),"scale":list(o.scale),"rotationMode":o.rotation_mode,
            "parentType":o.parent_type,"hideRender":bool(o.hide_render),"props":{k:serial(o[k]) for k in sorted(o.keys())},"modifiers":mods}

def snapshot():
    mats=[]
    for m in bpy.data.materials:
        nodes=[]; links=[]
        if m.use_nodes and m.node_tree:
            for n in m.node_tree.nodes:
                vals=[]
                for s in n.inputs:
                    if s.enabled and hasattr(s,"default_value"): vals.append((s.identifier,serial(s.default_value)))
                nodes.append((n.name,n.bl_idname,sorted(vals)))
            links=sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links)
        mats.append((m.name,tuple(m.diffuse_color),m.metallic,m.roughness,m.use_nodes,m.use_fake_user,sorted(nodes),links))
    return {"objects":{o.name:obj_sig(o) for o in bpy.data.objects},"materials":sorted(mats)}

def spline(rows,t):
    x=max(0,min(1,t))*(len(rows)-1); i=min(int(x),len(rows)-2); u=x-i
    p0,p1=rows[max(0,i-1)],rows[i]; p2,p3=rows[i+1],rows[min(len(rows)-1,i+2)]
    return tuple(.5*(2*p1[k]+(-p0[k]+p2[k])*u+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u*u*u) for k in range(len(p1)))

def cranial_width(y,z):
    for a,b in zip(HEAD_SECTIONS,HEAD_SECTIONS[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]); cy=a[1]+(b[1]-a[1])*t; rx=a[2]+(b[2]-a[2])*t; ry=a[3]+(b[3]-a[3])*t; break
    else: cy,rx,ry=HEAD_SECTIONS[0][1:] if z<HEAD_SECTIONS[0][0] else HEAD_SECTIONS[-1][1:]
    q=(y-cy)/max(.05,ry)
    return rx*math.sqrt(max(.12,1-q*q))

def replace_mesh(obj, world_vertices, faces, smooth=False):
    inv=obj.matrix_world.inverted(); verts=[inv@Vector(v) for v in world_vertices]; materials=list(obj.data.materials)
    mesh=obj.data; mesh.clear_geometry(); mesh.from_pydata(verts,[],faces); mesh.materials.clear()
    for m in materials: mesh.materials.append(m)
    mesh.update(calc_edges=True)
    for p in mesh.polygons: p.use_smooth=smooth
    mesh.validate(clean_customdata=False)
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()

def triangle_origin_distance(a,b,c):
    def cross(u,v): return u[0]*v[1]-u[1]*v[0]
    signs=[cross((b[0]-a[0],b[1]-a[1]),(-a[0],-a[1])),
           cross((c[0]-b[0],c[1]-b[1]),(-b[0],-b[1])),
           cross((a[0]-c[0],a[1]-c[1]),(-c[0],-c[1]))]
    if all(v>=-1e-9 for v in signs) or all(v<=1e-9 for v in signs):
        return 0.0
    def seg(p,q):
        d=(q[0]-p[0],q[1]-p[1]); den=d[0]*d[0]+d[1]*d[1]
        t=max(0.0,min(1.0,(-p[0]*d[0]-p[1]*d[1])/max(1e-12,den)))
        return math.hypot(p[0]+t*d[0],p[1]+t*d[1])
    return min(seg(a,b),seg(b,c),seg(c,a))

def world_bvh(names):
    vertices=[]; faces=[]
    for name in names:
        obj=bpy.data.objects[name]
        if obj.type!='MESH': raise RuntimeError(f"Expected mesh host: {name}")
        offset=len(vertices); vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
    return BVHTree.FromPolygons(vertices,faces),vertices,faces

def project_outside_ring(y,z,margin=1.22):
    cy,cz=-.368269,1.782820; ry,rz=.058365,.057098
    dy=(y-cy)/ry; dz=(z-cz)/rz; r=math.hypot(dy,dz)
    if r<margin:
        scale=margin/max(1e-9,r); dy*=scale; dz*=scale
    return cy+dy*ry,cz+dz*rz

def closest_projected_triangle(side,y,z,vertices,faces):
    """Nearest YZ projection, breaking symmetric ties toward this side's outer skin."""
    best=None
    for face in faces:
        if len(face)<3: continue
        a0=vertices[face[0]]
        for q in range(1,len(face)-1):
            tri=[a0,vertices[face[q]],vertices[face[q+1]]]; pts=[(p.y,p.z) for p in tri]
            ax,ay=pts[0]; bx,by=pts[1]; cx,cy=pts[2]
            v0=(cx-ax,cy-ay); v1=(bx-ax,by-ay); v2=(y-ax,z-ay)
            d00=v0[0]**2+v0[1]**2; d01=v0[0]*v1[0]+v0[1]*v1[1]
            d02=v0[0]*v2[0]+v0[1]*v2[1]; d11=v1[0]**2+v1[1]**2; d12=v1[0]*v2[0]+v1[1]*v2[1]
            den=d00*d11-d01*d01
            if abs(den)<1e-18: continue
            u=(d11*d02-d01*d12)/den; v=(d00*d12-d01*d02)/den
            if u>=0 and v>=0 and u+v<=1:
                weights=(1-u-v,v,u); py,pz=y,z
            else:
                candidates=[]
                for i,j in ((0,1),(1,2),(2,0)):
                    p0,p1=pts[i],pts[j]; dx,dy2=p1[0]-p0[0],p1[1]-p0[1]
                    t=max(0,min(1,((y-p0[0])*dx+(z-p0[1])*dy2)/(dx*dx+dy2*dy2+1e-20)))
                    candidates.append(((y-p0[0]-t*dx)**2+(z-p0[1]-t*dy2)**2,i,j,t,p0[0]+t*dx,p0[1]+t*dy2))
                _,i,j,t,py,pz=min(candidates); weights=[0.,0.,0.]; weights[i]=1-t; weights[j]=t
            distance=math.hypot(py-y,pz-z)
            point=Vector((sum(weights[i]*tri[i].x for i in range(3)),py,pz))
            outer=side*point.x
            if best is None or distance<best[0]-1e-7 or (abs(distance-best[0])<=1e-7 and outer>best[2]):
                best=(distance,point,outer)
    return best

def fitted_band(side,path,host_bvh,host_vertices,host_faces,half_width=None,ring_keepout=False,lift=.005):
    along, across=56,12; stride=across+1; verts=[]; faces=[]
    outer=[]; closest_fallbacks=0; misses=[]; projection_corrections=[]
    for skin in (0,1):
        for j in range(along+1):
            t=j/along; y,z,w,depth=spline(path,t)
            prev=spline(path,max(0,t-1/along)); nxt=spline(path,min(1,t+1/along))
            dy,dz=nxt[0]-prev[0],nxt[1]-prev[1]; mag=max(1e-8,math.hypot(dy,dz))
            for k in range(stride):
                u=k/across; offset=(2*u-1)*max(.001,w)
                yy=y-dz/mag*offset; zz=z+dy/mag*offset
                if ring_keepout: yy,zz=project_outside_ring(yy,zz)
                projected=closest_projected_triangle(side,yy,zz,host_vertices,host_faces)
                if projected is None or projected[0]>.020:
                    misses.append({"row":j,"column":k,"y":yy,"z":zz,"nearestProjectedYzMeters":None if projected is None else float(projected[0])})
                    continue
                projection_gap,host_point,_=projected
                if side*host_point.x < -1e-5: raise RuntimeError(f"Projected host is on wrong anatomical side {side}: x={host_point.x}")
                projection_corrections.append(float(projection_gap))
                if projection_gap>1e-6: closest_fallbacks+=1
                surface=host_bvh.find_nearest(host_point)
                if surface[0] is None or surface[3]>.002: raise RuntimeError(f"Projected location misses 3D host: gap={None if surface[0] is None else surface[3]}")
                hit,normal,face_index,_=surface; normal=normal.normalized()
                if normal.x*side<0: normal.negate()
                if normal.x*side<.20: normal=(normal+Vector((side*.20,0,0))).normalized()
                # Offset along the measured surface normal so a sloped crown or
                # hood still gets a consistent 5 mm proud skin.
                point=hit+normal*(lift if skin==0 else .0005)
                verts.append(tuple(point))
                if skin==0: outer.append(tuple(point))
    if misses: raise RuntimeError(f"Fitted band missed supported host surface at {len(misses)} vertices; first misses: {misses[:4]}")
    base=(along+1)*stride
    for j in range(along):
        for k in range(across):
            a=j*stride+k; b=a+1; c=b+stride; d=a+stride
            faces.extend([(a,b,c,d),(base+d,base+c,base+b,base+a)])
        a=j*stride; b=(j+1)*stride; faces.append((a,b,base+b,base+a))
        a=j*stride+across; b=(j+1)*stride+across; faces.append((b,a,base+a,base+b))
    for k in range(across):
        faces.append((k+1,k,base+k,base+k+1)); a=along*stride+k; faces.append((a,a+1,base+a+1,base+a))
    outer_distances=[host_bvh.find_nearest(Vector(point))[3] for point in outer]
    return verts,faces,{"projectedVertexCount":len(projection_corrections),"maxProjectedYzCorrectionMeters":max(projection_corrections),"medianProjectedYzCorrectionMeters":statistics.median(projection_corrections),"closestFallbackCount":closest_fallbacks,"outerVertexCount":len(outer),"outerVertices":outer,
        "nearestHostGapMeters":{"min":min(outer_distances),"median":statistics.median(outer_distances),
                                "p90":sorted(outer_distances)[int(.9*len(outer_distances))],"max":max(outer_distances)}}

def ring_face_clearance(vertices,faces):
    cy,cz=-.368269,1.782820; ry,rz=.058365,.057098
    min_score=float('inf'); min_face=None
    for fi,face in enumerate(faces):
        if len(face)<3: continue
        for tri_i in range(1,len(face)-1):
            inds=(face[0],face[tri_i],face[tri_i+1])
            tri=[((vertices[i][1]-cy)/ry,(vertices[i][2]-cz)/rz) for i in inds]
            score=triangle_origin_distance(*tri)
            if score<min_score: min_score,min_face=score,fi
    return min_score,min_face

def mesh_bvh(world_vertices,faces):
    tris=[]
    for face in faces:
        if len(face)>=3:
            for i in range(1,len(face)-1): tris.append((face[0],face[i],face[i+1]))
    return BVHTree.FromPolygons([Vector(v) for v in world_vertices],tris)

def bridge_mesh(obj, side=0):
    # One continuous, thick crown-to-cere saddle. Its broad ends overlap the existing brow and bill root.
    rows=[(-.382,1.930,.043,.006),(-.414,1.921,.068,.008),(-.450,1.892,.071,.009),(-.484,1.854,.056,.008),(-.507,1.821,.028,.006)]
    along,across=40,16; stride=across+1; verts=[]; faces=[]
    for skin in (0,1):
        for j in range(along+1):
            y,z,w,d=spline(rows,j/along)
            for k in range(stride):
                u=2*k/across-1; x=w*u
                dome=.012*(1-u*u)
                zz=z+dome+(0 if skin==0 else -max(.006,d))
                verts.append((x,y,zz))
    base=(along+1)*stride
    for j in range(along):
        for k in range(across):
            a=j*stride+k; faces.extend([(a,a+1,a+1+stride,a+stride),(base+a+stride,base+a+1+stride,base+a+1,base+a)])
        a=j*stride; b=(j+1)*stride; faces.append((a,b,base+b,base+a))
        a=j*stride+across; b=(j+1)*stride+across; faces.append((b,a,base+a,base+b))
    for k in range(across):
        faces.append((k+1,k,base+k,base+k+1)); a=along*stride+k; faces.append((a,a+1,base+a+1,base+a))
    return verts,faces

def target_contracts(targets):
    return {n:{"type":o.type,"parent":o.parent.name if o.parent else None,"vertices":len(o.data.vertices),
               "polygons":len(o.data.polygons),"transform":{"basis":obj_sig(o)["matrixBasis"],"parentInverse":obj_sig(o)["matrixParentInverse"],"location":list(o.location),"rotation":list(o.rotation_euler),"scale":list(o.scale)},
               "materials":[m.name if m else None for m in o.data.materials],
               "inventory":inventory_by_name[n]} for n,o in sorted(targets.items())}

def create_candidate():
    for path,expected in [(SOURCE,EXPECTED['source']),(INVENTORY,EXPECTED['inventory']),(HEAD_RECIPE,EXPECTED['headRecipe']),(JULY,EXPECTED['july'])]:
        if not path.is_file() or sha(path)!=expected: raise RuntimeError(f"Frozen input hash mismatch: {path}")
    for d in (ATTEMPT_MODEL_DIR,ATTEMPT_AUDIT_DIR): d.mkdir(parents=True,exist_ok=True)
    found=[str(p) for p in FINAL_OUTPUTS if p.exists()]
    if found: raise RuntimeError(f"Refusing to overwrite existing study outputs: {found}")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE)); before=snapshot()
    targets={name:bpy.data.objects.get(name) for name in TARGETS}
    if any(o is None or o.type!='MESH' for o in targets.values()): raise RuntimeError("Exact nine-mesh target allowlist not found")
    for n,o in targets.items():
        if not o.parent or o.parent.name!=TARGETS[n]: raise RuntimeError(f"Owner mismatch for {n}")
    bill_source_coords={n:[tuple(v.co) for v in targets[n].data.vertices] for n in ("Profiled upper bill blade 0","Profiled upper bill blade 1")}
    # Prepare all regional geometry and exact masks before mutating any source mesh.
    generated={}; fit_reports={}; ring_reports={}
    crown_names=[f"Rounded swept crown lamina {i}" for i in range(4)]
    # Narrow the plate around the original sweep so every sampled span can land on
    # the actual cover silhouette instead of forcing unsupported lateral rails.
    brow_path=[(-.245,1.916,.007,.004),(-.278,1.944,.015,.004),(-.338,1.952,.020,.004),
               (-.392,1.923,.017,.004),(-.438,1.883,.010,.004),(-.452,1.865,.004,.004)]
    cheek_path=[(-.282,1.812,.008,.004),(-.298,1.766,.012,.004),(-.332,1.726,.014,.004),
                (-.382,1.719,.014,.004),(-.430,1.726,.012,.004),(-.467,1.763,.007,.004)]
    cere_path=[(-.411,1.856,.010,.004),(-.440,1.842,.019,.004),(-.474,1.827,.019,.004),(-.505,1.807,.009,.004)]
    for side in (-1,1):
        brow_hosts=crown_names+[f"Swept temporal lamina {side} 0 0",f"Swept temporal lamina {side} 0 1",
                                f"Forged orbital mounting plate {side}", "Overlapping nasal hood"]
        brow_tree,brow_vertices,brow_faces=world_bvh(brow_hosts)
        v,f,stats=fitted_band(side,brow_path,brow_tree,brow_vertices,brow_faces,lift=.005)
        generated[f"Forged orbital brow {side}"]=(v,f,True); fit_reports[f"Forged orbital brow {side}"]={k:val for k,val in stats.items() if k!="outerVertices"}; fit_reports[f"Forged orbital brow {side}"]["_outerVertices"]=stats["outerVertices"]
        mount_tree,mount_vertices,mount_faces=world_bvh([f"Forged orbital mounting plate {side}"])
        v,f,stats=fitted_band(side,cheek_path,mount_tree,mount_vertices,mount_faces,ring_keepout=True,lift=.005)
        screen_gap,screen_face=ring_face_clearance(v,f)
        if screen_gap < 1.12: raise RuntimeError(f"Cheek face intrudes optical projected keepout: {side}/{screen_gap}")
        ring_tree,_,_=world_bvh([f"Recessed orbital bearing {side}",f"Seated Advanced optic {side}"])
        cheek_tree=mesh_bvh(v,f); overlaps=ring_tree.overlap(cheek_tree)
        nearest=[ring_tree.find_nearest(Vector(p))[3] for p in v]
        if overlaps or min(nearest)<.003: raise RuntimeError(f"Cheek intersects/approaches optic ring too closely: side={side}, overlaps={len(overlaps)}, min={min(nearest)}")
        ring_reports[str(side)]={"projectedFaceClearanceMinimumRadii":screen_gap,"closestFaceIndex":screen_face,
            "projectedVertexMinimumRadius":min(math.hypot((p[1]+.368269)/.058365,(p[2]-1.782820)/.057098) for p in v),
            "bvhTriangleOverlapCount":len(overlaps),"minimumWorldSurfaceDistanceMeters":min(nearest)}
        generated[f"Broad swept cheek band {side}"]=(v,f,True); fit_reports[f"Broad swept cheek band {side}"]={k:val for k,val in stats.items() if k!="outerVertices"}; fit_reports[f"Broad swept cheek band {side}"]["_outerVertices"]=stats["outerVertices"]
        cere_tree,cere_vertices,cere_faces=world_bvh(["Overlapping nasal hood","Profiled upper bill blade 0","Profiled upper bill blade 1"])
        v,f,stats=fitted_band(side,cere_path,cere_tree,cere_vertices,cere_faces,lift=.005)
        generated[f"Cere root transition {side}"]=(v,f,True); fit_reports[f"Cere root transition {side}"]={k:val for k,val in stats.items() if k!="outerVertices"}; fit_reports[f"Cere root transition {side}"]["_outerVertices"]=stats["outerVertices"]
    region_masks={}
    for name in ("Forged orbital brow -1","Forged orbital brow 1","Cere root transition -1","Cere root transition 1",
                 "Broad swept cheek band -1","Broad swept cheek band 1"):
        region_masks[name]={"region":"whole existing mesh","vertexIndices":list(range(len(targets[name].data.vertices)))}
    bill0=targets['Profiled upper bill blade 0']; bill1=targets['Profiled upper bill blade 1']; rows,cols=57,40
    if len(bill0.data.vertices)!=rows*cols or len(bill1.data.vertices)!=rows*cols: raise RuntimeError("Unexpected native bill blade grid")
    bill0_root=[]; bill1_root=[]; bill1_mid=[]; bill1_contact=[]
    for j in range(rows):
        t0=.245*j/(rows-1); t1=.25+.75*j/(rows-1)
        (bill0_root if t0<.34 else []).extend(range(j*cols,(j+1)*cols))
        if t1<.34: bill1_root.extend(range(j*cols,(j+1)*cols))
        elif t1<.88: bill1_mid.extend(range(j*cols,(j+1)*cols))
        else: bill1_contact.extend(range(j*cols,(j+1)*cols))
    region_masks['Profiled upper bill blade 0']={"rootTBelow034":bill0_root}
    region_masks['Profiled upper bill blade 1']={"rootTBelow034":bill1_root,"middlePlaneT034To088":bill1_mid,"preservedContactApexTAtLeast088":bill1_contact}
    PREMUTATION.write_text(json.dumps({"sourceSha256":EXPECTED['source'],"targets":target_contracts(targets),
        "sourceGeometrySignatures":{n:before['objects'][n]['data'] for n in sorted(TARGETS)},"regionalVertexMasks":region_masks,
        "fitPreflight":fit_reports,"opticKeepoutPreflight":ring_reports,
        "unreferencedMaterialsRetainedOnSave":[{"name":n,"sourceUsers":bpy.data.materials[n].users,
          "sourceFakeUser":bpy.data.materials[n].use_fake_user,
          "signature":next(row for row in before['materials'] if row[0]==n)} for n in sorted(UNUSED_RETAINED_MATERIALS)],
        "note":"Exact native object identities, owners, transforms, source geometry signatures, material slots and regional vertex masks recorded before mutation. Only the two confirmed zero-user material datablocks receive fake-user retention for Blender round-trip; shader nodes, values, names and assignments remain unchanged."},indent=2)+"\n")
    for name in ("Forged orbital brow -1","Forged orbital brow 1","Cere root transition -1","Cere root transition 1",
                 "Broad swept cheek band -1","Broad swept cheek band 1"):
        v,f,smooth=generated[name]; replace_mesh(targets[name],v,f,smooth)
    # Broaden only the existing upper-bill roots and side planes; preserve the entire Y/Z profile.
    intended_bill_masks={"Profiled upper bill blade 0":[],"Profiled upper bill blade 1":[]}
    for name in ("Profiled upper bill blade 0","Profiled upper bill blade 1"):
        obj=targets[name]; rows=57; cols=40
        if len(obj.data.vertices)!=rows*cols: raise RuntimeError(f"Unexpected bill blade topology: {name}")
        for j in range(rows):
            t=(.245*j/(rows-1)) if name.endswith('0') else (.25+.75*j/(rows-1))
            if name.endswith('0'):
                if t>=.34: continue
                weight=1.0 if t<=.20 else (lambda x: x*x*(3-2*x))(max(0.0,min(1.0,(.34-t)/.14)))
                amount=.18*weight
            else:
                if t>=.88: continue
                root_weight=1.0 if t<=.20 else (lambda x: x*x*(3-2*x))(max(0.0,min(1.0,(.34-t)/.14))) if t<.34 else 0.0
                middle_weight=math.sin(math.pi*(t-.34)/(.88-.34))**2 if .34<t<.88 else 0.0
                amount=.18*root_weight+.26*middle_weight
            for k in range(cols):
                v=obj.data.vertices[j*cols+k]
                v.co.x *= (1.0+amount)
                if abs(amount)>1e-9: intended_bill_masks[name].append(j*cols+k)
    # Save a held diagnostic native immediately after the requested geometry is built,
    # before later checks can fail. Never replace it with a later attempt.
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(PARTIAL_CANDIDATE),check_existing=False)
    actual_bill_masks={}
    for name in bill_source_coords:
        original=bill_source_coords[name]; current=[tuple(v.co) for v in targets[name].data.vertices]
        actual=[i for i,(a,b) in enumerate(zip(original,current)) if a!=b]
        allowed=set(region_masks[name].get("rootTBelow034",[]))|set(region_masks[name].get("middlePlaneT034To088",[]))
        if not set(actual).issubset(allowed): raise RuntimeError(f"Bill vertices changed outside recorded masks: {name}")
        if name.endswith('1') and any(original[i]!=current[i] for i in region_masks[name]['preservedContactApexTAtLeast088']):
            raise RuntimeError("Upper bill contact/apex vertices t>=0.88 changed")
        if any(a[1:]!=b[1:] for a,b in zip(original,current)):
            raise RuntimeError(f"Bill Y/Z dorsal profile or center contact plane changed: {name}")
        actual_bill_masks[name]=actual
    final_host_sets={}
    for side in (-1,1):
        final_host_sets[f"Forged orbital brow {side}"]=crown_names+[f"Swept temporal lamina {side} 0 0",f"Swept temporal lamina {side} 0 1",f"Forged orbital mounting plate {side}"]
        final_host_sets[f"Broad swept cheek band {side}"]=[f"Forged orbital mounting plate {side}"]
        final_host_sets[f"Cere root transition {side}"]=["Overlapping nasal hood","Profiled upper bill blade 0","Profiled upper bill blade 1"]
    for band,host_names in final_host_sets.items():
        host_final,_,_=world_bvh(host_names)
        distances=[host_final.find_nearest(Vector(p))[3] for p in fit_reports[band].pop("_outerVertices")]
        fit_reports[band]["finalHostSurfaceGapMeters"]={"min":min(distances),"median":statistics.median(distances),"p90":sorted(distances)[int(.9*len(distances))],"max":max(distances)}
        if min(distances)<.002 or max(distances)>.008: raise RuntimeError(f"Final host fit gap out of 2-8 mm band: {band} {fit_reports[band]['finalHostSurfaceGapMeters']}")
    after=snapshot(); changed={n for n in before['objects'] if before['objects'][n]!=after['objects'][n]}
    if not changed.issubset(set(TARGETS)): raise AssertionError(f"Out-of-allowlist mutation: {sorted(changed-set(TARGETS))}")
    assert before['materials']==after['materials'],"Material data changed during geometry mutation"
    for n in TARGETS:
        a,b=before['objects'][n],after['objects'][n]
        for key in ('type','parent','matrixBasis','matrixParentInverse','location','rotation','scale','rotationMode','hideRender','props','modifiers'):
            assert a[key]==b[key],f"Target metadata changed: {n}/{key}"
        assert a['data']['materials']==b['data']['materials'],f"Target materials changed: {n}"
    for n in before['objects'].keys()-set(TARGETS): assert before['objects'][n]==after['objects'][n],f"Unchanged object differs: {n}"
    unused={m.name for m in bpy.data.materials if m.users==0 and not m.use_fake_user}
    if unused!=UNUSED_RETAINED_MATERIALS:
        raise RuntimeError(f"Unexpected unreferenced material datablocks: {sorted(unused)}")
    for name in sorted(unused): bpy.data.materials[name].use_fake_user=True
    bpy.context.view_layer.update()
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),check_existing=False)
    saved=snapshot(); cand_sha=sha(CANDIDATE)
    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE)); reloaded=snapshot()
    assert saved==reloaded,"Saved candidate differs after reload"
    reloaded_changes={n for n in before['objects'] if before['objects'][n]!=reloaded['objects'][n]}
    assert reloaded_changes==changed
    return before,reloaded,cand_sha,{"actualChangedObjects":sorted(changed),"actualBillVertexChanges":actual_bill_masks,"intendedBillVertexMasks":intended_bill_masks,"fit":fit_reports,"opticKeepout":ring_reports}

def render(blend,phase):
    bpy.ops.wm.open_mainfile(filepath=str(blend)); scene=bpy.context.scene; scene.frame_set(1)
    scene.render.engine='BLENDER_WORKBENCH'; sh=scene.display.shading; sh.light='STUDIO'; sh.studio_light='paint.sl'; sh.color_type='MATERIAL'
    sh.show_shadows=True; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.curvature_ridge_factor=1.2; sh.curvature_valley_factor=1.1
    sh.background_type='WORLD'; scene.world.color=(.11,.12,.13); scene.render.resolution_x=1100; scene.render.resolution_y=1100
    scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    for o in scene.objects:
        if o.type=='MESH': o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
        o.hide_set(False)
    camdata=bpy.data.cameras.new('Head construction study camera'); cam=bpy.data.objects.new('Head construction study camera',camdata); scene.collection.objects.link(cam); scene.camera=cam
    rows=[]
    for spec in CAMERAS:
        cam.location=spec['position']; cam.rotation_euler=(Vector(spec['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
        camdata.type='ORTHO'; camdata.ortho_scale=spec['ortho']; out=ATTEMPT_AUDIT_DIR/f"{phase}-{spec['name']}.png"; scene.render.filepath=str(out)
        bpy.ops.render.render(write_still=True); rows.append({"path":str(out.relative_to(ROOT)),"sha256":sha(out),"bytes":out.stat().st_size,"camera":{**spec,"projection":"ORTHO","resolution":[1100,1100]}})
    return rows

if os.environ.get("HEAD_STUDY_DIAG") == "1":
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE)); baseline=snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE)); candidate_snapshot=snapshot()
    diffs={}
    for name in sorted(set(baseline['objects'])|set(candidate_snapshot['objects'])):
        a=baseline['objects'].get(name); b=candidate_snapshot['objects'].get(name)
        if a!=b:
            fields=sorted(k for k in set(a or {})|set(b or {}) if (a or {}).get(k)!=(b or {}).get(k))
            diffs[name]=fields
    print(json.dumps({"changedObjects":sorted(diffs),"fieldDifferences":diffs,
                      "materialDifference":baseline['materials']!=candidate_snapshot['materials']}))
    raise SystemExit(0)

inventory=json.loads(INVENTORY.read_text()); inventory_by_name={item['name']:item for item in inventory['parts'] if item['name'] in TARGETS}
if set(inventory_by_name)!=set(TARGETS): raise RuntimeError("Inventory does not contain every exact allowlisted target")
before,candidate,candidate_sha,geometry_checks=create_candidate()
before_views=render(SOURCE,'before'); after_views=render(CANDIDATE,'after')
if sha(SOURCE)!=EXPECTED['source'] or sha(CANDIDATE)!=candidate_sha: raise RuntimeError("Input/output changed during study")
shutil.copy2(Path(__file__).resolve(),SCRIPT_SNAPSHOT)
manifest={
 "title":"V7 native head-construction study V2",
 "status":"isolated editable native-only proposal; held for review; no GLB, runtime integration, or acceptance",
 "source":{"nativeBlend":{"path":str(SOURCE.relative_to(ROOT)),"sha256":EXPECTED['source']},
           "nativeInventory":{"path":str(INVENTORY.relative_to(ROOT)),"sha256":EXPECTED['inventory']},
           "headRecipe":{"path":str(HEAD_RECIPE.relative_to(ROOT)),"sha256":EXPECTED['headRecipe']},
           "julyReference":{"path":str(JULY.relative_to(ROOT)),"sha256":EXPECTED['july'],"scope":"head only"}},
 "attempt":ATTEMPT,
 "candidate":{"path":str(CANDIDATE.relative_to(ROOT)),"sha256":candidate_sha,"bytes":CANDIDATE.stat().st_size},
 "scriptSnapshot":{"path":str(SCRIPT_SNAPSHOT.relative_to(ROOT)),"sha256":sha(SCRIPT_SNAPSHOT)},
 "preMutationContracts":{"path":str(PREMUTATION.relative_to(ROOT)),"sha256":sha(PREMUTATION)},
 "changeAllowlist":sorted(TARGETS),"targetOwners":TARGETS,
 "roundTripRetentionException":{"materials":sorted(UNUSED_RETAINED_MATERIALS),"change":"fake-user flag only, to retain two source zero-user material datablocks across Blender save/reload","shaderNodesValuesAndAssignmentsPreserved":True},
 "verification":{"onlyAllowlistedMeshGeometryChanged":True,"allNonallowlistedNativeObjectsPreservedExactly":True,
                 "allObjectTransformsAndAssignmentsPreservedExactly":True,"allMaterialShaderSignaturesAndMeshAssignmentsPreservedExactly":True,
                 "candidateReloadedAndCompared":True,
                 "beforeAfterUseMatchedCameras":True,"distalBillBladeRowsAboveStudyRootT034Unchanged":True,
                 "jawOpticsCrownPivotsAndContactObjectDataUnchanged":True},
 "geometryChecks":geometry_checks,
 "renders":{"before":before_views,"after":after_views},
 "limits":["The July illustration guides head construction only; it is not exact-dimensional evidence.",
           "These are neutral static authoring renders, not runtime, shader, or animation evidence.",
           "Jaw, optic and crown native data were preserved, but full authored-motion collision checks were not run on this proposal.",
           "Visual coherence, opening clearance and likeness remain review questions; a preservation hash is not artistic acceptance."]}
MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"candidate":str(CANDIDATE),"sha256":candidate_sha,"changedObjects":sorted(TARGETS),"beforeViews":len(before_views),"afterViews":len(after_views)}))
