"""Render independent camera views, posed frames, or the matched retained04 baseline."""
from math import cos, sin, radians
import argparse
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from studio import studio

args=argparse.ArgumentParser()
args.add_argument('--out',required=True,type=Path)
args.add_argument('--baseline',action='store_true')
opt=args.parse_args(sys.argv[sys.argv.index('--')+1:])
out=opt.out.resolve();out.mkdir(parents=True,exist_ok=True)
sc=bpy.context.scene
if opt.baseline:
    for ob in sc.objects:
        if ob.type=='LIGHT' or (ob.type=='MESH' and 'ground' in ob.name.lower()):
            ob.hide_render=True
    _,cam=studio()
else:
    cam=sc.camera

def view(name,target,offset,lens,resolution,frame=0,samples=30):
    sc.frame_set(frame)
    cam.location=Vector(target)+Vector(offset)
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='PERSP';cam.data.lens=lens;cam.data.sensor_fit='VERTICAL'
    sc.render.resolution_x,sc.render.resolution_y=resolution
    sc.render.resolution_percentage=100;sc.cycles.samples=samples
    sc.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
    print('Captured '+name,flush=True)

hero=((0,-.17,.94),(-3.68,-1.92,.74),44,(1440,1024))
head=((0,-.24,1.624),(-1.61,-.67,.215),57,(1016,800))
view('portrait',*hero)
view('face',*head)
if not opt.baseline:
    view('first-choice-still', *hero,frame=154,samples=42)
    for i in range(8):
        angle=radians(-64+45*i)
        view('orbit-'+str(i), (0,-.14,.95),(3.72*sin(angle),-3.72*cos(angle),.52),
             40,(540,580),samples=20)
    target=(0,-.29,1.04);offset=(-2.88,-.90,.45)
    for frame,key in ((0,'seated'),(54,'give'),(73,'shift'),(155,'look')):
        view(key,target,offset,39,(720,720),frame,samples=24)
    view('mount',(.0,-.34,.816),(-1.48,-.52,.285),61,(1016,800),frame=54)
    view('talons',(0,-.10,.13),(-1.25,-1.49,.54),61,(1016,800),frame=73)
