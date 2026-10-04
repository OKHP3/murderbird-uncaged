"""Compact shield/upper breast proposal. Original geometry and graphs stay retained.

Integration API: apply(scene, root_path=None, era='builder').
Diagnostic CLI loads CG2b and renders identical before/after cameras.
"""
import math, json, hashlib, argparse, sys
from pathlib import Path
import bpy
from mathutils import Vector


def apply(scene, root_path=None, era='builder'):
    if any(o.get('cgSupervisedShoulder') for o in scene.objects):
        raise RuntimeError('Load a preserved source before applying again')
    originals = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render]
    mats = {}
    for region in ('wing', 'body'):
        for o in originals:
            if o.get('cg2bRegion') == region and o.data.materials:
                role = o.get('surfaceRole', 'armor')
                mats.setdefault((region, role), o.data.materials[0])
    coll = bpy.data.collections.new('Supervised compact shields and breast transition')
    scene.collection.children.link(coll)
    made, retired = [], []
    def mesh(name, vs, fs, uv, region='wing', role='armor', smooth=True):
        data = bpy.data.meshes.new(name); data.from_pydata(vs, [], fs); data.update()
        ob = bpy.data.objects.new(name, data); coll.objects.link(ob)
        ob['cgSupervisedShoulder'] = True; ob['cg1cRegion'] = region; ob['cg2bRegion'] = region
        ob['surfaceRole'] = role; ob['exteriorEras'] = 'maker,mechanic,builder'
        ob['detailStatus'] = 'Source-aligned visual proposal; owner review pending'
        mat = mats.get((region, role), mats.get((region, 'armor')))
        if mat: data.materials.append(mat)
        layer = data.uv_layers.new(name='shield-curved-sheet-uv')
        for p in data.polygons:
            p.use_smooth = smooth
            for li in p.loop_indices: layer.data[li].uv = uv[data.loops[li].vertex_index]
        made.append(ob); return ob
    def retire(ob):
        ob.hide_render = True; ob.hide_set(True); ob['cgSupervisedShoulderRetained'] = True; retired.append(ob)
    for ob in originals:
        # Hide complete old wing; only upper anterior body courses are replaced.
        if ob.get('cg2bRegion') == 'wing' or ob.get('cg1cRegion') == 'wing': retire(ob)
        elif ob.get('cg2bBodyOwner'):
            top = ob.get('cg2bPlateTop', 0)
            bounds = [ob.matrix_world @ v.co for v in ob.data.vertices]
            if (top > 1.20 and abs(ob.get('cg2bPlateAngle', 9)) < 1.05) or (
                bounds and min(p.z for p in bounds) > 1.205 and max(p.y for p in bounds) < -.08): retire(ob)

    # The baseline's lowest visible curtain is its posterior body casing, not
    # a wing. Preserve/hide each casing and adjust only the rear lower volume.
    # UVs, face assignments and materials are copied intact; machinery stays.
    compacted=[]
    for source in originals:
        if source.hide_render or not source.get('cg2bBodyOwner'):continue
        points=[source.matrix_world @ v.co for v in source.data.vertices]
        if not any(p.y>.18 and p.z<.96 for p in points):continue
        ob=source.copy();ob.data=source.data.copy();ob.name='CG supervised compact posterior '+source.name
        coll.objects.link(ob);ob['cgSupervisedShoulder']=True
        inv=ob.matrix_world.inverted()
        for v in ob.data.vertices:
            p=ob.matrix_world @ v.co
            if p.y>.12 and p.z<1.02:
                weight=max(0,min(1,(1.02-p.z)/.505));rear=max(0,min(1,(p.y+.03)/.20))
                p.y-=max(0,p.y-.12)*.40*weight;p.z+=.17*weight*rear;v.co=inv@p
        ob.data.update();retire(source);made.append(ob);compacted.append(ob.name)

    # Side shield cross sections: anterior edge, rear edge, inset x, outward bulge.
    # Broad rounded shoulder mass rolls into short layered posterior terminals.
    sections = [( .945,.115,.192,.246,.009), (1.005,.002,.249,.255,.040),
                (1.075,-.099,.261,.238,.094), (1.155,-.178,.253,.221,.134),
                (1.235,-.205,.218,.205,.147), (1.310,-.180,.147,.191,.121),
                (1.365,-.100,.077,.178,.079), (1.393,-.025,.014,.170,.025)]
    def sec(z):
        z = max(sections[0][0], min(sections[-1][0], z))
        for a,b in zip(sections, sections[1:]):
            if a[0] <= z <= b[0]:
                t=(z-a[0])/(b[0]-a[0]); t=t*t*(3-2*t)
                return [a[i]*(1-t)+b[i]*t for i in range(1,5)]
        return sections[-1][1:]
    def shield(side,y,z,lift=0):
        front,rear,x,bulge=sec(z); cy=(front+rear)/2; ry=max(.022,(rear-front)/2)
        q=max(-1,min(1,(y-cy)/ry))
        return Vector((side*(x+bulge*math.sqrt(max(.01,1-q*q))+lift),y,z))
    def sheet(name, outline, sample, region='wing', role='armor', thickness=.0022):
        # Multiple inward rings make a rounded editable cage, without a flat fan.
        n=len(outline); vs=[];uv=[];fs=[]
        for scale in (1,.74,.42,.12):
            for u,v in outline:
                uu=u*scale; vv=.43+(v-.43)*scale
                vs.append(sample(uu,vv,.0007*(1-scale)));uv.append((uu+.5,1-vv))
        for ring in range(3):
            for i in range(n):
                j=(i+1)%n;fs.append((ring*n+i,ring*n+j,(ring+1)*n+j,(ring+1)*n+i))
        fs.append(tuple(range(3*n,4*n)))
        for u,v in outline:vs.append(sample(u,v,-thickness));uv.append((u+.5,1-v))
        fs.append(tuple(reversed(range(4*n,5*n))))
        for i in range(n):
            j=(i+1)%n;fs.append((i,4*n+i,4*n+j,j))
        ob=mesh(name,[tuple(v) for v in vs],fs,uv,region,role)
        # Recalculate only these new mesh normals, preserving all source data.
        import bmesh
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
        bevel=ob.modifiers.new('Thin rolled cut boundary','BEVEL');bevel.width=.00055;bevel.segments=2
        return ob
    cap=[(-.42,0),(.30,-.02),(.49,.20),(.50,.55),(.33,.87),(.02,.98),(-.29,.88),(-.48,.58),(-.49,.20)]
    broad=[(-.40,0),(.41,.025),(.50,.28),(.44,.64),(.22,.94),(-.03,1),(-.33,.84),(-.48,.45)]
    vane=[(-.36,0),(.40,.04),(.44,.30),(.27,.72),(.04,1),(-.16,.94),(-.39,.65),(-.45,.26)]
    chamfer=[(-.43,0),(.44,.02),(.48,.24),(.37,.79),(.09,.94),(-.29,.90),(-.49,.59),(-.49,.22)]
    for side in (-1,1):
        label='left' if side<0 else 'right'
        # Continuous dark local backing only within the short shield silhouette.
        vs=[];uv=[];fs=[]
        for j in range(29):
            z=.945+j*(.446/28); front,rear,_,_=sec(z)
            for i in range(25):
                y=front+(rear-front)*i/24;vs.append(tuple(shield(side,y,z,-.009)));uv.append((i/24,j/28))
        for j in range(28):
            for i in range(24):k=j*25+i;fs.append((k,k+1,k+26,k+25))
        mesh('CG supervised '+label+' compact shield recess',vs,fs,uv,role='inner')
        # Explicit broad construction courses. Different directions and shapes
        # control each part; short scapular caps are not long terminal feathers.
        courses=[(1.370,[-.041,.002,.043],.063,.062,'cap'),
                 (1.345,[-.097,-.046,.009,.061,.108],.069,.083,'cap'),
                 (1.300,[-.153,-.070,.015,.096],.100,.127,'broad'),
                 (1.244,[-.178,-.103,-.022,.062,.141],.106,.139,'broad'),
                 (1.184,[-.159,-.074,.012,.097,.181],.100,.143,'chamfer'),
                 (1.125,[-.106,-.023,.062,.143,.208],.092,.139,'vane'),
                 (1.069,[-.033,.048,.127,.200],.086,.118,'vane'),
                 (1.014,[.097,.169,.216],.079,.079,'vane')]
        forms={'cap':cap,'broad':broad,'vane':vane,'chamfer':chamfer}
        for row,(z,ys,width,length,kind) in reversed(list(enumerate(courses))):
            for col,y in enumerate(ys):
                # Fan changes sign across shoulder; rear tips sweep posteriorly.
                dy=(.010 if row<2 else .024+col*.008) if row!=3 else -.012+col*.012
                dz=-length*(.92+.065*math.sin(col*1.71+row))
                axis=Vector((dy,dz)); along=axis.normalized(); cross=Vector((-along.y,along.x))
                lift=.007+(7-row)*.0013
                def sample(u,v,e,y=y,z=z,axis=axis,cross=cross,width=width,lift=lift):
                    yy=y+v*axis.x+u*width*cross.x;zz=z+v*axis.y+u*width*cross.y
                    return shield(side,yy,zz,lift+e+.0014*math.sin(v*math.pi)*(1-(u/.52)**2))
                ob=sheet(f'CG supervised {label} {kind} {row:02d}-{col:02d}',forms[kind],sample)
                ob['shieldSide']=label;ob['plateCourse']=row;ob['constructionFamily']=kind
        # Local overlapping yokes bridge shield root toward upper breast.
        for j in range(5):
            y=-.150+j*.052;z=1.323-j*.005
            def sample(u,v,e,y=y,z=z):return shield(side,y+u*.074+v*.014,z-v*.067,.014+e)
            sheet(f'CG supervised {label} scapular yoke {j}',chamfer,sample)

    # Upper breast keeps the established body profile up to z1.20, then rolls
    # inward toward the shared CG2b neck-root at z1.30. No neck meshes are edited.
    breast=[(1.155,-.050,.239,.322),(1.205,-.067,.229,.287),
            (1.255,-.083,.192,.232),(1.300,-.105,.134,.158),
            (1.328,-.105,.095,.110)]
    def chest(a,z,lift=0):
        z=max(breast[0][0],min(breast[-1][0],z))
        for p,q in zip(breast,breast[1:]):
            if p[0]<=z<=q[0]:
                t=(z-p[0])/(q[0]-p[0]);cy,rx,ry=[p[i]*(1-t)+q[i]*t for i in range(1,4)];break
        return Vector(((rx+lift)*math.sin(a),cy-(ry+lift)*math.cos(a),z))
    # Broader transverse throat/breast scales with angular stepped lower ends.
    throat=[(-.50,0),(.50,0),(.50,.43),(.40,.83),(.12,.99),(-.12,.94),(-.42,.83),(-.50,.45)]
    for row,(z,length,n,width) in enumerate([(1.327,.072,3,.083),(1.288,.087,5,.092),(1.237,.092,6,.096)]):
        for col in range(n):
            a=-.84+1.68*col/(n-1)+(row%2)*.045
            rad=.16 if row==0 else .21 if row==1 else .26
            def sample(u,v,e,a=a,z=z,rad=rad,width=width,length=length,row=row):
                return chest(a+u*width/rad,z-v*length+u*.013,.007+(2-row)*.002+e)
            sheet(f'CG supervised breast throat course {row}-{col}',throat,sample,'body')
    return {'module':'cg-supervised-shoulder-body','era':era,'newMeshes':len(made),'retainedHidden':len(retired),
            'retiredNames':[o.name for o in retired],'constructionSections':sections,'copiedCompactPosterior':compacted,
            'sharedNeckRoot':[0,-.105,1.30],'changes':['Short rounded convex shield mass','Broad scapular caps, medium oblique plates and short posterior terminals','Flank below shield exposed','Upper breast rolls inward to shared throat junction'],
            'limits':['Hidden rear construction inferred','Existing regional material graphs carried forward unchanged','No head/neck/stance edits, engineering or owner acceptance claim']}


def diagnostic():
    parser=argparse.ArgumentParser();parser.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));parser.add_argument('--resolution',type=int,default=720);parser.add_argument('--attempt',default='attempt01')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root=Path(args.root);out=root/'assets/audit/cg-supervised-shoulder01'/args.attempt;out.mkdir(parents=True,exist_ok=True)
    source=root/'assets/models/cinematic-cg-milestone02b/murderbird-cg-2b-builder.blend'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); source_hash=sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
    protected={o.name: {'matrix':list(sum((list(row) for row in o.matrix_world),[])), 'vertices':hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest(),'visible':not o.hide_render} for o in s.objects if o.type=='MESH' and (o.get('cg2bRegion') in ('head','neck','leg','foot') or o.get('cg1cRegion') in ('head','neck','leg','foot'))}
    s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.device='CPU'
    s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
    receipt=json.loads((root/'assets/audit/cinematic-cg-milestone02b/construction01/receipt.json').read_text())
    cam=s.camera;cam.data.type='ORTHO'
    import importlib.util
    spec=importlib.util.spec_from_file_location('light',root/'scripts/cinematic-cg-2b-lighting.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    profile=mod.profiles()['neutral'];bg=s.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(*profile['world_color'][:3],1);bg.inputs[1].default_value=profile['world_strength']
    lights=[o for o in s.objects if o.type=='LIGHT']
    for o,p in zip(lights,profile['areas']):
        o.location=p['position'];o.rotation_euler=(Vector(p['target'])-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=p['power'];o.data.color=p['color'];o.data.size=p['size']
    def render(name,kind='canon-neutral'):
        p=receipt['cameras'][kind];cam.location=p['location'];cam.rotation_euler=p['rotation_euler'];cam.data.ortho_scale=p['ortho_scale'];cam.data.shift_x=p['shift_x'];cam.data.shift_y=p['shift_y']
        s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*p['resolution'][1]/p['resolution'][0]);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    render('before-canon');result=apply(s,root,'builder');render('after-canon');render('after-wholebird','legacy-neutral')
    unchanged=[]
    for name,p in protected.items():
        o=s.objects[name];current={'matrix':list(sum((list(row) for row in o.matrix_world),[])), 'vertices':hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest(),'visible':not o.hide_render};unchanged.append(p==current)
    result['protectedHeadNeckLegFoot']={'count':len(unchanged),'unchanged':all(unchanged)}
    result['inputSHA256']=source_hash;result['inputPreserved']=sha(source)==source_hash;result['reviewStatus']='Unaccepted visual proposal'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'shoulder-body-proposal.blend'))
    result['images']={p.name:sha(p) for p in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print('SHOULDER_CHECKPOINT',str(out))


if __name__=='__main__':diagnostic()
