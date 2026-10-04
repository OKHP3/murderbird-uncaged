"""Camera-only diagnostic of frozen integration04; no native asset is saved.

Run Blender --background --python scripts/cg-supervised-camera04.py -- --run.
camera(root_path) returns the proposed matched-comparison camera from receipt.
Landmarks are declared image interpretations, not physical camera calibration.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'assets/audit/cg-supervised-camera04'
NATIVE_REL = 'assets/models/cg-supervised01/integration04/murderbird-supervised-builder.blend'
SOURCE_REL = 'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'
NATIVE_SHA = '5809c13d35c9a9ec52db098ebbdc543a335bcaa32d50baeb3e1a9f4a03bed254'
SOURCE_SHA = '645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
HYDRATED = Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')


def camera(root_path=None, hypothesis='best'):
    """Use identically on before/candidate; all values are Blender coordinates."""
    root = Path(root_path or ROOT)
    receipt = json.loads((root / 'assets/audit/cg-supervised-camera04/receipt.json').read_text())
    if hypothesis == 'body-only':
        return receipt['body_only_diagnostic']['camera'].copy()
    name = receipt['proposed_hypothesis'] if hypothesis == 'best' else hypothesis
    return receipt['hypotheses'][name]['camera'].copy()


def run(body_only=False):
    import bpy
    import numpy as np
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    def resolved(rel, expected):
        for base in (ROOT, HYDRATED):
            p = base / rel
            if p.exists() and p.stat().st_size > 1000 and sha(p) == expected:
                return p
        raise RuntimeError('Missing exact hydrated input: ' + rel)
    native = resolved(NATIVE_REL, NATIVE_SHA)
    source = resolved(SOURCE_REL, SOURCE_SHA)
    AUDIT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    originals = list(scene.objects)
    def payload(o):
        h = hashlib.sha256()
        h.update(np.asarray(o.matrix_world, dtype='<f8').tobytes())
        h.update(str((o.type, o.parent.name if o.parent else None, o.hide_render, o.hide_get(), sorted(o.items()))).encode())
        if o.type == 'MESH':
            a = np.empty(len(o.data.vertices)*3, dtype='<f4'); o.data.vertices.foreach_get('co', a); h.update(a.tobytes())
            h.update(str([(tuple(p.vertices),p.material_index) for p in o.data.polygons]).encode())
            for uv in o.data.uv_layers:
                a=np.empty(len(uv.data)*2,dtype='<f4');uv.data.foreach_get('uv',a);h.update(uv.name.encode());h.update(a.tobytes())
            h.update(str([m.name if m else None for m in o.data.materials]).encode())
            h.update(str([(m.name,m.type) for m in o.modifiers]).encode())
        return h.hexdigest()
    preserved = {o.name:payload(o) for o in originals}
    material_preserved = {m.name:repr([(n.name,n.type,[(i.name,repr(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes])+repr([(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]) for m in bpy.data.materials if m.use_nodes}
    def center(name):
        o=scene.objects[name]
        return sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
    crown_obj=scene.objects['CGH04 nine section cranial vault']
    crown=max((crown_obj.matrix_world@v.co for v in crown_obj.data.vertices),key=lambda v:v.z)
    bill_obj=scene.objects['CGH04 nine section convex hooked upper bill']
    bill=min((bill_obj.matrix_world@v.co for v in bill_obj.data.vertices),key=lambda v:v.z)
    # Pixel centers manually read from the exact 1280x853 source. Near/far labels
    # denote this image only; source anatomical handedness is not established.
    landmarks = [
      ('crown', [834,28], crown, 1, 'cranial-vault highest vertex; source crest includes separate plates'),
      ('near-optic', [916,113], center('CGH04 solid optical glass L'), 1, 'visible circular optic center'),
      ('bill-hook', [989,257], bill, 1, 'lowest upper-bill vertex; contour interpretation'),
      ('near-shoulder', [719,272], center('CGB04 -1 shield hard blade 0-1'), .7, 'upper shield-root center, broad ambiguous region'),
      ('breast-center', [898,402], center('CGB04 breast framing 4-1'), .5, 'frontal breast plate-course center, uncertain homologous surface'),
      ('near-knee', [610,550], center('CG1c left knee concentric hinge'), 1, 'source visible upper circular leg hinge'),
      ('far-knee', [840,552], center('CG1c right knee concentric hinge'), 1, 'source far upper hinge partly occluded'),
      ('near-hock', [610,644], center('CG1c left hock concentric hinge'), 1, 'source intermediate circular hinge'),
      ('far-hock', [830,643], center('CG1c right hock concentric hinge'), .7, 'far hinge partly occluded'),
      ('near-ankle', [639,731], center('CG1c left ankle concentric hinge'), 1, 'source instep/ankle hinge center'),
      ('far-ankle', [856,728], center('CG1c right ankle concentric hinge'), .7, 'source instep/ankle hinge center partly occluded'),
      ('near-foot', [665,768], center('CG1c left plantar foot housing'), .5, 'source proximal plantar housing, partly covered by instep'),
      ('far-foot', [885,747], center('CG1c right plantar foot housing'), .5, 'source proximal plantar housing, partly covered by instep'),
    ]
    visible=[o for o in originals if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide')]
    corners=[o.matrix_world@Vector(c) for o in visible for c in o.bound_box]
    # Use full evaluated world-vertex bounds for framing validation. Bounding-box
    # corners remain a conservative crop gate (entire bird, not fitted landmarks).
    points=np.array([list(v) for v in corners])
    xyz=np.array([list(v) for _,_,v,_,_ in landmarks]); dst=np.array([p for _,p,_,_,_ in landmarks]); weights=np.array([w for _,_,_,w,_ in landmarks])
    W,H=1280,853
    original_world=scene.world
    hidden={o.name:o.hide_render for o in originals}
    for o in originals:
        if o.type=='LIGHT' or o.get('authoringGuide'):o.hide_render=True
    world=bpy.data.worlds.new('Camera04 temporary neutral world');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.08,.08,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.4;scene.world=world
    for i,(loc,power,size) in enumerate([((-3,-4,5),700,4),((4,-1,3),250,4),((0,4,4),500,3)]):
        d=bpy.data.lights.new('Camera04 temporary area '+str(i),'AREA');o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.size=size
    data=bpy.data.cameras.new('Camera04 temporary comparison camera');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
    scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=100
    scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    clay=bpy.data.materials.new('Camera04 temporary neutral clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
    def setcam(c):
        cam.location=c['location'];cam.rotation_euler=c['rotation_euler'];data.type=c['projection'];data.ortho_scale=c['ortho_scale'];data.shift_x,data.shift_y=c['shift'];data.lens=c['lens_mm'];bpy.context.view_layer.update()
    def projected(vs):
        return np.array([[p.x*W,(1-p.y)*H] for p in [world_to_camera_view(scene,cam,Vector(v)) for v in vs]])
    def fit(yaw,pitch,projection='ORTHO'):
        y,p=math.radians(yaw),math.radians(pitch)
        target=Vector((0,0,.97));distance=6.4 if projection=='ORTHO' else 4.6
        loc=target+Vector((-math.cos(y)*math.cos(p),-math.sin(y)*math.cos(p),math.sin(p)))*distance
        rot=(target-loc).to_track_quat('-Z','Y').to_euler()
        c=dict(location=list(loc),rotation_euler=list(rot),projection=projection,ortho_scale=3.2,shift=[0,0],lens_mm=65,resolution=[W,H])
        setcam(c);q=projected(xyz)
        mean=lambda a:np.average(a,axis=0,weights=weights)
        qa=q-mean(q);da=dst-mean(dst)
        s=float(np.sum(weights[:,None]*qa*da)/np.sum(weights[:,None]*qa*qa))
        if projection=='ORTHO':c['ortho_scale']/=s
        else:
            # Keep requested 65mm hypothesis; change distance to match overall scale.
            c['location']=list(target+(loc-target)/s)
        setcam(c);q=projected(xyz);offset=mean(dst)-mean(q)
        # Empirically measured Blender shift basis also covers sensor fitting.
        c['shift']=[1,0];setcam(c);dx=projected(xyz)[0]-q[0]
        c['shift']=[0,1];setcam(c);dy=projected(xyz)[0]-q[0]
        c['shift']=list(np.linalg.solve(np.array([dx,dy]).T,offset));setcam(c)
        b=projected(points);bounds=[float(b[:,0].min()),float(b[:,1].min()),float(b[:,0].max()),float(b[:,1].max())]
        if min(bounds[:2])<12 or bounds[2]>W-12 or bounds[3]>H-12:
            # Do not crop a silhouette to improve landmark score: expand and refit shifts.
            expansion=max((bounds[2]-bounds[0])/(W-24),(bounds[3]-bounds[1])/(H-24),1)
            if projection=='ORTHO':c['ortho_scale']*=expansion
            else:c['location']=list(target+(Vector(c['location'])-target)*expansion)
            setcam(c);q=projected(xyz);offset=mean(dst)-mean(q)
            c['shift'][0]+=float(np.linalg.solve(np.array([dx,dy]).T,offset)[0]);c['shift'][1]+=float(np.linalg.solve(np.array([dx,dy]).T,offset)[1]);setcam(c)
            b=projected(points);bounds=[float(b[:,0].min()),float(b[:,1].min()),float(b[:,0].max()),float(b[:,1].max())]
            # Last shift constrained by full character margins, never by landmark crop.
            offset=np.array([max(12-bounds[0],0)+min(W-12-bounds[2],0),max(12-bounds[1],0)+min(H-12-bounds[3],0)])
            ds=np.linalg.solve(np.array([dx,dy]).T,offset);c['shift']=[float(c['shift'][i]+ds[i]) for i in (0,1)];setcam(c)
        return measure(c)
    def measure(c):
        setcam(c);q=projected(xyz);err=q-dst;b=projected(points)
        return {'camera':c,'weighted_rms_px':float(np.sqrt(np.average(np.sum(err*err,axis=1),weights=weights))),
          'landmarks':[{'name':n,'source_px':s,'world':list(v),'weight':w,'assumption':a,'projected_px':list(q[i]),'residual_px':list(err[i]),'distance_px':float(np.linalg.norm(err[i]))} for i,(n,s,v,w,a) in enumerate(landmarks)],
          'conservative_full_bird_bounds_px':[float(b[:,0].min()),float(b[:,1].min()),float(b[:,0].max()),float(b[:,1].max())],
          'knee_separation_px':float(abs(q[5,0]-q[6,0])),'ankle_separation_px':float(abs(q[9,0]-q[10,0]))}
    canonical=dict(location=[-6,-2.14,1.97],rotation_euler=[1.4070991277694702,-8.636930459715586e-08,-1.2341214418411255],projection='ORTHO',ortho_scale=3.195436239242554,shift=[-.10180506110191345,-.009439428336918354],lens_mm=65,resolution=[W,H])
    hypotheses={'canonical':measure(canonical)}
    for yaw in (0,20,35,50,65,80):
        fits=[fit(yaw,pitch) for pitch in (0,4,8,12,16)]
        hypotheses[f'ortho-{yaw:02d}']=min(fits,key=lambda r:r['weighted_rms_px'])
    ortho_best=min((n for n in hypotheses if n!='canonical'),key=lambda n:hypotheses[n]['weighted_rms_px'])
    yaw=int(ortho_best[-2:]);hypotheses['persp-65mm']=min([fit(yaw,p,'PERSP') for p in (0,4,8,12,16)],key=lambda r:r['weighted_rms_px'])
    best=ortho_best
    if body_only:
        full_weights=weights.copy();weights[:3]=0
        coarse=[(y,p,fit(y,p)) for y in range(0,91,10) for p in range(0,21,4)]
        y,p,h=min(coarse,key=lambda item:item[2]['weighted_rms_px'])
        fine=[(yy,pp,fit(yy,pp)) for yy in range(max(0,y-6),min(90,y+6)+1,2) for pp in range(max(0,p-4),min(24,p+4)+1,2)]
        y,p,h=min(fine,key=lambda item:item[2]['weighted_rms_px'])
        h['azimuth_degrees_from_side']=y;h['elevation_degrees']=p
        h['excluded_from_objective']=['crown','near-optic','bill-hook']
        h['full_landmark_rms_px']=float(np.sqrt(np.average([l['distance_px']**2 for l in h['landmarks']],weights=full_weights)))
        h['foot_housing_separation_px']=abs(h['landmarks'][11]['projected_px'][0]-h['landmarks'][12]['projected_px'][0])
        base=hypotheses['canonical']['landmarks']
        h['canonical_body_rms_px']=float(np.sqrt(np.average([l['distance_px']**2 for l in base[3:]],weights=full_weights[3:])))
        h['grid_note']='Body-only coarse yaw0..90 step10/pitch0..20 step4; local refinement ±6yaw/±4pitch step2, maximum24pitch. Entire bird remains crop-constrained.'
        weights=full_weights
        prior=json.loads((AUDIT/'receipt.json').read_text())
        prior['body_only_diagnostic']=h
        hypotheses={'body-only':h}
    receipt={'input_path':NATIVE_REL,'input_resolved_path':str(native),'input_sha256':NATIVE_SHA,'source_path':SOURCE_REL,'source_resolved_path':str(source),'source_sha256':SOURCE_SHA,'source_resolution':[W,H],
       'shared_goal_revision':'251f2f0243181e97140179c2aff6eb057e165438','source_approximate_bird_bounds_px':[550,25,1026,827],
       'source_knee_separation_px':230,'source_ankle_separation_px':217,'hypotheses':hypotheses,'proposed_hypothesis':best,
       'interpretation':'Declared-landmark compromise; not recovered physical source camera or artistic acceptance. Orthographic comparison proposed because perspective improvement is negligible; numeric minimum also recorded.',
       'numeric_minimum':min((n for n in hypotheses if n!='canonical'),key=lambda n:hypotheses[n]['weighted_rms_px']),
       'search_grid':{'azimuth_degrees_from_side':[0,20,35,50,65,80],'elevation_degrees':[0,4,8,12,16],'note':'Several fits hit maximum elevation; camera/pose identifiability remains unresolved'},
       'excluded':['July reference body is excluded; no July image used','Far optic not visible and not scored','Hidden source hip joints not scored','Feet toe tips vary by overlap and are excluded from fitting; entire foot silhouette remains in crop gate','Body center has lower weight due to uncertain anatomical homology','Source scene perspective and stylized/asymmetric construction remain unknown'],
       'lighting':{'profile':'neutral','source_rig':'scripts/cg-supervised-lighting02.py neutral values','samples':8,'view_transform':'AgX','look':'AgX - Medium High Contrast','transparent_world':True},'image_hashes':{}}
    if body_only:receipt=prior
    for name,r in hypotheses.items():
        setcam(r['camera'])
        for mode in ('clay','pbr'):
            scene.view_layers[0].material_override=clay if mode=='clay' else None
            out=AUDIT/(name+'-'+mode+'.png');scene.render.filepath=str(out);bpy.ops.render.render(write_still=True);receipt['image_hashes'][out.name]=sha(out)
        print('CAMERA04_RENDERED',name,r['weighted_rms_px'],flush=True)
    scene.view_layers[0].material_override=None
    scene.world=original_world
    for o in originals:o.hide_render=hidden[o.name]
    changed=[o.name for o in originals if payload(o)!=preserved[o.name]]
    changed_materials=[m.name for m in bpy.data.materials if m.name in material_preserved and material_preserved[m.name]!=(repr([(n.name,n.type,[(i.name,repr(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes])+repr([(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]))]
    receipt['preservation']={'original_object_count':len(originals),'changed_object_payloads':changed,'changed_material_graphs':changed_materials,'input_bytes_unchanged':sha(native)==NATIVE_SHA,'source_bytes_unchanged':sha(source)==SOURCE_SHA,'native_saved':False,
       'object_payload_sha256_before':hashlib.sha256(json.dumps(preserved,sort_keys=True).encode()).hexdigest(),
       'object_payload_sha256_after':hashlib.sha256(json.dumps({o.name:payload(o) for o in originals},sort_keys=True).encode()).hexdigest()}
    if changed or changed_materials or sha(native)!=NATIVE_SHA or sha(source)!=SOURCE_SHA:raise RuntimeError('Frozen payload changed')
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('CAMERA04_COMPLETE',best,flush=True)


def review():
    """Pillow diagram compositing only; source pixels never become texture maps."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    r=json.loads((AUDIT/'receipt.json').read_text());best=r['proposed_hypothesis'];W,H=r['source_resolution']
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
    source=Image.open(r['source_resolved_path']).convert('RGBA')
    render=Image.open(AUDIT/(best+'-clay.png')).convert('RGBA')
    alpha=render.getchannel('A');boundary=alpha.filter(ImageFilter.MaxFilter(5));inner=alpha.filter(ImageFilter.MinFilter(5))
    import PIL.ImageChops
    edge=PIL.ImageChops.subtract(boundary,inner)
    outline=Image.new('RGBA',(W,H),(0,230,255,0));outline.putalpha(edge)
    overlay=Image.alpha_composite(source,outline);d=ImageDraw.Draw(overlay)
    labeled=source.copy();ld=ImageDraw.Draw(labeled)
    for i,l in enumerate(r['hypotheses'][best]['landmarks']):
        x,y=l['source_px'];u,v=l['projected_px'];color=(255,184,45)
        for dd in (d,ld):dd.line((x-6,y,x+6,y),fill=color,width=2);dd.line((x,y-6,x,y+6),fill=color,width=2)
        ld.text((x+9,y-9),str(i+1)+' '+l['name'],font=font,fill=color,stroke_width=1,stroke_fill='black')
        d.line((x,y,u,v),fill=(255,80,180,210),width=2);d.ellipse((u-4,v-4,u+4,v+4),fill=(255,80,180));d.text((x+9,y-9),str(i+1),font=font,fill=color,stroke_width=1,stroke_fill='black')
    d.rectangle((0,0,540,23),fill=(0,0,0,235));d.text((5,2),'Amber: source points | Cyan: model outline | Pink: residual',font=font,fill='white')
    overlay.save(AUDIT/'best-overlay.png');labeled.save(AUDIT/'source-landmarks.png')
    if 'body_only_diagnostic' in r:
        body=Image.open(AUDIT/'body-only-clay.png').convert('RGBA');alpha=body.getchannel('A')
        edge=PIL.ImageChops.subtract(alpha.filter(ImageFilter.MaxFilter(5)),alpha.filter(ImageFilter.MinFilter(5)))
        outline=Image.new('RGBA',(W,H),(0,230,255,0));outline.putalpha(edge)
        body_overlay=Image.alpha_composite(source,outline);bd=ImageDraw.Draw(body_overlay)
        for i,l in enumerate(r['body_only_diagnostic']['landmarks']):
            x,y=l['source_px'];u,v=l['projected_px'];color=(255,184,45) if i>=3 else (200,200,200)
            bd.line((x-6,y,x+6,y),fill=color,width=2);bd.line((x,y-6,x,y+6),fill=color,width=2);bd.line((x,y,u,v),fill=(255,80,180,210),width=2);bd.ellipse((u-4,v-4,u+4,v+4),fill=(255,80,180));bd.text((x+9,y-9),str(i+1),font=font,fill=color,stroke_width=1,stroke_fill='black')
        bd.rectangle((0,0,720,23),fill=(0,0,0,235));bd.text((5,2),'Body-only fit: cyan model | amber scored body | gray excluded head | pink residual',font=font,fill='white')
        body_overlay.save(AUDIT/'body-only-overlay.png')
    sheet=Image.new('RGB',(2560,960),(29,31,33));sd=ImageDraw.Draw(sheet)
    for i,(n,h) in enumerate(r['hypotheses'].items()):
        x=(i%4)*640;y=(i//4)*480
        for j,mode in enumerate(('clay','pbr')):
            im=Image.open(AUDIT/(n+'-'+mode+'.png')).convert('RGBA');bg=Image.new('RGBA',im.size,(34,35,37,255));bg.alpha_composite(im)
            # Identical display-only crop removes empty left scenery in this
            # sheet. All camera renders and overlays retain exact source aspect.
            bg=bg.crop((540,0,1040,853));bg.thumbnail((320,427));sheet.paste(bg.convert('RGB'),(x+j*320+(320-bg.width)//2,y+35))
        sd.text((x+8,y+8),f'{n}: RMS {h["weighted_rms_px"]:.1f}px / ankle {h["ankle_separation_px"]:.0f}px',font=font,fill='white')
    sheet.save(AUDIT/'hypothesis-sheet.png')
    for n,h in r['hypotheses'].items():
        for mode in ('clay','pbr'):
            im=Image.open(AUDIT/(n+'-'+mode+'.png'));h.setdefault('render_alpha_bounds_px',{})[mode]=list(im.getchannel('A').getbbox())
    if 'body_only_diagnostic' in r:
        r['body_only_diagnostic']['render_alpha_bounds_px']={m:list(Image.open(AUDIT/('body-only-'+m+'.png')).getchannel('A').getbbox()) for m in ('clay','pbr')}
    r['derived_review_images']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [AUDIT/'best-overlay.png',AUDIT/'source-landmarks.png',AUDIT/'hypothesis-sheet.png']}
    if (AUDIT/'body-only-overlay.png').exists():r['derived_review_images']['body-only-overlay.png']=hashlib.sha256((AUDIT/'body-only-overlay.png').read_bytes()).hexdigest()
    (AUDIT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
    (AUDIT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Camera04 diagnostic</title><style>body{background:#181b1d;color:#eee;font:17px system-ui;margin:24px}img{max-width:100%;height:auto}a{color:#6df}section{margin:40px 0}h1{font-size:25px}</style><h1>Frozen integration04: camera-only diagnostic</h1><p>Declared image landmarks, not recovered physical camera. No geometry/material/pose changes. Entire bird retained. July body excluded. Source creative content all rights reserved; internal review only.</p><p><a href="README.md">Handoff</a> · <a href="receipt.json">Exact cameras and residuals</a></p><section><h2>Source points and proposed '+best+'</h2><img src="source-landmarks.png"><img src="best-overlay.png"></section><section><h2>Eight hypotheses, each clay / neutral PBR</h2><img src="hypothesis-sheet.png"></section>'+''.join('<section><h2>'+n+'</h2><p>Weighted RMS '+str(round(h['weighted_rms_px'],1))+' px</p><img src="'+n+'-clay.png"><img src="'+n+'-pbr.png"></section>' for n,h in r['hypotheses'].items()))


if __name__ == '__main__':
    if '--run' in sys.argv:run('--body-only' in sys.argv)
    if '--review' in sys.argv:review()
