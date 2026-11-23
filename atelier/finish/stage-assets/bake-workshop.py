"""Original procedural workshop textures. Optional final GLB supplies the contact mask."""
from pathlib import Path
import json
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(112326)
N=1024
yy,xx=np.mgrid[:N,:N].astype('f')
u,v=xx/N,yy/N


def field(nx, ny=None):
    ny=ny or nx
    grid=rng.random((ny,nx))
    x,y=u*nx,v*ny
    i,j=x.astype(int),y.astype(int)
    a,b=x-i,y-j
    a,b=a*a*(3-2*a),b*b*(3-2*b)
    return ((grid[j,i]*(1-a)+grid[j,(i+1)%nx]*a)*(1-b)
            +(grid[(j+1)%ny,i]*(1-a)+grid[(j+1)%ny,(i+1)%nx]*a)*b)


def color(base, variation, tint=1):
    return np.clip(np.array(base)[None,None,:]+variation[:,:,None]*np.broadcast_to(tint,(3,)),0,255).astype('uint8')


def save(name, rgb):
    Image.fromarray(rgb).save(OUT/name,quality=90,subsampling=0)


# Rough limewash. Unequal stains, vertical water runs and a few plaster repairs.
broad=.52*field(3,5)+.26*field(12,9)+.14*field(32)+.08*field(115)
runs=field(170,3)*.55+field(36,5)*.45
dust=.47*field(15)+.28*field(37)+.16*field(86)+.09*field(220)
fine=rng.normal(0,2.1,(N,N))
plaster=(broad-.48)*88+(dust-.5)*39+(runs-.51)*25+fine
plaster-=20*np.exp(-(1-v)*8)*(1+.5*runs)
save('plaster.jpg',color((103,94,75),plaster,(1.0,.93,.80)))

# Timber goes lengthways across U. End grain is intentionally subdued under wear.
grain=.22*field(10,32)+.38*field(4,148)+.27*field(6,365)+.13*field(20,280)
g=2*np.pi
phase=v*152+2.8*field(6,5)+.4*field(20,9)
fibers=(.5+.5*np.sin(phase*g))**8
timber=(grain-.5)*101-(fibers-.2)*15+(field(6)-.5)*37+rng.normal(0,2,(N,N))
save('oak.jpg',color((116,86,60),timber,(1.0,.84,.66)))

# Scale: each concrete tile spans several metres. Its aggregate is small and low contrast.
mottle=.48*field(4)+.3*field(11)+.14*field(31)+.08*field(96)
grit=.36*field(71)+.64*field(175)
f=(mottle-.5)*41+(grit-.5)*25+rng.normal(0,2.8,(N,N))
for _ in range(65):
    cx,cy=rng.uniform(0,1,2);rx,ry=rng.uniform(.006,.04,2)
    dist=((np.minimum(abs(u-cx),1-abs(u-cx))/rx)**2
          +(np.minimum(abs(v-cy),1-abs(v-cy))/ry)**2)
    f-=np.exp(-dist*1.5)*rng.uniform(1,7)
floor=Image.fromarray(color((103,93,80),f,(1,.96,.91)))
scratches=Image.new('RGBA',(N,N))
draw=ImageDraw.Draw(scratches)
for _ in range(90):
    x,y=rng.uniform(0,N,2)
    length=rng.uniform(4,55);a=rng.normal(-.25,.5)
    dx,dy=np.cos(a)*length,np.sin(a)*length
    for i in (-N,0,N):
        for j in (-N,0,N):
            pts=[(x+i,y+j),(x+i+dx*.36,y+j+dy*.36+1),(x+i+dx,y+j+dy)]
            draw.line(pts,fill=(185,176,145,int(rng.uniform(8,32))),width=1)
floor=Image.alpha_composite(floor.convert('RGBA'),scratches).convert('RGB')
floor.save(OUT/'concrete.jpg',quality=90,subsampling=0)

# A blued, thinly painted sheet. Chip break-up comes from several independent scales.
oxide=.45*field(8,15)+.32*field(24,30)+.16*field(59)+.07*field(148)
enamel=(oxide-.5)*43+(field(45,106)-.5)*16+rng.normal(0,1.9,(N,N))
chips=np.clip((oxide-.61)*9,0,1)
rgb=color((105,103,92),enamel,(1,.96,.88)).astype('f')
rgb=rgb*(1-.46*chips[...,None])+np.array((76,61,44))*.46*chips[...,None]
save('enamel.jpg',np.uint8(rgb))

# The CRT emits fine parallel phosphor lines and a modest diagnostic trace.
w,h=640,464
sy,sx=np.mgrid[:h,:w]
x,y=2*sx/w-1,2*sy/h-1
vignette=np.clip(1-.49*(x*x+y*y),.08,1)
scan=.87+.13*np.cos(sy*np.pi)
signal=(42+29*np.exp(-((x+.16)**2+(y+.1)**2)*2.7))*vignette*scan
signal+=rng.normal(0,.8,(h,w))
rgb=np.stack((signal*.59,signal*1.32,signal*.98),axis=-1)
crt=Image.fromarray(np.clip(rgb,0,255).astype('uint8'))
pen=ImageDraw.Draw(crt)
for k in range(4):
    y0=85+k*13
    for start,end in [(72,90),(105,126+k*3),(164,196-k*3),(211,227)]:
        pen.line((start,y0,end,y0),fill=(36,63,47),width=2)
pts=[]
for i in range(74,559,2):
    baseline=306+int(3*np.sin(i*.024))
    phase=(i-74)%99
    peak=int(-26*np.exp(-((phase-50)/2.1)**2)+12*np.exp(-((phase-54)/3)**2))
    pts.append((i,baseline+peak))
pen.line(pts,fill=(43,89,62),width=2)
crt.save(OUT/'phosphor.png',optimize=True)


def ground_mask(path):
    with path.open('rb') as stream:
        stream.seek(12)
        length,typ=struct.unpack('<II',stream.read(8))
        gltf=json.loads(stream.read(length))
        length,typ=struct.unpack('<II',stream.read(8))
        binary=stream.read(length)
    def array(idx):
        acc=gltf['accessors'][idx]
        view=gltf['bufferViews'][acc['bufferView']]
        dims={'VEC3':3,'SCALAR':1}[acc['type']]
        dt=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[acc['componentType']])
        stride=view.get('byteStride',dims*dt.itemsize)
        return np.ndarray((acc['count'],dims),dtype=dt,buffer=binary,
                          offset=acc.get('byteOffset',0)+view.get('byteOffset',0),
                          strides=(stride,dt.itemsize))
    # These named rigid native groups store standing positions directly in glTF Y-up.
    candidates=[n for n in gltf['nodes'] if n.get('name') in
                ('Ground – foot','Ground – leg','Stand – assembly support stand')]
    if len(candidates)!=3 or any(n.get('translation',[0,0,0])!=[0,0,0] for n in candidates):
        raise ValueError("Check the fixed-foot/stand coordinate contract before baking contact")
    size=768
    x0,z0,width=-1.15,-.76,2.30
    levels=[(.03,.008,.57),(.07,.017,.52),(.15,.034,.36),(.27,.062,.24),(.49,.102,.15)]
    masks=[Image.new('L',(size,size)) for _ in levels]
    drawings=[ImageDraw.Draw(im) for im in masks]
    for node in candidates:
        for p in gltf['meshes'][node['mesh']]['primitives']:
            positions=array(p['attributes']['POSITION'])
            faces=array(p['indices']).reshape(-1,3)
            pts=positions[faces]
            heights=np.max(pts[:,:,1],axis=1)
            for dr,(maximum,blur,weight) in zip(drawings,levels):
                for face in pts[heights<maximum]:
                    dr.polygon([((float(a[0])-x0)*size/width,(float(a[2])-z0)*size/width) for a in face],fill=255)
    opacity=np.ones((size,size),dtype='f')
    for mask,(_,sigma,weight) in zip(masks,levels):
        spread=np.asarray(mask.filter(ImageFilter.GaussianBlur(sigma*size/width)),dtype='f')/255
        opacity*=1-spread*weight
    opacity=(1-opacity)*255
    rgba=np.empty((size,size,4),dtype='uint8')
    rgba[:,:,:3]=(20,15,11)
    rgba[:,:,3]=np.clip(opacity,0,255).astype('uint8')
    Image.fromarray(rgba).save(OUT/'standing-contact.png',optimize=True)
    print('Fixed ground profiles:',[n['name'] for n in candidates], 'extent x/z',x0,z0,width)

if len(sys.argv)>1:ground_mask(Path(sys.argv[1]))
