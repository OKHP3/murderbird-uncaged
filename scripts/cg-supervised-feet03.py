"""Heavy source-aligned foot exterior proposal; retained stance and source payload.

apply(scene, root_path=None, era='builder') adds editable UV geometry only below
ankle. CG construction inferred from pinned composite, not validated engineering.
Run with Blender --python this-file -- --preview to freeze matched audit images.
"""
import hashlib
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

TAG='cgSupervisedFeet03'

def _digest(o):
    h=hashlib.sha256()
    h.update(str([tuple(r) for r in o.matrix_world]).encode())
    h.update(str(o.parent.name if o.parent else None).encode())
    if o.type=='MESH':
        h.update(str([tuple(v.co) for v in o.data.vertices]).encode())
        h.update(str([(tuple(p.vertices),p.material_index) for p in o.data.polygons]).encode())
        h.update(str([m.name if m else None for m in o.data.materials]).encode())
        for uv in o.data.uv_layers:
            h.update(str((uv.name,[tuple(v.uv) for v in uv.data])).encode())
    return h.hexdigest()

def apply(scene, root_path=None, era='builder'):
    if any(o.get(TAG) for o in scene.objects):
        raise RuntimeError('Reload frozen receiving native before applying feet03')
    bpy.context.view_layer.update()
    originals=list(scene.objects)
    payload={o.name:_digest(o) for o in originals if o.type in ('MESH','EMPTY')}
    mats={}
    for o in originals:
        if o.type=='MESH' and o.get('cg1cRegion')=='foot' and o.data.materials:
            mats.setdefault(o.get('surfaceRole'),o.data.materials[0])
    ankle_ceiling=min(max((scene.objects['CG1c '+side+' ankle concentric hinge'].matrix_world@Vector(c)).z
        for c in scene.objects['CG1c '+side+' ankle concentric hinge'].bound_box) for side in ('left','right'))
    made=[];hidden=[];toe_receipt=[]
    anchor_receipt={o.name:{'matrix':[list(r) for r in o.matrix_world],
        'center':list(sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices))}
        for o in originals if o.type=='MESH' and o.name.startswith('CG1c ')
        and ('concentric hinge' in o.name or 'plantar foot housing' in o.name)}
    coll=bpy.data.collections.new('CG supervised heavy feet03 exterior')
    scene.collection.children.link(coll)
    def mesh(name,v,f,uv,role='plate'):
        # Strictly keep the new exterior below original ankle joint bounds.
        v=[(q[0],q[1],min(q[2],ankle_ceiling-.000001)) for q in v]
        d=bpy.data.meshes.new('CGF03 '+name);d.from_pydata(v,[],f);d.update()
        o=bpy.data.objects.new('CGF03 '+name,d);coll.objects.link(o)
        o[TAG]=True;o['cg1cRegion']='foot';o['cg2bRegion']='foot';o['surfaceRole']=role
        o['exteriorEras']='maker,mechanic,builder';o['era']=era
        o['cgConstructionStatus']='source-inferred exterior proposal; owner review pending'
        material=mats.get(role) or mats.get('armor' if role=='plate' else role) or mats.get('bearing')
        if material:d.materials.append(material)
        layer=d.uv_layers.new(name='cg-feet03-uv')
        for p in d.polygons:
            p.use_smooth=True
            for li in p.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
        made.append(o);return o
    def sweep(name,fn,start,end,role='plate',nr=24,ns=14,caps=True):
        v=[];uv=[];f=[]
        for j in range(ns):
            t=start+(end-start)*j/(ns-1)
            for k in range(nr):
                a=math.tau*k/nr;v.append(fn(t,a));uv.append((k/nr,j/(ns-1)))
        for j in range(ns-1):
            for k in range(nr):f.append((j*nr+k,j*nr+(k+1)%nr,(j+1)*nr+(k+1)%nr,(j+1)*nr+k))
        if caps:f += [tuple(reversed(range(nr))),tuple(range((ns-1)*nr,ns*nr))]
        return mesh(name,v,f,uv,role)
    def center(o):return sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
    def sections(o,n=12):
        v=[o.matrix_world@q.co for q in o.data.vertices]
        return [sum(v[i:i+n],Vector())/n for i in range(0,len(v),n)]
    for side in ('left','right'):
        ankle=center(scene.objects['CG1c '+side+' ankle concentric hinge'])
        plant=center(scene.objects['CG1c '+side+' plantar foot housing'])
        # Bridge rises into existing ankle seat, never higher than its center.
        # Three curved interlocking instep plates, dark gap beneath each overlap.
        end=Vector((plant.x,plant.y-.032,.078))
        start=Vector((ankle.x,ankle.y,min(ankle.z,.155)))
        h=(end-start);horizontal=Vector((h.x,h.y,0)).normalized()
        across=Vector((-horizontal.y,horizontal.x,0))
        def instep(t,a,shrink=0):
            p=start.lerp(end,t);p.z+=.014*math.sin(math.pi*t)
            w=.046+.014*math.sin(math.pi*t)-shrink
            z=.024+.006*math.sin(math.pi*t)-shrink
            return p+across*w*math.cos(a)+Vector((0,0,z*math.sin(a)))
        sweep(side+' instep dark receiver',lambda t,a:instep(t,a,.008),0,1,'inner')
        for i in range(3):
            lo=i/3;hi=min(1,(i+1)/3+.028)
            sweep(side+' curved instep shell '+str(i),instep,lo+.010,hi)
            sweep(side+' warm instep recessed band '+str(i),lambda t,a:instep(t,a,.003),lo,lo+.018,'bearing',ns=3)
        toes=[o for o in originals if o.name.startswith('CG1c '+side) and 'dark tendon chassis' in o.name]
        for toe in toes:
            label=toe.name.replace('CG1c ','').replace(' dark tendon chassis','')
            a,b=sections(toe);direction=Vector((b.x-a.x,b.y-a.y,0)).normalized()
            across=Vector((-direction.y,direction.x,0))
            # Heavier envelope follows inherited endpoint direction; the blunt
            # arch gives the toes substance without translating foot centers.
            def toeform(t,ang,delta=0):
                p=a.lerp(b,t);p.z+=.017+.012*math.sin(math.pi*t)
                w=.041*(1-.18*t)+delta
                z=.034*(1-.20*t)+delta*.7
                return p+across*w*math.cos(ang)+Vector((0,0,z*math.sin(ang)))
            sweep(label+' recessed tendon body',lambda t,q:toeform(t,q,-.007),0,1,'inner')
            for i in range(5):
                lo=i/5;hi=(i+1)/5
                # Small dark recess at each proximal edge; softly bulged shells
                # interlock around the arch instead of a series of thin rings.
                def shell(t,q,lo=lo,hi=hi):
                    # Nearly constant sleeve section with short rolled shoulders.
                    u=(t-lo)/(hi-lo)
                    shoulder=min(1,max(0,(u-.10)/.09),max(0,(1-u)/.07))
                    return toeform(t,q,-.0015+.002*shoulder)
                sweep(label+' interlocking toe shell '+str(i),shell,lo+.025,hi-.003)
                sweep(label+' warm seam band '+str(i),lambda t,q:toeform(t,q,-.001),lo+.012,lo+.028,'bearing',ns=3)
            # Solid sharp hook, thicker base and pronounced high arch descending
            # to the unchanged contact plane; not an extended flat nail.
            tip=sections(scene.objects['CG1c '+label+' recurved steel talon'])[-1]
            contact_z=.015
            points=[b+Vector((0,0,.018)),b+direction*.026+Vector((0,0,.036)),
                    b+direction*.060+Vector((0,0,.027)),tip+direction*.021+Vector((0,0,.016)),
                    Vector((tip.x+direction.x*.029,tip.y+direction.y*.029,contact_z))]
            radii=[.034,.035,.025,.009,.0007]
            def spline(t):
                k=min(3,int(t*4));u=t*4-k
                pa,pb,pc,pd=points[max(0,k-1)],points[k],points[k+1],points[min(4,k+2)]
                p=.5*((2*pb)+(-pa+pc)*u+(2*pa-5*pb+4*pc-pd)*u*u+(-pa+3*pb-3*pc+pd)*u*u*u)
                r=radii[k]*(1-u)+radii[k+1]*u
                return p,r
            def claw(t,q):
                p,r=spline(t)
                tangent=(spline(min(1,t+.002))[0]-spline(max(0,t-.002))[0]).normalized()
                up=tangent.cross(across).normalized()
                v=p+across*(r*.80*math.cos(q))+up*(r*.85*math.sin(q))
                v.z=max(.0144,v.z)
                return v
            sweep(label+' substantial descending talon',claw,0,1,'talon',nr=32,ns=49)
            sweep(label+' talon-root cuff',lambda t,q:toeform(t,q,.001),.93,1.018,'bearing',ns=5)
            toe_receipt.append({'label':label,'inheritedRoot':list(a),'inheritedDistal':list(b),'oldTip':list(tip),'newTip':list(points[-1])})
    # Superseded narrow toes/flat dorsum retained; ankle machinery stays visible.
    for o in originals:
        if o.type=='MESH' and o.get('cg1cRegion')=='foot' and not o.hide_render and 'ankle ferrule' not in o.name:
            o.hide_render=True;o.hide_set(True);hidden.append(o.name)
    bpy.context.view_layer.update()
    changed=[n for n,d in payload.items() if scene.objects.get(n) is None or _digest(scene.objects[n])!=d]
    assert not changed,changed
    verts=[v.co for o in made for v in o.data.vertices]
    return {'module':'cg-supervised-feet03','era':era,'originalPayloadSHA256':payload,
            'sourceMeshUVTransformsMaterialSlotsPreserved':not changed,'changedSourcePayloads':changed,
            'stanceMeshAnchorsUnchanged':anchor_receipt,
            'visibleRetainedOldToeClawMeshes':[o.name for o in originals if o.type=='MESH' and not o.hide_render and any(t in o.name.lower() for t in ('talon','claw','hook','toe'))],
            'sourceEmptyAnchors':{o.name:[list(r) for r in o.matrix_world] for o in originals if o.type=='EMPTY'},
            'hiddenRetainedMeshes':hidden,'newMeshes':[o.name for o in made],
            'editableUVLayers':True,'toeSourceAndProposalPoints':toe_receipt,
            'newBounds':[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)],
            'limitations':['Hidden rear details inferred','Source toe direction/stance unchanged; exterior volume increases','Existing role material graphs reused unchanged; finish worker remaps','Not engineering or owner artistic acceptance']}


def preview():
    import importlib.util
    root=Path(__file__).resolve().parents[1]
    out=root/'assets/audit/cg-supervised-feet03';out.mkdir(parents=True,exist_ok=True)
    source=root/'assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend'
    reference=root/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(source)=='e5fc6a39662bcb7f5ab82679dd719757edc4f0f39fc3cc5ae433bae962409d43'
    assert sha(reference)=='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
    bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
    camera=scene.camera
    canon=json.loads((root/'assets/audit/cg-supervised01/attempt01/builder/receipt.json').read_text())['cameras']['canon-neutral']
    spec=importlib.util.spec_from_file_location('lighting',root/'scripts/cinematic-cg-2b-lighting.py')
    lighting=importlib.util.module_from_spec(spec);spec.loader.exec_module(lighting)
    rig=lighting.profiles()['neutral']
    bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(*rig['world_color'][:3],1);bg.inputs[1].default_value=rig['world_strength']
    lights=[o for o in scene.objects if o.type=='LIGHT']
    for o,s in zip(lights,rig['areas']):
        o.location=s['position'];o.rotation_euler=(Vector(s['target'])-o.location).to_track_quat('-Z','Y').to_euler()
        o.data.energy=s['power'];o.data.color=s['color'];o.data.size=s['size']
    scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    receipt={'nativeInputSHA256':sha(source),'referenceSHA256':sha(reference),'renderEngine':scene.render.engine,'samples':scene.cycles.samples,'canonCamera':canon,'cameras':{},'artisticAcceptance':'not claimed'}
    def render(name,feet=False):
        if feet:
            camera.location=(-2,-1.7,.78);camera.rotation_euler=(Vector((0,-.05,.15))-camera.location).to_track_quat('-Z','Y').to_euler()
            camera.data.ortho_scale=.80;camera.data.shift_x=0;camera.data.shift_y=0
        else:
            camera.location=canon['location'];camera.rotation_euler=canon['rotation_euler'];camera.data.ortho_scale=canon['ortho_scale']
            camera.data.shift_x,camera.data.shift_y=canon['shift']
        camera.data.type='ORTHO';camera.data.lens=canon['lens_mm']
        scene.render.resolution_x=768;scene.render.resolution_y=512
        scene.render.filepath=str(out/(name+'.png'))
        receipt['cameras'][name]={'location':list(camera.location),'rotation':list(camera.rotation_euler),'scale':camera.data.ortho_scale,'shift':[camera.data.shift_x,camera.data.shift_y],'resolution':[768,512],'lighting':'frozen neutral'}
        bpy.ops.render.render(write_still=True)
    render('before-canon');render('before-feet',True)
    receipt['application']=apply(scene,root)
    render('after-canon');render('after-feet',True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'murderbird-feet03-study.blend'))
    receipt['nativeOutputSHA256']=sha(out/'murderbird-feet03-study.blend')
    assert sha(source)==receipt['nativeInputSHA256']
    receipt['sourceBinaryPreserved']=True
    receipt['images']={p.name:sha(p) for p in out.glob('*.png')}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('FEET03_COMPLETE',out)

if __name__=='__main__':
    import sys
    if '--preview' in sys.argv:preview()
