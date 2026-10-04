"""Regional finish revision, using retained authored CG2b maps, never artwork pixels.
API: apply(scene, output_dir, era='builder', reference_root=None).
Preserves every slot index, polygon assignment, UV and mesh/pose; protected optics untouched.
"""
from pathlib import Path
import json, hashlib
import bpy
import numpy as np

ERAS=('maker','mechanic','builder')
# Scene-linear map targets: dark green protective finish, warm worked bare metal.
# Blender image pixels are linear; PNG writing encodes the color image to sRGB.
PALETTES={
 'head-armor':((.050,.073,.040),(.145,.112,.045),.66,.30),
 'breast-armor':((.037,.059,.033),(.130,.095,.033),.70,.25),
 'wing-armor':((.031,.054,.034),(.115,.083,.030),.71,.24),
 'forged-steel':((.193,.211,.186),(.39,.37,.29),.53,.88),
 'machined-steel':((.350,.307,.231),(.50,.45,.33),.40,.93),
 'worn-bronze':((.330,.252,.135),(.48,.37,.20),.51,.85),
 'black-iron':((.034,.043,.038),(.12,.12,.085),.76,.20)}

def pixels(im):
 a=np.empty(im.size[0]*im.size[1]*4,dtype=np.float32);im.pixels.foreach_get(a)
 return a.reshape(im.size[1],im.size[0],4)[:,:,:3].copy()

def write(path,values,data):
 h,w,_=values.shape
 im=bpy.data.images.new(path.name,width=w,height=h,alpha=False)
 im.colorspace_settings.name='Non-Color' if data else 'sRGB'
 rgba=np.ones((h,w,4),np.float32);rgba[:,:,:3]=np.clip(values,0,1)
 im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(path);im.file_format='PNG';im.save();im.pack()
 return im

def digest(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(np.asarray(v.co[:],dtype='<f4').tobytes())
 for p in o.data.polygons:
  h.update(np.asarray(p.vertices[:],dtype='<i4').tobytes());h.update(int(p.material_index).to_bytes(4,'little'))
 for uv in o.data.uv_layers:
  h.update(uv.name.encode())
  for v in uv.data:h.update(np.asarray(v.uv[:],dtype='<f4').tobytes())
 h.update(np.asarray(o.matrix_world,dtype='<f8').tobytes());h.update(str((o.parent.name if o.parent else None,len(o.data.materials),o.hide_render)).encode())
 return h.hexdigest()

def apply(scene,output_dir,era='builder',reference_root=None):
 if era not in ERAS:raise ValueError(era)
 out=Path(output_dir)/'textures'/era
 if out.exists() and any(out.glob('*.png')):raise RuntimeError('Write-once finish output exists; choose a new output directory')
 out.mkdir(parents=True,exist_ok=True)
 targets=[o for o in scene.objects if o.type=='MESH' and not o.get('authoringGuide')]
 before={o.name:digest(o) for o in targets}; cache={}; records=[];slots=0;preserved=[]
 for o in targets:
  for idx,old in enumerate(o.data.materials):
   family=old.get('cg2bFamily') if old else None
   if not family or old.get('cg2aPreserveMaterial'):
    preserved.append((o.name,idx,old.name if old else None));continue
   if old.name not in cache:
    mat=old.copy();mat.name='CG supervised finish02 / '+family+' / '+era
    nodes=mat.node_tree.nodes
    tex={n.label:n for n in nodes if n.type=='TEX_IMAGE'}
    source_color=tex['color'].image;source_orm=tex['orm'].image
    # Select the exact corresponding existing era map if local files are present.
    if reference_root:
     root=Path(reference_root)/'assets/models/cg-supervised01/surface01/textures'
     cp=root/f'{family}-{era}-2b-color.png';op=root/f'{family}-{era}-2b-orm.png'
     if cp.exists() and cp.stat().st_size>1000:source_color=bpy.data.images.load(str(cp),check_existing=True)
     if op.exists() and op.stat().st_size>1000:source_orm=bpy.data.images.load(str(op),check_existing=True);source_orm.colorspace_settings.name='Non-Color'
    c=pixels(source_color);orm=pixels(source_orm)
    base,edge,rough,metal=PALETTES[family]
    lum=c.mean(axis=2);relative=lum/(lum.mean()+1e-8)
    # Existing bright abrasion pixels and existing rough/grime variation retain placement.
    worn=np.clip((relative-1.05)*2.4,0,.6)
    patina=np.clip((orm[:,:,1]-np.median(orm[:,:,1]))*3.5,0,.5)
    b=np.array(base,np.float32)
    if era=='maker':b*=np.array((1.03,1.00,.94));patina*=.2;worn*=.5
    elif era=='mechanic':b*=np.array((.98,.95,.90))
    rgb=b[None,None,:]*np.clip(relative,.66,1.35)[:,:,None]
    rgb=rgb*(1-worn[:,:,None])+np.array(edge)*worn[:,:,None]
    if family.endswith('armor'):
     # Oxide/paint are nonmetal; exposed abrasion carries bare metal response.
     rgb=rgb*(1-patina[:,:,None])+np.array((.019,.039,.026))*patina[:,:,None]
     orm[:,:,2]=np.clip(metal+worn*.95-patina*.35,.05,.92)
    else:orm[:,:,2]=np.clip(metal-patina*.40,.12,.96)
    orm[:,:,1]=np.clip(rough+(orm[:,:,1]-np.mean(orm[:,:,1]))*1.4+patina*.17-worn*.15,.28,.88)
    orm[:,:,0]=np.clip(orm[:,:,0]-.03*patina,.70,1)
    tex['color'].image=write(out/f'{family}-finish02-color.png',rgb,False)
    tex['orm'].image=write(out/f'{family}-finish02-orm.png',orm,True)
    mat['cgFinish02Family']=family;mat['cgFinish02Era']=era
    mat['surfaceStatus']='Regional proposal; owner artistic acceptance pending'
    cache[old.name]=mat
    records.append({'family':family,'source_color':source_color.name,'source_orm':source_orm.name,'color_mean':rgb.mean(axis=(0,1)).tolist(),'orm_mean':orm.mean(axis=(0,1)).tolist(),'normal':'Original retained unchanged'})
   o.data.materials[idx]=cache[old.name];slots+=1
 after={o.name:digest(o) for o in targets}
 assert before==after,'Geometry/pose/UV/polygon-index/slot-count preservation failed'
 receipt={'era':era,'assigned_slots':slots,'materials':records,'preserved_other_slots':preserved,'preservation':'PASS: all meshes, transforms, parents, UVs, polygon material indices, visibility and slot counts unchanged','texture_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.png')},'authorship':'Color and ORM derived from existing original CG2b maps; no reference pixels reused; normals retained','limits':['Regional finish artistic proposal, not owner likeness acceptance','Existing UV layout and geometry constrain wear placement','Optical slots remain untouched; integrator head-neck.apply must set Maker/Mechanic dark optics before finish.apply']}
 (Path(output_dir)/f'finish02-{era}-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt
