"""Original deterministic 2K CG2a metal tiles. No source artwork/map pixels reused.
Direct image PBR only; apply preserves object shape, pose, UV and glass shaders.
"""
from pathlib import Path
import hashlib,json
import bpy
import numpy as np

SIZE=2048
SEED=202610032
ERAS=('maker','mechanic','builder')
FAMILIES=('armor','steel','bronze','machinery')

def noise(rng,cells):
    a=rng.random((cells,cells),dtype=np.float32)
    c=np.arange(SIZE,dtype=np.float32)*cells/SIZE;i=c.astype(int);f=c-i;f=f*f*(3-2*f)
    return (a[i[:,None],i[None,:]]*(1-f[:,None])*(1-f[None,:])+a[(i+1)[:,None]%cells,i[None,:]]*f[:,None]*(1-f[None,:])+a[i[:,None],(i+1)[None,:]%cells]*(1-f[:,None])*f[None,:]+a[(i+1)[:,None]%cells,(i+1)[None,:]%cells]*f[:,None]*f[None,:])

def write(path,rgb,data=False):
    im=bpy.data.images.new(path.name,width=SIZE,height=SIZE,alpha=False)
    im.colorspace_settings.name='Non-Color' if data else 'sRGB'
    rgba=np.ones((SIZE,SIZE,4),dtype=np.float32);rgba[:,:,:3]=np.clip(rgb,0,1)
    im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(path);im.file_format='PNG';im.save();im.pack();return im

def generate(directory,family):
    """Thin plate steel, etched rather than camouflage-scale weathering."""
    normal=directory/f'{family}-2a-normal.png'
    paths={era:{'color':directory/f'{family}-{era}-2a-color.png','orm':directory/f'{family}-{era}-2a-orm.png'} for era in ERAS}
    if normal.exists() and all(p.exists() for pp in paths.values() for p in pp.values()):return paths,normal
    n=SIZE;rng=np.random.default_rng(SEED+FAMILIES.index(family)*173)
    uneven=noise(rng,42);etch=noise(rng,230);grain=rng.random((n,n),dtype=np.float32)
    pits=np.clip((grain-.993)*140,0,1)*(etch>.42)
    scratches=np.zeros((n,n),dtype=np.float32)
    for _ in range(1800):
        x,y=rng.integers(0,n,2);length=int(rng.integers(7,140));step=np.arange(length)
        xx=(x+step)%n;yy=(y+step*rng.uniform(-.75,.75)).astype(int)%n
        scratches[yy,xx]=rng.uniform(.2,.85)
    d=np.minimum(np.arange(n),np.arange(n)[::-1]).astype(np.float32)
    border=np.maximum(np.exp(-d[:,None]/4),np.exp(-d[None,:]/4))
    # Interrupted worn edges and faint scored patches; no continuous gold lattice.
    wear=np.clip(border*np.clip((etch-.32)*2,0,1)+scratches*.25,0,1)
    dirt=border*.32+np.clip((uneven-.64)*3.5,0,.45)
    height=(etch-.5)*.027+(grain-.5)*.008-pits*.085-scratches*.035
    gy,gx=np.gradient(height);normal_pixels=np.stack((-gx*3.6,-gy*3.6,np.ones_like(gx)),axis=-1)
    normal_pixels/=np.linalg.norm(normal_pixels,axis=-1,keepdims=True)
    write(normal,normal_pixels*.5+.5,True)
    base={'armor':(.245,.244,.215),'steel':(.255,.264,.257),'bronze':(.29,.247,.177),'machinery':(.086,.094,.088)}[family]
    for era in ERAS:
        age={'maker':.12,'mechanic':1,'builder':.82}[era]
        c=np.array(base,dtype=np.float32)
        if era=='maker':c*=np.array((1.02,1.025,1.06),dtype=np.float32)
        oxidation=np.clip((uneven-.50)*3.5,0,1)*np.clip((etch-.37)*2.4,0,1)*age
        ox=oxidation*{'armor':.40,'steel':.12,'bronze':.18,'machinery':.06}[family]
        variation=1+(etch-.5)*.27+(grain-.5)*.16+(uneven-.5)*.12
        rgb=c[None,None,:]*variation[:,:,None]
        rgb=rgb*(1-ox[:,:,None])+np.array((.115,.204,.171),dtype=np.float32)*ox[:,:,None]
        rgb*= (1-dirt*age*.55-pits*.30)[:,:,None]
        edge=np.array((.47,.39,.255) if family in ('armor','bronze') else (.48,.49,.46),dtype=np.float32)
        rgb=rgb*(1-wear[:,:,None]*.68)+edge*wear[:,:,None]*.68
        rough_base={'armor':.40,'steel':.30,'bronze':.34,'machinery':.40}[family]
        rough=np.clip(rough_base+(etch-.5)*.17+ox*.24+pits*.30+age*.035-wear*.15,.18,.76)
        metal=np.clip(.94-ox*.45-pits*.19-dirt*.12,.48,.96)
        orm=np.stack((np.clip(1-dirt*.4-pits*.25,.55,1),rough,metal),axis=-1)
        write(paths[era]['color'],rgb);write(paths[era]['orm'],orm,True)
    return paths,normal

def classify(o):
    role=str(o.get('surfaceRole','plate')).lower();name=o.name.lower()
    if o.get('cg2aPreserveMaterial') or role in ('glass','lens-glass'):return None
    if role in ('optic','lens'):return 'optic'
    if role in ('inner','recess','frame','liner','backing','machinery') or (o.get('study_part') and not o.get('cg1cRegion')):return 'machinery'
    if role in ('rivet','repair','trim'):return 'bronze'
    if role in ('edge','rim','bill','talon','bearing','piston','shaft') or any(x in name for x in ('bill','talon','claw')):return 'steel'
    return 'armor'

def material(family,era,images):
    m=bpy.data.materials.new(f'CG2a / {family} / {era}');m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear();bs=nt.nodes.new('ShaderNodeBsdfPrincipled');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    if family=='optic':
        bs.inputs['Base Color'].default_value=(.024,.010,.002,1) if era=='builder' else (.003,.005,.005,1)
        bs.inputs['Metallic'].default_value=.22;bs.inputs['Roughness'].default_value=.19
        bs.inputs['Emission Color'].default_value=(1,.13,.008,1) if era=='builder' else (0,0,0,1)
        bs.inputs['Emission Strength'].default_value=.55 if era=='builder' else 0
    else:
        t={}
        for role,im in images[family].items():
            node=nt.nodes.new('ShaderNodeTexImage');node.image=im;node.label=role;t[role]=node
        nt.links.new(t['color'].outputs['Color'],bs.inputs['Base Color'])
        sep=nt.nodes.new('ShaderNodeSeparateColor');sep.mode='RGB';nt.links.new(t['orm'].outputs['Color'],sep.inputs['Color'])
        nt.links.new(sep.outputs['Green'],bs.inputs['Roughness']);nt.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
        nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.50 if family=='armor' else .32
        nt.links.new(t['normal'].outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    m['cg2aFamily']=family;m['cg2aEra']=era;m['seed']=SEED
    return m

def apply(scene,output_dir,era='builder',reference_root=None):
    if era not in ERAS:raise ValueError(era)
    directory=Path(output_dir)/'textures';directory.mkdir(parents=True,exist_ok=True)
    paths={};images={};hashes={}
    for f in FAMILIES:
        pp,normal=generate(directory,f);paths[f]=pp[era]|{'normal':normal};images[f]={}
        for role,p in paths[f].items():
            im=bpy.data.images.load(str(p),check_existing=True);im.colorspace_settings.name='sRGB' if role=='color' else 'Non-Color'
            if not im.packed_file:im.pack()
            images[f][role]=im
    mats={f:material(f,era,images) for f in (*FAMILIES,'optic')};counts={f:0 for f in mats};preserved=[];missing_uv=[]
    for o in scene.objects:
        if o.type!='MESH' or o.get('authoringGuide'):continue
        if not (o.get('cg2aRegion') or o.get('cg3Region') or o.get('cg1cRegion') or o.get('study_part')):continue
        f=classify(o)
        if f is None:preserved.append(o.name);continue
        if not o.data.uv_layers and f!='optic':missing_uv.append(o.name)
        for slot in o.material_slots:slot.material=mats[f]
        if not o.material_slots:o.data.materials.append(mats[f])
        o['cg2aSurfaceFamily']=f;counts[f]+=1
    for p in sorted(directory.glob('*.png')):hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    record={'seed':SEED,'size':[SIZE,SIZE],'authorship':'Original deterministic CG2a proposal maps; no source/reference/old-map pixels reused','textureHashes':hashes,'limits':['Perimeter wear depends on retained normalized plate UVs.','Metal properties are a CG proposal, not physical measurements or artistic acceptance.']}
    (directory/'surface-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
    return record|{'era':era,'familyCounts':counts,'glassPreserved':preserved,'missingUVs':missing_uv,'materials':[m.name for m in mats.values()]}
