"""Constructed bill and mandible revision on the preserved V12 neck/body.

Authored interpretation of July head-only and owner resupplied target. Native
rigid pieces are editable and independently owned. No recovered dimensions or
likeness acceptance are asserted. Never overwrite an earlier attempt.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,runpy,shutil,sys,argparse
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='01');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
BASE=ROOT/'assets/models/uncaged-cervical-envelope-v12/attempt-02/murderbird-cervical-envelope-v12.blend'
BASE_SHA='28b18c810784a1e6872ef3743f16e5cff36e5aac66c01c9299e5195064ac7c60'
OUT=ROOT/f'assets/models/uncaged-constructed-head-v13/attempt-{args.attempt}'
AUDIT=ROOT/f'assets/audit/uncaged-constructed-head-v13/attempt-{args.attempt}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def point(p):
    x,y,z=p
    return Vector((x*1.14,y+.20*max(-.12,min(.12,y+.369))-.070*smooth((z-.68)/1.25)+.012*smooth((y+.28)/.23)*smooth((1.94-z)/.22),1.53+(z-1.65)*1.20+.010*smooth((y+.32)/.22)))
def sample(rows,t):
    u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);f=u-i
    return tuple(a+(b-a)*f for a,b in zip(rows[i],rows[i+1]))
def spline(rows,t):
    u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);v=u-i
    a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
    return tuple(.5*(2*b[k]+(-a[k]+c[k])*v+(2*a[k]-5*b[k]+4*c[k]-d[k])*v*v+(-a[k]+3*b[k]-3*c[k]+d[k])*v*v*v) for k in range(len(b)))
assert sha(BASE)==BASE_SHA and not OUT.exists() and not AUDIT.exists()
OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);shutil.copy2(__file__,AUDIT/'executed-generator.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='head_v13_helpers')
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();changed=[]
def replace(name,verts,faces):
    o=bpy.data.objects[name];inv=o.matrix_world.inverted();old=o.data
    mesh=bpy.data.meshes.new(name+' constructed v13');mesh.from_pydata([inv@point(p) for p in verts],[],faces);mesh.update()
    for mat in old.materials:mesh.materials.append(mat)
    o.data=mesh
    if not old.users:bpy.data.meshes.remove(old)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    for f in mesh.polygons:f.use_smooth=True
    changed.append(name)

# The inherited exterior edge stays at the same full profile; a deeper cutting
# edge and a broad side section replace the narrow rounded wedge. The real
# plate boundary is moved below the broad proximal face, with a separate hook.
outer=[(-.421,1.853),(-.493,1.839),(-.565,1.796),(-.624,1.738),(-.657,1.676),(-.665,1.618),(-.651,1.567),(-.625,1.535)]
inner=[(-.420,1.706),(-.468,1.681),(-.505,1.646),(-.549,1.626),(-.590,1.604),(-.617,1.579),(-.633,1.552),(-.625,1.535)]
widths=[(.079,),(.082,),(.075,),(.063,),(.048,),(.031,),(.014,),(.0008,)]
for index,(start,end) in enumerate([(0,.545),(.552,1)]):
    verts=[];faces=[];rows=56;n=40
    for j in range(rows+1):
        t=start+(end-start)*j/rows;oy,oz=sample(outer,t);iy,iz=sample(inner,t);w=sample(widths,t)[0]
        for k in range(n):
            a=math.tau*k/n;cross=1-2*abs((a+math.pi)%math.tau-math.pi)/math.pi;s=math.sin(a)
            # Broad flatter cheeks of the bill, smoothly joining dorsal and
            # cutting ridges. This changes actual section, not painted marks.
            x=w*math.copysign(abs(s)**.55,s)
            verts.append((x,(oy+iy)/2+(oy-iy)*cross/2,(oz+iz)/2+(oz-iz)*cross/2))
    for j in range(rows):
        for k in range(n):
            a=j*n+k;b=j*n+(k+1)%n;faces.append((a,b,b+n,a+n))
    faces.extend([tuple(reversed(range(n))),tuple(rows*n+k for k in range(n))])
    replace('Profiled upper bill blade '+str(index),verts,faces)

# A cheek-attached substantial rear arm, becoming a short lower cutting member.
# All coordinates here already include the earlier hinge raise: do not add it
# again. The true jaw pivot, journal and cap are unchanged.
jaw_path=[(-.302,1.755,.013,.012),(-.344,1.714,.024,.014),
          (-.400,1.676,.022,.014),(-.460,1.638,.019,.013),
          (-.518,1.610,.014,.012),(-.553,1.596,.009,.010),
          (-.576,1.594,.003,.006)]
for side in (-1,1):
    verts=[];faces=[];along=48;across=8;stride=across+1
    for skin in (0,1):
        for j in range(along+1):
            t=j/along;y,z,w,d=spline(jaw_path,t);a=spline(jaw_path,max(0,t-1/along));b=spline(jaw_path,min(1,t+1/along));dy,dz=b[0]-a[0],b[1]-a[1];mag=max(1e-8,math.hypot(dy,dz))
            for k in range(stride):
                u=k/across;off=(2*u-1)*w;yy=y-dz/mag*off;zz=z+dy/mag*off
                x=.128-.286*max(0,-yy-.310)+(.0025*math.sin(math.pi*u) if skin==0 else -d)
                verts.append((side*x,yy,zz))
    count=(along+1)*stride
    for j in range(along):
        for k in range(across):
            a=j*stride+k;b=a+1;c=b+stride;d=a+stride;faces.extend([(a,b,c,d),(count+d,count+c,count+b,count+a)])
        a=j*stride;b=a+stride;faces.append((a,b,count+b,count+a));a+=across;b+=across;faces.append((b,a,count+a,count+b))
    for k in range(across):
        faces.append((k+1,k,count+k,count+k+1));a=along*stride+k;faces.append((a,a+1,count+a+1,count+a))
    replace('Forked forged mandible '+str(side),verts,faces)
verts=[];faces=[];n=24
sections=[(-.541,1.600,.059,.004),(-.557,1.594,.055,.004),(-.573,1.591,.050,.003)]
for y,z,w,height in sections:
    for k in range(n):
        a=math.tau*k/n;verts.append((w*math.cos(a),y,z+height*math.sin(a)))
for j in range(len(sections)-1):
    for k in range(n):
        a=j*n+k;b=j*n+(k+1)%n;faces.append((a,b,b+n,a+n))
faces.extend([tuple(reversed(range(n))),tuple((len(sections)-1)*n+k for k in range(n))])
replace('Distal mandible bridge',verts,faces)

after=h['scene_snapshot']()
assert before['empties']==after['empties'] and before['curves']==after['curves']
for n,record in before['meshes'].items():
    if n not in changed:assert record==after['meshes'][n],n
    else:
        for k in record:
            if k!='mesh':assert record[k]==after['meshes'][n][k],(n,k)
native=OUT/'murderbird-constructed-head-v13.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'constructed head proposal, unapproved','base':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'changedMeshes':changed,'profiles':{'outer':outer,'inner':inner,'mandible':jaw_path,'bridge':sections},'preservation':{'52PivotsExact':True,'734OtherMeshesExact':True,'462InheritedGuidesExact':True,'editedMeshParentsTransformsMaterialsEligibilityExact':True,'saveReopenExact':True},'referenceScope':'July controls head construction; resupplied target controls resting expression. Pose and unillustrated topology are reconstructions.','limits':['Historical construction curves retained but do not trace revised bill/jaw meshes.','Bill root fastener seating and cheek/jaw/neck moving clearance require review.','Orbital surround, crown, body and legs remain unresolved; no texture finishing.'],'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def render(path,label):
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
    scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    for o in bpy.data.objects:
        o.hide_set(False)
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
    cd=bpy.data.cameras.new('Head comparison camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
    views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('profile',(-7.5,0,1.25),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('head',(-6,-3.5,2.45),(0,-.27,1.62),1.10),('head-profile',(-7.5,0,1.62),(0,-.27,1.62),.85)]
    for name,pos,target,scale in views:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;f=AUDIT/f'{label}-{name}.png';scene.render.filepath=str(f);bpy.ops.render.render(write_still=True);receipt['views'].append({**art(f),'camera':{'position':pos,'target':target,'scale':scale},'lighting':'neutral native Workbench'})
render(native,'after');render(BASE,'before');(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(BASE)==BASE_SHA
print(json.dumps(receipt['native']))
