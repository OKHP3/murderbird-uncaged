"""Versioned structural reconciliation. Blender 5.2; rigid mechanical assemblies.
Derives editable inherited legs/wings from the preserved presence study. Rebuilds
head/neck/breast geometry; neutral materials deliberately defer finished surfaces.
No historical source is overwritten. See docs/structural-reference-audit.md.
"""
from pathlib import Path
import ast, math, random, json, hashlib
import bpy
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/models/uncaged-structure-v1';OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'assets/models/uncaged-presence-study/murderbird-presence-study.blend'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='2206e8d6b63c9adec672523f94158323555938932163f6205c8a391030a05666', 'Preserved source changed; choose a new version before regeneration'
bpy.ops.wm.open_mainfile(filepath=str(BASE))
for o in bpy.data.objects:o.animation_data_clear()
for action in list(bpy.data.actions):bpy.data.actions.remove(action)
# Reuse deterministic mesh primitives, not the predecessor's scene execution.
source=ast.parse((ROOT/'scripts/build-uncaged-presence-study.py').read_text())
helpers={'material','group','mesh','bevel','rod','ring','tube','plate','loft','shell_scales','reparent_keep_world','depth'}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in helpers],type_ignores=[]),'<preserved-mesh-primitives>','exec'))
random.seed(927)
root=bpy.data.objects['murderbird'];body=bpy.data.objects['body'];neck=bpy.data.objects['neck'];head=bpy.data.objects['head'];jaw=bpy.data.objects['jaw'];chest=bpy.data.objects['breastplate'];crown=bpy.data.objects['cranial-cover'];optics=bpy.data.objects['builder-optics'];mind=bpy.data.objects['processing']
bronze=material('Structural clay / inherited shell',(.36,.39,.40),.15,.62)
patina=bronze
iron=material('Structural clay / passive frame',(.15,.18,.20),.28,.56)
brass=material('Structural clay / bearing surfaces',(.29,.32,.34),.30,.50)
dark=material('Structural clay / recessed frame',(.065,.078,.088),.1,.7)
bill_metal=material('Structural clay / forged bill',(.29,.32,.34),.20,.52)
optic=material('Advanced amber sensor only',(.35,.15,.03),.15,.4)
optic.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(.6,.17,.015,1)
optic.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.65

def under(o,p):
    q=o.parent
    while q:
        if q==p:return True
        q=q.parent
    return False

def delete_meshes(test):
    doomed=[o for o in bpy.data.objects if o.type=='MESH' and test(o)]
    for o in doomed:bpy.data.objects.remove(o,do_unlink=True)

# The previous shared powered-looking tubes are removed, not recolored as Maker.
removed=[]
for o in list(bpy.data.objects):
    if o.type=='MESH' and any(s in o.name.lower() for s in ['actuator','piston','hydraulic','tendon take-off']):
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Remove head/neck skins, retaining dedicated processing empty and its lattice.
delete_meshes(lambda o:under(o,neck) and not under(o,mind))
# Retire the hidden legacy wind-up model; the era-specific runtime chain is active.
drive=bpy.data.objects['winding-drive'];delete_meshes(lambda o:under(o,drive))
# Replace thoracic envelope and breast cover, preserving internal cage/load rails.
delete_meshes(lambda o:any(o.name.startswith(n) for n in ['Curved breast scale','Rear fitted scale','Rear overlap','Rear armor','Formed breast shell','Thoracic yoke','Pelvic rail','Spinal transmission housing','Spine collar','Transverse rib']))
# Neutral inherited surfaces. No weathering/no painted-seam workaround.
for o in bpy.data.objects:
    if o.type!='MESH':continue
    for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
    for i,m in enumerate(o.data.materials):
        o.data.materials[i]=bronze if any(x in m.name.lower() for x in ['bronze','patina']) else brass if 'brass' in m.name.lower() else iron

# Existing pelvis and legs stay attached at their measured pivots. Frame ends
# widen toward the shoulders, and the lower envelope wraps the hip saddle.
chest.matrix_world=Matrix.Translation(Vector((-.255,-.25,1.38)))
sections=[(.86,.055,.18,.17),(1.00,.035,.26,.245),(1.18,-.035,.305,.31),(1.34,-.075,.275,.30),(1.46,-.095,.175,.205),(1.51,-.09,.11,.14)]
cover=loft('Structural breast formed cover',sections,bronze,chest,24,-math.pi/2,math.pi,.014);cover.location=(.255,.25,-1.38)
shell_scales('Breast broad structural lamella',sections,5,7,-math.pi/2,math.pi,chest,(-.255,-.25,1.38))
rear=[(.86,.065,.18,.17),(1.00,.06,.27,.25),(1.18,.045,.30,.28),(1.34,.01,.275,.24),(1.46,-.06,.17,.17),(1.50,-.07,.11,.12)]
rear_shell=loft('Rear formed structural shell',rear,iron,body,24,math.pi/2,math.pi,.012);rear_shell.location.z=-.90
shell_scales('Rear broad structural lamella',rear,5,7,math.pi/2,math.pi,body,(0,0,.90))
# Passive yoke follows the corrected exterior, ending at actual shoulder pivots.
for s in [-1,1]:
    tube('Corrected passive thoracic yoke',[(s*.20,.08,.00),(s*.26,.085,.22),(s*.30,.06,.47),(s*.18,-.06,.53)],[.032,.030,.035,.028],iron,body)
rod('Passive dorsal spine',(0,.18,.02),(0,.11,.53),.029,iron,body)
for label in ['left','right']:
    w=bpy.data.objects[label+'-mantle'];w.location.z-=.145;w.location.y+=.04
for z,rx,ry in [(.14,.25,.23),(.30,.27,.24),(.47,.20,.19)]:
    r=ring('Corrected passive transverse rib',(0,.01,z),1,.009,iron,body,'Z',32);r.scale=(rx,ry,1)
# Refit the anatomical-left repair to the corrected shoulder attachment.
# Its fixed bracket and moving lug have deliberately asymmetric limited travel.
repair=bpy.data.objects['industrial-repairs'];delete_meshes(lambda o:under(o,repair))
bpy.context.view_layer.update()
shoulder=bpy.data.objects['left-mantle']
repair.matrix_world=Matrix.Translation(shoulder.matrix_world.translation)
for z in [-.045,.045]:
    rod('Left refitted fixed stop bracket',(.018,-.035,z),(.108,.075,z),.014,iron,repair,8)
    rod('Left refitted stop pin',(.055,-.016,z),(.115,-.016,z),.014,brass,repair,12)
rod('Left passive restricted-travel lug',(.046,.040,-.04),(.106,.040,-.04),.022,iron,shoulder,10)
# Open side windows reveal real hip-to-yoke paths. No floating exterior plates.
for s in [-1,1]:
    tube('Passive pelvic fork',[(s*.21,.08,-.01),(s*.27,.09,.16),(s*.29,.065,.33)],[.032,.037,.03],iron,body)
    rod('Passive hip cross shaft',(s*.20-.07,.087,-.008),(s*.20+.07,.087,-.008),.068,brass,body,24)

# Articulated S-shaped cervical frame. Local geometry meets the two actual
# pivots, without the old compact thick collar or any telescoping extension.
neck.matrix_world=Matrix.Translation(Vector((0,-.10,1.34)))
head.matrix_world=Matrix.Translation(Vector((0,-.30,1.79)))
head.animation_data_clear();head.rotation_euler=(0,0,0)
crown.location=(0,0,0);optics.location=(0,0,0)
mind.location=(0,.045,.09)
jaw.location=(0,-.01,-.04)
bpy.context.view_layer.update()
for s in [-1,1]:
    tube('Cervical passive fork',[(s*.071,.01,0),(s*.083,-.12,.16),(s*.072,-.11,.30),(s*.060,-.20,.45)],[.022,.025,.023,.024],iron,neck)
    for z,y,r in [(0,0,.087),(.16,-.12,.073),(.30,-.11,.067),(.45,-.20,.066)]:
        rod('Cervical transverse hinge',(s*.061,y,z),(s*.092,y,z),r,brass,neck,24)
        ring('Cervical hinge rim',(s*.096,y,z),r*.77,.008,bronze,neck)
# The curved armor is split into broad short overlapping rigid guards. The
# upper and lower joints have open bearing clearance, no flexible biological skin.
neck_sections=[(.015,.0,.105,.112),(.115,-.065,.11,.13),(.23,-.11,.098,.12),(.33,-.13,.091,.10),(.435,-.20,.084,.087)]
shell_scales('Cervical ventral guard',neck_sections,5,5,-math.pi*.62,math.pi*1.24,neck)
for row in range(5):
    z=.075+row*.076;y=-.045-row*.034
    plate('Cervical dorsal guard',(0,y+.102,z+.035),.19,.13,bronze,neck,(1.25,0,0))
# Dedicated restrained cable chain on back of neck: short articulated links,
# passive guides at all eras; power hoses are added only in Advanced runtime.
for i in range(9):
    f=i/8; y=.07-.20*f; z=.025+.40*f
    ring('Passive cervical restraint link',(0,y,z),.028,.006,iron,neck,'Y',16)

# Skull is a shaped roof + swept occiput, with an intentionally open cheek.
# It is not a closed ellipsoid covering the mandible opening.
loft('Occipital cranial shell',[(-.10,.115,.086,.082),(.01,.065,.163,.17),(.12,.045,.163,.18),(.20,.055,.12,.155),(.255,.10,.032,.09)],iron,head,24,math.pi*.45,math.pi*1.10,.008)
loft('Cranial roof panel',[(.13,.035,.162,.182),(.205,.07,.12,.17),(.26,.10,.022,.07)],bronze,crown,24,0,math.tau,.011)
# Swept crown plates are larger differentiated shields, directed toward rear.
for row in range(3):
    for s in [-1,0,1]:
        plate('Swept crown structural plate',(s*(.072-row*.011),-.058+row*.09,.24-row*.030),.11,.17-row*.015,bronze,crown,(-.25,s*.34,s*-.15))
for s in [-1,1]:
    for row in range(4):
        plate('Swept occipital structural plate',(s*(.13-row*.012),.082+row*.014,.17-row*.060),.13,.19,bronze,head,(-.52,s*1.1,0))
    # Passive eye sockets exist before powered sensing; the dark inner opening
    # has no lens/electronics unless the dedicated Advanced node is visible.
    ey=(s*.166,-.077,.105)
    rod('Passive circular eye socket',(s*.145,ey[1],ey[2]),(s*.172,ey[1],ey[2]),.070,dark,head,36)
    ring('Passive eye socket rim',(s*.177,ey[1],ey[2]),.073,.011,bronze,head)
    ring('Passive eye socket inner rim',(s*.181,ey[1],ey[2]),.057,.006,brass,head)
    rod('Advanced optical lens',(s*.177,ey[1],ey[2]),(s*.184,ey[1],ey[2]),.041,optic,optics,32)
    # A forked cheek bridge surrounds open space, never fills it with a skin.
    tube('Forged cheek upper bridge',[(s*.157,.065,.088),(s*.173,.018,.015),(s*.151,-.084,.00),(s*.125,-.19,.022)],[.031,.025,.024,.034],bronze,head,8)
    rod('Mandible actual hinge',(s*.116,-.01,-.04),(s*.16,-.01,-.04),.045,brass,head,24)
    ring('Mandible hinge rim',(s*.166,-.01,-.04),.036,.007,iron,head)
# Solid manufactured bill panels use deliberate planar cross sections. Each
# neighboring polygon has a 2mm separation and a real edge thickness.
def forged_panel(name,profile,parent,mat):
    verts=[]
    for side in [-1,1]:
        verts += [(side*w,y,z) for y,z,w in profile]
    n=len(profile);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    o=bevel(mesh(name,verts,faces,mat,parent),.003)
    o.modifiers.new('Manufactured panel triangulation','TRIANGULATE')
    return o
upper=bpy.data.objects['upper-bill'];upper.location=(0,0,0)
for name,profile in [
 ('Bill forehead bridge',[(-.12,.20,.119),(-.203,.168,.102),(-.265,.090,.108),(-.217,.038,.117),(-.133,.071,.141)]),
 ('Bill main cheek plate',[(-.267,.087,.106),(-.312,.052,.101),(-.351,.003,.083),(-.371,-.060,.064),(-.310,-.079,.063),(-.266,-.004,.092),(-.220,.035,.114)]),
 ('Bill forged hook',[(-.373,-.060,.063),(-.387,-.104,.050),(-.385,-.153,.032),(-.372,-.196,.014),(-.348,-.225,.002),(-.347,-.172,.012),(-.335,-.127,.03),(-.312,-.081,.061)])]:forged_panel(name,profile,upper,bill_metal)
for s in [-1,1]:
    ring('Bill recessed vent rim',(s*.112,-.249,.051),.022,.004,brass,upper)
    rod('Bill recessed vent',(s*.108,-.249,.051),(s*.111,-.249,.051),.017,dark,upper,20)
    tube('Mandible side fork',[(s*.124,0,0),(s*.116,-.078,-.056),(s*.088,-.185,-.111),(s*.016,-.275,-.127)],[.025,.025,.021,.009],bill_metal,jaw,8)
forged_panel('Mandible lower cutting plate',[(-.095,-.074,.089),(-.225,-.112,.066),(-.282,-.129,.011),(-.243,-.15,.035),(-.12,-.12,.068)],jaw,bill_metal)
# New passive leg rails replace cylinders shared across eras. Ends terminate at
# each corresponding joint; the runtime era-specific drive remains separate.
for side,label in [(1,'left'),(-1,'right')]:
    thigh=bpy.data.objects[label+'-thigh'];shin=bpy.data.objects[label+'-shin'];foot=bpy.data.objects[label+'-foot']
    for parent,child,r in [(thigh,shin,.020),(shin,foot,.018)]:
        delta=child.location.copy()
        for offset in [-.048,.048]:
            rod('Passive '+label+' paired load rail',(offset,0,0),tuple(delta+Vector((offset,0,0))),r,iron,parent,8)

# Deep head envelope retains the selected bill/crown height while preserving
# the fixed skull pivot. This is a measured model choice, not a raster dimension.
head.scale.z=1.20
# Contact/focus landmarks are recomputed from the actual revised geometry.
bpy.context.view_layer.update()
verts=[o.matrix_world@v.co for o in upper.children if o.type=='MESH' for v in o.data.vertices]
bpy.data.objects['bill-contact'].matrix_world=Matrix.Translation(min(verts,key=lambda p:p.y))
for name,parent,pos in [('anchor-beak',head,(0,-.25,.03)),('anchor-shell',chest,(.255,-.03,-.12)),('anchor-mind',mind,(0,0,.04))]:
    o=bpy.data.objects[name];o.parent=parent;o.location=pos
root['status']='Structural reconciliation v1; neutral exterior; early owner likeness review pending'
root['construction']='Rigid frame/plates; constrained bearing joints; no skeletal skinning or organic tissue'
root['base-source']=str(BASE.relative_to(ROOT));root['base-sha256']=hashlib.sha256(BASE.read_bytes()).hexdigest()
root['structure-version']='1'
root['removed-shared-powered-components']=json.dumps(removed)
neck['joint-contract']='Base hinge + skull hinge, no translating neck extension; curved rigid mechanical frame'
head['joint-contract']='Counter-rotating skull at fixed cervical attachment'
root['rights']='MurderBird creative content all rights reserved; NOTICE.md'
bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=31
for frame,angle in [(1,0),(16,.12),(31,0)]:
    head.rotation_euler.z=angle;head.keyframe_insert(data_path='rotation_euler',frame=frame)
head.animation_data.action.name='attention-export-proof';bpy.context.scene.frame_set(1)
bpy.context.preferences.filepaths.save_version=0
bpy.context.view_layer.update()
inventory={'base':str(BASE.relative_to(ROOT)),'removedSharedPoweredMeshes':removed,'rig':{o.name:list(o.matrix_world.translation) for o in bpy.data.objects if o.type=='EMPTY'},'meshObjects':sum(o.type=='MESH' for o in bpy.data.objects),'status':'structural proposal; owner review pending'}
(OUT/'construction-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'murderbird-structure-v1.blend'))
# Preserve all separate editable plates in .blend; batch runtime rigid assemblies.
for parent in [o for o in bpy.context.scene.objects if o.type=='EMPTY']:
    descendants=[]
    for o in list(bpy.context.scene.objects):
        if o.type!='MESH':continue
        p=o.parent
        while p and p.type!='EMPTY':p=p.parent
        if p==parent:descendants.append(o)
    if not descendants:continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in descendants:
        world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world;o.select_set(True)
    bpy.context.view_layer.objects.active=descendants[0]
    bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name=parent.name+'-geometry'
bpy.ops.export_scene.gltf(filepath=str(OUT/'murderbird-structure-v1.glb'),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=True,export_animation_mode='ACTIONS',export_frame_range=True)
print('STRUCTURE_V1_EXPORT',OUT)
