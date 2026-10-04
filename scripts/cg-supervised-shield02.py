"""Wing-only compact shield construction correction; retained source meshes.

API: apply(scene, root_path=None, era='builder'), after head-neck01/shoulder01.
"""
import math, json, hashlib, argparse, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

SECTIONS=[(.945,.115,.192,.246,.009),(1.005,.002,.249,.255,.040),
 (1.075,-.099,.261,.238,.094),(1.155,-.178,.253,.221,.134),
 (1.235,-.205,.218,.205,.147),(1.310,-.180,.147,.191,.121),
 (1.365,-.100,.077,.178,.079),(1.393,-.025,.014,.170,.025)]

def section(z):
    z=max(SECTIONS[0][0],min(SECTIONS[-1][0],z))
    for a,b in zip(SECTIONS,SECTIONS[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);t=t*t*(3-2*t)
            return [a[i]*(1-t)+b[i]*t for i in range(1,5)]
    return SECTIONS[-1][1:]

def apply(scene,root_path=None,era='builder'):
    if any(o.get('cgSupervisedShield02') for o in scene.objects):
        raise RuntimeError('Reload preserved input before reapplying shield02')
    old=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.get('cgSupervisedShoulder') and o.get('cg2bRegion')=='wing']
    if not old:raise RuntimeError('shoulder01 compact shields must precede shield02')
    mats={}
    for o in old:
        if o.data.materials:mats.setdefault(o.get('surfaceRole','armor'),o.data.materials[0])
    armor=mats.get('armor');inner=mats.get('inner',armor)
    # Reuse source regional graphs. A separate sidewall slot carries recessed metal.
    edge=next((o.data.materials[0] for o in scene.objects if o.type=='MESH' and o.data.materials and o.get('surfaceRole') in ('black-iron','inner','machinery')),inner)
    coll=bpy.data.collections.new('CG supervised shield02 thin scalloped sheets');scene.collection.children.link(coll)
    hidden=[];made=[]
    for o in old:
        if 'compact shield recess' in o.name:continue
        o.hide_render=True;o.hide_set(True);o['cgSupervisedShield02Retained']=True;hidden.append(o.name)
    def point(side,q,z,offset):
        front,rear,x,bulge=section(z);q=max(-.98,min(.98,q))
        return Vector((side*(x+bulge*math.sqrt(1-q*q)+offset),(front+rear)/2+q*(rear-front)/2,z))
    def plate(name,side,q,z,width,length,sweep,row):
        # Rounded root, narrowed curved tip and gently scalloped shoulders.
        # u is lateral and v runs toward the exposed distal boundary.
        shape=[(-.40,0),(-.20,-.028),(.18,-.022),(.39,.012),(.49,.16),
          (.49,.35),(.43,.58),(.31,.80),(.16,.95),(0,1),(-.17,.95),
          (-.32,.82),(-.42,.64),(-.49,.42),(-.49,.20)]
        n=len(shape);vs=[];uv=[];faces=[];surfacefaces=0
        # 4 curved rings prevent broad flat fan shading or pillow doming.
        for scale in (1,.70,.37,.07):
            for u,v in shape:
                uu=u*scale;vv=.45+(v-.45)*scale
                zz=z-vv*length
                q2=q+uu*width+vv*sweep
                vs.append(tuple(point(side,q2,zz,.0040+row*.0014)))
                uv.append((uu+.5,vv))
        for r in range(3):
            for i in range(n):j=(i+1)%n;faces.append((r*n+i,r*n+j,(r+1)*n+j,(r+1)*n+i))
        faces.append(tuple(range(3*n,4*n)));surfacefaces=len(faces)
        for u,v in shape:vs.append(tuple(point(side,q+u*width+v*sweep,z-v*length,.0018+row*.0014)));uv.append((u+.5,v))
        faces.append(tuple(reversed(range(4*n,5*n))))
        for i in range(n):j=(i+1)%n;faces.append((i,4*n+i,4*n+j,j))
        data=bpy.data.meshes.new(name);data.from_pydata(vs,[],faces);data.update()
        ob=bpy.data.objects.new(name,data);coll.objects.link(ob)
        for mat in (armor,edge,inner):
            if mat:data.materials.append(mat)
        layer=data.uv_layers.new(name='scalloped-sheet-uv')
        for p in data.polygons:
            p.material_index=0 if p.index<surfacefaces else (2 if p.index==surfacefaces else 1)
            p.use_smooth=p.index<surfacefaces
            for li in p.loop_indices:layer.data[li].uv=uv[data.loops[li].vertex_index]
        bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
        ob['cgSupervisedShield02']=True;ob['cg1cRegion']='wing';ob['cg2bRegion']='wing';ob['surfaceRole']='armor'
        ob['shieldSide']='left' if side<0 else 'right';ob['plateCourse']=row;ob['exteriorEras']='maker,mechanic,builder'
        ob['detailStatus']='Thin compact scalloped shield proposal; owner likeness review pending'
        ob['sheetThickness']=.0022;ob['constructionFamily']='small root scallop' if row>=7 else 'diagonal compact covert'
        made.append(ob)
    # Close overlap, varying regional density and posterior obliquity. q width
    # follows local envelope width, avoiding former caps outside the curved recess.
    rows=[(1.388,3,.062,.83,.025),(1.362,5,.076,.54,.035),
      (1.327,6,.095,.44,.08),(1.283,7,.109,.37,.13),
      (1.231,7,.119,.36,.17),(1.177,6,.127,.41,.20),
      (1.121,5,.124,.48,.23),(1.068,4,.105,.56,.20),
      (1.023,2,.073,.75,.12)]
    for side in (-1,1):
        label='left' if side<0 else 'right'
        for idx,(z,n,length,width,sweep) in reversed(list(enumerate(rows))):
            # Start/end near same short shield outline. Less symmetry in the
            # middle shoulder rows; rear terminals turn toward posterior edge.
            for col in range(n):
                q=-.84+1.62*col/max(1,n-1)
                q+=.035*math.sin(col*1.7+idx)
                ll=length*(1+.06*math.sin(col*1.4+idx))
                plate(f'CG shield02 {label} scallop {idx:02d}-{col:02d}',side,q,z,width,ll,sweep*(.5+col/max(1,n-1)),8-idx)
    return {'module':'cg-supervised-shield02','era':era,'newMeshes':len(made),'retainedHidden':hidden,
      'preservedCompactRecess':True,'sections':SECTIONS,'sheetThickness':.0022,
      'changes':['Curved tapered scallops follow existing compact envelope','Close diagonal overlap with regional row density','Original compact recess/exposed underwing machinery retained','Three material slots: face, thin sidewall, underside'],
      'limits':['No hardware added; original underwing hardware retained','Posterior construction remains inferred','Artistic acceptance not claimed']}

def digest(o):
    h=hashlib.sha256()
    for data in ([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[tuple(r) for r in o.matrix_world],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons],o.hide_render):h.update(repr(data).encode())
    return h.hexdigest()

def diagnostic():
    parser=argparse.ArgumentParser();parser.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));parser.add_argument('--resolution',type=int,default=900);parser.add_argument('--samples',type=int,default=12)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root=Path(args.root);out=root/'assets/audit/cg-supervised-shield02';out.mkdir(parents=True,exist_ok=True)
    source=root/'assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend';ref=root/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();input_hash=sha(source)
    if sha(ref)!='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114':raise RuntimeError('Reference pin mismatch')
    bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
    frozen={o.name:digest(o) for o in scene.objects if o.type=='MESH'}
    protected={o.name:digest(o) for o in scene.objects if o.type=='MESH' and o.get('cg2bRegion')!='wing'}
    scene.render.engine='CYCLES';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True;scene.cycles.device='CPU'
    scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100
    # Use frozen neutral world/lights already in native. Camera alone is reset
    # to the receipt, identical before/after. No light/material mutation.
    receipt=json.loads((root/'assets/audit/cg-supervised01/attempt01/builder/receipt.json').read_text());cam=scene.camera
    cams={}
    def render(name,kind):
        p=receipt['cameras'][kind];cam.location=p['location'];cam.rotation_euler=p['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=p['ortho_scale'];cam.data.shift_x,cam.data.shift_y=p['shift']
        scene.render.resolution_x=args.resolution;scene.render.resolution_y=round(args.resolution*p['resolution'][1]/p['resolution'][0]);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);cams[name]=p
    render('before-whole','canon-neutral');render('before-shield','side-profile')
    result=apply(scene,root,'builder');render('after-whole','canon-neutral');render('after-shield','side-profile')
    result.update(inputPath=str(source.relative_to(root)),inputSHA256=input_hash,inputPreserved=sha(source)==input_hash,referencePath=str(ref.relative_to(root)),referenceSHA256=sha(ref),referenceScope='Owner reissued fullbird JPEG controls shield; July excluded',cameras=cams)
    changed=[n for n,d in protected.items() if digest(scene.objects[n])!=d];result['protectedNonWingMeshes']={'count':len(protected),'changed':changed}
    # Original mesh geometry/UV/material data is unchanged, visibility differs
    # only for explicit former wing plates. Source .blend stays byte preserved.
    retained=[n for n,d in frozen.items() if n in result['retainedHidden']]
    result['retainedOriginalsPresent']=len(retained)==len(result['retainedHidden'])
    result['newEditableMeshes']=[{'name':o.name,'uvLayers':len(o.data.uv_layers),'materialSlots':len(o.data.materials),'sidewallFaces':sum(p.material_index==1 for p in o.data.polygons)} for o in scene.objects if o.get('cgSupervisedShield02')]
    result['lighting']='Unchanged from frozen native; matched before/after'
    result['reviewStatus']='Unaccepted construction proposal; no release or engineering claim'
    if changed:raise RuntimeError('Non-wing preservation failed '+repr(changed[:10]))
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'murderbird-shield02.blend'))
    result['outputSHA256']=sha(out/'murderbird-shield02.blend');result['images']={p.name:sha(p) for p in out.glob('*.png')}
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('SHIELD02_COMPLETE',out)
if __name__=='__main__':diagnostic()
