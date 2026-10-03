"""Small armor crown relief on the accepted posed character; edges stay fixed."""
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    changed=vertices=0;largest=0.0;skipped=[]
    for obj in list(scene.objects):
        region=obj.get('cg1cRegion')
        if region not in ('body','wing') or obj.get('surfaceRole')!='plate' or obj.type!='MESH' or obj.get('cg3ArmorCrown'):continue
        mesh=obj.data
        # 1C plates are nine-point outlines, nine-point curved inner rings,
        # one crown vertex and nine underside points. Work from actual posed
        # coordinates and face normals; no old anchors or global resizing.
        if len(mesh.vertices)!=28 or len(mesh.polygons)!=27:
            skipped.append(obj.name);continue
        normal=Vector()
        for i,face in enumerate(mesh.polygons):
            if i%3!=2:normal+=face.normal*face.area
        if normal.length<1e-8:
            skipped.append(obj.name);continue
        normal.normalize()
        world_normal=(obj.matrix_world.to_3x3().inverted().transposed()@normal).normalized()
        inverse=obj.matrix_world.inverted()
        # Boundary and underside stay fixed, maintaining the approved outer
        # silhouette/root attachments. Interior relief adds overlap shadows.
        peak=.0030 if region=='wing' else .0025
        for idx in range(9,19):
            v=mesh.vertices[idx];world=obj.matrix_world@v.co
            amount=peak if idx==18 else peak*.68
            v.co=inverse@(world+world_normal*amount)
            largest=max(largest,amount);vertices+=1
        mesh.update();obj['cg3ArmorCrown']=True;obj['cg3CrownPeak']=peak;changed+=1
    return {'module':'cg3-body-crown','platesChanged':changed,'verticesChanged':vertices,'maximumDisplacement':largest,'skippedUnexpectedTopology':skipped,'change':'Lift existing curved crown rings and centres outward along current posed face normals; preserve boundaries, backing, rolled edges, fasteners, UVs and materials','limits':'Local relief only; no new shells or global silhouette/pose change. Integrated lighting review required to establish stronger layering.'}
