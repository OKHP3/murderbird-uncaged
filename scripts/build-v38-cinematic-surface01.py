"""Cinematic surface pass from retained hanging-breast02 source.

Run with Blender 5.2: blender -b --python scripts/build-v38-cinematic-surface01.py
This is a versioned material/UV derivative. It does not alter app source.
"""
from pathlib import Path
import bpy, hashlib, json, math, random, struct
from array import array
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/whole-character-v38/hanging-breast01/attempt02/murderbird-v38-hanging-breast01-attempt02.blend'
BASE_GLB=BASE.with_name(BASE.stem+'-rigid.glb')
OUT=ROOT/'assets/models/whole-character-v38/cinematic-surface01/attempt02'
AUD=ROOT/'assets/audit/whole-character-v38/cinematic-surface01/attempt02'
NATIVE=OUT/'murderbird-v38-cinematic-surface01-attempt02.blend'
GLB=OUT/'murderbird-v38-cinematic-surface01-attempt02-rigid.glb'
ERAS=('maker','mechanic','builder')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
    if not ok: raise RuntimeError(msg)
need(not NATIVE.exists() and not GLB.exists() and not (AUD/'receipt.json').exists(),'Write-once output exists; preserve it and scope a new version.')
need(sha(BASE)=='d32f187f98e34827f31828035d81324ee3af9f28a2aeb21e9d869e16d8d5192d','Native input SHA mismatch')
need(sha(BASE_GLB)=='051477ffcf62a4e08a3f1968d6cec7fd7f8b0677661cd72dde6ad7bbd5514650','GLB input SHA mismatch')
OUT.mkdir(parents=True,exist_ok=True); AUD.mkdir(parents=True,exist_ok=True); (AUD/'textures').mkdir(exist_ok=True)

def read_glb(path):
    raw=Path(path).read_bytes(); need(raw[:4]==b'glTF' and struct.unpack_from('<I',raw,4)[0]==2,'Invalid GLB')
    offset=12; chunks=[]
    while offset<len(raw):
        n,k=struct.unpack_from('<II',raw,offset);offset+=8;chunks.append((k,raw[offset:offset+n]));offset+=n
    return raw,chunks,json.loads(chunks[0][1])
_,_,source_doc=read_glb(BASE_GLB)
source_names={n['name'] for n in source_doc['nodes'] if 'name' in n}
source_parent={source_doc['nodes'][c]['name']:n['name'] for n in source_doc['nodes'] for c in n.get('children',[]) if 'name' in source_doc['nodes'][c]}

def mesh_hash(o):
    d=o.data
    return hashlib.sha256(json.dumps({'v':[list(v.co) for v in d.vertices], 'f':[list(p.vertices) for p in d.polygons]},separators=(',',':')).encode()).hexdigest()
def state():
    bpy.context.view_layer.update()
    return {o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[[round(v,8) for v in row] for row in o.matrix_world],
      'hide':[o.hide_render,o.hide_viewport,o.hide_get()],'eras':o.get('exteriorEras'),'mesh':mesh_hash(o) if o.type=='MESH' else None} for o in bpy.data.objects}

# Tiled neutral relief carries fine scuffs, forged grain, and shallow pits into
# every era. Era scalar profiles tint the same physical microstructure.
def make_maps():
    import numpy as np
    n=512; rng=np.random.default_rng(80317)
    coarse=rng.random((32,32),dtype=np.float32); fine=rng.random((n,n),dtype=np.float32)
    coords=np.linspace(0,31,n,dtype=np.float32); x0=np.floor(coords).astype(int);x1=np.minimum(x0+1,31);t=coords-x0
    broad=(coarse[x0[:,None],x0[None,:]]*(1-t[:,None])*(1-t[None,:])+
           coarse[x1[:,None],x0[None,:]]*t[:,None]*(1-t[None,:])+
           coarse[x0[:,None],x1[None,:]]*(1-t[:,None])*t[None,:]+
           coarse[x1[:,None],x1[None,:]]*t[:,None]*t[None,:])
    h=.49+.075*(broad-.5)+.018*(fine-.5)
    # Repeated fine directional scoring and small irregular rubbed flecks.
    for _ in range(130):
        x=int(rng.integers(0,n));y=int(rng.integers(0,n));length=int(rng.integers(5,39));slope=float(rng.normal(0,.035))
        for j in range(length): h[y% n,x% n]=min(h[y%n,x%n],float(rng.uniform(.34,.43))); x+=1; y+=int(round(slope))
    # Slight raised wear at plate edges from UV borders, plus non-directional pitting.
    edge=np.minimum(np.minimum(np.arange(n),np.arange(n)[::-1])[:,None],np.minimum(np.arange(n),np.arange(n)[::-1])[None,:]).astype(np.float32)
    h=np.clip(h,0,1)
    gy,gx=np.gradient(h)
    normal=np.stack([np.clip(.5-gx*4,0,1),np.clip(.5-gy*4,0,1),np.ones_like(h)],axis=-1)
    normal=np.clip(normal,0,1)
    base=np.clip(.86+(broad-.5)*.16+(fine-.5)*.08, .76,1.0)
    rough=np.clip(.92+(broad-.5)*.08+(fine-.5)*.06, .82,1.0)
    maps=[]
    for name,arr in [('surface-neutral-base.png',np.stack([base,base,base],-1)),('surface-neutral-roughness.png',np.stack([rough,rough,rough],-1)),('surface-forged-normal.png',normal)]:
        if arr.ndim==2: arr=np.stack([arr,arr,arr],-1)
        rgba=np.concatenate([arr,np.ones((n,n,1),dtype=np.float32)],axis=-1)
        im=bpy.data.images.new(name,width=n,height=n,alpha=False,float_buffer=False)
        im.pixels.foreach_set(array('f',rgba.astype('float32',copy=False).reshape(-1).tolist()));im.filepath_raw=str(AUD/'textures'/name);im.file_format='PNG';im.save();im.pack();maps.append(im)
    return maps

def lin(rgb): return tuple(float(x) for x in rgb)
def palette(region,surf,era):
    s=surf.lower(); r=region.lower()
    if s=='optic':
        return {'baseColorFactor':[.022,.015,.012,1],'metallicFactor':.18,'roughnessFactor':.24,'emissiveFactor':[.16,.045,.009] if era=='builder' else [0,0,0]}
    if s in ('inner','recess','liner'):
        return {'baseColorFactor':[.018,.023,.024,1],'metallicFactor':.28,'roughnessFactor':.72}
    if s=='repair':
        return {'baseColorFactor':([.18,.095,.038,1] if era=='maker' else [.105,.064,.036,1]),'metallicFactor':.76,'roughnessFactor':.53 if era=='mechanic' else .44}
    if 'edge' in s or s in ('brow-roof','receiving-plate','cheek-bridge'):
        c={'maker':[.22,.129,.052,1],'mechanic':[.105,.088,.060,1],'builder':[.135,.114,.079,1]}[era]
        return {'baseColorFactor':c,'metallicFactor':.78,'roughnessFactor':{'maker':.36,'mechanic':.48,'builder':.42}[era]}
    if 'bearing' in s or s in ('frame','bearing-frame'):
        c={'maker':[.073,.060,.044,1],'mechanic':[.045,.047,.041,1],'builder':[.052,.058,.059,1]}[era]
        return {'baseColorFactor':c,'metallicFactor':.84,'roughnessFactor':{'maker':.61,'mechanic':.70,'builder':.64}[era]}
    if era=='maker':
        # Newly made deep bronze with warm reflected edges, not bright gold.
        c={'head':[.135,.098,.063,1],'breast':[.145,.096,.058,1],'neck':[.118,.082,.050,1],
           'shoulder':[.132,.093,.053,1],'wing':[.124,.087,.051,1],'leg-structure':[.093,.072,.050,1],
           'foot':[.104,.080,.054,1]}.get(r,[.116,.082,.052,1])
        return {'baseColorFactor':c,'metallicFactor':.76,'roughnessFactor':{'breast':.62,'neck':.64}.get(r,.58)}
    if era=='mechanic':
        c={'head':[.060,.071,.065,1],'breast':[.062,.076,.067,1],'neck':[.055,.067,.061,1],
           'shoulder':[.059,.071,.065,1],'wing':[.057,.072,.066,1],'leg-structure':[.048,.056,.054,1],
           'foot':[.053,.061,.057,1]}.get(r,[.057,.069,.063,1])
        return {'baseColorFactor':c,'metallicFactor':.82,'roughnessFactor':{'breast':.69,'neck':.67}.get(r,.64)}
    c={'head':[.062,.075,.078,1],'breast':[.064,.075,.072,1],'neck':[.058,.070,.073,1],
       'shoulder':[.058,.072,.075,1],'wing':[.057,.073,.076,1],'leg-structure':[.050,.060,.064,1],
       'foot':[.055,.064,.068,1]}.get(r,[.060,.073,.075,1])
    return {'baseColorFactor':c,'metallicFactor':.83,'roughnessFactor':{'breast':.64,'neck':.65}.get(r,.61)}

def add_surface_maps(material,maps,protect_lens=False):
    material.use_nodes=True; nt=material.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    if protect_lens:
        nt.links.new(bs.outputs['BSDF'],out.inputs['Surface']);material['surfaceMapSet']='clear optic protected from forged maps';return bs
    tex=nt.nodes.new('ShaderNodeTexCoord')
    base=nt.nodes.new('ShaderNodeTexImage');base.image=maps[0]; base.image.colorspace_settings.name='sRGB'
    tint=nt.nodes.new('ShaderNodeMixRGB');tint.name='Era base-color factor';tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1.0;tint.label='Era base-color factor'
    rou=nt.nodes.new('ShaderNodeTexImage');rou.image=maps[1];rou.image.colorspace_settings.name='Non-Color'
    rough_scale=nt.nodes.new('ShaderNodeMath');rough_scale.name='Era roughness factor';rough_scale.operation='MULTIPLY';rough_scale.inputs[1].default_value=.5;rough_scale.label='Era roughness factor'
    nor=nt.nodes.new('ShaderNodeTexImage');nor.image=maps[2];nor.image.colorspace_settings.name='Non-Color'
    nm=nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value=.24
    nt.links.new(tex.outputs['UV'],base.inputs['Vector']);nt.links.new(tex.outputs['UV'],rou.inputs['Vector']);nt.links.new(tex.outputs['UV'],nor.inputs['Vector'])
    nt.links.new(base.outputs['Color'],tint.inputs[1]);nt.links.new(tint.outputs['Color'],bs.inputs['Base Color']);nt.links.new(rou.outputs['Color'],rough_scale.inputs[0]);nt.links.new(rough_scale.outputs['Value'],bs.inputs['Roughness']);nt.links.new(nor.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],bs.inputs['Normal']);nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    material['surfaceMapSet']='cinematic-surface01 shared neutral base, roughness and forged normal maps'
    return bs

def ensure_uv(obj):
    if obj.type!='MESH' or obj.name not in source_names or not obj.data.polygons:return
    if len(obj.data.uv_layers): return
    hidden=obj.hide_get();hidden_view=obj.hide_viewport
    obj.hide_set(False);obj.hide_viewport=False
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=.012,angle_limit=math.radians(68),area_weight=0.0)
    bpy.ops.object.mode_set(mode='OBJECT');obj.hide_viewport=hidden_view;obj.hide_set(hidden)

def apply_finish(maps):
    assignments={}; profile_data={}; created={}
    for obj in bpy.data.objects:
        if obj.type!='MESH' or obj.name not in source_names or obj.get('authoringGuide') is True: continue
        eras=tuple(sorted(x.strip().lower() for x in str(obj.get('exteriorEras','maker,mechanic,builder')).split(',') if x.strip().lower() in ERAS))
        if not eras: continue
        region=str(obj.get('region') or 'body'); surf=str(obj.get('surfaceRole') or 'plate')
        ensure_uv(obj)
        for i,slot in enumerate(obj.material_slots):
            old=slot.material
            key=(region,surf,eras)
            if key not in created:
                name='Cinematic01 / '+region+' / '+surf+' / '+'-'.join(eras)
                mat=bpy.data.materials.new(name); profiles={era:palette(region,surf,era) for era in eras}
                mat['eraFinishes']=json.dumps(profiles,separators=(',',':'),sort_keys=True);mat['finishStudy']='cinematic-surface01';mat['materialRole']=region+'/'+surf
                bs=add_surface_maps(mat,maps,protect_lens=(surf=='optic')); chosen=profiles.get('builder') or profiles.get('mechanic') or profiles.get('maker')
                c=chosen['baseColorFactor'];mat.diffuse_color=tuple(c);mat.metallic=chosen['metallicFactor'];mat.roughness=chosen['roughnessFactor']
                tint=mat.node_tree.nodes.get('Era base-color factor');rs=mat.node_tree.nodes.get('Era roughness factor');nm=mat.node_tree.nodes.get('Normal Map')
                if tint:tint.inputs[2].default_value=tuple(c)
                else:bs.inputs['Base Color'].default_value=tuple(c)
                if rs:rs.inputs[1].default_value=chosen['roughnessFactor']
                if nm:nm.inputs['Strength'].default_value=.10 if 'maker' in eras else (.34 if 'mechanic' in eras else .22)
                bs.inputs['Metallic'].default_value=chosen['metallicFactor'];bs.inputs['Emission Color'].default_value=(*chosen.get('emissiveFactor',[0,0,0]),1);bs.inputs['Emission Strength'].default_value=1.0 if chosen.get('emissiveFactor') else 0
                created[key]=mat;profile_data[name]=profiles
            slot.material=created[key];assignments.setdefault(region+'/'+surf,0);assignments[region+'/'+surf]+=1
    return assignments,profile_data

def apply_era(era,profile_data):
    for name,profiles in profile_data.items():
        p=profiles.get(era)
        if not p: continue
        m=bpy.data.materials[name]; c=p['baseColorFactor'];m.diffuse_color=tuple(c);m.metallic=p['metallicFactor'];m.roughness=p['roughnessFactor']
        tint=m.node_tree.nodes.get('Era base-color factor');rs=m.node_tree.nodes.get('Era roughness factor');nm=m.node_tree.nodes.get('Normal Map');bs=m.node_tree.nodes.get('Principled BSDF')
        if tint:tint.inputs[2].default_value=tuple(c)
        else:bs.inputs['Base Color'].default_value=tuple(c)
        if rs:rs.inputs[1].default_value=p['roughnessFactor']
        if nm:nm.inputs['Strength'].default_value=.10 if era=='maker' else (.34 if era=='mechanic' else .22)
        bs.inputs['Metallic'].default_value=p['metallicFactor']
        e=p.get('emissiveFactor',[0,0,0]);bs.inputs['Emission Color'].default_value=(*e,1);bs.inputs['Emission Strength'].default_value=1.0 if any(e) else 0

def render(label,profile_data):
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.render.image_settings.color_mode='RGBA'
    world=scene.world or bpy.data.worlds.new('cinematic review world');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.035,.043,.052,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
    original_hide={o.name:o.hide_render for o in bpy.data.objects};camera_data=bpy.data.cameras.new('temporary cinematic review camera');camera_data.type='ORTHO';camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera);scene.camera=camera
    lights=[]
    def area(name,loc,energy,color,size):
        d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.04))-o.location).to_track_quat('-Z','Y').to_euler();lights.append(o)
    captures=[]
    for lighting in ('neutral','exhibit'):
        for o in list(lights):
            d=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.lights.remove(d)
        lights=[]
        if lighting=='neutral':
            area('neutral soft key',(-4,-5,6),950,(1,.96,.90),4.5);area('neutral sky fill',(4,-3,3),660,(.76,.86,1),4.0);area('neutral edge',(1,4,4),1100,(1,.86,.68),3.0)
        else:
            area('exhibit amber key',(-4,-5,5),1450,(1,.72,.43),2.8);area('exhibit blue rim',(1,4,4),1800,(.36,.62,1),2.4);area('exhibit broad fill',(4,-2,2),480,(.78,.88,1),3.8)
        for era in ERAS:
            for o in bpy.data.objects:
                if o.type=='MESH':
                    allowed={x.strip().lower() for x in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')}
                    o.hide_render=original_hide.get(o.name,False) or o.get('authoringGuide') is True or era not in allowed
            apply_era(era,profile_data)
            camera.location=(-6,-3.5,2.75);camera.rotation_euler=(Vector((0,-.08,1.03))-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=2.45
            p=AUD/f'{label}-{era}-{lighting}-fullbird.png';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
            captures.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'era':era,'lighting':lighting,'view':'matched whole-bird three-quarter','size':[900,900]});print('IMAGE',p,flush=True)
    for o in list(lights):
        d=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.lights.remove(d)
    bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(camera_data);scene.camera=None
    return captures

def export_profile_patch(path,profile_data):
    raw,chunks,doc=read_glb(path)
    for m in doc.get('materials',[]):
        name=m.get('name')
        if name in profile_data:
            active=profile_data[name].get('builder') or profile_data[name].get('mechanic') or profile_data[name].get('maker')
            pbr=m.setdefault('pbrMetallicRoughness',{})
            pbr['baseColorFactor']=active['baseColorFactor'];pbr['metallicFactor']=active['metallicFactor'];pbr['roughnessFactor']=active['roughnessFactor']
            extras=m.setdefault('extras',{});extras['finishStudy']='cinematic-surface01';extras['materialRole']=name.split(' / ',1)[1].rsplit(' / ',1)[0]
            extras['eraFinishes']=profile_data[name]
    payload=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();payload+=b' '*((-len(payload))%4)
    out=bytearray(struct.pack('<4sII',b'glTF',2,0))
    for kind,data in chunks:
        val=payload if kind==0x4e4f534a else data;out+=struct.pack('<II',len(val),kind)+val
    struct.pack_into('<I',out,8,len(out));path.write_bytes(out)
    _,_,patched=read_glb(path)
    return patched

bpy.ops.wm.open_mainfile(filepath=str(BASE));before=state();map_images=make_maps();maps=[Path(im.filepath_raw) for im in map_images]
profiles={}; assignments={}
# Capture current source appearance before assigning the new maps/palette.
# Existing source material era data is faithfully interpreted for the baseline.
def source_render():
    original_hide={o.name:o.hide_render for o in bpy.data.objects}; scene=bpy.context.scene
    # Reuse the candidate camera/light renderer after defining source profiles.
    old_profiles={}
    for m in bpy.data.materials:
        raw=m.get('eraFinishes')
        if not raw: continue
        try: old_profiles[m.name]=json.loads(raw) if isinstance(raw,str) else raw
        except Exception: pass
    camera_data=bpy.data.cameras.new('temporary source cinematic camera');camera_data.type='ORTHO';camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera);scene.camera=camera
    scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=scene.render.resolution_y=900;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    world=scene.world or bpy.data.worlds.new('source review world');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.035,.043,.052,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
    lights=[]
    def area(name,loc,energy,color,size):
        d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.04))-o.location).to_track_quat('-Z','Y').to_euler();lights.append(o)
    captures=[]
    for lighting in ('neutral','exhibit'):
        for o in list(lights): d=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.lights.remove(d)
        lights=[]
        if lighting=='neutral': area('source neutral key',(-4,-5,6),950,(1,.96,.90),4.5);area('source neutral fill',(4,-3,3),660,(.76,.86,1),4);area('source neutral edge',(1,4,4),1100,(1,.86,.68),3)
        else: area('source exhibit key',(-4,-5,5),1450,(1,.72,.43),2.8);area('source exhibit rim',(1,4,4),1800,(.36,.62,1),2.4);area('source exhibit fill',(4,-2,2),480,(.78,.88,1),3.8)
        for era in ERAS:
            for o in bpy.data.objects:
                if o.type=='MESH':o.hide_render=original_hide.get(o.name,False) or o.get('authoringGuide') is True or era not in {x.strip().lower() for x in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')}
            for n,ps in old_profiles.items():
                p=ps.get(era)
                if not p: continue
                m=bpy.data.materials[n]; c=p.get('baseColorFactor',[.4,.4,.4,1]);m.diffuse_color=tuple(c);m.metallic=p.get('metallicFactor',0);m.roughness=p.get('roughnessFactor',.5)
                bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
                if bs:
                    bs.inputs['Base Color'].default_value=tuple(c);bs.inputs['Metallic'].default_value=m.metallic;bs.inputs['Roughness'].default_value=m.roughness
            camera.location=(-6,-3.5,2.75);camera.rotation_euler=(Vector((0,-.08,1.03))-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=2.45
            p=AUD/f'source-{era}-{lighting}-fullbird.png';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
            captures.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'era':era,'lighting':lighting,'view':'matched whole-bird three-quarter','size':[900,900]});print('IMAGE',p,flush=True)
    for o in list(lights):d=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.lights.remove(d)
    bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(camera_data);scene.camera=None
    return captures

source_captures=source_render()
# The matched baseline pass temporarily swaps material scalars and render flags;
# reload the frozen source before authoring so those are restored byte-for-byte.
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=state();map_images=[bpy.data.images.load(str(p),check_existing=False) for p in maps]
for im in map_images: im.pack()
assignments,profiles=apply_finish(map_images)
after=state()
need(set(before)==set(after),'Object names changed')
need(all(before[n]['type']==after[n]['type'] and before[n]['parent']==after[n]['parent'] and before[n]['matrix']==after[n]['matrix'] and before[n]['hide']==after[n]['hide'] and before[n]['eras']==after[n]['eras'] for n in before),'Part identity, transforms, visibility, or era tags changed')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False)
candidate_captures=render('candidate',profiles)
# Reopen native before GLB export, then select exactly the source browser nodes.
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));
for o in bpy.data.objects:
    o.select_set(False)
selected=[]
for n in source_names:
    o=bpy.data.objects.get(n)
    if o and o.type in ('MESH','EMPTY'):
        o.hide_set(False);o.hide_viewport=False;o.select_set(True);selected.append(o)
need(len(selected)==len([n for n in source_names if bpy.data.objects.get(n) and bpy.data.objects[n].type in ('MESH','EMPTY')]),'Source node selection incomplete')
bpy.context.view_layer.objects.active=next((o for o in selected if o.type=='MESH'),selected[0])
bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT',export_image_format='AUTO')
doc=export_profile_patch(GLB,profiles)
names={n.get('name') for n in doc.get('nodes',[])};need(names==source_names,'Export node name set changed')
need({doc['nodes'][c]['name']:n['name'] for n in doc['nodes'] for c in n.get('children',[]) if 'name' in doc['nodes'][c]}==source_parent,'Export parent map changed')
uv_objects=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name in source_names and any(x.strip().lower() in ERAS for x in str(o.get('exteriorEras','maker,mechanic,builder')).split(','))]
uv_count=sum(1 for n in uv_objects if bpy.data.objects[n].data.uv_layers)
receipt={'status':'Cinematic surface and regional PBR proposal; artistic acceptance pending','source':{'native':str(BASE.relative_to(ROOT)),'nativeSha256':sha(BASE),'glb':str(BASE_GLB.relative_to(ROOT)),'glbSha256':sha(BASE_GLB)},
 'outputs':{'native':str(NATIVE.relative_to(ROOT)),'nativeSha256':sha(NATIVE),'glb':str(GLB.relative_to(ROOT)),'glbSha256':sha(GLB)},
 'references':{'maker':'assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png','mechanic':'assets/img/library/murderbird-unified-mechanic-candidate-2026-09-06.png','advanced':'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png','julyHead':'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png','firstChoiceVideo':'assets/video/murderbird-first-choice-635f0e15.mp4','firstChoiceVideoSha256':'2dc0bd9ad5d079ead1f100c334ba620965dd19d5ebed9cf2cca6dd96f25e93cc','firstChoiceVideoMaterialization':'Owner-reviewed selected-video frames copied from root integration audit; local repository video path remains an LFS pointer.','firstChoiceFrames':[{'path':'assets/audit/whole-character-v38/cinematic-surface01/attempt02/first-choice-0s.png','sha256':sha(AUD/'first-choice-0s.png')},{'path':'assets/audit/whole-character-v38/cinematic-surface01/attempt02/first-choice-4s.png','sha256':sha(AUD/'first-choice-4s.png')}]},
 'surface':{'changedRegionSurfaceAssignments':assignments,'materialProfileCount':len(profiles),'sharedMapFiles':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in maps], 'uvMappedEligibleMeshCount':uv_count,'uvMapCount':sum(len(bpy.data.objects[n].data.uv_layers) for n in uv_objects),'eligibleMeshCount':len(uv_objects),'texturesPackedInNative':True,'texturesEmbeddedInGlb':bool(doc.get('images')),'glbImageCount':len(doc.get('images',[])),'glbTextureCount':len(doc.get('textures',[])),'estimatedTextureMemoryWithMipmapsBytes':len(doc.get('images',[]))*512*512*4*4//3,'outputTransferBytes':NATIVE.stat().st_size+GLB.stat().st_size,'outputTransferMiB':round((NATIVE.stat().st_size+GLB.stat().st_size)/1048576,2),'sourceGlbAnimationCount':len(source_doc.get('animations',[])),'candidateGlbAnimationCount':len(doc.get('animations',[]))},
 'preservation':{'nativeObjectNamesExact':set(before)==set(after),'parentsTransformsVisibilityAndEraTagsExact':True,'glbNodeNamesExact':names==source_names,'glbParentRelationshipsExact':True,'bodyAndHeadGeometryExact':all(before[n]['mesh']==after[n]['mesh'] for n in before if before[n]['type']=='MESH')},
 'captures':source_captures+candidate_captures,'limits':['Surface response and lighting are proposals; no owner likeness acceptance.','This is a browser GLB export artifact, not runtime app integration or deployment.','No mechanical fit, manufacturing or engineering validation is asserted.']}
(AUD/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('READY',json.dumps({'native':str(NATIVE),'glb':str(GLB),'renders':len(receipt['captures']),'uv':uv_count,'maps':len(maps),'nodeCount':len(source_names)}),flush=True)
