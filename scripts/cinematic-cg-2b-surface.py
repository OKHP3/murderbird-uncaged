"""CG2b regional finish proposal derived from the deterministic CG2a tile method.
Original generated pixels only; pinned artwork controls judgments, never textures.
Direct image PBR graphs preserve mesh coordinates, UVs and face assignments.
"""
from pathlib import Path
import hashlib, json, math
import bpy
import numpy as np

SIZE = 1024
SEED = 202610037
ERAS = ('maker', 'mechanic', 'builder')
FAMILIES = ('head-armor', 'breast-armor', 'wing-armor', 'forged-steel', 'machined-steel', 'worn-bronze', 'black-iron')
# sRGB texture values: restrained green-gray plates, different steel operations,
# brown bronze edges and recesses. These are visual proposals, not metrology.
PALETTES = {
    'head-armor': ((.290,.302,.274), (.430,.422,.355), .53, .76),
    'breast-armor': ((.267,.287,.261), (.410,.405,.337), .57, .74),
    'wing-armor': ((.254,.278,.258), (.414,.405,.329), .57, .76),
    'forged-steel': ((.284,.296,.286), (.480,.483,.444), .43, .87),
    'machined-steel': ((.365,.380,.362), (.535,.550,.516), .34, .91),
    'worn-bronze': ((.290,.241,.167), (.437,.367,.250), .46, .84),
    'black-iron': ((.075,.085,.080), (.176,.187,.170), .63, .78),
}


def noise(rng, cells):
    # Smooth repeatable value noise, carried forward from the original CG2a
    # method. No previous image maps or artwork are loaded during generation.
    a = rng.random((cells,cells),dtype=np.float32)
    c = np.arange(SIZE,dtype=np.float32)*cells/SIZE
    i = c.astype(int); f = c-i; f = f*f*(3-2*f)
    return (a[i[:,None],i[None,:]]*(1-f[:,None])*(1-f[None,:])+
            a[(i+1)[:,None]%cells,i[None,:]]*f[:,None]*(1-f[None,:])+
            a[i[:,None],(i+1)[None,:]%cells]*(1-f[:,None])*f[None,:]+
            a[(i+1)[:,None]%cells,(i+1)[None,:]%cells]*f[:,None]*f[None,:])


def write(path, rgb, data=False):
    im = bpy.data.images.new(path.name,width=SIZE,height=SIZE,alpha=False)
    im.colorspace_settings.name = 'Non-Color' if data else 'sRGB'
    rgba = np.ones((SIZE,SIZE,4),dtype=np.float32); rgba[:,:,:3] = np.clip(rgb,0,1)
    im.pixels.foreach_set(rgba.ravel()); im.filepath_raw = str(path)
    im.file_format = 'PNG'; im.save(); im.pack()
    return im


def generate(directory, family):
    normal = directory/f'{family}-2b-normal.png'
    paths = {era:{'color':directory/f'{family}-{era}-2b-color.png',
                  'orm':directory/f'{family}-{era}-2b-orm.png'} for era in ERAS}
    if normal.exists() and all(p.exists() for pp in paths.values() for p in pp.values()):
        return paths,normal
    rng = np.random.default_rng(SEED+FAMILIES.index(family)*173)
    uneven = noise(rng,22); mill = noise(rng,90); etch = noise(rng,190)
    grain = rng.random((SIZE,SIZE),dtype=np.float32)
    pits = np.clip((grain-.986)*65,0,1)*np.clip((etch-.44)*4,0,1)
    scratches = np.zeros((SIZE,SIZE),dtype=np.float32)
    for _ in range(760):
        x,y = rng.integers(0,SIZE,2); length = int(rng.integers(5,77)); step = np.arange(length)
        xx = (x+step)%SIZE; yy = (y+step*rng.uniform(-.5,.5)).astype(int)%SIZE
        scratches[yy,xx] = rng.uniform(.12,.72)
    d = np.minimum(np.arange(SIZE),np.arange(SIZE)[::-1]).astype(np.float32)
    border = np.maximum(np.exp(-d[:,None]/7),np.exp(-d[None,:]/7))
    # Interrupted wear plus modest broad abrasion makes each retained leaf UV
    # readable. Physical sheet-edge meshes receive the bronze family separately.
    wear = np.clip(border*np.clip((mill-.29)*2.1,0,1)+scratches*.50,0,1)
    rubbed = np.clip((mill-.61)*3.4,0,.36)
    grime = np.clip((uneven-.53)*2.6,0,.65)*(1-rubbed)+border*.10
    oxidation = np.clip((uneven-.41)*2.1,0,1)*np.clip((etch-.38)*2.4,0,1)
    machining = .5+.5*np.sin(np.arange(SIZE,dtype=np.float32)[:,None]*1.15)
    height = (etch-.5)*.011+(grain-.5)*.003-pits*.030-scratches*.013
    if family == 'machined-steel': height += machining*.002
    gy,gx = np.gradient(height)
    normal_pixels = np.stack((-gx*3,-gy*3,np.ones_like(gx)),axis=-1)
    normal_pixels /= np.linalg.norm(normal_pixels,axis=-1,keepdims=True)
    write(normal,normal_pixels*.5+.5,True)
    base, edge, rough_base, metal_base = PALETTES[family]
    armor = family.endswith('armor')
    for era in ERAS:
        age = {'maker':.20,'mechanic':1,'builder':.88}[era]
        ox = oxidation*age*(.23 if armor else .10 if family=='worn-bronze' else .08)
        variation = 1+(etch-.5)*.20+(grain-.5)*.06+(uneven-.5)*.18
        rgb = np.array(base,dtype=np.float32)[None,None,:]*variation[:,:,None]
        # Maker is cleaner, while the inherited Advanced finish stays close
        # to Mechanic; no general glow or global color filter is introduced.
        if era == 'maker': rgb *= np.array((1.02,1.015,1.01),dtype=np.float32)
        oxide_tone = np.array((.170,.240,.211) if armor else (.174,.147,.109),dtype=np.float32)
        rgb = rgb*(1-ox[:,:,None])+oxide_tone*ox[:,:,None]
        rgb *= (1-grime*age*.23-pits*age*.18)[:,:,None]
        edge_strength = .40 if armor else .55
        w = wear*edge_strength*(.60+.40*age)+rubbed*.28
        rgb = rgb*(1-w[:,:,None])+np.array(edge,dtype=np.float32)*w[:,:,None]
        rough = np.clip(rough_base+(etch-.5)*.14+grime*age*.11+ox*.20+pits*age*.12-wear*.12-rubbed*.06,.27,.79)
        metal = np.clip(metal_base-ox*.30-grime*age*.09-pits*age*.08,.50,.94)
        if family == 'machined-steel':
            rgb *= (1+(machining-.5)*.05)[:,:,None]
            rough = np.clip(rough+(machining-.5)*.055,.25,.58)
        orm = np.stack((np.clip(1-grime*.24-pits*.13,.72,1),rough,metal),axis=-1)
        write(paths[era]['color'],rgb); write(paths[era]['orm'],orm,True)
    return paths,normal


def region(o):
    r = str(o.get('cg1cRegion') or o.get('cg2bRegion') or o.get('cg2aRegion') or o.get('cg3Region') or o.get('study_part') or '').lower()
    if any(v in r for v in ('leg','foot','talon')): return 'leg-foot'
    return r


def classify(o, slot_material=None):
    role = str(o.get('surfaceRole','plate')).lower(); name = o.name.lower(); r = region(o)
    # Preserve both object-level and slot-level authored optical shaders.
    if o.get('cg2aPreserveMaterial') or (slot_material and slot_material.get('cg2aPreserveMaterial')) or role in ('glass','lens-glass'):
        return None
    if role in ('optic','lens'): return None
    # The new breast leaves deliberately have dark sidewall slots. Never turn
    # every slot into the material assigned to the top face.
    prior_family = str(slot_material.get('cg2aFamily','')) if slot_material else ''
    if prior_family == 'machinery' and len(o.data.materials)>1: return 'black-iron'
    if role in ('inner','recess','frame','liner','backing','machinery','cavity','hose','cable'):
        return 'black-iron'
    if role in ('rivet','repair','trim','bronze','copper'): return 'worn-bronze'
    if role in ('bearing','piston','shaft','gear','rod','steel','machine','hinge','axle','bolt'):
        return 'machined-steel'
    if role in ('bill','talon','claw') or any(x in name for x in ('bill sheet','mandible','talon','claw')):
        return 'forged-steel'
    if role in ('edge','rim'):
        return 'worn-bronze' if r in ('head','neck','body','wing') else 'machined-steel'
    if r in ('head','neck'): return 'head-armor'
    if r == 'wing' or r == 'shoulder-wing': return 'wing-armor'
    if r == 'leg-foot': return 'forged-steel'
    return 'breast-armor'


def material(family, era, images, repair=False):
    m = bpy.data.materials.new(f'CG2b / {family} / {era}'+(' / repair' if repair else ''))
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    bs = nt.nodes.new('ShaderNodeBsdfPrincipled'); out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    nodes = {}
    for role,im in images[family].items():
        node = nt.nodes.new('ShaderNodeTexImage'); node.image = im; node.label = role
        node.interpolation = 'Linear'; nodes[role] = node
    nt.links.new(nodes['color'].outputs['Color'],bs.inputs['Base Color'])
    sep = nt.nodes.new('ShaderNodeSeparateColor'); sep.mode = 'RGB'
    nt.links.new(nodes['orm'].outputs['Color'],sep.inputs['Color'])
    nt.links.new(sep.outputs['Green'],bs.inputs['Roughness']); nt.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = .30 if family.endswith('armor') else .18
    nt.links.new(nodes['normal'].outputs['Color'],nm.inputs['Color']); nt.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    m['cg2bFamily'] = family; m['cg2bEra'] = era; m['seed'] = SEED
    m['surfaceStatus'] = 'Original regional CG proposal; owner artistic review pending'
    return m


def _digest_mesh(o):
    h = hashlib.sha256()
    for v in o.data.vertices: h.update(np.array(v.co[:],dtype='<f4').tobytes())
    for p in o.data.polygons:
        h.update(np.array(p.vertices[:],dtype='<i4').tobytes()); h.update(int(p.material_index).to_bytes(4,'little'))
    for layer in o.data.uv_layers:
        h.update(layer.name.encode())
        for d in layer.data:h.update(np.array(d.uv[:],dtype='<f4').tobytes())
    h.update(np.array([v for row in o.matrix_world for v in row],dtype='<f8').tobytes())
    return h.hexdigest()


def apply(scene, output_dir, era='builder', reference_root=None):
    if era not in ERAS: raise ValueError(era)
    directory = Path(output_dir)/'textures'; directory.mkdir(parents=True,exist_ok=True)
    images = {}; generated_paths = []
    for family in FAMILIES:
        pp,normal = generate(directory,family); images[family] = {}
        paths = pp[era]|{'normal':normal}
        generated_paths.extend([p for ep in pp.values() for p in ep.values()]); generated_paths.append(normal)
        for role,p in paths.items():
            im = bpy.data.images.load(str(p),check_existing=True)
            im.colorspace_settings.name = 'sRGB' if role=='color' else 'Non-Color'
            if not im.packed_file: im.pack()
            images[family][role] = im
    mats = {f:material(f,era,images) for f in FAMILIES}
    counts = {f:0 for f in FAMILIES}; preserved=[]; missing_uv=[]; slots=0; repaired=[]
    targets = [o for o in scene.objects if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide') and
               (o.get('cg2bRegion') or o.get('cg2aRegion') or o.get('cg3Region') or o.get('cg1cRegion') or o.get('study_part'))]
    before = {o.name:_digest_mesh(o) for o in targets}
    for o in targets:
        assignments=[]
        for i,old in enumerate(o.data.materials):
            f = classify(o,old)
            if f is None: preserved.append({'object':o.name,'slot':i,'material':old.name if old else None});continue
            # Named repair objects use the separate aged bronze/steel family;
            # the continuity is inherited, rather than inventing repair geometry.
            if 'repair' in o.name.lower() and era in ('mechanic','builder'):
                f = 'machined-steel'; repaired.append(o.name)
            o.data.materials[i] = mats[f]; assignments.append(f); slots += 1
        if not o.data.materials:
            f = classify(o)
            if f is not None:o.data.materials.append(mats[f]);assignments.append(f);slots+=1
        for f in set(assignments):counts[f]+=1
        if assignments:
            o['cg2bSurfaceFamily'] = ','.join(sorted(set(assignments)))
            if not o.data.uv_layers:missing_uv.append(o.name)
    after = {o.name:_digest_mesh(o) for o in targets}
    assert before == after, 'Surface operation changed geometry, pose, UV or polygon assignments'
    references = {}
    if reference_root:
        root = Path(reference_root)
        for name in ('murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg','murderbird-unified-maker-clean-candidate-2026-09-06.png','murderbird-unified-mechanic-candidate-2026-09-06.png','murderbird-unified-heart-candidate-2026-09-06.png'):
            p = root/'assets/img/library'/name
            if p.exists():references[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    record = {'module':'cg2b-surface','era':era,'seed':SEED,'size':[SIZE,SIZE],
              'authorship':'Original deterministic CG2b maps derived from CG2a algorithm; no artwork pixels or prior map pixels reused',
              'algorithmSource':'scripts/cinematic-cg-2a-surface.py','mapIngredients':[],
              'textureHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(generated_paths))},
              'referenceHashes':references,'familyCounts':counts,'assignedSlots':slots,'glassPreserved':preserved,
              'missingUVs':missing_uv,'repairObjects':sorted(set(repaired)),'materials':[m.name for m in mats.values()],
              'preservation':{'geometryPoseUVAndPolygonMaterialIndices':'PASS','checkedVisibleMeshes':len(targets),'slotCountsPreserved':True},
              'eraRules':{'maker':'Clean fabrication, dark optical shaders preserved','mechanic':'Aged metal and named selective repair accents; dark optics preserved','builder':'Inherited aged metal; only existing authored awakened optics preserved'},
              'limits':['Regional color and optical finish are CG proposals awaiting owner review.','Wear follows retained UVs; sheet perimeter meshes carry selected bronze edges.','No pose, geometry, engineering, runtime or publication change.']}
    (directory/'surface-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
    return record
