"""Whole-body rest-shape reconstruction after the owner's likeness rejection.

Versioned editable mesh study. All shapes/pivot positions are authored proposals;
no runtime selection, source overwrite, or physical/motion approval is implied.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,runpy,shutil,sys,argparse
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--attempt',default='01');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
BASE=ROOT/'assets/models/uncaged-whole-body-v10/attempt-02/murderbird-whole-body-v10.blend'
SHA='6b2b43209d0474771010f3711f7d7ad2c00521f4d331c22a17d998f61a86c69f'
OUT=ROOT/f'assets/models/uncaged-silhouette-v11/attempt-{args.attempt}'
AUDIT=ROOT/f'assets/audit/uncaged-silhouette-v11/attempt-{args.attempt}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def lerp(rows,t):
    u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);v=u-i
    return tuple(a+(b-a)*v for a,b in zip(rows[i],rows[i+1]))
def zmap(z):
    rows=[(-.1,-.1),(.10,.10),(.28,.245),(.53,.425),(.81,.675),(1.1,1.015),(1.3,1.255),(1.5,1.49),(1.65,1.65),(1.80,1.81),(2.10,2.12)]
    for (a,b),(c,d) in zip(rows,rows[1:]):
        if a<=z<=c:return b+(d-b)*(z-a)/(c-a)
    return z
assert sha(BASE)==SHA and not OUT.exists() and not AUDIT.exists()
OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);shutil.copy2(__file__,AUDIT/'executed-generator.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='shape_helper')
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
oldworld={o.name:o.matrix_world.copy() for o in bpy.data.objects}
oldowner={o.name:o.parent.name if o.parent else None for o in bpy.data.objects}
# Keep the declared construction/era identity of every inherited piece.
def chain(o):
    out=[]
    while o:out.append(o.name);o=o.parent
    return out
chains={o.name:chain(o) for o in bpy.data.objects}

def map_general(p,n):
    q=p.copy();c=chains[n]
    # Lower the load-bearing pelvis and shorten the exposed leg silhouette;
    # preserve the tall curved neck and increase cranial breadth behind the eye.
    q.z=zmap(p.z)
    q.y-=.070*smooth((p.z-.68)/1.25)
    if 'head' in c:
        q.x*=1.14
        q.y=-.36+(p.y+.36)*(1.32 if p.y>-.36 else 1.0)-.070*smooth((p.z-.68)/1.25)
        # Rear blades sweep backward instead of hanging as a round cap.
        q.y+=.045*smooth((p.y+.28)/.23)*smooth((1.94-p.z)/.22)
        q.z+=.023*smooth((p.y+.32)/.22)
    elif any(x in c for x in ('left-mantle','right-mantle')):
        side=1 if p.x>0 else -1
        q.x-=side*.040
        q.y+=.018
        q.z+=.005
    elif p.z>.68:
        # Carry fuller high breast into the neck; taper the low abdomen.
        f=1+.09*smooth((p.z-.93)/.25)-.10*smooth((.94-p.z)/.25)
        q.x*=f
        q.y-=.024*math.exp(-((p.z-1.22)/.20)**2)*smooth((-p.y+.06)/.3)
    return q

# Map all rest attachment points first. Jaw closes toward the upper cutting
# surface by relocating the real hinge and its head-owned journal together.
def point(p,n):
    p=p.copy()
    if 'jaw' in chains[n] or n.startswith('Coaxial mandible journal'):
        p.z+=.055
    return map_general(p,n)
newworld={}
for o in bpy.data.objects:
    w=oldworld[o.name].copy();w.translation=point(w.translation,o.name);newworld[o.name]=w

# Straight structural limbs use one affine map along their actual pivot span,
# rather than bending rails through a nonlinear height field.
limb_maps={}
for side in ('left','right'):
    for owner,child in [('thigh','shin'),('shin','foot'),('foot','toes')]:
        name=f'{side}-{owner}';end=f'{side}-{child}'
        a=oldworld[name].translation;b=oldworld[end].translation
        aa=point(a,name);bb=point(b,end)
        axis=(b-a).normalized();dest=(bb-aa).normalized();rot=axis.rotation_difference(dest)
        limb_maps[name]=(a,aa,axis,(b-a).length,(bb-aa).length,rot)
def meshpoint(p,o):
    owner=oldowner[o.name]
    if owner in limb_maps:
        a,aa,axis,length,newlength,rot=limb_maps[owner]
        d=p-a;along=d.dot(axis);radial=d-axis*along
        # Constant transverse expansion, not swollen midsection armor.
        factor=1.22 if 'foot' not in owner else 1.16
        return aa+rot@(axis*(along*newlength/length)+radial*factor)
    if any('digit-' in name or name.endswith('-toes') for name in chains[o.name]):
        q=point(p,o.name);side=1 if p.x>0 else -1
        centre=side*.251
        q.x=centre+(q.x-centre)*1.18
        return q
    return point(p,o.name)

# Save complete old geometry in memory before changing parenting transforms.
oldverts={o.name:[oldworld[o.name]@v.co for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH'}
for o in sorted(bpy.data.objects,key=lambda o:len(chains[o.name])):o.matrix_world=newworld[o.name]
bpy.context.view_layer.update()
for o in bpy.data.objects:
    if o.type!='MESH':continue
    inv=o.matrix_world.inverted()
    for v,p in zip(o.data.vertices,oldverts[o.name]):v.co=inv@meshpoint(p,o)
    o.data.update()
# Update preserved section curves to the same authored rest envelope.
for o in bpy.data.objects:
    if o.type!='CURVE':continue
    inv=o.matrix_world.inverted()
    for spline in o.data.splines:
        for p in spline.points:
            q=point(oldworld[o.name]@Vector(p.co[:3]),o.name);w=p.co.w;p.co=(*list(inv@q),w)
        for p in spline.bezier_points:
            for attr in ('co','handle_left','handle_right'):
                setattr(p,attr,inv@point(oldworld[o.name]@getattr(p,attr),o.name))

# Re-author the blade stations, replacing the smooth pendant hook impression
# with a deep proximal face and short terminal cutting hook. Keep two real
# separately editable plates, with their existing rigid upper-bill owner.
outer=[(-.421,1.853),(-.493,1.839),(-.565,1.796),(-.624,1.738),(-.657,1.676),(-.665,1.618),(-.651,1.567),(-.625,1.535)]
inner=[(-.420,1.706),(-.480,1.697),(-.521,1.688),(-.553,1.668),(-.584,1.638),(-.613,1.600),(-.629,1.563),(-.625,1.535)]
widths=[(.079,),(.082,),(.075,),(.063,),(.048,),(.031,),(.014,),(.0008,)]
for name in ('Profiled upper bill blade 0','Profiled upper bill blade 1'):
    o=bpy.data.objects[name];inv=o.matrix_world.inverted();assert len(o.data.vertices)==57*40
    for j in range(57):
        t=.245*j/56 if name.endswith('0') else .25+.75*j/56
        oy,oz=lerp(outer,t);iy,iz=lerp(inner,t);w=lerp(widths,t)[0]
        for k in range(40):
            a=k*math.tau/40;cross=1-2*abs((a+math.pi)%math.tau-math.pi)/math.pi
            raw=Vector((w*math.sin(a),(oy+iy)/2+(oy-iy)*cross/2,(oz+iz)/2+(oz-iz)*cross/2))
            o.data.vertices[j*40+k].co=inv@point(raw,name)
    o.data.update()

# Reconstruct the missing posterior neck envelope with rigid directional
# lap guards. This is load-covering neck geometry, not a floating collar.
# Upper and lower courses belong to their respective cervical assemblies.
nape_sections=[(1.30,.035,.238,.166),(1.38,.004,.225,.165),(1.46,-.050,.205,.155),(1.54,-.105,.183,.179),(1.62,-.145,.159,.207),(1.70,-.165,.139,.220),(1.76,-.185,.125,.210)]
def nape(z,angle,offset=0):
    z=max(nape_sections[0][0],min(nape_sections[-1][0],z))
    for row,nxt in zip(nape_sections,nape_sections[1:]):
        if row[0]<=z<=nxt[0]:
            t=(z-row[0])/(nxt[0]-row[0]);cy,rx,ry=[row[k]+(nxt[k]-row[k])*t for k in (1,2,3)];break
    return Vector(((rx+offset)*math.sin(angle),cy+(ry+offset)*math.cos(angle),z))
new_nape=[]
for course,(top,bottom) in enumerate([(1.742,1.642),(1.666,1.564),(1.588,1.489),(1.512,1.414),(1.437,1.338),(1.360,1.306)]):
    owner=bpy.data.objects['cervical-upper' if course<3 else 'neck']
    for column,angle0 in enumerate([-.99,0,.99]):
        name=f'V11 posterior cervical lap {course+1} {column+1}'
        verts=[];faces=[];rows=8;cols=8
        for j in range(rows+1):
            t=j/rows;z=top+(bottom-top)*t;half=.55*(1-.22*smooth((t-.65)/.35))
            for k in range(cols+1):
                a=angle0+half*(2*k/cols-1)
                zc=z+.010*(1-abs(2*k/cols-1))*smooth((t-.65)/.35)
                raw=nape(zc,a,.009+.010*t)
                q=map_general(raw,owner.name)
                verts.append(owner.matrix_world.inverted()@q)
        for j in range(rows):
            for k in range(cols):
                a=j*(cols+1)+k;faces.append((a,a+1,a+cols+2,a+cols+1))
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
        o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=owner
        o['region']='neck';o['surfaceRole']='plate';o['exteriorEras']='maker,mechanic,builder';o['constructionStatus']='proposed passive rigid posterior neck covering'
        mesh.materials.append(bpy.data.materials['Neutral / plate'])
        for f in mesh.polygons:f.use_smooth=True
        mod=o.modifiers.new('Rigid wall thickness','SOLIDIFY');mod.thickness=.005;mod.offset=-1
        mod=o.modifiers.new('Formed guard edge','BEVEL');mod.width=.0012;mod.segments=2
        new_nape.append({'name':name,'parent':owner.name,'rawTopBottom':[top,bottom]})

# Keep individual eye housings, the closed cheek and cranial layers inspectable.
# Broad render-ready face geometry remains editable, with no image trickery.
for o in bpy.data.objects:
    if o.type=='MESH':
        o['silhouetteRevision']='V11 whole-body rest reconstruction; unapproved'
        if o.data.users>1:raise AssertionError('Shared editable mesh '+o.name)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.context.view_layer.update()
assert all(oldowner[n]==(bpy.data.objects[n].parent.name if bpy.data.objects[n].parent else None) for n in oldowner)
native=OUT/'murderbird-silhouette-v11.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(native));after=h['scene_snapshot']()
receipt={'status':'whole-body proportion proposal; not selected or approved','base':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'sourceObjects':len(before['meshes']),'outputMeshes':len(after['meshes']),'pivots':len(after['empties']),'parentGraphPreserved':True,'addedPosteriorGuards':new_nape,'changes':['shorter load-bearing stance and lower pelvis','straight, uniformly broader passive limb sections','wider swept posterior cranium','re-seated jaw hinge and journal for smaller cheek gap','deep bill face with short terminal hook','inset mantle and fuller high breast'],'limits':['Rest construction only; no motion/contact pass or owner acceptance.','Authored proportions are qualitative interpretations, not dimensions recovered from the perspective reference.','Runtime mechanisms require reconciliation to altered attachment positions before integration.','No texture, material-history, publication or default runtime change.'],'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')

def render(path,label):
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
    scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    for o in bpy.data.objects:
        o.hide_set(False)
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
    cd=bpy.data.cameras.new('Silhouette comparison camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
    views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('profile',(-7.5,0,1.25),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5)]
    if label=='after':views += [('rear',(0,7,1.65),(0,-.08,1.02),2.5),('head',(-6,-3.5,2.45),(0,-.27,1.78),1.10)]
    for name,pos,target,scale in views:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;f=AUDIT/f'{label}-{name}.png';scene.render.filepath=str(f);bpy.ops.render.render(write_still=True);receipt['views'].append({**art(f),'label':label,'camera':{'position':pos,'target':target,'scale':scale},'lighting':'neutral Workbench; native rest geometry only','referenceCamera':'approximate interpretation of owner view, not calibrated metrology'})
render(BASE,'before');render(native,'after');(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(BASE)==SHA
print(json.dumps(receipt['native']))
