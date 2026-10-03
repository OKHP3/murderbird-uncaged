"""Render a NEW rounded-form proposal; never edits the detailed MurderBird asset.

Run with Blender --background --python scripts/build-basic-shape-study.py
All coordinates and cameras are saved for later owner corrections and overlays.
"""
import bpy
import math
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audit/basic-shape-study01'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.engine = 'BLENDER_WORKBENCH'
s.render.resolution_x = s.render.resolution_y = 384
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.film_transparent = False
s.display.shading.light = 'STUDIO'
s.display.shading.studiolight_rotate_z = .4
s.display.shading.color_type = 'MATERIAL'
s.display.shading.show_shadows = False
s.display.shading.show_cavity = False
s.display.shading.show_specular_highlight = False
s.display.shading.show_object_outline = True
s.display.shading.object_outline_color = (.045, .06, .075)
s.display.shading.background_type = 'WORLD'
s.world = bpy.data.worlds.new('Study background')
s.world.color = (.93, .94, .95)
s.view_settings.view_transform = 'Standard'
bpy.context.preferences.filepaths.save_version = 0

COLORS = {'head':(.77,.47,.25,1), 'neck':(.78,.65,.35,1),
          'torso':(.28,.58,.54,1), 'legs':(.32,.48,.70,1)}
materials = {}
for part, color in COLORS.items():
    m = bpy.data.materials.new(part)
    m.diffuse_color = color
    materials[part] = m
shapes = []

def tag(o, part, spec):
    o.data.materials.append(materials[part])
    o['study_part'] = part
    o['status'] = 'proposal awaiting owner shape notes'
    shapes.append(dict(name=o.name, part=part, **spec))
    return o

def ellipsoid(name, part, center, radius, tilt=0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1,
                                       location=center)
    o = bpy.context.object
    o.name = name
    o.scale = radius
    o.rotation_euler.x = tilt
    return tag(o, part, dict(type='rounded-polygon', center=center,
                            radius=radius, tilt_x=tilt))

def capsule(name, part, a, b, radius):
    a,b = Vector(a),Vector(b)
    o = ellipsoid(name, part, tuple((a+b)/2),
                  (radius, radius, (b-a).length/2+radius))
    o.rotation_mode='QUATERNION'
    o.rotation_quaternion=(b-a).to_track_quat('Z','Y')
    shapes[-1] = dict(name=name, part=part, type='rounded-segment',
                      start=list(a), end=list(b), radius=radius)
    return o

# Coordinates: Z up, negative Y toward beak; units are visual study units.
# These are artist estimates from the locked canon, not anatomical measurements.
profile=[(.59,.11,.025,.04),(.65,.12,.13,.20),(.74,.11,.205,.29),
         (.84,.065,.25,.335),(.96,.015,.275,.345),
         (1.08,-.025,.26,.325),(1.20,-.06,.22,.275),
         (1.31,-.085,.145,.19),(1.39,-.09,.025,.035)]
tv=[]
for z,y,rx,ry in profile:
    for i in range(16):
        a=i*math.tau/16;tv.append((rx*math.cos(a),y+ry*math.sin(a),z))
tf=[tuple(reversed(range(16)))]
for j in range(len(profile)-1):
    for i in range(16):
        tf.append((j*16+i,j*16+(i+1)%16,(j+1)*16+(i+1)%16,(j+1)*16+i))
tf.append(tuple(range((len(profile)-1)*16,len(profile)*16)))
td=bpy.data.meshes.new('Continuous pear torso cage');td.from_pydata(tv,[],tf);td.update()
to=bpy.data.objects.new('T01 continuous torso and compact rear',td);s.collection.objects.link(to)
tag(to,'torso',dict(type='continuous-rounded-torso',sections=profile))
ellipsoid('H01 head and swept crown mass', 'head', (0,-.21,1.615), (.185,.25,.195))

# One continuous hooked bill mesh; intentionally no plating, eye or machinery.
sections=[(-.39,1.635,.105,.105),(-.49,1.59,.083,.102),
          (-.565,1.515,.058,.087),(-.59,1.425,.032,.054),
          (-.575,1.365,.006,.012)]
verts=[]
for y,z,rx,rz in sections:
    for i in range(8):
        a=i*math.tau/8
        verts.append((rx*math.cos(a),y,z+rz*math.sin(a)))
faces=[tuple(reversed(range(8)))]
for j in range(len(sections)-1):
    for i in range(8):
        faces.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
faces.append(tuple(range((len(sections)-1)*8,len(sections)*8)))
d=bpy.data.meshes.new('Hooked bill polygon cage')
d.from_pydata(verts,[],faces);d.update()
o=bpy.data.objects.new('H03 hooked bill',d);s.collection.objects.link(o)
bevel=o.modifiers.new('Small rounded edges','BEVEL');bevel.width=.012;bevel.segments=2
tag(o,'head',dict(type='hooked-bill-cage',sections=sections))

capsule('N01 shoulder neck', 'neck', (0,-.105,1.30),(0,-.15,1.425),.115)
capsule('N02 head neck', 'neck', (0,-.15,1.425),(0,-.23,1.495),.11)
for sign, side in [(-1,'left'),(1,'right')]:
    hip=(sign*.165,.105,.865)
    knee=(sign*.177,-.09,.61)
    hock=(sign*.185,.105,.285)
    ankle=(sign*.188,.015,.105)
    capsule('L '+side+' upper thigh','legs',hip,knee,.075)
    capsule('L '+side+' shank','legs',knee,hock,.051)
    capsule('L '+side+' lower segment','legs',hock,ankle,.04)
    for name,point,r in [('hip',hip,.081),('knee',knee,.060),('hock',hock,.051)]:
        ellipsoid('L '+side+' '+name,'legs',point,(r,r,r))
    ellipsoid('L '+side+' foot pad','legs',(sign*.188,-.045,.065),(.072,.12,.04))
    for i,dx in enumerate([-.066,0,.066]):
        capsule('L '+side+' forward toe '+str(i+1),'legs',
                (sign*.188+dx*.3,-.065,.06),
                (sign*.188+dx,-.225+(abs(dx)*.4),.036),.023)
    capsule('L '+side+' rear toe','legs',
            (sign*.188,.02,.058),(sign*.188,.13,.034),.022)

cdata=bpy.data.cameras.new('Orthographic study camera');cdata.type='ORTHO'
cam=bpy.data.objects.new('Orthographic study camera',cdata)
s.collection.objects.link(cam);s.camera=cam
VIEWS={'front':(0,-6,0),'top':(0,0,6),'side':(-6,0,0),'rear':(0,6,0)}
# Each part uses one scale across all four views. Part rows have different scales.
GROUPS={'assembled':((0,-.04,.92),2.08),
        'head':((0,-.28,1.60),.86),'neck':((0,-.155,1.40),.49),
        'torso':((0,.04,1.00),.94),'legs':((0,-.02,.48),1.13)}
receipt={'status':'new proposed blockout, not extracted from or applied to detailed model',
         'authority':'locked Sept22 composite, owner shape review pending',
         'reference':'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg',
         'reference_sha256':'645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114',
         'axes':{'up':'+Z','forward':'-Y','left_right':'X'},
         'shapes':shapes,'groups':GROUPS,'views':VIEWS,
         'render_resolution':[384,384],
         'limitations':['Hidden surfaces are inferred proposals.',
                       'Simplified anatomy is visual guidance, not balance validation.',
                       'No shield wings, plates, materials or machinery in this scope.',
                       'Part rows magnified independently; compare sizes in assembled row.',
                       'Overlay and detailed-model edits wait for owner notes.']}
objects=[o for o in s.objects if o.type=='MESH']
for group,(center,scale) in GROUPS.items():
    for o in objects:
        o.hide_render = group!='assembled' and o['study_part']!=group
    target=Vector(center);cdata.ortho_scale=scale
    for view,offset in VIEWS.items():
        cam.location=target+Vector(offset)
        direction=target-cam.location
        if view=='top':
            # Image top is forward (-Y), same orientation in all top projections.
            cam.rotation_euler=(0,0,math.pi)
        else:
            cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
        s.render.filepath=str(OUT/(group+'-'+view+'.png'))
        bpy.ops.render.render(write_still=True)
for o in objects:o.hide_render=False
cam.location=Vector(GROUPS['assembled'][0])+Vector(VIEWS['side'])
cam.rotation_euler=(Vector(GROUPS['assembled'][0])-cam.location).to_track_quat('-Z','Y').to_euler()
cdata.ortho_scale=GROUPS['assembled'][1]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'murderbird-basic-shapes.blend'))
(OUT/'study.json').write_text(json.dumps(receipt,indent=2)+'\n')
