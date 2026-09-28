"""Versioned stepped optic enclosure and swept rigid crown on V13.

July governs this head-only reconstruction. Each complete optic assembly is
reseated inward without changing its internal fit; motion joints and body stay fixed. Faceted socket walls and thinner crown guards are geometry,
not a texture pass. Authoring dimensions are proposals, not image metrology.
"""
from pathlib import Path
import argparse,sys,math,hashlib,json,runpy,shutil
import bpy,bmesh
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='01');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
BASE=ROOT/'assets/models/uncaged-constructed-head-v13/attempt-01/murderbird-constructed-head-v13.blend'
SHA='32f9af41c93603ebdad3b12148c432acfe8c896b338364fdc9cf73700c918d27'
OUT=ROOT/f'assets/models/uncaged-orbital-crown-v14/attempt-{args.attempt}'
AUDIT=ROOT/f'assets/audit/uncaged-orbital-crown-v14/attempt-{args.attempt}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def point(p):
    x,y,z=p
    return Vector((x*1.14,y+.20*max(-.12,min(.12,y+.369))-.070*smooth((z-.68)/1.25)+.012*smooth((y+.28)/.23)*smooth((1.94-z)/.22),1.53+(z-1.65)*1.20+.010*smooth((y+.32)/.22)))
def sample(rows,t):
    u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);v=u-i
    a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
    return Vector([.5*(2*b[k]+(-a[k]+c[k])*v+(2*a[k]-5*b[k]+4*c[k]-d[k])*v*v+(-a[k]+3*b[k]-3*c[k]+d[k])*v*v*v) for k in range(len(b))])
def closed_grid(front,back,along,across):
    verts=front+back;faces=[];s=across+1;n=(along+1)*s
    for j in range(along):
        for k in range(across):
            a=j*s+k;faces.extend([(a,a+1,a+s+1,a+s),(n+a+s,n+a+s+1,n+a+1,n+a)])
        a=j*s;b=a+s;faces.append((a,b,n+b,n+a));a+=across;b+=across;faces.append((b,a,n+a,n+b))
    for k in range(across):
        faces.append((k+1,k,n+k,n+k+1));a=along*s+k;faces.append((a,a+1,n+a+1,n+a))
    return verts,faces
assert sha(BASE)==SHA and not OUT.exists() and not AUDIT.exists()
OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);shutil.copy2(__file__,AUDIT/'executed-generator.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='orbital_crown_helpers')
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();changes={};old_owners={}
def world(o):return [o.matrix_world@v.co for v in o.data.vertices]
def install(name,verts,faces,hard=False):
    o=bpy.data.objects[name];old=o.data;inv=o.matrix_world.inverted();m=bpy.data.meshes.new(name+' v14')
    m.from_pydata([inv@p for p in verts],[],faces)
    for mat in old.materials:m.materials.append(mat)
    m.update();o.data=m
    if not old.users:bpy.data.meshes.remove(old)
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
    for f in m.polygons:f.use_smooth=not hard
    changes.setdefault(name,{})['vertices']=len(m.vertices)
def reposition(name,points):
    o=bpy.data.objects[name];inv=o.matrix_world.inverted()
    for v,p in zip(o.data.vertices,points):v.co=inv@p
    o.data.update();changes.setdefault(name,{})['vertices']=len(o.data.vertices)
def tree(names):
    pts=[];faces=[]
    for n in names:
        o=bpy.data.objects[n];offset=len(pts);pts.extend(world(o));faces.extend(tuple(offset+i for i in f.vertices) for f in o.data.polygons)
    return BVHTree.FromPolygons(pts,faces)

# Recess the complete optic assembly 35 mm inside the surrounding cranial
# envelope. This corrects the projecting earphone appearance seen front-on.
# Internal lens / bearing / passive-housing dimensions and era tags stay intact.
OPTIC_INSET=.035
OPTIC_RAISE=.060
for side in (-1,1):
    for prefix in ('Recessed orbital bearing','Seated passive optic housing','Seated Advanced optic'):
        name=f'{prefix} {side}';o=bpy.data.objects[name]
        reposition(name,[p+Vector((-side*OPTIC_INSET,0,OPTIC_RAISE)) for p in world(o)])
        changes[name].update({'rigidWorldTranslation':[-side*OPTIC_INSET,0,OPTIC_RAISE],'shapeUnchanged':True})
# The advanced-only processing rack used to cross the newly recessed optic.
# Narrow its complete set of rails/boards coherently into the inner skull; the
# owner, upgrade eligibility, fastening topology and inspection pivot stay put.
for o in list(bpy.data.objects):
    if o.type=='MESH' and o.parent and o.parent.name=='processing':
        reposition(o.name,[Vector((p.x*.68,p.y,p.z)) for p in world(o)])
        changes[o.name].update({'worldWidthScale':.68,'construction':'advanced processing rack resized inside recessed optic housings'})
# Keep paired aperture edges fitted to those relocated assemblies; the outer
# return stays at its original supporting cranial envelope.
socket_centres={}
for side in (-1,1):
    name=f'Forged orbital mounting plate {side}';o=bpy.data.objects[name];old=world(o);assert len(old)==896
    inner=[old[i*7] for i in range(64)];centre=sum(inner,Vector())/64;socket_centres[side]=centre+Vector((0,0,OPTIC_RAISE))
    verts=[]
    for skin in (0,1):
        for i in range(64):
            p=old[skin*448+i*7];dy=inner[i].y-centre.y;dz=inner[i].z-centre.z;a=math.atan2(dz,dy)
            # A relieved rear-lower corner leaves the actual jaw journal clear.
            radial=1.10+.40*max(0,math.sin(a))+.55*max(0,-math.cos(a))-.04*max(0,math.cos(a))*max(0,-math.sin(a))
            outer_x=abs(p.x)-.009-.046*max(0,-math.cos(a))**3
            for j,f in enumerate([0,.13,.23,.36,.62,.82,1]):
                r=1+(radial-1)*f
                x=[abs(p.x),abs(p.x)+.001,abs(p.x)+.005,abs(p.x)+.005,abs(p.x)+.001,(abs(p.x)+outer_x)/2-.002,outer_x][j]
                verts.append(Vector((side*(x-OPTIC_INSET*(1-f)**.65),centre.y+dy*r,centre.z+dz*r+OPTIC_RAISE*(1-.70*f*max(0,math.sin(a))))))
    faces=[tuple(f.vertices) for f in o.data.polygons]
    install(name,verts,faces,hard=True)
    assert max((verts[i*7]-(old[i*7]+Vector((-side*OPTIC_INSET,0,OPTIC_RAISE)))).length for i in range(64))<1e-7
    assert max((verts[448+i*7]-(old[448+i*7]+Vector((-side*OPTIC_INSET,0,OPTIC_RAISE)))).length for i in range(64))<1e-7
    changes[name].update({'apertureShapesExact':True,'apertureRigidInsetM':OPTIC_INSET,'apertureRigidRiseM':OPTIC_RAISE,'construction':'seven-station rigid socket wall; faceted lip and recessed outer return','centreWorld':list(centre)})

# A broad diagonal brow remains fixed around the eye while the crown opens.
# This explicitly changes only the two brow ownership relationships.
UPPER=[(.104,-.278,1.929),(.098,-.329,1.939),(.081,-.388,1.920),(.084,-.440,1.883),(.064,-.482,1.837)]
LOWER=[(.162,-.287,1.885),(.173,-.331,1.890),(.158,-.389,1.866),(.131,-.439,1.826),(.104,-.482,1.792)]
def brow_point(side,t,u):
    p=sample(UPPER,t).lerp(sample(LOWER,t),u);p.x*=side;p=point(p);p.x*=.70;p.z-=.020;return p
for side in (-1,1):
    name=f'Forged orbital brow {side}';o=bpy.data.objects[name];m=o.matrix_world.copy();old_owners[name]=o.parent.name
    o.parent=bpy.data.objects['head'];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=m;bpy.context.view_layer.update()
    front=[];back=[]
    for j in range(41):
        for k in range(9):
            p=brow_point(side,j/40,k/8);front.append(p);back.append(p-Vector((side*.006,0,0)))
    verts,faces=closed_grid(front,back,40,8);install(name,verts,faces)
    changes[name].update({'previousOwner':old_owners[name],'owner':'head','worldWidthScale':.70,'underlapDropM':.020,'wallM':.006,'construction':'fixed sloping brow above rigidly recessed optic; independently opening crown behind'})

# Reshape the complete crown substrate and its plates coherently. The nape
# moves aft/up and the high rear dome flattens. All head/motion pivots stay put.
def crown_point(p):
    q=p.copy();rear=smooth((p.y+.46)/.50);lower=smooth((1.96-p.z)/.46)
    q.y+=.025*rear*lower;q.z+=.045*rear*lower-.013*rear*smooth((p.z-1.82)/.13)
    return q
for o in list(bpy.data.objects):
    if o.type!='MESH' or not o.parent or o.parent.name!='cranial-cover':continue
    old=world(o)
    if 'pin' in o.name.lower():
        centre=sum(old,Vector())/len(old);delta=crown_point(centre)-centre;new=[p+delta for p in old]
    else:new=[crown_point(p) for p in old]
    if o.name.startswith(('Swept temporal lamina','Rounded swept crown lamina')):
        half=len(new)//2;assert len(new)%18==0
        rows=half//9
        # Verified original closed 9-column strip: same front/back vertex
        # correspondence, with finite thinner walls and a sharper aft tongue.
        for j in range(rows):
            t=j/(rows-1);tip=smooth((t-.61)/.39)
            centres=[sum(new[skin*half+j*9:skin*half+(j+1)*9],Vector())/9 for skin in (0,1)]
            for k in range(9):
                idx=j*9+k
                for skin in (0,1):
                    i=skin*half+idx;p=new[i];p=centres[skin]+(p-centres[skin])*(1-.35*tip)
                    p.y+=.006*tip;new[i]=p
                wall=new[half+idx]-new[idx]
                assert wall.length>1e-6
                new[half+idx]=new[idx]+wall.normalized()*.004
        changes[o.name]={'wallM':.004,'construction':'thinner swept rigid guard; narrowed aft tongue','rows':rows,'columns':9}
    reposition(o.name,new)

# Seat the retained cheek strips on the new socket: both skins translate
# together in X so their thickness and YZ contour survive. Explicitly retain
# any terminal overhang; do not collapse vertices onto nearest edges.
for side in (-1,1):
    name=f'Broad swept cheek band {side}';o=bpy.data.objects[name];pts=world(o)
    for p in pts:p.z+=.045*smooth((-p.y-.350)/.160)
    half=len(pts)//2;t=tree([f'Forged orbital mounting plate {side}'])
    matched=0;overhang=[]
    for i in range(half):
        p=pts[i];hit,_,_,_=t.ray_cast(Vector((side*.4,p.y,p.z)),Vector((-side,0,0)),.5)
        if hit is None:overhang.append(i);continue
        delta=side*(abs(hit.x)+.004-abs(p.x));pts[i].x+=delta;pts[i+half].x+=delta;matched+=1
    reposition(name,pts);changes[name].update({'seatedVertexPairs':matched,'terminalOverhangPairs':len(overhang),'forwardCheekRiseM':.045,'rearAttachmentPreserved':True})

# Reseat retained cheek fixings at three actual centre-strip vertices. The
# old front fixing was outside its supporting strip; do not preserve that miss.
for side in (-1,1):
    host=bpy.data.objects[f'Broad swept cheek band {side}'];host_points=world(host)
    assert len(host_points)==882
    targets=sorted([host_points[j*9+4] for j in (12,24,36)],key=lambda p:p.y)
    pins=[]
    for o in bpy.data.objects:
        if o.type=='MESH' and o.name.startswith('Recessed cheek fixing'):
            pts=world(o);c=sum(pts,Vector())/len(pts)
            if c.x*side>0:pins.append((c.y,o,pts,c))
    assert len(pins)==3
    for (_,o,pts,c),target in zip(sorted(pins,key=lambda row:row[0]),targets):
        base=min(side*p.x for p in pts)
        delta=Vector((side*(side*target.x-.001-base),target.y-c.y,target.z-c.z))
        reposition(o.name,[p+delta for p in pts]);changes[o.name].update({'host':'reprofiled cheek band','hostSurfacePoint':list(target),'nominalEmbedM':.001})

# Reuse each passive fixing, relocate its complete mesh rigidly onto its real
# revised supporting surface. No powered or sensing part is introduced.
fixings=[]
for side in (-1,1):
    host=tree([f'Forged orbital mounting plate {side}',f'Forged orbital brow {side}'])
    pins=sorted([o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(f'Orbital mounting fixing {side} ')],key=lambda o:o.name)
    assert len(pins)==5
    for j,o in enumerate(pins):
        if j<2:target=brow_point(side,.23 if j==0 else .70,.53)
        else:
            a=[-.32,-1.4,-2.6][j-2];c=socket_centres[side];target=Vector((side*.3,c.y+.069*math.cos(a),c.z+.069*math.sin(a)))
        hit,_,_,_=host.ray_cast(Vector((side*.4,target.y,target.z)),Vector((-side,0,0)),.5)
        assert hit is not None,('Unsupported fixing',o.name,list(target))
        pts=world(o);centre=sum(pts,Vector())/len(pts);base=min(side*p.x for p in pts)
        delta=Vector((side*(side*hit.x-.001-base),hit.y-centre.y,hit.z-centre.z));reposition(o.name,[p+delta for p in pts]);fixings.append({'name':o.name,'deltaWorld':list(delta),'hostHit':list(hit)})

after=h['scene_snapshot']();assert before['empties']==after['empties'] and before['curves']==after['curves']
assert set(before['meshes'])==set(after['meshes'])
for n,record in before['meshes'].items():
    if n not in changes:assert after['meshes'][n]==record,n
    else:
        for k in record:
            if k not in {'mesh','parent'}:assert after['meshes'][n][k]==record[k],(n,k)
        if n not in old_owners:assert after['meshes'][n]['parent']==record['parent'],n
native=OUT/'murderbird-orbital-crown-v14.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'orbital and crown geometry proposal; not accepted or selected','base':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'changed':changes,'fixings':fixings,'browUpper':UPPER,'browLower':LOWER,'preservation':{'pivotsExact':len(after['empties']),'otherMeshesExact':len(after['meshes'])-len(changes),'allGuidesExact':True,'opticBearingHousingAndLensShapeExactWithRigidInsetM':OPTIC_INSET,'opticRigidRiseM':OPTIC_RAISE,'billMandibleBodyAndWingsExact':True,'saveReopenExact':True},'referenceScope':'July head only; no excluded body/long-wing proportions imported. Hidden sections and crown inspection separation are reconstructed.','limits':['Historical curves are preserved and not current shape authority.','Brow changes owner from opening cranial cover to fixed head.','Crown opening, brow/socket clearance and cheek overhang require review.','No finished materials, owner acceptance or publication.'],'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def render(path,label):
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';s.world.color=(.12,.13,.14)
    s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    for o in bpy.data.objects:
        o.hide_set(False)
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
    cd=bpy.data.cameras.new('Temporary matched head camera');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO'
    views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('head',(-6,-3.5,2.45),(0,-.27,1.62),1.10),('head-profile',(-7.5,-.3,1.63),(0,-.3,1.63),1.15),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5)]
    for name,pos,target,scale in views:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;f=AUDIT/f'{label}-{name}.png';s.render.filepath=str(f);bpy.ops.render.render(write_still=True);receipt['views'].append({**art(f),'camera':{'position':pos,'target':target,'scale':scale},'lighting':'neutral native Workbench'})
render(native,'after');render(BASE,'before');(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(BASE)==SHA
print(json.dumps(receipt['native']))
