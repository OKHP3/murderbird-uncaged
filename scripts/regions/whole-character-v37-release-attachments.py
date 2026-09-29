"""Seat the inherited Maker wing control on the existing V37 load member.

No mesh or pivot change. Point derived from the actual release01 GLB triangle
surface in right-mantle local space; full integration verifies release02.
"""
import bpy,json

def apply():
    owner=bpy.data.objects['right-mantle']
    old=owner['makerControlSocketV1']
    data=json.loads(old) if isinstance(old,str) else dict(old)
    assert data['surfaceObject']=='right swept upper wing load member'
    assert data['coordinateSpace']=='gltf-node-local'
    data['point']=[-0.08643899773165903,-0.20761706436182026,-0.03922407128577299]
    owner['makerControlSocketV1']=json.dumps(data)
    return {'region':'V37 release control attachment','changedMeshes':[],'addedMeshes':[],'removedMeshes':[],'changedNodes':['right-mantle'],'changedFootMeshes':[],'changedCurves':[],'socket':data,'status':'Existing surface seating only; no geometry, pivot or material change'}
