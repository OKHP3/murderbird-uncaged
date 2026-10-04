"""Successor regional metal finish; original objects, slots, graphs and images exact.
apply(scene, root_path, era) uses only currently visible assigned materials.
"""
from pathlib import Path
import hashlib, importlib.util, json, struct, zlib
import bpy
import numpy as np
PALETTE={
 'head-armor':((.022,.029,.025),(.20,.142,.064),.43,.83),
 'breast-armor':((.020,.027,.023),(.19,.125,.050),.46,.81),
 'wing-armor':((.023,.030,.025),(.20,.140,.061),.44,.84),
 'forged-steel':((.039,.042,.034),(.17,.135,.078),.45,.87),
 'machined-steel':((.078,.075,.058),(.24,.205,.129),.35,.94),
 'worn-bronze':((.081,.058,.025),(.22,.151,.062),.47,.88),
 'black-iron':((.008,.012,.010),(.040,.047,.036),.64,.53)}
def mod(root,name):
 p=Path(root)/'scripts'/name;s=importlib.util.spec_from_file_location('finish01_'+p.stem.replace('-','_'),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def write_exact(writer,path,values,data):
 """Immutable deterministic map reuse, verifying exact encoded PNG bytes."""
 h,w,_=values.shape;encoded=np.clip(values,0,1) if data else writer.linear_to_srgb(values)
 rgb8=np.floor(encoded*255+.5).astype(np.uint8)
 def chunk(tag,payload):return struct.pack('>I',len(payload))+tag+payload+struct.pack('>I',zlib.crc32(tag+payload)&0xffffffff)
 raw=b''.join(b'\x00'+row.tobytes() for row in rgb8[::-1])
 content=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))
 if not data:content+=chunk(b'sRGB',b'\x00')
 content+=chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b'')
 if path.exists():
  if path.read_bytes()!=content:raise RuntimeError('Existing successor map differs: '+str(path))
  im=bpy.data.images.load(str(path.resolve()),check_existing=False);im.colorspace_settings.name='Non-Color' if data else 'sRGB';im.pack();return im
 return writer.write(path,values,data)

def apply(scene,root_path,era='builder'):
 if era not in ('maker','mechanic','builder'):raise ValueError(era)
 if any(o.get('cgRecursiveFinish01') for o in scene.objects):raise RuntimeError('Reload exact receiving scene')
 root=Path(root_path);writer=mod(root,'cg-supervised-finish04.py');metal=mod(root,'cg-supervised-metal05.py')
 own=Path(__file__).resolve().parents[1];out=own/'assets/models/cg-recursive-finish01'/'attempt02'/'textures'/era
 out.mkdir(parents=True,exist_ok=True)

 coll=bpy.data.collections.new('Recursive FINISH01 regional successor');scene.collection.children.link(coll)
 cache={};records=[];replacements=[];hidden={};new=[]
 age={'maker':.20,'mechanic':1.0,'builder':.80}[era]
 # Selection uses actual visible current slots, never a global first-family lookup.
 sources=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide') and not o.hide_get()]
 for original in sources:
  slots=[]
  for i,slot in enumerate(original.material_slots):
   old=slot.material
   family=old.get('cgMetal05Family') if old else None
   if family not in PALETTE or old.get('cg2aPreserveMaterial'):continue
   local=any('local' in u.name for u in original.data.uv_layers)
   variant=int(hashlib.sha256(original.name.encode()).hexdigest()[:8],16)%3 if local else 0
   role='bill' if 'bill' in original.name.lower() else 'brow' if family=='worn-bronze' and ('brow' in original.name.lower() or 'dorsal' in original.name.lower()) else 'plate'
   key=(old.name,family,local,variant,role)
   if key not in cache:
    mat=old.copy();mat.name=f'CGRF01 {era} {family} {role} {len(cache):02d}'
    tex={n.label:n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'}
    if not all(k in tex and tex[k].image for k in ('color','orm')):raise RuntimeError('Unsupported source graph '+old.name)
    c=writer.pixels(tex['color'].image);orm=writer.pixels(tex['orm'].image);h,w,_=c.shape
    yy,xx=np.mgrid[:h,:w].astype(np.float32);u=xx/max(1,w-1);v=yy/max(1,h-1)
    field=metal.mottling(h,w,4117+variant*129+list(PALETTE).index(family)*67)
    relative=np.clip(c.mean(2)/(c.mean()+1e-8),.55,1.65)
    base,edge,rough,met=PALETTE[family];base=np.array(base);edge=np.array(edge)
    if era=='maker':base*=np.array((1.15,1.10,.98));rough-=.065
    elif era=='mechanic':base*=np.array((.96,.91,.85));rough+=.05
    if role=='bill':base=np.array((.017,.023,.022));edge=np.array((.14,.128,.091));met=.88
    if role=='brow':base=np.array((.095,.072,.035));edge=np.array((.23,.184,.101));rough=.44
    # Existing wear determines placement on historic UVs. Local sheet borders
    # have separately directional overlap shadows and discontinuous rubbed tips.
    wear=np.clip((relative-1.03)*.34,0,.25)*(.35+.65*age)
    overlap=np.zeros((h,w),np.float32)
    if local:
     distance=np.minimum(np.minimum(u,1-u),1-v)
     border=np.clip(1-distance/.037,0,1)
     broken=np.clip(.44+field*1.8,0,1)
     wear=np.maximum(wear,border*broken*(.37+.55*age))
     overlap=np.clip(1-v/.125,0,1)*(.12+.12*age)*(1+.3*field)
    # A few irregular chipped patches; no periodic uniform noise overlay.
    chips=np.zeros((h,w),np.float32)
    if local and family.endswith('armor'):
     rng=np.random.default_rng(192+variant)
     for n in range(7):
      cx,cy=rng.uniform(.06,.94),rng.uniform(.1,.94);rx,ry=rng.uniform(.015,.043),rng.uniform(.010,.025)
      patch=np.clip(1-((u-cx)/rx)**2-((v-cy)/ry)**2,0,1)
      chips=np.maximum(chips,patch*np.clip(.45+field,0,1))
     wear=np.maximum(wear,chips*age*.76)
    patina=np.clip(field+.05,0,.65)*age*.40
    rgb=base[None,None,:]*np.clip(.9+(relative-1)*.32+field*.38,.5,1.45)[:,:,None]
    rgb=rgb*(1-wear[:,:,None])+edge*wear[:,:,None]
    rgb=rgb*(1-patina[:,:,None])+np.array((.019,.029,.022))*patina[:,:,None]
    rgb*=1-overlap[:,:,None]
    orm[:,:,0]=np.clip(orm[:,:,0]-overlap*.3,.65,1)
    orm[:,:,1]=np.clip(rough+field*.065+patina*.3+overlap*.15-wear*.17,.25,.88)
    orm[:,:,2]=np.clip(met-patina*.46-overlap*.16+wear*.10,.40,.98)
    stem=f'{len(cache):02d}-{family}-{role}'
    cp=out/(stem+'-color.png');op=out/(stem+'-orm.png')
    tex['color'].image=write_exact(writer,cp,rgb,False);tex['orm'].image=write_exact(writer,op,orm,True)
    for node in mat.node_tree.nodes:
     if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=min(node.inputs['Strength'].default_value,.06)
    mat['cgRecursiveFinish01']=True;mat['surfaceStatus']='Source-informed regional proposal; owner acceptance pending'
    cache[key]=mat
    records.append(dict(material=mat.name,sourceMaterial=old.name,family=family,role=role,localBoundaries=local,variant=variant,color=str(cp),orm=str(op),linearColorMean=rgb.mean((0,1)).tolist(),roughMetalMean=orm.mean((0,1)).tolist()))
   slots.append((i,cache[key],old.name))
  if not slots:continue
  successor=original.copy();successor.data=original.data.copy();successor.data.name='CGRF01 exact geometry '+original.data.name;successor.name='CGRF01 '+original.name;coll.objects.link(successor)
  # Independent exact mesh copy supplies DATA bindings for modifier evaluation.
  for i,mat,oldname in slots:successor.material_slots[i].link='DATA';successor.material_slots[i].material=mat
  successor['cgRecursiveFinish01']=True;successor['cgFinishSourceObject']=original.name
  successor.hide_render=False;successor.hide_set(False)
  hidden[original.name]=dict(before=[original.hide_render,original.hide_viewport,original.hide_get()],after=[True,original.hide_viewport,True],hide_set=True)
  original.hide_render=True;original.hide_set(True)
  new.append(successor.name);replacements.append(dict(original=original.name,successor=successor.name,slots=[dict(index=i,source=m,new=mat.name) for i,mat,m in slots]))
 bpy.context.view_layer.update()
 return dict(module='cg-recursive-finish01',era=era,newMeshes=new,hideOverrides=hidden,materials=records,replacements=replacements,newMaps=[str(p) for p in out.glob('*.png')],custody='Original mesh datablocks, slots and graph/image IDs unchanged; exact successor mesh copies use DATA material bindings',scope='Visual regional proposal from pinned source; no source pixels copied, no optical changes',limits=['UV-constrained wear; broader construction remains simplified','Visual gain requires whole neutral/workshop comparison','Owner likeness acceptance pending'])
