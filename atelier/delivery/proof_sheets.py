"""Collect native renders into two compact, offline review sheets."""
from pathlib import Path
import argparse,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
parser=argparse.ArgumentParser();parser.add_argument('--before',type=Path,required=True)
parser.add_argument('--after',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
opt=parser.parse_args();opt.out.mkdir(parents=True,exist_ok=True)
def font(size,bold=False):
    paths=([Path('/System/Library/Fonts/Supplemental/Georgia Bold.ttf')] if bold else [Path('/System/Library/Fonts/Supplemental/Georgia.ttf')])+[Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    for p in paths:
        if p.exists():return ImageFont.truetype(str(p),size)
    return ImageFont.load_default(size=size)
dark=(26,26,24);pale=(237,231,215);mute=(190,186,170)
w,h=1944,1410;im=Image.new('RGB',(w,h),dark);draw=ImageDraw.Draw(im)
draw.text((42,24),'MurderBird / First Choice',font=font(46,True),fill=pale)
draw.text((42,91),'Advanced character study   ·   Matched native cameras',font=font(25),fill=mute)
margin=40;gap=26;ww=(w-2*margin-gap)//2
for col,(folder,title) in enumerate(((opt.before,'Retained04'),(opt.after,'First Choice'))):
    xx=margin+(ww+gap)*col;draw.text((xx,156),title,font=font(32,True),fill=pale)
    for name,y,hh in (('portrait',217,649),('face',890,470)):
        src=Image.open(folder/(name+'.jpg')).convert('RGB')
        if name=='face':
            # Same crop in both panels, a wide view of the skull.
            src=src.crop((10,75,1006,717))
        dest=ImageOps.contain(src,(ww,hh))
        im.paste(dest,(xx+(ww-dest.width)//2,y+(hh-dest.height)//2))
im.save(opt.out/'matched-native-views.jpg',quality=93)
w,h=1884,1194;im=Image.new('RGB',(w,h),dark);draw=ImageDraw.Draw(im)
draw.text((34,18),'First Choice / Orbit',font=font(42,True),fill=pale)
for i in range(8):
    xx=32+(i%4)*460;yy=90+(i//4)*542
    src=Image.open(opt.after/f'orbit-{i}.jpg').convert('RGB')
    im.paste(ImageOps.contain(src,(442,477)),(xx,yy))
    draw.text((xx,yy+486),f'{(-64+i*45)%360}°',font=font(20),fill=mute)
im.save(opt.out/'eight-angle-review.jpg',quality=91)
