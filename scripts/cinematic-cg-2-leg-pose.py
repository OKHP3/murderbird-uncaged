"""Owner-requested visual stance correction; rigid hinges and planted feet."""
from pathlib import Path
import json
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    p=Path(scaffold_path) if scaffold_path else Path(__file__).resolve().parents[1]/'assets/audit/basic-shape-study05/study.json'
    if p.suffix=='.blend':p=p.with_name('study.json')
    shapes=json.loads(p.read_text())['shapes'];count=0;report={}
    for side,sign in [('left',-1),('right',1)]:
        parts={q['name'].split(side+' ')[1]:q for q in shapes if q['part']=='legs' and 'L '+side+' ' in q['name']}
        old={label:Vector(parts[label]['center']) for label in ('hip','knee','hock')};old['ankle']=Vector(parts['lower segment']['end'])
        new={'hip':old['hip'].copy(),'knee':Vector((sign*.167,.01,old['knee'].z)),'hock':Vector((sign*.175,.075,old['hock'].z)),'ankle':old['ankle']+Vector((sign*.030,0,0))}
        transforms={}
        for label,a,b in [('upper','hip','knee'),('shank','knee','hock'),('tarsus','hock','ankle')]:
            source=old[b]-old[a];target=new[b]-new[a];rotation=source.rotation_difference(target)
            transforms[label]=(old[a],new[a],source.normalized(),rotation,target.length/source.length)
        report[side]={label:{'oldLength':(old[b]-old[a]).length,'newLength':(new[b]-new[a]).length} for label,a,b in [('upper','hip','knee'),('shank','knee','hock'),('tarsus','hock','ankle')]}
        for obj in list(scene.objects):
            region=obj.get('cg1cRegion');name=obj.name.lower()
            if region not in ('leg','foot') or side not in name or obj.type!='MESH' or obj.get('cg2OwnerPosture'):continue
            inv=obj.matrix_world.inverted()
            if region=='foot':
                delta=Vector((sign*.030,0,0));mapping=lambda v: v+delta
            else:
                joint=next((j for j in ('hip','knee','hock','ankle') if ' '+j+' ' in name),None)
                segment='upper' if ('upper' in name or 'thigh' in name) else 'shank' if 'shank' in name else 'tarsus'
                if joint:
                    delta=new[joint]-old[joint];mapping=lambda v: v+delta
                else:
                    origin,target,axis,rotation,scale=transforms[segment]
                    if 'collar' in name:
                        # Move each ring centre along the new axis, rotate rigidly.
                        coords=[obj.matrix_world@v.co for v in obj.data.vertices];centre=sum(coords,Vector())/len(coords);t=(centre-origin).dot(axis)
                        relocated=target+rotation@(centre-origin+axis*t*(scale-1))
                        mapping=lambda v: relocated+rotation@(v-centre)
                    else:
                        # Length changes are confined to segment direction; radial section retained.
                        mapping=lambda v: target+rotation@(v-origin+axis*((v-origin).dot(axis)*(scale-1)))
            for vertex in obj.data.vertices:vertex.co=inv@mapping(obj.matrix_world@vertex.co)
            obj.data.update();obj['cg2OwnerPosture']=True;count+=1
    return {'module':'cg2-owner-leg-pose','objectsChanged':count,'segmentLengths':report,'footShiftOutward':.03,'feetVerticalShift':0,'targetAnchors':{'hip':[.165,.105,.865],'knee':[.167,.01,.59],'hock':[.175,.075,.285]},'limits':'Visual stance deformation with rigid hinge translations; segment lengths intentionally change, no IK or mechanical validation. Source study hips remain fixed at .165; target angles/positions are integrator proposals from the locked image.'}
