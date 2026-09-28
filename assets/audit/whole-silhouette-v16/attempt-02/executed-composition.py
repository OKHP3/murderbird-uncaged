"""Versioned rest-construction edit, not animated scaling or biological skinning.

Maps the inherited geometry AND its joint/attachment locations to proposed
regional proportions. Runtime objects retain their original rigid bases.
Perspective sources guide qualitative proportions, not recovered dimensions.
"""
from pathlib import Path
import argparse,sys,json,hashlib,runpy,shutil,math
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--attempt',required=True)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
BASE=ROOT/'assets/models/whole-character-v15/attempt-04/murderbird-whole-character-v15.blend'
EXPECTED='dd4e6a78396a384be6d38b00c23a3c43c47ab0a9371e6546ad4896b1c6a93cfe'
OUT=ROOT/f'assets/models/whole-silhouette-v16/attempt-{args.attempt}'
AUDIT=ROOT/f'assets/audit/whole-silhouette-v16/attempt-{args.attempt}'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
assert sha(BASE)==EXPECTED and not OUT.exists() and not AUDIT.exists()
OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);shutil.copy2(__file__,AUDIT/'executed-composition.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='v16_snapshot_helpers')
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
material_before={m.name:h['material_signature'](m) for m in bpy.data.materials}
objects=list(bpy.data.objects);matrices={o.name:o.matrix_world.copy() for o in objects}
positions={o.name:o.matrix_world.translation.copy() for o in objects if o.type=='EMPTY'}
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def ancestry(o):
    names=[]
    while o:names.append(o.name);o=o.parent
    return names
def category(o):
    chain=ancestry(o)
    if 'head' in chain:return 'head'
    if 'neck' in chain:return 'neck'
    for side in ('left','right'):
        if side+'-foot' in chain:return side+'-foot'
        if side+'-shin' in chain:return side+'-shin'
        if side+'-thigh' in chain:return side+'-thigh'
        if side+'-mantle' in chain:return side+'-mantle'
    if o.name=='murderbird':return 'root'
    return 'body'
categories={o.name:category(o) for o in objects}

def body(p):
    q=p.copy()
    # More lower breast and shoulder mass, not a uniform barrel inflation.
    low=1-smooth((p.z-.68)/.45)
    q.x*=1.10+.15*low
    q.y*=1.18 if p.y<0 else 1.08
    q.z+=.025*smooth((p.z-1.08)/.25)-.045*smooth((.98-p.z)/.335)
    return q

HEAD=positions['head'];NECK=positions['neck']
def head(p):return HEAD+(p-HEAD)*.94+Vector((0,.025,-.105))
def neck(p):
    # Lower visible span compresses into the upper breast. Upper guards meet
    # the moved head exactly; the inherited throat/back curve is retained.
    t=smooth((p.z-NECK.z)/(HEAD.z-NECK.z))
    return body(p)*(1-t)+head(p)*t

foot_origins={};foot_floors={};new_knees={};new_hips={}
for side,sign in [('left',1),('right',-1)]:
    foot_origins[side]=positions[side+'-foot'].copy()
    foot_meshes=[o for o in objects if o.type=='MESH' and categories[o.name]==side+'-foot']
    foot_floors[side]=min((matrices[o.name]@v.co).z for o in foot_meshes for v in o.data.vertices)
    new_knees[side]=positions[side+'-shin']+Vector((sign*.026,0,-.005))
    new_hips[side]=body(positions[side+'-thigh'])
def foot(p,side):
    c=foot_origins[side].copy();c.z=foot_floors[side]
    sign=1 if side=='left' else -1
    return c+(p-c)*1.10+Vector((sign*.026,0,0))
def bone(p,side,segment):
    if segment=='thigh':
        a=positions[side+'-thigh'];b=positions[side+'-shin'];na=new_hips[side];nb=new_knees[side]
    else:
        a=positions[side+'-shin'];b=positions[side+'-foot'];na=new_knees[side];nb=foot(b,side)
    axis=(b-a).normalized();new_axis=(nb-na).normalized();rot=axis.rotation_difference(new_axis)
    delta=p-a;u=delta.dot(axis)/(b-a).length;radial=delta-axis*delta.dot(axis)
    return na+(nb-na)*u+(rot@radial)*1.18
def mantle(p,side):
    c=positions[side+'-mantle'];nc=body(c)+Vector((0,0,-.015));d=p-c
    return nc+Vector((d.x*1.10,d.y*1.14,d.z))
def mapping(p,cat):
    if cat=='head':return head(p)
    if cat=='neck':return neck(p)
    if cat=='body':return body(p)
    if cat=='root':return p.copy()
    side,part=cat.split('-',1)
    if part=='foot':return foot(p,side)
    if part=='mantle':return mantle(p,side)
    return bone(p,side,part)

def optic_edit(o,p,index=None):
    # All passive housings and the advanced lens shrink together. Their round
    # mechanical shape stays round; the surrounding skull field stays broad.
    if o.get('region')=='optic':
        side=1 if p.x>=0 else -1;c=Vector((side*.145,-.43575,1.7494))
        return c+(p-c)*.83
    if o.name.startswith('Forged orbital mounting plate'):
        assert len(o.data.vertices)==896,'Expected V15 constructed aperture topology'
        f=(index%7)/6;amount=.83+.17*smooth(f/.70)
        q=p.copy();q.y=-.43575+(p.y+.43575)*amount;q.z=1.7494+(p.z-1.7494)*amount
        return q
    return p

def depth(o):return 0 if o.parent is None else depth(o.parent)+1
# Capture all proposed world transforms before editing parents. No rest scale
# is injected into the joint hierarchy; the dimensions are baked into source.
new_matrices={}
for o in objects:
    m=matrices[o.name].copy();m.translation=mapping(m.translation,categories[o.name])
    if o.name=='anchor-joint':m.translation=bone(matrices[o.name].translation,'left','shin')
    new_matrices[o.name]=m
for o in sorted(objects,key=depth):o.matrix_world=new_matrices[o.name]
bpy.context.view_layer.update()
changed=[];guides=[]
for o in objects:
    old=matrices[o.name];inv=o.matrix_world.inverted();cat=categories[o.name]
    if o.type=='MESH':
        if o.data.users>1:o.data=o.data.copy()
        center=sum((old@v.co for v in o.data.vertices),Vector())/max(1,len(o.data.vertices))
        for i,v in enumerate(o.data.vertices):
            p=old@v.co
            if cat.endswith(('-thigh','-shin')) and o.get('surfaceRole')=='bearing':
                # Keep journals circular rather than shortening a bearing as
                # though it were a section of a long frame member.
                target=mapping(center,cat)+(p-center)*1.18
            else:target=mapping(optic_edit(o,p,i),cat)
            v.co=inv@target
        o.data.update();o['proportionStudy']='whole-silhouette-v16';changed.append(o.name)
    elif o.type=='CURVE':
        if o.data.users>1:o.data=o.data.copy()
        for spline in o.data.splines:
            for p in spline.bezier_points:
                for attr in ('co','handle_left','handle_right'):
                    setattr(p,attr,inv@mapping(old@getattr(p,attr),cat))
            for p in spline.points:
                q=inv@mapping(old@Vector(p.co[:3]),cat);p.co=(*q,p.co.w)
        o.hide_render=True;o['historicalAuthoringGuide']=True;guides.append(o.name)
bpy.context.view_layer.update()
assert set(before['empties'])=={o.name for o in objects if o.type=='EMPTY'}
for o in objects:
    if o.type=='EMPTY':
        a=matrices[o.name].to_3x3();b=o.matrix_world.to_3x3()
        assert max(abs(a[i][j]-b[i][j]) for i in range(3) for j in range(3))<1e-6,'Joint basis changed'
# Re-seat contact to the actual leading vertex after all proposed dimensions.
pts=[o.matrix_world@v.co for o in objects if o.type=='MESH' and o.parent and o.parent.name=='upper-bill' for v in o.data.vertices]
marker=bpy.data.objects['bill-contact'];m=marker.matrix_world.copy();m.translation=min(pts,key=lambda p:p.y);marker.matrix_world=m
bpy.context.view_layer.update();after=h['scene_snapshot']()
assert material_before=={m.name:h['material_signature'](m) for m in bpy.data.materials},'This is a construction pass, not a material pass'
pivot_changes=[{'name':name,'before':list(pos),'after':list(bpy.data.objects[name].matrix_world.translation)} for name,pos in positions.items() if (pos-bpy.data.objects[name].matrix_world.translation).length>1e-7]
native=OUT/'murderbird-whole-silhouette-v16.blend';bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native))
assert h['scene_snapshot']()==after,'Save/reopen mismatch'
receipt={'status':'whole-silhouette proposal; not accepted or a release','base':art(BASE),'native':art(native),'composer':art(AUDIT/'executed-composition.py'),
 'changes':{'headUniformScale':.94,'headOffsetNativeXYZ':[0,.025,-.105],'opticAndHousingScale':.83,'bodyWidthLowerUpper':[1.25,1.10],'bodyDepthFrontBack':[1.18,1.08],'bodyTopBottomDelta':[.025,-.045],'footUniformScale':1.10,'footLateralOffset':.026,'legMemberThicknessFactor':1.18,'mantleRelativeScaleXYZ':[1.10,1.14,1]},
 'construction':'Static editable rest geometry and attachments move together. Joint bases unchanged; no animated scaling or deforming metal.',
 'preservation':{'rigidNodes':52,'materialsExact':True,'originalNativeUnchanged':sha(BASE)==EXPECTED,'saveReopenExact':True,'meshNamesRetained':len(changed),'historicalGuidesRetainedAndRefitted':len(guides)},
 'pivotChanges':pivot_changes,
 'limits':['Proportions are proposed, not dimensions recovered from perspective art.','All prior attachment and motion-clearance evidence is stale for this candidate.','Known inherited crown intersections are not solved by this proportion edit.','Historic guides remain editable but hidden from render and absent from runtime.'],'views':[]}

def render(path,label):
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';s.world.color=(.12,.13,.14)
    s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    for o in bpy.data.objects:
        o.hide_set(False)
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
        if o.type=='CURVE':o.hide_render=True
    cd=bpy.data.cameras.new('Temporary matched camera');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO'
    for name,pos,target,scale in [('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('head',(-6,-3.5,2.45),(0,-.27,1.56),1.12),('legs',(-6,-3.5,1.65),(0,-.03,.42),1.25)]:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;f=AUDIT/f'{label}-{name}.png';s.render.filepath=str(f);bpy.ops.render.render(write_still=True);receipt['views'].append({**art(f),'camera':{'position':pos,'target':target,'scale':scale}})
render(native,'after');render(BASE,'before')
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(BASE)==EXPECTED
print(json.dumps({'native':receipt['native'],'movedPivots':len(receipt['pivotChanges']),'preservation':receipt['preservation']}))
