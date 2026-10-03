"""Deterministic CG 1b image PBR finish; importable apply(scene, output_dir, era).
No procedural-only shader or baking fallback. Original meshes/hierarchy stay intact.
Role image atlases are authored proposals, not extracted reference textures.
"""
from pathlib import Path
import hashlib
import json
import bpy
import numpy as np

SIZE = 2048
ERAS = ('maker', 'mechanic', 'builder')
FAMILIES = ('steel', 'patina', 'bronze', 'machinery')

def _noise(rng, n, cells):
    a = rng.random((cells, cells), dtype=np.float32)
    t = np.arange(n, dtype=np.float32) * cells / n
    i = t.astype(int); f = t - i; f = f*f*(3-2*f)
    return (a[i[:,None],i[None,:]]*(1-f[:,None])*(1-f[None,:]) +
            a[(i+1)[:,None]%cells,i[None,:]]*f[:,None]*(1-f[None,:]) +
            a[i[:,None],(i+1)[None,:]%cells]*(1-f[:,None])*f[None,:] +
            a[(i+1)[:,None]%cells,(i+1)[None,:]%cells]*f[:,None]*f[None,:])

def _write(path, rgb, noncolor=False):
    im = bpy.data.images.new(path.name, width=SIZE, height=SIZE, alpha=False)
    im.colorspace_settings.name = 'Non-Color' if noncolor else 'sRGB'
    rgba = np.ones((SIZE,SIZE,4), dtype=np.float32); rgba[:,:,:3] = np.clip(rgb,0,1)
    im.pixels.foreach_set(rgba.ravel()); im.filepath_raw = str(path); im.file_format='PNG'; im.save()
    # Keep editability in the native blend even if its checkout moves.
    im.pack(); return im

def _load(path, noncolor=False):
    im=bpy.data.images.load(str(path),check_existing=True)
    im.colorspace_settings.name='Non-Color' if noncolor else 'sRGB'
    im.pack(); return im

def _generate(directory, family):
    """A plate tile: mostly dark metal, many small corrosion flecks and scuffs.
    Worn UV perimeter follows the generated plate projection; no large camouflage.
    """
    paths={e:{k:directory/f'{family}-{e}-{k}.png' for k in ('color','orm')} for e in ERAS}
    normal_path=directory/f'{family}-normal.png'
    if all(p.exists() for e in paths.values() for p in e.values()) and normal_path.exists():
        return {e:{k:_load(p,k=='orm') for k,p in pp.items()}|{'normal':_load(normal_path,True)} for e,pp in paths.items()}
    n=SIZE; rng=np.random.default_rng(1917+FAMILIES.index(family)*137)
    broad=_noise(rng,n,32); fine=_noise(rng,n,170); grain=rng.random((n,n),dtype=np.float32)
    stain=np.clip((broad-.48)*3,0,1)*np.clip((fine-.38)*2.3,0,1)
    pits=np.clip((grain-.985)*50,0,1)
    # Fine hand-scored irregular grooves; distributed rather than a regular grid.
    scratches=np.zeros((n,n),dtype=np.float32)
    for _ in range(1000):
        x=int(rng.integers(n));y=int(rng.integers(n));length=int(rng.integers(8,100));slope=float(rng.uniform(-.22,.22))
        xx=(x+np.arange(length))%n; yy=(y+np.arange(length)*slope).astype(int)%n
        scratches[yy,xx]=rng.uniform(.3,1)
    d=np.minimum(np.arange(n),np.arange(n)[::-1]).astype(np.float32)
    edge=np.maximum(np.exp(-d[:,None]/10),np.exp(-d[None,:]/10))
    wear=np.clip(edge*(.35+.65*fine)+scratches*.22,0,1)
    height=.5+(fine-.5)*.035+(grain-.5)*.01-pits*.10-scratches*.06
    gy,gx=np.gradient(height); normal=np.stack((-gx*4,-gy*4,np.ones_like(gx)),axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True); normal=normal*.5+.5
    normal_image=_write(normal_path,normal,True)
    result={}
    colors={'steel':(.29,.30,.29),'patina':(.255,.285,.263),'bronze':(.35,.29,.205),'machinery':(.145,.153,.15)}
    for era in ERAS:
        aging={'maker':.15,'mechanic':.88,'builder':.72}[era]
        base=np.array(colors[family],dtype=np.float32)
        if era=='maker':base=base*np.array((1.07,1,.88),dtype=np.float32)
        variation=1+(broad-.5)*.23+(fine-.5)*.22+(grain-.5)*.09
        col=base[None,None,:]*variation[:,:,None]
        # Oxidation is dark and muted, with its strongest presence on wing armor.
        strength=aging*{'steel':.15,'patina':.56,'bronze':.18,'machinery':.04}[family]
        ox=stain*strength
        col=col*(1-ox[:,:,None])+np.array((.17,.255,.224),dtype=np.float32)*ox[:,:,None]
        col*= (1-pits*.32)[:,:,None]
        rim=np.array((.52,.435,.30) if family in ('patina','bronze') else (.46,.45,.41),dtype=np.float32)
        col=col*(1-wear[:,:,None]*.65)+rim*wear[:,:,None]*.65
        rough=np.clip({'steel':.43,'patina':.57,'bronze':.48,'machinery':.52}[family]+aging*.055+(fine-.5)*.16+pits*.22-wear*.22,.22,.8)
        metal=np.clip(.88-ox*.35-pits*.12, .52,.9)
        orm=np.stack((np.clip(1-pits*.3,0,1),rough,metal),axis=-1)
        result[era]={'color':_write(paths[era]['color'],col),'orm':_write(paths[era]['orm'],orm,True),'normal':normal_image}
    return result

def _uv(obj):
    if obj.data.uv_layers:return False
    mesh=obj.data; uv=mesh.uv_layers.new(name='CG1b projected plate UV')
    if not mesh.vertices:return False
    coords=np.array([v.co[:] for v in mesh.vertices],dtype=np.float32)
    lo=coords.min(axis=0); span=np.maximum(coords.max(axis=0)-lo,.00001)
    # Project each face onto the least-distorted box plane. Plate front faces get
    # continuous islands and worn perimeters. No context-dependent UV operators.
    for face in mesh.polygons:
        axes=[a for a in range(3) if a!=max(range(3),key=lambda a:abs(face.normal[a]))]
        for li in face.loop_indices:
            c=coords[mesh.loops[li].vertex_index]
            uv.data[li].uv=((c[axes[0]]-lo[axes[0]])/span[axes[0]],(c[axes[1]]-lo[axes[1]])/span[axes[1]])
    return True

def _family(region,role,name):
    text=(role+' '+name).lower()
    if role == 'optic' or 'lens' in text:return 'optic'
    if role in ('inner','recess','liner','frame','bearing-frame'):return 'machinery'
    if any(x in text for x in ('rivet','edge','rim','repair','brow-roof','cheek-bridge','trim')):return 'bronze'
    if role=='bearing':return 'steel'
    if any(x in text for x in ('crown','nape','plume')):return 'patina'
    if 'foot' in region or 'talon' in text or 'bill' in text or 'beak' in text:return 'steel'
    if any(x in region for x in ('wing','shoulder','breast','neck','crown','torso','mantle','body')):return 'patina'
    return 'steel'

def _material(family,era,maps):
    name=f'CG1b / {family} / {era}'; mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes=True; nt=mat.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    if family=='optic':
        c=(.10,.032,.008,1) if era=='builder' else (.012,.014,.015,1)
        bs.inputs['Base Color'].default_value=c;bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.22
        bs.inputs['Emission Color'].default_value=(1,.20,.018,1) if era=='builder' else (0,0,0,1)
        bs.inputs['Emission Strength'].default_value=.65 if era=='builder' else 0
    else:
        uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='CG1b projected plate UV'
        # UVMap node would fail on retained source UVs: default TexCoord supports
        # both retained and generated active UV sets in Blender and glTF.
        nt.nodes.remove(uv);uv=nt.nodes.new('ShaderNodeTexCoord')
        tex={}
        for k,image in maps[family][era].items():
            t=nt.nodes.new('ShaderNodeTexImage');t.image=image;t.extension='REPEAT';t.label=k;tex[k]=t
            nt.links.new(uv.outputs['UV'],t.inputs['Vector'])
        nt.links.new(tex['color'].outputs['Color'],bs.inputs['Base Color'])
        sep=nt.nodes.new('ShaderNodeSeparateColor');sep.mode='RGB';nt.links.new(tex['orm'].outputs['Color'],sep.inputs['Color'])
        nt.links.new(sep.outputs['Green'],bs.inputs['Roughness']);nt.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
        nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.55
        nt.links.new(tex['normal'].outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    mat['cg1bFamily']=family;mat['cg1bEra']=era;mat['surfaceProvenance']='Deterministic original proposed surface maps; no reference image pixels copied'
    return mat

def apply(scene, output_dir, era='builder'):
    if era not in ERAS:raise ValueError('era must be maker, mechanic or builder')
    directory=Path(output_dir)/'textures';directory.mkdir(parents=True,exist_ok=True)
    maps={f:_generate(directory,f) for f in FAMILIES}
    materials={f:_material(f,era,maps) for f in (*FAMILIES,'optic')}
    counts={f:0 for f in materials};uv_count=0
    for obj in scene.objects:
        if obj.type!='MESH' or obj.get('authoringGuide'):continue
        region=str(obj.get('cg1bRegion') or obj.get('region') or '')
        role=str(obj.get('surfaceRole') or 'plate')
        if not region:continue
        uv_count+=int(_uv(obj))
        family=_family(region,role,obj.name)
        if not obj.data.materials:obj.data.materials.append(materials[family])
        else:
            for slot in obj.material_slots:
                # Preserve slot-level gaps on mixed armor/frame meshes.
                slot_family=family
                if len(obj.material_slots)>1 and slot.material and ('frame' in slot.material.name.lower() or slot.material.get('cg1bFamily')=='machinery'):slot_family='machinery'
                slot.material=materials[slot_family]
        obj['cg1bSurfaceFamily']=family;counts[family]+=1
    files=sorted(directory.glob('*.png'))
    return {'era':era,'families':counts,'generatedUVs':uv_count,'size':[SIZE,SIZE],
            'textureCount':len(files),'textureHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            'method':'Direct image base color, ORM green roughness/blue metallic, tangent normal. Deterministic projected plate UV. No bake fallback.',
            'limits':['Plate projection approximates perimeter wear; tiny cylindrical bearings may show seams.','Owner likeness acceptance pending; no engineering claim.']}
