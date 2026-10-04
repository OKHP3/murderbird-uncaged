"""Regional worked-metal overlay. Call after surface03 and finish04.

API apply(scene, output_dir, era='builder', reference_root=None). Existing
graphs/normal-image bytes survive; novel UV border wear only on Body05 sheets.
Source artwork is consulted visually, never sampled into these maps.
"""
from pathlib import Path
import hashlib, importlib.util, json
import bpy
import numpy as np

ERAS=('maker','mechanic','builder')
PALETTES={
 'head-armor':((.030,.042,.032),(.19,.145,.070),.48,.70),
 'breast-armor':((.025,.038,.027),(.17,.125,.055),.52,.65),
 'wing-armor':((.028,.043,.032),(.16,.125,.061),.51,.68),
 'forged-steel':((.065,.068,.058),(.20,.18,.125),.47,.83),
 'machined-steel':((.145,.151,.137),(.30,.29,.245),.34,.94),
 'worn-bronze':((.145,.104,.048),(.30,.225,.100),.45,.87),
 'black-iron':((.012,.018,.015),(.050,.054,.039),.71,.38)}
WRITER_SHA='000a8c09e7f3cef9987dfdc54ac08caa466937734b56a201ee0a5bd5a89d32b4'

def helper(root):
 p=Path(root)/'scripts/cg-supervised-finish04.py'
 if hashlib.sha256(p.read_bytes()).hexdigest()!=WRITER_SHA:raise RuntimeError('Unpinned finish04 FILE writer')
 s=importlib.util.spec_from_file_location('metal05_finish04_writer',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def packed(im):
 return hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im and im.packed_file else None

def aggregate(rows):return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def apply(scene,output_dir,era='builder',reference_root=None):
 if era not in ERAS:raise ValueError(era)
 root=Path(reference_root or Path(__file__).resolve().parents[1]);f=helper(root)
 out=Path(output_dir);texout=out/'textures'/era
 if texout.exists() and any(texout.glob('*.png')):raise RuntimeError('Write-once overlay; choose new output')
 texout.mkdir(parents=True,exist_ok=True)
 objects=[o for o in scene.objects if o.type=='MESH' and not o.get('authoringGuide')]
 before={o.name:f.digest(o) for o in objects};cache={};records=[];preserved=[];routes=[]
 for o in objects:
  families=o.get('cgSurfaceFamilies')
  if isinstance(families,str):families=json.loads(families)
  if families is not None and len(families)!=len(o.data.materials):raise ValueError('Ordered slot count mismatch: '+o.name)
  local=bool(o.get('cgSupervisedBody05')) and any(u.name=='body05-local-curved-uv' for u in o.data.uv_layers)
  # Four deterministic tile variants break repetitive wear; shared geometry stays untouched.
  variant=int(hashlib.sha256(o.name.encode()).hexdigest()[:8],16)%4 if local else 0
  for idx,old in enumerate(o.data.materials):
   family=families[idx] if families is not None else (old.get('cg2bFamily') if old else None)
   if family in ('protected-optic','protected-glass') or (old and old.get('cg2aPreserveMaterial')) or family is None:
    preserved.append([o.name,idx,old.name if old else None,old.as_pointer() if old else None]);continue
   if family not in PALETTES:raise ValueError(f'{o.name} slot {idx}: unknown {family}')
   key=(old.name,family,local,variant)
   if key not in cache:
    if not old.use_nodes:raise ValueError('Expected existing hard surface graph')
    mat=old.copy();mat.name=f'CG metal05 / {family} / {era} / '+(f'local{variant}' if local else 'retained-uv')
    nodes=mat.node_tree.nodes;tex={n.label:n for n in nodes if n.type=='TEX_IMAGE'}
    if any(k not in tex or not tex[k].image for k in ('color','orm')):raise ValueError('Missing texture graph '+old.name)
    retained=[(n,n.image,packed(n.image)) for n in nodes if n.type=='TEX_IMAGE' and n.label not in ('color','orm')]
    c=f.pixels(tex['color'].image);orm=f.pixels(tex['orm'].image);h,w,_=c.shape
    y,x=np.mgrid[0:h,0:w].astype(np.float32);u=x/(w-1);t=y/(h-1)
    phase=variant*1.83
    # Procedural mineral mottling plus existing authored grime. No image pixels from art.
    field=(np.sin(u*21+t*9+phase)+.55*np.sin(u*53-t*37+phase*2)+.3*np.sin(u*139+t*123))/1.85
    relative=np.clip(c.mean(2)/(c.mean()+1e-8),.68,1.4)
    grime=np.clip((orm[:,:,1]-np.median(orm[:,:,1]))*2.1,0,.45)
    patina=np.clip((field-.22)*.33,0,.23)+grime*.28
    age={'maker':.34,'mechanic':1.0,'builder':.82}[era]
    grime*=age;patina*=age
    base,edge,rough,metal=PALETTES[family];base=np.array(base,dtype=np.float32)
    if era=='maker':base*=np.array((1.12,1.08,1.00));rough-=.065
    elif era=='mechanic':base*=np.array((.94,.94,.91));rough+=.025
    # Tiny discontinuous worked abrasions; boundaries are interpreted ONLY on local sheets.
    authored=np.clip((relative-1.18)*.20,0,.055)
    wear=authored
    overlap=np.zeros((h,w),np.float32)
    if local and family.endswith('armor'):
     dist=np.minimum(np.minimum(u,1-u),1-t)
     border=np.clip(1-dist/.032,0,1)
     broken=np.clip(.40+field*.78,0,1)
     wear=np.maximum(wear,border*broken*(.42 if era=='maker' else .68))
     overlap=np.clip(1-t/.17,0,1)*(.12+np.clip(field,0,1)*.10)*age
    # Sparse broad-direction scratch traces; strength kept small to avoid hair/banding.
    trace=np.power(np.clip(np.sin(u*173+t*83+phase),0,1),55)*np.clip(field-.45,0,.55)
    wear=np.clip(wear+trace*.13*age,0,.7)
    rgb=base[None,None,:]*np.clip(.98+field*.22+(relative-1)*.32,.64,1.38)[:,:,None]
    rgb=rgb*(1-wear[:,:,None])+np.array(edge)*wear[:,:,None]
    rgb=rgb*(1-patina[:,:,None])+np.array((.016,.036,.028))*patina[:,:,None]
    rgb*=1-(grime*.27+overlap)[:,:,None]
    orm[:,:,0]=np.clip(orm[:,:,0]-overlap*.25-grime*.04,.68,1)
    orm[:,:,1]=np.clip(rough+field*.045+grime*.15+overlap*.20-wear*.20,.25,.86)
    orm[:,:,2]=np.clip(metal+wear*(.94-metal)-patina*.62-grime*.12-overlap*.22,.16,.97)
    stem=f'{family}-'+(f'body05-local{variant}' if local else 'retained-uv')
    cp=texout/(stem+'-color.png');op=texout/(stem+'-orm.png')
    tex['color'].image=f.write(cp,rgb,False);tex['orm'].image=f.write(op,orm,True)
    strength=[]
    for n in nodes:
     if n.type=='NORMAL_MAP':
      initial=float(n.inputs['Strength'].default_value);adjusted=min(initial,.14 if local else .23)
      n.inputs['Strength'].default_value=adjusted;strength.append([n.name,initial,adjusted])
    assert all(n.image==im and packed(n.image)==sha for n,im,sha in retained)
    mat['cgMetal05Family']=family;mat['cgMetal05Era']=era;mat['cgMetal05LocalBoundary']=local
    mat['surfaceStatus']='Worked-metal proposal; owner likeness acceptance pending'
    cache[key]=mat
    encoded=np.floor(f.linear_to_srgb(rgb)*255+.5)/255
    records.append({'family':family,'local_body05_boundary':local,'variant':variant,'paths':[str(cp.relative_to(out)),str(op.relative_to(out))],
     'intended_linear_mean':rgb.mean((0,1)).tolist(),'written_srgb_mean':encoded.mean((0,1)).tolist(),'decoded_linear_mean':f.srgb_to_linear(encoded).mean((0,1)).tolist(),'orm_mean':orm.mean((0,1)).tolist(),
     'normal_strengths':strength,'retained_images':[{'label':n.label,'name':im.name,'packed_sha256':sha} for n,im,sha in retained],
     'preserved_links':aggregate([(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links])})
   o.data.materials[idx]=cache[key];routes.append([o.name,idx,family,local,variant])
 after={o.name:f.digest(o) for o in objects};assert before==after,'Frozen mesh/UV/transform/face-index/slot-count changed'
 assert all(scene.objects[n].data.materials[i].as_pointer()==ptr for n,i,name,ptr in preserved if ptr),'Protected material changed'
 receipt={'era':era,'writer_sha256':WRITER_SHA,'encoding':'Explicit scene-linear to sRGB RGB8 PNG, FILE reload sRGB. ORM numeric RGB8 PNG, FILE reload Non-Color; packed. Original normal pixels/UV unchanged.',
  'materials':records,'routes':routes,'texture_hashes':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in texout.glob('*.png')},
  'preservation':{'meshes':len(before),'before_digest':aggregate(before),'after_digest':aggregate(after),'pass':before==after,'protected_slots':len(preserved),'protected_order_digest':aggregate([p[:3] for p in preserved]),'slot_counts_polygon_indices_uvs_transforms':'Unchanged'},
  'source_inference':'Visual palette and material separation inferred from pinned full-bird and three era images. Lighting, tone mapping and source materials cannot be recovered from pixels. No reference artwork pixels used in textures.',
  'limits':['UV-edge wear applies only to Body05 local sheets; historic UVs retain authored placement','Normal bytes unchanged; strength reduced to cap oversized grain','Seven material families preserved; machinery topology remains stylized','Optics untouched; head integrator must set Maker/Mechanic dark optics','No full native or full geometry export; inherited glass UV defect excluded from this scope','Unaccepted proposal; source likeness and publication not established']}
 (out/f'metal05-{era}-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
