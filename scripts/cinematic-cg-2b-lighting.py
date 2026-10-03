"""Original 2b lighting/stage proposal. Character assets and exposure are untouched.

Use identical returned parameters for before/candidate. Neutral deliberately
retains the inherited diagnostic rig. Ground is an authoring guide, never GLB.
"""


def profiles():
    def area(position, target, power, color, size):
        return dict(position=position, target=target, power=power,
                    color=color, size=size)
    return {
        'neutral': dict(world_color=(.08, .08, .08), world_strength=.4, areas=[
            area((-3, -4, 5), (0, 0, 1), 700, (1, 1, 1), 4),
            area((4, -1, 3), (0, 0, 1), 250, (1, 1, 1), 4),
            area((0, 4, 4), (0, 0, 1), 500, (1, 1, 1), 3)]),
        'workshop': dict(world_color=(.08, .08, .08), world_strength=.08, areas=[
            area((-3, -4, 5), (0, 0, 1), 450, (1, .82, .65), 4),
            area((4, -1, 3), (0, 0, 1), 65, (.62, .74, .85), 4),
            area((0, 4, 4), (0, 0, 1), 150, (1, .7, .45), 3)]),
        'cinematic': dict(world_color=(.075, .080, .086), world_strength=.065, areas=[
            area((-3, -3.0, 4.2), (0, -.05, 1.05), 650, (1, .84, .69), 2.7),
            area((-3.5, .3, 1.8), (0, .0, .85), 180, (.70, .79, .90), 3.0),
            area((2, 2.5, 4), (0, .08, 1.1), 400, (1, .77, .57), 2.3)])
    }


def camera_profile():
    return dict(
        canon_scale_multiplier=1.08,
        hero=dict(position=(-3.0, -3.9, 1.32), target=(0, -.04, .99), lens=65),
        profile=dict(position=(-4.35, -1.875, 1.31), target=(0, -.01, .99), lens=65))


def stage(scene, min_z):
    """Create only original low-contrast procedural ground at shared foot datum."""
    import bpy
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, min_z - .0005))
    ground = bpy.context.object
    ground.name = 'CG2b procedural ground proposal'
    ground['authoringGuide'] = True
    ground['source'] = 'Original procedural CG proposal; no reference pixels or HDRI'
    floor = bpy.data.materials.new('CG2b procedural dark workshop ground')
    floor.use_nodes = True
    nodes, links = floor.node_tree.nodes, floor.node_tree.links
    bs = nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value = .92
    bs.inputs['Specular IOR Level'].default_value = .2
    coords = nodes.new('ShaderNodeTexCoord')
    broad = nodes.new('ShaderNodeTexNoise')
    broad.inputs['Scale'].default_value = 1.7
    broad.inputs['Detail'].default_value = 3
    links.new(coords.outputs['Object'], broad.inputs['Vector'])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .15
    ramp.color_ramp.elements[0].color = (.012, .014, .013, 1)
    ramp.color_ramp.elements[1].position = .85
    ramp.color_ramp.elements[1].color = (.030, .026, .021, 1)
    links.new(broad.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    grain = nodes.new('ShaderNodeTexNoise')
    grain.inputs['Scale'].default_value = 135
    grain.inputs['Detail'].default_value = 2
    links.new(coords.outputs['Object'], grain.inputs['Vector'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .2
    bump.inputs['Distance'].default_value = .0015
    links.new(grain.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    ground.data.materials.append(floor)
    return ground
