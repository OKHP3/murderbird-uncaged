"""CG 1c regional image PBR finishing, reusing preserved original 1b maps.
API: apply(scene, output_dir, era='builder', reference_root=None).
No geometry, lighting, camera, source pixel copying or procedural-only textures.
"""
from pathlib import Path
import hashlib
import bpy

ERAS=('maker','mechanic','builder')
FAMILIES=('patina','steel','bronze','machinery')

def _uv(obj):
    mesh=obj.data
    if mesh.uv_layers:return False
    uv=mesh.uv_layers.new(name='CG1c plate projection')
    if not mesh.vertices:return False
    lo=[min(v.co[a] for v in mesh.vertices) for a in range(3)]
    span=[max(max(v.co[a] for v in mesh.vertices)-lo[a],1e-6) for a in range(3)]
    for p in mesh.polygons:
        drop=max(range(3),key=lambda a:abs(p.normal[a]))
        axes=[a for a in range(3) if a!=drop]
        for i in p.loop_indices:
            v=mesh.vertices[mesh.loops[i].vertex_index].co
            uv.data[i].uv=((v[axes[0]]-lo[axes[0]])/span[axes[0]],(v[axes[1]]-lo[axes[1]])/span[axes[1]])
    return True

def _family(obj):
    role=str(obj.get('surfaceRole','plate')).lower()
    name=obj.name.lower();region=str(obj.get('cg1cRegion','')).lower()
    if role in ('optic','lens'):return 'optic'
    if obj.get('cg1cMaterialFamily')=='machinery-steel':return 'machinery'
    if 'study_part' in obj and not region:
        return 'steel' if 'bill' in name else 'machinery'
    if role in ('inner','frame','liner','recess','machinery','backing'):return 'machinery'
    if role in ('rivet','edge','rim','trim','repair'):return 'bronze'
    if role in ('bill','talon','bearing','piston','shaft'):return 'steel'
    if any(x in name+' '+region for x in ('bill','talon','claw')):return 'steel'
    return 'patina'

def _material(family,era,images):
    name=f'CG1c / {family} / {era}'
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    m['cg1cFamily']=family;m['cg1cEra']=era
    m['surfaceProvenance']='Original deterministic 1b PBR tiles, reused without copying pinned artwork pixels'
    if family=='optic':
        c=(.07,.025,.006,1) if era=='builder' else (.008,.010,.011,1)
        bs.inputs['Base Color'].default_value=c;bs.inputs['Metallic'].default_value=.4;bs.inputs['Roughness'].default_value=.19
        bs.inputs['Emission Color'].default_value=(1,.20,.015,1) if era=='builder' else (0,0,0,1)
        bs.inputs['Emission Strength'].default_value=.6 if era=='builder' else 0
        m.diffuse_color=c;return m
    tex={}
    uv=nt.nodes.new('ShaderNodeTexCoord')
    for role in ('color','orm','normal'):
        t=nt.nodes.new('ShaderNodeTexImage');t.image=images[family][role];t.extension='REPEAT';t.label=role
        nt.links.new(uv.outputs['UV'],t.inputs['Vector']);tex[role]=t
    nt.links.new(tex['color'].outputs['Color'],bs.inputs['Base Color'])
    sep=nt.nodes.new('ShaderNodeSeparateColor');sep.mode='RGB';nt.links.new(tex['orm'].outputs['Color'],sep.inputs['Color'])
    nt.links.new(sep.outputs['Green'],bs.inputs['Roughness']);nt.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
    normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.5
    nt.links.new(tex['normal'].outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
    m.diffuse_color={'patina':(.08,.10,.085,1),'steel':(.09,.095,.09,1),'bronze':(.16,.10,.04,1),'machinery':(.015,.018,.017,1)}[family]
    m.metallic=.85;m.roughness=.5
    return m

def apply(scene,output_dir,era='builder',reference_root=None):
    if era not in ERAS:raise ValueError('Unknown CG1c era: '+str(era))
    root=Path(reference_root) if reference_root else Path(__file__).resolve().parents[1]
    maps=root/'assets/models/cinematic-cg-milestone01b/textures'
    # Missing maps fail explicitly: a uniform fallback would hide lost surfaces.
    paths={f:{'color':maps/f'{f}-{era}-color.png','orm':maps/f'{f}-{era}-orm.png','normal':maps/f'{f}-normal.png'} for f in FAMILIES}
    missing=[str(p) for pp in paths.values() for p in pp.values() if not p.is_file()]
    if missing:raise FileNotFoundError('Required preserved PBR maps unavailable: '+', '.join(missing))
    images={};hashes={}
    for f,pp in paths.items():
        images[f]={}
        for role,p in pp.items():
            im=bpy.data.images.load(str(p),check_existing=True)
            im.colorspace_settings.name='sRGB' if role=='color' else 'Non-Color'
            if not im.packed_file:im.pack()
            images[f][role]=im;hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    materials={f:_material(f,era,images) for f in (*FAMILIES,'optic')}
    counts={f:0 for f in materials};uv_count=0;skipped=0
    for obj in scene.objects:
        if obj.type!='MESH' or obj.get('authoringGuide'):continue
        if not (obj.get('cg1cRegion') or obj.get('study_part')):
            skipped+=1;continue
        family=_family(obj);uv_count+=int(_uv(obj));counts[family]+=1
        obj.data.materials.clear();obj.data.materials.append(materials[family])
        for poly in obj.data.polygons:poly.material_index=0
        obj['cg1cSurfaceFamily']=family
    return {'era':era,'objectCounts':counts,'generatedUVs':uv_count,'untaggedMeshesSkipped':skipped,
            'materials':[m.name for m in materials.values()],'textureHashes':hashes,'textureCount':len(hashes),
            'textureSource':str(maps),'embeddedNativeImages':True,
            'method':'Existing original image tiles: direct BaseColor, packed ORM G/Roughness B/Metallic, tangent normal; no procedural-only nodes.',
            'limitations':['Projected plate UV approximate edge wear; curved source cages retain their original UVs.','Original surface proposal; artistic likeness requires owner review.']}
