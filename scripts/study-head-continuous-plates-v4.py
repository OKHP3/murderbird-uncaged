"""Bounded smooth head study; preserves frozen V7 except eight mesh datasets.

Plate parameters are authored interpretations, not reference measurements.
Run in Blender; the saved native is reviewed before any export or integration.
"""
from pathlib import Path
import hashlib, json, math, runpy, shutil
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend'
BASE_SHA='a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f'
HELPER=ROOT/'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA='39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
OUT=ROOT/'assets/models/uncaged-head-continuous-plates-study-v4'
AUDIT=ROOT/'assets/audit/head-continuous-plates-study-v4'
ALLOWED=[f'{prefix} {side}' for prefix in ('Forged orbital brow','Broad swept cheek band','Cere root transition') for side in (-1,1)]+['Profiled upper bill blade 0','Profiled upper bill blade 1']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p): return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def lerp_rows(rows,t):
    v=max(0,min(1,t))*(len(rows)-1); i=min(int(v),len(rows)-2); u=v-i
    p0,p1,p2,p3=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(len(rows)-1,i+2)]
    return [.5*(2*p1[k]+(-p0[k]+p2[k])*u+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u**3) for k in range(len(p1))]

def linear(rows,y):
    y=max(rows[0][0],min(rows[-1][0],y))
    for a,b in zip(rows,rows[1:]):
        if a[0]<=y<=b[0]:
            t=(y-a[0])/(b[0]-a[0]); return [a[k]+t*(b[k]-a[k]) for k in range(1,len(a))]
    raise AssertionError(y)

ROOF=[(-.465,1.867,.065),(-.370,1.938,.115),(-.272,1.970,.133),(-.161,1.967,.127),(-.049,1.923,.091),(.038,1.845,.033)]

def roof(x,y):
    z,w=linear(ROOF,y); return z-.039*(x/max(.025,w))**2

def closed_grid(outer,inner,along,across):
    stride=across+1; n=(along+1)*stride; verts=outer+inner; faces=[]
    for j in range(along):
        for k in range(across):
            a=j*stride+k; faces.extend([(a,a+1,a+1+stride,a+stride),(n+a+stride,n+a+1+stride,n+a+1,n+a)])
        a=j*stride; b=a+stride; faces.append((a,b,n+b,n+a))
        a=j*stride+across; b=a+stride; faces.append((b,a,n+a,n+b))
    for k in range(across):
        faces.append((k+1,k,n+k,n+k+1));a=along*stride+k;faces.append((a,a+1,n+a+1,n+a))
    return verts,faces

def apply_mesh(name,vertices,faces):
    obj=bpy.data.objects[name]; inv=obj.matrix_world.inverted(); mesh=obj.data
    materials=list(mesh.materials); mesh.clear_geometry();mesh.from_pydata([inv@Vector(p) for p in vertices],[],faces)
    mesh.materials.clear()
    for m in materials:mesh.materials.append(m)
    mesh.update(); bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
    assert all(p.area>1e-12 for p in mesh.polygons), f'Degenerate face: {name}'
    for p in mesh.polygons:p.use_smooth=True
    return {'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'minimumFaceArea':min(p.area for p in mesh.polygons)}

def host(name):
    o=bpy.data.objects[name];return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])

def brow(side):
    # Frame the upper orbit with a broad continuous plate. Host sampling only
    # determines depth; the regular YZ grid remains authored and monotonic.
    names=[f'Forged orbital mounting plate {side}',f'Swept temporal lamina {side} 0 0',f'Swept temporal lamina {side} 0 1','Overlapping nasal hood']+[f'Rounded swept crown lamina {i}' for i in range(4)]
    vertices=[];faces=[]
    for name in names:
        obj=bpy.data.objects[name];offset=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
    tree=BVHTree.FromPolygons(vertices,faces)
    path=[(-.275,1.834,.008),(-.302,1.883,.020),(-.369,1.902,.023),(-.435,1.877,.020),(-.472,1.844,.007)]
    along,across=48,8;samples=[]
    for j in range(along+1):
        t=j/along;y,z,w=lerp_rows(path,t);prev=lerp_rows(path,max(0,t-1/along));nxt=lerp_rows(path,min(1,t+1/along));dy,dz=nxt[0]-prev[0],nxt[1]-prev[1];mag=math.hypot(dy,dz)
        for k in range(across+1):
            off=(2*k/across-1)*w;yy=y-dz/mag*off;zz=z+dy/mag*off
            hit,_,_,_=tree.ray_cast(Vector((side*.4,yy,zz)),Vector((-side,0,0)),.4)
            if hit is None:
                near,_,_,_=tree.find_nearest(Vector((side*.12,yy,zz)));gap=math.hypot(near.y-yy,near.z-zz)
                assert gap<.020,f'Unsupported brow edge {gap}'
                x=abs(near.x)
            else:x=abs(hit.x)
            samples.append([x,yy,zz])
    for _ in range(16):
        previous=[p[0] for p in samples]
        for j in range(1,along):
            for k in range(across+1):
                i=j*9+k;neighbors=[previous[i-9],previous[i+9]]
                if k:neighbors.append(previous[i-1])
                if k<across:neighbors.append(previous[i+1])
                samples[i][0]=.5*previous[i]+.5*sum(neighbors)/len(neighbors)
    outer=[(side*(x+.008),y,z) for x,y,z in samples];inner=[(side*(x+.003),y,z) for x,y,z in samples]
    return closed_grid(outer,inner,along,across)

def cheek(side):
    tree=host(f'Forged orbital mounting plate {side}')
    along,across=48,8; samples=[];misses=[]
    for j in range(along+1):
        theta=.12-2.69*j/along
        for k in range(across+1):
            q=k/across; taper=math.sin(math.pi*j/along)**.6
            ry=.079+(.007+.009*taper)*q; rz=.063+(.005+.010*taper)*q
            y=-.369+ry*math.cos(theta);z=1.786+rz*math.sin(theta)
            hit,normal,index,distance=tree.ray_cast(Vector((side*.4,y,z)),Vector((-side,0,0)),.4)
            if hit is None:
                near,_,_,gap=tree.find_nearest(Vector((side*.15,y,z)))
                assert near is not None
                yz=math.hypot(near.y-y,near.z-z);misses.append(yz)
                assert yz<.013, f'Unsupported cheek rim {yz}'
                x=abs(near.x)
            else:x=abs(hit.x)
            samples.append([x,y,z])
    # Smooth only transverse depth; preserve a monotonic annular YZ grid and
    # its full optic keepout instead of collapsing rows onto a nearest edge.
    for _ in range(8):
        previous=[p[0] for p in samples]
        for j in range(1,along):
            for k in range(across+1):
                i=j*(across+1)+k;samples[i][0]=(previous[i-9]+2*previous[i]+previous[i+9])/4
    outside=[(side*(x+.006),y,z) for x,y,z in samples]
    inside=[(side*(x+.001),y,z) for x,y,z in samples]
    return closed_grid(outside,inside,along,across),{'rimSamplesOutsideMountProjection':len(misses),'maximumRimExtensionM':max(misses,default=0)}

def cere(side):
    # Continue the inherited nasal hood analytically along its lateral margin.
    # Each plate has one monotonic XY grid and an explicit metal return.
    profile=[(-.503,1.825,.042),(-.466,1.883,.076),(-.421,1.925,.086),(-.384,1.935,.070)]
    path=[(.060,-.425,.011),(.064,-.450,.012),(.056,-.477,.011),(.035,-.497,.006)]
    along,across=32,8;outside=[];inside=[]
    for j in range(along+1):
        x,y,w=lerp_rows(path,j/along);z0,host_width=linear(profile,y)
        for k in range(across+1):
            q=2*k/across-1;xx=x+q*w
            z=z0-.024*(xx/host_width)**2+.008+.001*(1-q*q)
            outside.append((side*xx,y,z));inside.append((side*xx,y,z-.005))
    return closed_grid(outside,inside,along,across),{'method':'Analytical continuation of inherited nasal hood surface; no per-vertex nearest-surface projection.'}


def render(native):
    bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
    sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.11,.12,.13)
    scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    for o in scene.objects:
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
        o.hide_set(False)
    cd=bpy.data.cameras.new('Read-only head camera');cam=bpy.data.objects.new('Read-only head camera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
    views=[]
    for name,position,target,scale in [('front',(0,-6,1.78),(0,-.3,1.78),1.05),('anatomical-right-profile',(-6,-.3,1.78),(0,-.3,1.78),1.1),('three-quarter',(-6,-3,2.4),(0,-.29,1.78),.88)]:
        cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
        p=AUDIT/f'{name}.png';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True);views.append({**art(p),'camera':{'position':position,'target':target,'ortho':scale}})
    return views

def main():
    assert sha(BASE)==BASE_SHA and sha(HELPER)==HELPER_SHA
    assert not OUT.exists() and not AUDIT.exists(),'Write-once study'
    h=runpy.run_path(str(HELPER),run_name='shared_snapshot');bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
    geometry={}
    for side in (-1,1):
        v,f=brow(side);geometry[f'Forged orbital brow {side}']=apply_mesh(f'Forged orbital brow {side}',v,f)
        (v,f),info=cheek(side);geometry[f'Broad swept cheek band {side}']={**apply_mesh(f'Broad swept cheek band {side}',v,f),**info}
    for name in ALLOWED[-2:]:
        obj=bpy.data.objects[name];assert len(obj.data.vertices)==57*40;changed=[]; original=[tuple(v.co) for v in obj.data.vertices]
        for j in range(57):
            t=.245*j/56 if name.endswith('0') else .25+.75*j/56
            if t>=.88:continue
            root=1 if t<=.20 else max(0,min(1,(.34-t)/.14));root=root*root*(3-2*root)
            middle=math.sin(math.pi*(t-.34)/.54)**2 if .34<t<.88 else 0
            width=1+.18*root+.26*middle
            for k in range(40):
                v=obj.data.vertices[j*40+k];v.co.x*=width
                if tuple(v.co)!=original[j*40+k]:changed.append(j*40+k)
        assert all(tuple(v.co)[1:]==old[1:] for v,old in zip(obj.data.vertices,original))
        if name.endswith('1'):assert all(tuple(obj.data.vertices[j*40+k].co)==original[j*40+k] for j in range(57) if .25+.75*j/56>=.88 for k in range(40))
        geometry[name]={'changedVertexIndices':changed,'yzProfileUnchanged':True,'distalTAtLeast088Unchanged':True}
    for side in (-1,1):
        (v,f),info=cere(side);geometry[f'Cere root transition {side}']={**apply_mesh(f'Cere root transition {side}',v,f),**info}
    for name in ('Neutral / edge.001','Neutral / plate.001'):bpy.data.materials[name].use_fake_user=True
    after=h['scene_snapshot']();assert before['empties']==after['empties'] and before['curves']==after['curves']
    assert set(before['meshes'])==set(after['meshes'])
    for name,b in before['meshes'].items():
        a=after['meshes'][name]
        assert (a==b) if name not in ALLOWED else all(a[k]==b[k] for k in a if k!='mesh'),name
    assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
    OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);native=OUT/'murderbird-head-continuous-plates-v4.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
    shutil.copy2(Path(__file__),AUDIT/'executed-generator.py')
    receipt={'status':'isolated neutral geometry proposal; visual and motion review pending','base':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'replace':ALLOWED,'add':[],'preservation':{'51PivotsUnchanged':True,'462GuidesUnchanged':True,'OtherMeshesUnchanged':True,'TransformOwnersMaterialsUnchanged':True,'SaveReloadSnapshotExact':True},'geometry':geometry,'limits':['Crown roof is analytically continued between original control stations; no illustration metrology.','Cheek is an explicitly modeled annular plate with smooth depth, not nearest-surface relocation.','The two pre-existing unused materials have fake-user retention only.','No clearance, browser, artistic acceptance, or publication claim.']}
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'saved':art(native)}),flush=True)
    receipt['views']=render(native);(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__':main()
