"""One sampled-sweep edge relief for the V15 cranial-cover/brow interface.

Subtracts the actual evaluated fixed brow/mount solids at the checker offsets
from only the crown meshes that cross those solids. This is a discrete fitted
relief proposal, not a continuous collision guarantee or accepted design.
"""
import bpy
from mathutils import Vector

OFFSETS = (0.0, .02, .04, .06)
TARGETS = {
    'Continuous temporal shell -1': ('Forged orbital mounting plate -1',),
    'Continuous temporal shell 1': ('Forged orbital mounting plate 1',),
    'Rounded swept crown lamina 0': ('Forged orbital brow -1', 'Forged orbital brow 1'),
    'Swept temporal lamina -1 0 0': ('Forged orbital brow -1', 'Forged orbital mounting plate -1'),
    'Swept temporal lamina 1 0 0': ('Forged orbital brow 1', 'Forged orbital mounting plate 1'),
}


def _world_cutter(source, dz, label):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = source.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        matrix = evaluated.matrix_world.copy()
        vertices = [matrix @ v.co + Vector((0.0, 0.0, -dz)) for v in mesh.vertices]
        faces = [tuple(p.vertices) for p in mesh.polygons]
    finally:
        evaluated.to_mesh_clear()
    cutter_mesh = bpy.data.meshes.new(f'.crown-clearance-cutter-mesh-{label}')
    cutter_mesh.from_pydata(vertices, [], faces)
    cutter_mesh.update()
    cutter = bpy.data.objects.new(f'.crown-clearance-cutter-{label}', cutter_mesh)
    bpy.context.scene.collection.objects.link(cutter)
    cutter.matrix_world.identity()
    return cutter


def apply():
    """Apply one actual-target sampled sweep to the five reported crown meshes."""
    created = []
    operations = []
    for moving_name, target_names in TARGETS.items():
        moving = bpy.data.objects.get(moving_name)
        assert moving and moving.type == 'MESH' and moving.parent and moving.parent.name == 'cranial-cover', moving_name
        for target_name in target_names:
            target = bpy.data.objects.get(target_name)
            assert target and target.type == 'MESH' and target.parent, target_name
            for dz in OFFSETS:
                cutter = _world_cutter(target, dz, f'{len(created):03d}')
                created.append(cutter)
                mod = moving.modifiers.new(name=f'.crown-clearance-{len(operations):03d}', type='BOOLEAN')
                mod.operation = 'DIFFERENCE'
                mod.solver = 'EXACT'
                mod.object = cutter
                bpy.context.view_layer.objects.active = moving
                moving.select_set(True)
                bpy.ops.object.modifier_apply(modifier=mod.name)
                moving.select_set(False)
                operations.append({'movingMesh': moving_name, 'fixedTarget': target_name,
                                   'inverseLiftM': dz, 'solver': 'EXACT',
                                   'resultVertices': len(moving.data.vertices),
                                   'resultPolygons': len(moving.data.polygons)})
                assert moving.data.vertices and moving.data.polygons, f'Boolean emptied {moving_name} against {target_name} at {dz}'
    for cutter in created:
        mesh = cutter.data
        bpy.data.objects.remove(cutter, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    bpy.context.view_layer.update()
    return {
        'region': 'crown-clearance',
        'changedMeshes': sorted(TARGETS),
        'newMeshes': [],
        'method': 'sequential exact differences against evaluated brow/mount solids shifted by the inverse of discrete cranial-cover lifts 0, 0.02, 0.04, and 0.06 m',
        'sampledOffsetsM': list(OFFSETS),
        'operations': operations,
        'fixed': ['brows', 'orbital mounts', 'optic assemblies', 'jaw', 'all pivots', 'all curves'],
        'limits': ['The relief is a finite sampled sweep, not a continuous Minkowski sweep.',
                   'Only the named crossing crown pieces are edited; other crown components may retain contacts.',
                   'Boolean success and sampled clearance do not establish artistic or owner acceptance.'],
    }
