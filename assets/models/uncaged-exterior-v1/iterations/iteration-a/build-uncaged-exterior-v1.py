"""Versioned rigid exterior, regional UVs and portable glTF PBR surfaces.

Run in Blender. Region modules change geometry before this pipeline assigns
era-specific surface history. Existing manual output edits cause a hard stop.
"""
from pathlib import Path
import ast, hashlib, json, math, random, runpy
import bpy
import numpy as np
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/models/uncaged-exterior-v1';OUT.mkdir(exist_ok=True,parents=True)
BASE=ROOT/'assets/models/uncaged-structure-v1/murderbird-structure-v1.blend'
BASE_SHA='9859c1044fe035f140448b23cef477eb9fb3cc4daa8aaf42837ebb8d7dba7541'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(BASE)==BASE_SHA,'Structural source changed; reconcile before generation'
receipt=OUT/'exterior-inventory.json'
if receipt.exists():
    for f in json.loads(receipt.read_text()).get('generatedFiles',[]):
        p=ROOT/f['path']
        if p.exists() and digest(p)!=f['sha256']:
            raise RuntimeError(f'Manual change detected: {p}. Preserve it as a new version before regeneration.')
bpy.ops.wm.open_mainfile(filepath=str(BASE))
for o in bpy.data.objects:o.animation_data_clear()
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
helpers={'material','group','mesh','bevel','rod','ring','tube','plate','loft','reparent_keep_world','depth'}
source=ast.parse((ROOT/'scripts/build-uncaged-presence-study.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in helpers],type_ignores=[]),'<rigid-primitives>','exec'))
def under(o,p):
    while o.parent:
        o=o.parent
        if o==p:return True
    return False
def delete_meshes(test):
    # Evaluate the whole subtree before unlinking its parents.
    doomed=[o for o in bpy.data.objects if o.type=='MESH' and test(o)]
    for o in doomed:bpy.data.objects.remove(o,do_unlink=True)
mats={key:material('Authoring '+key,col,metal,rough) for key,col,metal,rough in [
 ('shell',(.24,.19,.11),.78,.48),('bill',(.09,.105,.10),.78,.40),('frame',(.07,.065,.05),.75,.56),
 ('bearing',(.32,.225,.095),.85,.32),('dark',(.018,.024,.021),.35,.72),('edge',(.32,.25,.135),.82,.38),
 ('repair',(.115,.14,.145),.80,.48),('optic',(.22,.085,.01),.18,.28),('ceramic',(.5,.49,.41),.10,.40)]}
# The inherited plate helper references these globals for its edge/rivet children.
bronze=mats['edge'];brass=mats['bearing'];random.seed(92727)
ctx={k:globals()[k] for k in helpers}
ctx.update(bpy=bpy,Vector=Vector,Matrix=Matrix,delete_meshes=delete_meshes,under=under,mats=mats)
region_notes={}
for module in ['exterior-head-neck.py','exterior-body-regions.py']:
    region_notes[module]=runpy.run_path(str(ROOT/'scripts'/module))['build'](ctx)
bpy.context.view_layer.update()
# The retained power package previously protruded through the new closed breast.
# Seat the whole Advanced-only assembly inside the available breast volume;
# inspection and conduits continue to use this assembly's actual transform.
power=bpy.data.objects['power-core']
points=[o.matrix_world@Vector(c) for o in power.children_recursive if o.type=='MESH' for c in o.bound_box]
center=Vector(tuple((min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)))
power.matrix_world.translation+=Vector((0,-.07,1.19))-center
bpy.context.view_layer.update()

REGIONS=['head','neck','breast','shoulder','wing','pelvis','leg','back']
ROLE_TILE={'bill':8,'frame':9,'bearing':10,'edge':11,'repair':12,'dark':13,'optic':14,'ceramic':15}
ERAS=['maker','mechanic','builder']
SIZE=1024;CELL=256
texture_dir=OUT/'textures';texture_dir.mkdir(exist_ok=True)
def image_from_array(name,arr,noncolor=False):
    im=bpy.data.images.new(name,width=SIZE,height=SIZE,alpha=True)
    im.colorspace_settings.name='Non-Color' if noncolor else 'sRGB'
    im.pixels.foreach_set(arr.astype(np.float32).ravel())
    im.filepath_raw=str(texture_dir/(name+'.png'));im.file_format='PNG';im.save();im.pack()
    return im
yy,xx=np.mgrid[0:CELL,0:CELL];u=(xx+.5)/CELL;v=(yy+.5)/CELL
# Restrained periodic forging relief. Oblique phases avoid a woven/checker
# pattern under moving highlights; these are manufacturing marks, not wear.
rng=np.random.default_rng(92727)
hammer=np.zeros_like(u)
for _ in range(16):
    kx,ky=rng.integers(8,36,size=2)
    hammer+=np.sin((u*kx+v*ky)*math.tau+rng.uniform(0,math.tau))*.055
grain=.12*np.sin((u*83+v*13)*math.tau)+.05*np.sin((u*71-v*7)*math.tau+1.2)
edge=np.minimum.reduce([u,1-u,v,1-v]);shelter=np.exp(-v*28)+.25*np.exp(-edge*45)
normal=np.ones((SIZE,SIZE,4),dtype=np.float32)
for tile in range(16):
    h=hammer*.0016+grain*.00032
    if tile in [8,10,11]:h=grain*.00035
    dy,dx=np.gradient(h);nx=-dx*CELL;ny=-dy*CELL
    nz=np.ones_like(nx);den=np.sqrt(nx*nx+ny*ny+nz*nz)
    rgba=np.stack([nx/den*.5+.5,ny/den*.5+.5,nz/den*.5+.5,np.ones_like(nx)],axis=-1)
    row,col=divmod(tile,4);normal[row*CELL:(row+1)*CELL,col*CELL:(col+1)*CELL]=rgba
normal_image=image_from_array('regional-forging-normal',normal,True)
maps={}
for era in ERAS:
    color=np.ones((SIZE,SIZE,4),dtype=np.float32);orm=np.ones_like(color)
    aged=era!='maker'
    for tile in range(16):
        base=np.array((.095,.077,.050) if not aged else (.061,.065,.051))
        rough=.58 if not aged else .66;metal=.78
        if tile<8:
            base*= [1.07,.91,.97,1.0,.92,.83,.82,.78][tile]
        else:
            base,rough,metal={8:((.065,.078,.073),.38,.82),9:((.044,.039,.030),.56,.72),10:((.25,.15,.060),.29,.88),11:((.19,.125,.060),.39,.82),12:((.075,.085,.09),.52,.82),13:((.012,.015,.012),.74,.25),14:((.40,.135,.008),.26,.15),15:((.52,.51,.435),.43,.08)}[tile]
            base=np.array(base)
        # Maker is newly fabricated, lightly oxidized/oiled, before immersion.
        # Later deposits collect only in sheltered seams; clean overlap paths
        # and service edges retain warm metal. No global green overlay.
        tone=1+hammer*.045+grain*.016
        c=tone[:,:,None]*base
        polished=np.exp(-edge*100)
        c+=polished[:,:,None]*np.array([.045,.030,.012])
        if aged and tile<8:
            deposit=np.clip(shelter*.29,0,.35)[:,:,None]
            c=c*(1-deposit)+np.array([.047,.090,.075])*deposit
            rough+=.07
        # Working bill and bearing surfaces stay burnished across eras.
        if tile in [8,10]:rough-=.035*np.sin(v*math.pi)**2
        r=np.clip(rough+hammer*.045-polished*.12,.18,.88)
        row,col=divmod(tile,4);sl=np.s_[row*CELL:(row+1)*CELL,col*CELL:(col+1)*CELL]
        # Base palette values are linear reflectance; PNG color maps are sRGB.
        linear=np.clip(c,0,1)
        srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
        color[sl]=np.concatenate([srgb,np.ones((CELL,CELL,1))],axis=2)
        orm[sl]=np.stack([np.ones_like(u),r,np.full_like(u,metal),np.ones_like(u)],axis=-1)
    maps[era]=(image_from_array(era+'-regional-color',color),image_from_array(era+'-regional-orm',orm,True))

material_cache={}
def finish(era,role):
    key=era,role
    if key in material_cache:return material_cache[key]
    mat=material(era+' / '+role,(1,1,1),1,1);bs=mat.node_tree.nodes.get('Principled BSDF');nt=mat.node_tree
    base=nt.nodes.new('ShaderNodeTexImage');base.image=maps[era][0];nt.links.new(base.outputs['Color'],bs.inputs['Base Color'])
    orm=nt.nodes.new('ShaderNodeTexImage');orm.image=maps[era][1];split=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(orm.outputs['Color'],split.inputs['Color']);nt.links.new(split.outputs['Green'],bs.inputs['Roughness']);nt.links.new(split.outputs['Blue'],bs.inputs['Metallic'])
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=normal_image;norm=nt.nodes.new('ShaderNodeNormalMap');norm.inputs['Strength'].default_value=.20;nt.links.new(tex.outputs['Color'],norm.inputs['Color']);nt.links.new(norm.outputs['Normal'],bs.inputs['Normal'])
    if role=='optic':bs.inputs['Emission Color'].default_value=(.40,.10,.003,1);bs.inputs['Emission Strength'].default_value=.35
    mat['surfaceEra']=era;mat['surfaceRole']=role;mat['pipeline']='glTF metallic-roughness plus tangent normal; no custom shader'
    material_cache[key]=mat;return mat
def inherited_property(o,key,default=None):
    while o:
        if key in o:return o[key]
        o=o.parent
    return default
def default_region(o):
    name=o.name.lower();p=o
    lineage=[]
    while p:lineage.append(p.name);p=p.parent
    if any('toe' in x or '-foot' in x for x in lineage):return 'foot'
    if any('-shin' in x or '-thigh' in x for x in lineage):return 'leg'
    if 'neck' in lineage and 'head' not in lineage:return 'neck'
    if 'head' in lineage:return 'head'
    if any('wing-shield' in x for x in lineage):return 'wing'
    if any('mantle' in x for x in lineage):return 'shoulder'
    if 'breastplate' in lineage:return 'breast'
    return 'back'
def default_role(o):
    n=o.name.lower()
    if any(s in n for s in ['lens','optic']):return 'optic'
    if any(s in n for s in ['rivet','bolt','edge','trim']):return 'edge'
    if any(s in n for s in ['bearing','bushing','pin','hinge','socket rim']):return 'bearing'
    if 'claw' in n or 'talon' in n:return 'bill'
    if under(o,bpy.data.objects['power-core']):return 'ceramic'
    if under(o,bpy.data.objects['industrial-repairs']):return 'repair'
    if any(s in n for s in ['plate','shield','cover','armor','guard','shell']):return 'shell'
    return 'frame'
inventory=[]
# Apply modifiers while source objects are still separate, then project each
# rigid face at a stable scale into its region/role tile. Bevels get own islands.
source_meshes=[o for o in bpy.data.objects if o.type=='MESH']
for o in source_meshes:
    region=inherited_property(o,'region',default_region(o));role=inherited_property(o,'surfaceRole',default_role(o))
    if role not in mats:role='shell'
    eras=str(inherited_property(o,'exteriorEras','maker,mechanic,builder')).split(',')
    if under(o,bpy.data.objects['builder-optics']) or under(o,bpy.data.objects['power-core']) or under(o,bpy.data.objects['processing']):eras=['builder']
    if under(o,bpy.data.objects['industrial-repairs']):eras=['mechanic','builder']
    o.modifiers.new('Stable export triangulation','TRIANGULATE')
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
    uv=o.data.uv_layers.active or o.data.uv_layers.new(name='RegionalSurface')
    tile=ROLE_TILE.get(role,REGIONS.index(region) if region in REGIONS else 6)
    row,col=divmod(tile,4);coords=np.array([tuple(v.co) for v in o.data.vertices]);mins=coords.min(axis=0);span=np.maximum(coords.max(axis=0)-mins,1e-5)
    for poly in o.data.polygons:
        axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=axis];scale=max(span[axes[0]],span[axes[1]])
        for li in poly.loop_indices:
            co=coords[o.data.loops[li].vertex_index];a=.03+.94*(co[axes[0]]-mins[axes[0]])/scale;b=.03+.94*(co[axes[1]]-mins[axes[1]])/scale
            uv.data[li].uv=((col+a)/4,(row+b)/4)
    # Detach descendants before replacing objects; every fastener retains its
    # local assembly and inherits its source plate's region/eligibility metadata.
    for child in list(o.children):
        world=child.matrix_world.copy()
        for key,val in [('region',region),('surfaceRole',default_role(child)),('exteriorEras',','.join(eras))]:
            if key not in child:child[key]=val
        child.parent=o.parent;child.matrix_world=world
    source_name=o.name;world=o.matrix_world.copy();parent=o.parent
    for era in eras:
        copy=o.copy();copy.data=o.data.copy();bpy.context.collection.objects.link(copy);copy.name=f'{source_name} [{era}]';copy.parent=parent;copy.matrix_world=world
        copy.data.materials.clear();copy.data.materials.append(finish(era,role));copy['region']=region;copy['surfaceRole']=role;copy['exteriorEras']=era;copy['inheritedPart']=source_name
        copy.hide_render=era!='builder';copy.hide_set(era!='builder')
        inventory.append({'part':source_name,'era':era,'region':region,'role':role,'attachment':parent.name if parent else None,'vertices':len(copy.data.vertices),'uvTile':tile})
    bpy.data.objects.remove(o,do_unlink=True)
root=bpy.data.objects['murderbird'];root['status']='Three exterior construction states v1; owner artistic review pending';root['base-source']=str(BASE.relative_to(ROOT));root['base-sha256']=BASE_SHA
root['surface-pipeline']='Stable regional planar UV islands; seven 1024px PBR maps; rigid geometry; era eligibility extras'
head=bpy.data.objects['head'];bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=31
for frame,angle in [(1,0),(16,.12),(31,0)]:head.rotation_euler.z=angle;head.keyframe_insert(data_path='rotation_euler',frame=frame)
head.animation_data.action.name='attention-export-proof';bpy.context.scene.frame_set(1)
bpy.context.preferences.filepaths.save_version=0;bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'murderbird-exterior-v1.blend'))
# Batch only objects with identical attachment, era and region. Independently
# opening covers and toe groups remain distinct transforms through export.
groups={}
for o in list(bpy.context.scene.objects):
    if o.type!='MESH':continue
    o.hide_set(False);o.hide_render=False
    p=o.parent
    while p and p.type!='EMPTY':p=p.parent
    groups.setdefault((p,o.get('exteriorEras'),o.get('region')),[]).append(o)
for (parent,era,region),objs in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        w=o.matrix_world.copy();o.parent=parent;o.matrix_world=w;o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=f'{parent.name}-{region}-{era}';o['exteriorEras']=era;o['region']=region
def export(path,selection=False):
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=True,export_animation_mode='ACTIONS',export_frame_range=True,use_selection=selection,export_tangents=True)
export(OUT/'murderbird-exterior-v1.glb')
for era in ERAS:
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:o.select_set(o.type!='MESH' or o.get('exteriorEras')==era)
    export(OUT/f'murderbird-exterior-{era}-v1.glb',True)
generated=[p for p in OUT.rglob('*') if p.is_file() and (p.suffix in {'.blend','.glb'} or p.parent==texture_dir)]
receipt.write_text(json.dumps({'base':str(BASE.relative_to(ROOT)),'baseSha256':BASE_SHA,'status':'Implemented local exterior proposal, owner artistic acceptance pending','makerMoment':'Newly fabricated, before immersion; dark oiled bronze with restrained tool relief, no water deposits','regions':region_notes,'parts':inventory,'textureBudget':{'images':7,'width':SIZE,'height':SIZE,'decodedRgbaWithMipsMiB':7*SIZE*SIZE*4*4/3/1024**2,'limitMiB':48,'bundleTransferLimitMiB':16},'generatedFiles':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(generated)]},indent=2)+'\n')
print('EXTERIOR_V1_EXPORT',len(inventory),'parts',OUT)
