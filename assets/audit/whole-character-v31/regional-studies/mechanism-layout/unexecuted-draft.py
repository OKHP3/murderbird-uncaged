"""Fresh V31 complete runtime layout, changing only cervical receiver placements.
All existing measured Maker overrides and default apparatus placements remain.
No historical priorV21 layout activation, geometry or runtime changes.
"""
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
DEFAULT_CONTROLS={'leg':[.065,.015,.045],'wing':[-.095,-.10,.10],'tail':[-.07,0,-.16],'neck':[-.16,.06,.02],'jaw':[-.18,-.06,.20]}
def gltf(p):return [p.x,p.z,-p.y]
def receiver(owner,name,desired):
    o=bpy.data.objects[name];assert o.parent==owner and o.get('surfaceRole')=='frame'
    assert set(o.get('exteriorEras','').split(','))=={'maker','mechanic','builder'}
    assert o.get('constructionClass') in {'inherited-passive','proposed-passive'}
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
    points=[ev.matrix_world@v.co for v in m.vertices];triangles=[tuple(t.vertices) for t in m.loop_triangles]
    p,n,i,d=BVHTree.FromPolygons(points,triangles,all_triangles=True).find_nearest(desired)
    assert p is not None and all(math.isfinite(v) for v in p)
    local=owner.matrix_world.inverted()@p;ids=triangles[i]
    record={'owner':owner.name,'surfaceObject':name,'nativeWorld':list(p),'nativeOwnerLocal':list(local),'gltfOwnerLocal':gltf(local),'desiredNativeWorld':list(desired),'triangleIndex':i,'triangleVertexIds':list(ids),'triangleNativeWorld':[list(points[k]) for k in ids],'surfaceNormalNativeWorld':list(n),'searchPointDistanceM':d}
    ev.to_mesh_clear();return p,record

def apply():
    bpy.context.view_layer.update();body=bpy.data.objects['body'];neck=bpy.data.objects['neck'];mid=bpy.data.objects['cervical-mid-a']
    controls={k:list(v) for k,v in DEFAULT_CONTROLS.items()};override=[]
    for key,name in [('wing','right-mantle'),('jaw','jaw')]:
        raw=bpy.data.objects[name].get('makerControlSocketV1');assert raw is not None,'Run new head and wing socket modules first'
        socket=json.loads(raw) if isinstance(raw,str) else dict(raw)
        assert socket['schema']==1 and socket['coordinateSpace']=='gltf-node-local'
        controls[key]=list(socket['point']);override.append({'control':key,'owner':name,'point':controls[key],'surfaceObject':socket['surfaceObject']})
    rows=[];proof=[]
    for sign,side in [(1,'left'),(-1,'right')]:
        fork=bpy.data.objects[f'V23 root load fork {sign}'];ev=fork.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();assert len(m.vertices)==48
        # Existing elbow in the passive root fork carries the body-side eye.
        # Centre is evaluated middle ring; choose its outward finite wall.
        centre=sum((ev.matrix_world@m.vertices[k].co for k in range(16,32)),Vector())/16
        ev.to_mesh_clear();bodyDesired=centre+Vector((sign*.013,0,0))
        # Moving-side eye remains on the first neck owner, 72% along its
        # actual load span, rather than the old offset beside cervical link3.
        a=neck.matrix_world.translation.copy();b=mid.matrix_world.translation.copy();a.x=b.x=sign*.053
        neckDesired=a.lerp(b,.72)+Vector((sign*.0105,0,0))
        bp,br=receiver(body,fork.name,bodyDesired);np,nr=receiver(neck,f'V23 cervical 1 load link {sign}',neckDesired)
        neckLever=math.hypot(*(neck.matrix_world.inverted()@np)[1:]);span=(np-bp).length
        assert neckLever>.035 and .09<span<.22
        rows.append({'side':side,'bodyPoint':br['gltfOwnerLocal'],'neckPoint':nr['gltfOwnerLocal']})
        proof.append({'side':side,'bodyReceiver':br,'neckReceiver':nr,'restEndpointDistanceM':span,'firstNeckPitchLeverArmM':neckLever,'construction':'Existing root-fork elbow wall and first-link outer wall carry a proposed local actuator clevis/clamp interface. No new lug, weld or fastening geometry is claimed.'})
    layout={'version':1,'status':'Fresh V31 reconstructed receiving-point proposal; no engineering or continuous-clearance acceptance','coordinateSpace':'glTF owner-local metres; no object scale applied to runtime mechanisms','makerControlOffsets':controls,'tailPosition':[0,.20,-.31],'distributionPosition':[-.21,.29,.07],'transmissionPosition':[0,0,0],'makerCradleWidth':.56,'cervical':rows,'source':'V31 actual evaluated passive root fork / first neck load member; priorV21 layout is historical only','limits':['Receiving centres lie on actual finite passive load members; mounting clevises/clamps and load capacity remain proposals.','No change to Maker points, tail, gearbox or distribution placement; no wholesale apparatus refit.','No canopy/body guard collision or continuous actuator swept-clearance claim.']}
    body['mechanismLayoutV1']=json.dumps(layout,separators=(',',':'))
    return {'region':'runtime-mechanism-layout','status':'Metadata-only fresh cervical receiving-layout reconstruction','changedNodes':['body'],'changedProperties':['body.mechanismLayoutV1'],'changedMeshes':[],'added':[],'removed':[],'layout':layout,'receivingProof':proof,'preservedMakerOwnerOverrides':override,'allOtherLayoutPlacements':'Exact current runtime defaults, not restored historical placements','priorV21MetadataReadOrActivated':False,'limits':layout['limits']}
