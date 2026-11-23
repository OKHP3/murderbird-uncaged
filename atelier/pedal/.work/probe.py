import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
scene=bpy.context.scene; cam=scene.camera
cam.data.type='ORTHO';cam.data.ortho_scale=1.27
cam.location=(-1.36,-2.18,.92)
cam.rotation_euler=(Vector((0,-.065,.305))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=1024; scene.render.resolution_y=720;scene.render.resolution_percentage=100
bpy.context.view_layer.update()
lst=[]
for o in scene.objects:
 n=o.name.lower()
 if o.hide_render or o.get('cg1cRegion')!='leg' or o.type != 'MESH': continue
 if any(w in n for w in ('rod','piston','paired ram','sleeve','yoke','end','rail')):
    if not any(seg in n for seg in ('tarsus','shank','upper')): continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    zmin=min(v.z for v in vs); zmax=max(v.z for v in vs)
    low=[v for v in vs if v.z<zmin+.006]
    tip=sum(low,Vector((0,0,0)))/len(low)
    p=world_to_camera_view(scene,cam,tip)
    lst.append((o.name,[round(x,5) for x in tip],(round(1024*p.x),round(720*(1-p.y)))))
for pix in ((382,341),(527,294),(375,493),(568,464),(403,0)):
 print(pix,sorted(lst,key=lambda x:(x[2][0]-pix[0])**2+(x[2][1]-pix[1])**2)[:5])
for x in lst:
 if 'medial exposed rod' in x[0] and 'left' in x[0]: print(x)
