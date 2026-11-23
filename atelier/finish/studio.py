"""Studio lighting and camera for the native review edition."""
import math
import bpy
from mathutils import Vector

def studio():
    scene=bpy.context.scene
    world=bpy.data.worlds.new('Foundry · overcast')
    scene.world=world; world.use_nodes=True
    bg=world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value=(.22,.25,.25,1)
    bg.inputs['Strength'].default_value=.42
    def area(name, pos, target, power, color, sz, sz_y=None):
        data=bpy.data.lights.new(name,'AREA')
        data.energy=power
        data.shape='RECTANGLE'; data.size=sz; data.size_y=sz if sz_y is None else sz_y
        data.color=color
        ob=bpy.data.objects.new(name,data)
        scene.collection.objects.link(ob)
        ob.location=pos
        ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    area('High north window',(-2,-2.4,3.6),(0,-.08,.91),260,(1,.89,.71),2.1,2.8)
    area('Cool overhead rake',(-2.1,1.3,2.6),(0,0,1.08),170,(.77,.85,1),1.7,2.8)
    area('Brass edge light',(1.4,.94,3.),(0,0,1.15),270,(1,.73,.5),1.55,.78)
    area('Low reflected strip',(.15,-2.7,1.0),(0,-.03,.8),65,(.88,.93,1),2,.57)
    floor_mesh=bpy.data.meshes.new('Native ground')
    # A seamless curved sweep avoids the hard horizon of a finite plane.
    turns=96
    cross=[(3.8,-.001),(4.8,-.001),(5.15,.055),(5.45,.19),(5.72,.46),
           (5.92,.83),(6.03,1.25),(6.07,1.76),(6.08,4.0),(6.08,8.0)]
    verts=[(0,0,-.001)]
    faces=[]
    for j,(r,z) in enumerate(cross):
        for i in range(turns):
            a=2*math.pi*i/turns
            verts.append((r*math.cos(a),r*math.sin(a),z))
            a0=1+j*turns+i; a1=1+j*turns+(i+1)%turns
            faces.append((0,a0,a1) if j==0 else (a0-turns,a0,a1,a1-turns))
    floor_mesh.from_pydata(verts,[],faces)
    for f in floor_mesh.polygons: f.use_smooth=True
    plane=bpy.data.objects.new('Studio floor • native staging',floor_mesh); scene.collection.objects.link(plane)
    mat=bpy.data.materials.new('Studio • charcoal earth');mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bs=nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.05,.043,.033,1);bs.inputs['Roughness'].default_value=.80
    tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=6.
    coords=nodes.new('ShaderNodeTexCoord');links.new(coords.outputs['Object'],tex.inputs['Vector'])
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.029,.025,.022,1)
    ramp.color_ramp.elements[1].color=(.074,.063,.050,1);links.new(tex.outputs['Fac'],ramp.inputs[0])
    links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    plane.data.materials.append(mat)
    camdata=bpy.data.cameras.new('First Choice review lens')
    cam=bpy.data.objects.new('First Choice · camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
    cam.location=(-3.68,-1.92,1.74)
    target=Vector((0,-.13,.97))
    direction=target-cam.location
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    camdata.lens=44;camdata.sensor_fit='VERTICAL'
    scene.render.resolution_x=1380;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    scene.render.engine='CYCLES'
    scene.cycles.samples=32;scene.cycles.use_denoising=True
    prefs=bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type='METAL'; prefs.get_devices()
        for d in prefs.devices: d.use=d.type=='METAL'
        if any(d.use for d in prefs.devices): scene.cycles.device='GPU'
    except (RuntimeError,TypeError): pass
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=0
    scene.render.film_transparent=False
    scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=94
    scene.use_nodes=False
    for scr in bpy.data.screens:
        for a in scr.areas:
            if a.type=='VIEW_3D':
                a.spaces.active.region_3d.view_perspective='CAMERA'
                a.spaces.active.region_3d.view_distance=3
                a.spaces.active.overlay.show_overlays=False
    return plane,cam
