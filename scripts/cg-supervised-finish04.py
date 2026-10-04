"""Color-transfer correction of frozen finish04, using retained authored CG2b maps, never artwork pixels.
API: apply(scene, output_dir, era='builder', reference_root=None).
Preserves every slot index, polygon assignment, UV and mesh/pose; protected optics untouched.
"""
from pathlib import Path
import json, hashlib, struct, zlib
import bpy
import numpy as np

ERAS=('maker','mechanic','builder')
# Scene-linear map targets: dark green protective finish, warm worked bare metal.
# Explicitly encode linear targets to sRGB PNG bytes; load FILE images for decoding.
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

def linear_to_srgb(values):
 a=np.clip(np.asarray(values),0,1)
 return np.where(a<=.0031308,a*12.92,1.055*np.power(a,1/2.4)-.055)

def srgb_to_linear(values):
 a=np.asarray(values)
 return np.where(a<=.04045,a/12.92,np.power((a+.055)/1.055,2.4))

def write(path,values,data):
 """Write RGB8 with explicit transfer; bpy rows are bottom-up, PNG top-down.

 ORM stays numeric Non-Color. Colors use IEC 61966-2-1 transfer exactly once.
 FILE reload is essential: GENERATED pixels marked sRGB save raw pixel values.
 """
 path=Path(path);h,w,_=values.shape
 encoded=np.clip(values,0,1) if data else linear_to_srgb(values)
 rgb8=np.floor(encoded*255+.5).astype(np.uint8)
 def chunk(tag,payload):
  return struct.pack('>I',len(payload))+tag+payload+struct.pack('>I',zlib.crc32(tag+payload)&0xffffffff)
 raw=b''.join(b'\x00'+row.tobytes() for row in rgb8[::-1])
 content=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))
 if not data:content+=chunk(b'sRGB',b'\x00')
 content+=chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b'')
 path.write_bytes(content)
 im=bpy.data.images.load(str(path.resolve()),check_existing=False)
 im.colorspace_settings.name='Non-Color' if data else 'sRGB'
 im.pack()
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
    mat=old.copy();mat.name='CG supervised finish04 / '+family+' / '+era
    nodes=mat.node_tree.nodes
    tex={n.label:n for n in nodes if n.type=='TEX_IMAGE'}
    source_color=tex['color'].image;source_orm=tex['orm'].image
    normal_images={n.label:n.image for n in nodes if n.type=='TEX_IMAGE' and n.label not in ('color','orm')}
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
    tex['color'].image=write(out/f'{family}-finish04-color.png',rgb,False)
    tex['orm'].image=write(out/f'{family}-finish04-orm.png',orm,True)
    assert all(n.image==normal_images[n.label] for n in nodes if n.type=='TEX_IMAGE' and n.label in normal_images),'Retained normal image changed'
    mat['cgFinish04Family']=family;mat['cgFinish04Era']=era
    mat['surfaceStatus']='Regional proposal; owner artistic acceptance pending'
    cache[old.name]=mat
    records.append({'family':family,'source_color':source_color.name,'source_orm':source_orm.name,'color_path':str((out/f'{family}-finish04-color.png').resolve()),'orm_path':str((out/f'{family}-finish04-orm.png').resolve()),'intended_linear_mean':rgb.mean(axis=(0,1)).tolist(),'encoded_png_mean':(np.floor(linear_to_srgb(rgb)*255+.5)/255).mean(axis=(0,1)).tolist(),'decoded_linear_mean':srgb_to_linear(np.floor(linear_to_srgb(rgb)*255+.5)/255).mean(axis=(0,1)).tolist(),'orm_mean':orm.mean(axis=(0,1)).tolist(),'normal':'Original retained unchanged','retained_images':[{'label':label,'name':im.name,'colorspace':im.colorspace_settings.name,'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im and im.packed_file else None} for label,im in normal_images.items() if im]})
   o.data.materials[idx]=cache[old.name];slots+=1
 after={o.name:digest(o) for o in targets}
 assert before==after,'Geometry/pose/UV/polygon-index/slot-count preservation failed'
 receipt={'encoding':'Color RGB8 PNG: explicit linear to sRGB transfer; FILE reload sRGB and pack. ORM RGB8 PNG: numeric values, FILE reload Non-Color and pack.','era':era,'assigned_slots':slots,'materials':records,'preserved_other_slots':preserved,'preservation':'PASS: all meshes, transforms, parents, UVs, polygon material indices, visibility and slot counts unchanged','texture_hashes':{str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.png')},'authorship':'Color and ORM derived from existing original CG2b maps; no reference pixels reused; normals retained','mesh_digests_before':before,'mesh_digests_after':after,'limits':['RGB8 quantization remains; no palette or lighting change','Regional finish artistic proposal, not owner likeness acceptance','Existing UV layout and geometry constrain wear placement','Optical slots remain untouched; integrator head-neck.apply must set Maker/Mechanic dark optics before finish.apply']}
 (Path(output_dir)/f'finish04-{era}-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt
