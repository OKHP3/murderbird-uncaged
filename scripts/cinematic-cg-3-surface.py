"""Regional PBR assignment using retained original images, without UV/shape edits."""
from pathlib import Path
import bpy

def apply(scene,output_dir,era='builder',reference_root=None):
    if era not in ('maker','mechanic','builder'):raise ValueError(era)
    root=Path(reference_root) if reference_root else Path(__file__).resolve().parents[1]
    maps=root/'assets/models/cinematic-cg-milestone01b/textures'
    images={};materials={};counts={};normal_strength={'patina':.72,'steel':.38,'bronze':.24,'machinery':.46}
    for family in ('patina','steel','bronze','machinery','optic'):
        old=next((m for m in bpy.data.materials if m.get('cg1cFamily')==family and m.get('cg1cEra')==era),None)
        mat=old.copy() if old else bpy.data.materials.new(f'CG3 / {family} / {era}')
        mat.name=f'CG3 / {family} / {era}';mat.use_nodes=True
        nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
        if not bs:raise RuntimeError('Missing preserved PBR shader '+family)
        if family=='optic':
            bs.inputs['Base Color'].default_value=(.04,.018,.004,1) if era=='builder' else (.008,.009,.01,1)
            bs.inputs['Metallic'].default_value=.25;bs.inputs['Roughness'].default_value=.16
            bs.inputs['Coat Weight'].default_value=.45;bs.inputs['Coat Roughness'].default_value=.10
            bs.inputs['Emission Strength'].default_value=.48 if era=='builder' else 0
        else:
            for n in nt.nodes:
                if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=normal_strength[family]
                if n.type=='TEX_IMAGE' and n.image:images[n.image.name]=n.image
        mat['cg3Family']=family;mat['cg3Era']=era;materials[family]=mat;counts[family]=0
    for o in scene.objects:
        if o.type!='MESH' or o.get('authoringGuide'):continue
        region=o.get('cg3Region') or o.get('cg1cRegion') or o.get('study_part')
        if not region:continue
        role=str(o.get('surfaceRole','plate')).lower();name=o.name.lower()
        if role in ('optic','lens'):f='optic'
        elif role in ('inner','recess','frame','liner','backing','machinery'):f='machinery'
        elif role in ('edge','rivet','rim','repair','trim') or 'rivet' in name:f='bronze'
        elif role in ('bill','talon','bearing','piston','shaft') or any(x in name for x in ('bill','talon','claw')):f='steel'
        elif o.get('cg1cMaterialFamily')=='machinery-steel':f='machinery'
        elif o.get('study_part') and not o.get('cg1cRegion'):f='machinery'
        else:f='patina'
        o.data.materials.clear();o.data.materials.append(materials[f]);counts[f]+=1;o['cg3SurfaceFamily']=f
    return {'era':era,'familyCounts':counts,'materials':[m.name for m in materials.values()],
            'imageNames':sorted(images),'normalStrength':normal_strength,'roughnessMetallic':'Retained original ORM G/B maps, no scalar replacement',
            'optic':{'emission':.48 if era=='builder' else 0,'coat':.45,'roughness':.16},
            'limits':['Source PBR maps reused unchanged; sparse exposed edges depend on geometry roles.','Geometry, pose, UV, cameras and lighting unchanged.','Owner likeness acceptance remains separate.']}
