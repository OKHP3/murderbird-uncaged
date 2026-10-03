"""Material-faithful, temporary CG2b browser export. Never edits native meshes."""
from collections import Counter
from pathlib import Path
import math

import bpy
import bmesh


def export(scene, filepath):
    """Export visible evaluated character geometry; return a compact receipt.

    Face assignments are read from the evaluated mesh, including material slots
    introduced by modifiers. A source object can contribute to several groups.
    All geometry, materials and resized images used here are temporary copies.
    """
    view_layer = bpy.context.view_layer
    depsgraph = bpy.context.evaluated_depsgraph_get()
    sources = [o for o in scene.objects if o.type == 'MESH'
               and not o.hide_render and not o.hide_viewport
               and not o.hide_get(view_layer=view_layer)
               and o.visible_get(view_layer=view_layer)
               and not o.get('authoringGuide')]
    if not sources:
        raise ValueError('No visible character meshes to export')
    selected = list(bpy.context.selected_objects)
    active = view_layer.objects.active
    collection = bpy.data.collections.new('CG2b temporary material export')
    scene.collection.children.link(collection)
    groups, materials, images, temporary_meshes = {}, {}, {}, []
    source_faces, split_faces, multi_material = Counter(), Counter(), []
    texture_sizes, glass_thickness = {}, {}
    uv_layers, uv_loops = 0, 0
    source_counts = (len(bpy.data.objects), len(bpy.data.meshes),
                     len(bpy.data.materials), len(bpy.data.images))

    def copy_material(source):
        if source in materials:
            return materials[source]
        if source is None:
            raise ValueError('Visible face has no assigned material')
        material = source.copy()
        material.name = 'CG2b browser ' + source.name
        materials[source] = material
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type != 'TEX_IMAGE' or node.image is None:
                    continue
                original = node.image
                if original not in images:
                    image = original.copy()
                    image.name = 'CG2b browser 1024 ' + original.name
                    images[original] = image
                    width, height = original.size
                    if width < 1 or height < 1:
                        raise ValueError('Unreadable texture: ' + original.name)
                    factor = min(1.0, 1024 / max(width, height))
                    size = (max(1, round(width * factor)), max(1, round(height * factor)))
                    if tuple(image.size) != size:
                        image.scale(*size)
                    image.file_format = 'PNG'
                    image.pack()
                    texture_sizes[original.name] = list(size)
                node.image = images[original]
        return material

    try:
        for source in sources:
            evaluated = source.evaluated_get(depsgraph)
            mesh = bpy.data.meshes.new_from_object(
                evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
            temporary_meshes.append(mesh)
            assigned = Counter(p.material_index for p in mesh.polygons)
            if len(assigned) > 1:
                multi_material.append(source.name)
            # The active render UV has a common name for joining. Retain every
            # original UV layer, so explicit UV Map nodes still resolve by name.
            render_uv = next((u for u in mesh.uv_layers if u.active_render), mesh.uv_layers.active)
            if render_uv is not None:
                canonical = mesh.uv_layers.get('cg2b-export-uv')
                if canonical is None:
                    canonical = mesh.uv_layers.new(name='cg2b-export-uv')
                for old, new in zip(render_uv.data, canonical.data):
                    new.uv = old.uv
                canonical.active_render = True
                mesh.uv_layers.active = canonical
                uv_layers += len(mesh.uv_layers)
                uv_loops += len(mesh.loops)
            for index, count in assigned.items():
                source_material = mesh.materials[index] if index < len(mesh.materials) else None
                material = copy_material(source_material)
                source_faces[source_material.name] += count
                split = mesh.copy()
                temporary_meshes.append(split)
                bm = bmesh.new()
                try:
                    bm.from_mesh(split)
                    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index != index], context='FACES')
                    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
                    bm.to_mesh(split)
                finally:
                    bm.free()
                split.materials.clear()
                split.materials.append(material)
                for polygon in split.polygons:
                    polygon.material_index = 0
                split.update()
                split_faces[source_material.name] += len(split.polygons)
                obj = bpy.data.objects.new('CG2b export ' + source.name, split)
                collection.objects.link(obj)
                obj.matrix_world = evaluated.matrix_world.copy()
                groups.setdefault(source_material, []).append(obj)
                node = material.node_tree.nodes.get('Principled BSDF') if material.use_nodes else None
                transmission = node.inputs.get('Transmission Weight') if node else None
                if transmission is not None and transmission.default_value > 0 and split.vertices:
                    # Physical lens depth in authored units; independent of its
                    # camera orientation and of the spacing between both eyes.
                    extents = [max(v.co[i] for v in split.vertices) - min(v.co[i] for v in split.vertices) for i in range(3)]
                    depths = [extents[i] * evaluated.matrix_world.to_3x3().col[i].length for i in range(3)]
                    depth = min(d for d in depths if d > 1e-9)
                    glass_thickness.setdefault(source_material.name, []).append(depth)
                    material['cg2bGlassThickness'] = min(glass_thickness[source_material.name])
            bpy.data.meshes.remove(mesh)

        if source_faces != split_faces:
            raise AssertionError('Evaluated face assignments changed during material split')
        merged = []
        for material, objects in groups.items():
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects:
                obj.select_set(True)
            view_layer.objects.active = objects[0]
            if len(objects) > 1:
                bpy.ops.object.join()
            obj = view_layer.objects.active
            obj.name = 'CG2b ' + material.name
            merged.append(obj)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in merged:
            obj.select_set(True)
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(
            filepath=str(filepath), export_format='GLB', use_selection=True,
            export_extras=True, export_apply=False, export_materials='EXPORT',
            export_image_format='AUTO', export_texcoords=True, export_normals=True)
        receipt = {
            'visible_meshes': len(sources), 'mesh_groups': len(merged),
            'material_groups': [m.name for m in groups],
            'material_face_counts': dict(source_faces),
            'split_face_counts': dict(split_faces),
            'multi_material_meshes': multi_material,
            'texture_resolution': 1024, 'embedded_texture_sizes': texture_sizes,
            'uv_layers_copied': uv_layers, 'uv_loops_copied': uv_loops,
            'preserved_optic_materials': [m.name for m in groups if m.get('cg2aPreserveMaterial')],
            'glass_thickness': {name: min(values) for name, values in glass_thickness.items()},
            'method': 'Evaluated temporary geometry split by face material, joined per material; original UV layers and world transforms retained; copied embedded maps capped at 1024px',
            'native_source_unchanged': True,
        }
    finally:
        # Also runs when split/join/export raises. Removed join-input meshes can
        # remain as orphan datablocks, so track their identities explicitly.
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)
        for mesh in temporary_meshes:
            try:
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            except ReferenceError:
                pass
        for material in materials.values():
            bpy.data.materials.remove(material, do_unlink=True)
        for image in images.values():
            bpy.data.images.remove(image, do_unlink=True)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            if obj.name in view_layer.objects:
                obj.select_set(True)
        view_layer.objects.active = active
    after_counts = (len(bpy.data.objects), len(bpy.data.meshes),
                    len(bpy.data.materials), len(bpy.data.images))
    receipt['temporary_datablocks_removed'] = source_counts == after_counts
    if not receipt['temporary_datablocks_removed']:
        raise AssertionError('Temporary export datablocks remain')
    return receipt
