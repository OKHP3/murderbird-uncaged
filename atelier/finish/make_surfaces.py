"""Bake repeatable patina, relief and roughness tiles. No source image is sampled."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / 'maps'
OUT.mkdir(exist_ok=True)
N = 768
rng = np.random.default_rng(231109)
y, x = np.mgrid[:N, :N].astype('f')
u, v = x/N, y/N

def field(cells_x, cells_y=None):
    cy = cells_y or cells_x
    grid = rng.random((cy,cells_x), dtype=np.float32)
    xx, yy = u*cells_x, v*cy
    xi, yi = xx.astype(int), yy.astype(int)
    dx, dy = xx-xi, yy-yi
    dx, dy = dx*dx*(3-2*dx), dy*dy*(3-2*dy)
    a = grid[yi,xi]*(1-dx) + grid[yi,(xi+1)%cells_x]*dx
    b = grid[(yi+1)%cy,xi]*(1-dx) + grid[(yi+1)%cy,(xi+1)%cells_x]*dx
    return a*(1-dy) + b*dy

def blend(a,b,t):
    return a*(1-t[...,None])+b*t[...,None]

def smooth(lo,hi,a):
    t=np.clip((a-lo)/(hi-lo),0,1)
    return t*t*(3-2*t)

def scratches(n, width=1):
    im=Image.new('L',(N,N))
    pen=ImageDraw.Draw(im)
    for _ in range(n):
        sx,sy=rng.uniform(0,N,2)
        length=rng.uniform(3,62)**1.04
        angle=rng.normal(.26,.65)
        dx,dy=np.cos(angle)*length,np.sin(angle)*length
        kink=rng.uniform(-1.8,1.8)
        pts=[(sx,sy),(sx+.38*dx,sy+.38*dy+kink),(sx+dx,sy+dy)]
        strength=int(rng.uniform(36,188))
        for ox in (-N,0,N):
            for oy in (-N,0,N):
                pen.line([(px+ox,py+oy) for px,py in pts],fill=strength,width=width)
    return np.asarray(im,dtype='f')/255

# Colors are sRGB swatches: exposed parent metal, sheltered oxide, mineral bloom.
families={
 'mantle': ((109,113,97),(64,63,54),(78,91,76),.54,.86),
 'breast': ((112,101,78),(70,62,48),(80,87,70),.54,.86),
 'bill': ((93,98,101),(53,57,61),(70,77,73),.46,.86),
 'brow': ((145,118,83),(84,70,49),(89,94,73),.48,.84),
 'bronze': ((136,105,69),(72,57,38),(75,84,65),.43,.84),
 'iron': ((72,73,71),(39,38,35),(53,56,48),.58,.79),
 'steel': ((112,117,116),(71,72,69),(89,91,82),.37,.89),
 'talon': ((75,80,84),(40,43,45),(58,62,61),.36,.87),
 'stand': ((66,69,63),(43,44,41),(58,61,52),.63,.73),
 'floor': ((99,90,76),(61,53,44),(92,86,72),.88,.02),
}
for family,(bright,dark,verde,rough,metal) in families.items():
    garden=family=='floor'
    hammered=.41*field(27)+.31*field(59)+.18*field(125)+.1*field(298)
    broad=.47*field(4)+.30*field(11)+.14*field(32)+.09*field(128)
    salt=.55*field(20)+.30*field(52)+.15*field(177)
    fine=rng.normal(0,1,(N,N))
    fragment=field(190)
    bright,dark,verde=[np.array(c,dtype='f') for c in (bright,dark,verde)]
    exposed=smooth(.32,.69,broad+.17*(hammered-.5))
    mineral=smooth(.53,.69,salt+.51*(.54-broad))*.72
    if family in ('steel','talon','iron','bill','stand'): mineral*=.18
    if not garden:
        exposed=.30+.57*exposed
        mineral*=.57
    recess=smooth(.73,.94,fragment+.28*(salt-.5))
    scar=scratches(95 if garden else 165)
    if garden:
        exposed=.25+exposed*.65
        mineral*=.35
    color=blend(dark,bright,exposed)
    color=blend(color,verde,mineral)
    color+=((hammered-.5)*(58 if garden else 28)+fine*(3.5 if garden else 1.7)-recess*(12 if garden else 8))[...,None]
    color+=scar[...,None]*(12 if garden else 19)
    if family in ('steel','bill','talon','brow'):
        # Soft tool striations in an exposed metal face, interrupted by oxidation.
        brush=field(12,290)-.5
        color+=brush[...,None]*(1-mineral[...,None])*9
    color=np.uint8(np.clip(color,0,255))
    roughness=np.clip(rough+.18*(.50-exposed)+.14*mineral+.09*(hammered-.5)+.03*recess-.13*scar,.22,1)
    metallic=np.clip(metal-.31*mineral-.16*(1-exposed),.01,.95) if not garden else np.zeros_like(roughness)+.02
    # Blue channel holds metalness and green holds roughness as required by glTF.
    orm=np.uint8(np.stack([np.ones_like(roughness),roughness,metallic],axis=-1)*255)
    height=2.2*hammered+1.8*(field(16)-.5)+.11*fine-.9*recess-.52*scar
    dx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*.64
    dy=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*.64
    normal=np.stack([-dx,dy,np.ones_like(dx)],axis=-1)
    normal=normal/np.linalg.norm(normal,axis=-1,keepdims=True)
    Image.fromarray(color).save(OUT/f'{family}-albedo.jpg',quality=93,subsampling=0)
    Image.fromarray(orm).save(OUT/f'{family}-orm.png',optimize=True)
    Image.fromarray(np.uint8((normal*.5+.5)*255)).save(OUT/f'{family}-normal.jpg',quality=94,subsampling=0)
