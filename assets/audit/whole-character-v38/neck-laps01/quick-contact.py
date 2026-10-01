"""Bounded actual finite triangle surfaces, strict crossing counts and first witnesses."""
import bpy,json,hashlib,bmesh
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SCOPE=json.loads((OUT/'scope.json').read_text());CHANGED=SCOPE['changed']+list(SCOPE['added']);CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper'];OWNERS=CHAIN+['cervical-skull-cover','head','jaw','upper-bill','cranial-cover','builder-optics','body','breastplate']
POSES=[('neutral',0,0,0,0,0),('maker-neck-jaw',-.14,-.45,0,.32,0),('captured-contact',4*.10675220489501955,0,-.5090505059024657,.1,0),('attention-yaw-minus',0,0,0,0,-.312),('attention-yaw-plus',0,0,0,0,.312),('contact-yaw-minus',4*.10675220489501955,0,-.5090505059024657,.1,-.312),('contact-yaw-plus',4*.10675220489501955,0,-.5090505059024657,.1,.312)]
def inside(p,t):
 x,y,z=t;a=y-x;b=z-x;c=p-x;aa=a.dot(a);ab=a.dot(b);bb=b.dot(b);den=aa*bb-ab*ab
 if abs(den)<1e-18:return False
 u=(bb*c.dot(a)-ab*c.dot(b))/den;v=(aa*c.dot(b)-ab*c.dot(a))/den;return min(u,v,1-u-v)>1e-6
 def_unused=0

def edge(p,q,t):
 n=(t[1]-t[0]).cross(t[2]-t[0]);length=n.length
 if length<1e-12:return False
 n/=length;d0=n.dot(p-t[0]);d1=n.dot(q-t[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 d=q-p;hit=intersect_ray_tri(*t,d,p,True)
 if hit is None:return False
 u=(hit-p).dot(d)/max(d.length_squared,1e-30);return 1e-6<u<1-1e-6 and inside(hit,t)
def load(path,pose):
 bpy.ops.wm.open_mainfile(filepath=str(path));label,pitch,yaw,head,jaw,headyaw=pose
 for i,n in enumerate(CHAIN):
  o=bpy.data.objects[n];d=Matrix.Rotation(pitch/4,4,'X')
  if i==0:d=d@Matrix.Rotation(yaw,4,'Z')
  o.matrix_basis=o.matrix_basis@d
 delta=Matrix.Rotation(head,4,'X')@Matrix.Rotation(headyaw,4,'Z');o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@delta
 o=bpy.data.objects['jaw'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(jaw,4,'X')
 if 'cervical-skull-cover'in bpy.data.objects:
  o=bpy.data.objects['cervical-skull-cover'];half=Quaternion().slerp(delta.to_quaternion(),.5);o.matrix_basis=o.matrix_basis@half.to_matrix().to_4x4()
 bpy.context.view_layer.update();
 if label=='captured-contact':
  import runpy
  runpy.run_path(str(OUT/'pose-render.py'))['render'](('baseline'if str(path).endswith('curved-neck01.blend')else'candidate')+'-'+label)
 return None

source=ROOT/'assets/models/whole-character-v38/curved-neck01/murderbird-v38-curved-neck01.blend';candidate=ROOT/'assets/models/whole-character-v38/neck-laps01/murderbird-v38-neck-laps01.blend';
load(source,POSES[2]);load(candidate,POSES[2])
