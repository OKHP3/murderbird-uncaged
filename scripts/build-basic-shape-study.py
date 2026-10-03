"""Render a NEW rounded-form proposal; never edits the detailed MurderBird asset.

Run with Blender --background --python scripts/build-basic-shape-study.py
All coordinates and cameras are saved for later owner corrections and overlays.
"""
import bpy
import math
import json
import sys
import argparse
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--revision',choices=['01','02','03'],default='03')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT = ROOT / ('assets/audit/basic-shape-study'+args.revision)
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
if args.revision in ('02','03'):
    # Owner's drawn lower-rear contour: a longer diagonal egg/keel, ending
    # in a narrow rounded point behind the embedded hips, not a second ball.
    profile=[(.505,.355,.006,.012),(.555,.32,.045,.065),
             (.64,.255,.105,.14),(.735,.175,.175,.22),
             (.84,.09,.23,.285),(.96,.025,.275,.335),
             (1.08,-.025,.26,.325),(1.20,-.06,.22,.275),
             (1.31,-.085,.145,.19),(1.39,-.09,.025,.035)]
if args.revision=='03':
    # Orange owner trace: fuller continuous rear flank and low belly,
    # retaining the rear tip rather than collapsing to a thin triangle.
    profile=[(.515,.355,.008,.015),(.575,.255,.080,.13),
             (.65,.165,.15,.245),(.735,.11,.205,.30),
             (.84,.06,.245,.355),(.96,.04,.275,.355),
             (1.08,-.02,.26,.335),(1.20,-.065,.22,.285),
             (1.31,-.075,.15,.205),(1.39,-.09,.025,.035)]
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
if args.revision=='01':
    ellipsoid('H01 head and swept crown mass', 'head', (0,-.21,1.615), (.185,.25,.195))
else:
    # Blend the posterior skull into the nape/crown, with no round rear node.
    hp=[(.055,1.585,.012,.024),(.02,1.605,.075,.09),
        (-.055,1.64,.137,.14),(-.16,1.65,.176,.17),
        (-.275,1.63,.18,.18),(-.375,1.61,.143,.145),
        (-.455,1.59,.075,.10),(-.485,1.575,.012,.035)]
    hv=[]
    for y,z,rx,rz in hp:
        for i in range(16):
            a=i*math.tau/16;hv.append((rx*math.cos(a),y,z+rz*math.sin(a)))
    hf=[tuple(reversed(range(16)))]
    for j in range(len(hp)-1):
        for i in range(16):
            hf.append((j*16+i,j*16+(i+1)%16,(j+1)*16+(i+1)%16,(j+1)*16+i))
    hf.append(tuple(range((len(hp)-1)*16,len(hp)*16)))
    hd=bpy.data.meshes.new('Soft continuous rear crown cage');hd.from_pydata(hv,[],hf);hd.update()
    ho=bpy.data.objects.new('H01 soft rear head and continuous crown',hd);s.collection.objects.link(ho)
    tag(ho,'head',dict(type='continuous-rounded-head',sections=hp))

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
    knee=(sign*.177,-.14,.59) if args.revision=='03' else (sign*.177,-.09,.61)
    hock=(sign*.185,.105,.285)
    ankle=(sign*.188,.015,.105)
    if args.revision=='03':
        # Purple owner trace: a rounded proximal thigh tapering into a
        # forward knee; keep the lower ankle, planted feet and hip anchors.
        a,b=Vector(hip),Vector(knee);axis=(b-a).normalized()
        u=Vector((1,0,0));v=axis.cross(u).normalized()
        thigh_sections=[(-.16,.018),(0,.085),(.24,.108),(.5,.104),
                        (.76,.092),(1,.072),(1.14,.018)]
        lv=[]
        for t,r in thigh_sections:
            center=a+(b-a)*t
            for i in range(16):
                ang=i*math.tau/16
                lv.append(tuple(center+r*(math.cos(ang)*u+math.sin(ang)*v)))
        lf=[tuple(reversed(range(16)))]
        for j in range(len(thigh_sections)-1):
            for i in range(16):
                lf.append((j*16+i,j*16+(i+1)%16,(j+1)*16+(i+1)%16,(j+1)*16+i))
        lf.append(tuple(range((len(thigh_sections)-1)*16,len(thigh_sections)*16)))
        ld=bpy.data.meshes.new(side+' rounded taper thigh cage');ld.from_pydata(lv,[],lf);ld.update()
        lo=bpy.data.objects.new('L '+side+' rounded upper thigh',ld);s.collection.objects.link(lo)
        tag(lo,'legs',dict(type='rounded-taper-thigh',start=hip,end=knee,sections=thigh_sections))
        capsule('L '+side+' shank','legs',knee,hock,.061)
    else:
        capsule('L '+side+' upper thigh','legs',hip,knee,.075)
        capsule('L '+side+' shank','legs',knee,hock,.051)
    capsule('L '+side+' lower segment','legs',hock,ankle,.04)
    for name,point,r in [('hip',hip,.092 if args.revision=='03' else .081),
                         ('knee',knee,.073 if args.revision=='03' else .060),('hock',hock,.051)]:
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
if args.revision in ('02','03'):
    GROUPS['torso']=((0,.09,.96),1.06)
receipt={'status':'new proposed blockout, not extracted from or applied to detailed model',
         'revision':args.revision,
         'owner_adjustment':'Soften posterior head node; elongate torso toward drawn lower-rear point' if args.revision=='02' else None,
         'comparison':'Assembly cameras and scale unchanged; isolated torso framing expanded to avoid clipping.' if args.revision=='02' else None,
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
if args.revision=='03':
    receipt['owner_adjustment']='Orange: fuller rear torso and lower belly taper. Purple: rounder upper thigh, forward knee and fuller shank.'
    receipt['comparison']='Assembly and isolated part cameras unchanged from study02; head/neck, hip/hock/ankle anchors and feet preserved.'
    receipt['assumption']='The colored traces specify contours, not exact numeric proportions; subtle knee repositioning and hidden-view widths are visual estimates.'
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
