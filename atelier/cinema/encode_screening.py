"""Encode and independently inspect the frozen 24 fps First Choice screen preview."""
import argparse, hashlib, json, struct, subprocess
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--frames',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--receipt',type=Path,required=True)
args=parser.parse_args()
def call(cmd,**options):
    return subprocess.run(cmd,check=True,**options)
def sha(p):
    with p.open('rb') as f:
        h=hashlib.sha256()
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        return h.hexdigest()
def json_output(cmd):
    return json.loads(call(cmd,stdout=subprocess.PIPE).stdout)
def atom_order(path):
    names=[]
    with path.open('rb') as f:
        while head:=f.read(8):
            length,tag=struct.unpack('>I4s',head); header=8
            if length==1:
                length=struct.unpack('>Q',f.read(8))[0];header=16
            names.append(tag.decode('ascii'))
            if not length:break
            f.seek(length-header,1)
    return names
def rgb_sample(path,frame):
    cmd=['ffmpeg','-v','error','-i',str(path),'-vf',f'select=eq(n\\,{frame}),scale=960:540:flags=lanczos,format=rgb24','-frames:v','1','-f','rawvideo','-']
    data=call(cmd,stdout=subprocess.PIPE).stdout
    if len(data)!=960*540*3:raise ValueError(f'Cannot decode frame {frame}')
    return data
def region_difference(a,b,rectangle):
    x0,y0,x1,y1=rectangle
    total=0;n=0;strong=0
    for y in range(y0,y1):
        for x in range(x0,x1):
            off=(y*960+x)*3
            delta=sum(abs(a[off+c]-b[off+c]) for c in range(3))/3
            total+=delta;n+=1
            if delta>12:strong+=1
    return {'mean_absolute_channel_change_8bit':round(total/n,3),'fraction_pixels_changing_over_12':round(strong/n,5)}
for i in range(252):
    p=args.frames/f'hero-{i:04d}.png'
    if not p.is_file() or p.stat().st_size<16000:raise ValueError(f'Missing completed frame {i}')
args.out.mkdir(parents=True,exist_ok=True)
movie=args.out/'first-choice-native-preview.mp4'
encoded=args.frames/'screening-encode.partial.mp4'
# Input is a display-referred sRGB PNG. Explicitly map sRGB to a tagged BT.709
# transfer function and the limited luma range for ordinary SDR video playback.
flt='scale=in_range=full:out_range=full:out_color_matrix=bt709,format=yuv444p,colorspace=iall=bt709:itrc=srgb:irange=pc:all=bt709:range=tv:format=yuv420p'
call(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-y','-framerate','24','-start_number','0','-i',str(args.frames/'hero-%04d.png'),
      '-frames:v','252','-an','-vf',flt,'-c:v','libx264','-preset','slow','-crf','16','-profile:v','high','-level','4.1','-pix_fmt','yuv420p',
      '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',
      '-metadata','title=First Choice • native motion study','-metadata','comment=Private Advanced candidate. Rendered from the native 3D performance.',str(encoded)])
info=json_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(encoded)])
v=info['streams'][0]
assert len(info['streams'])==1 and v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'24/1',252)
assert abs(float(v['duration'])-10.5)<.00001
atoms=atom_order(encoded)
assert atoms.index('moov')<atoms.index('mdat')
call(['ffmpeg','-v','error','-xerror','-nostdin','-i',str(encoded),'-map','0:v:0','-f','null','-'])
r0=rgb_sample(encoded,0)
rects={'head_and_optic':[399,29,579,159], 'seat_arm':[467,296,531,329],
       'base_front':[580,492,636,504], 'near_talons':[394,472,511,501]}
changes={str(f):{name:region_difference(r0,img,rect) for name,rect in rects.items()}
    for f in [36,54,73,155,251] for img in [rgb_sample(encoded,f)]}
assert changes['155']['head_and_optic']['fraction_pixels_changing_over_12']>.10
assert changes['54']['seat_arm']['fraction_pixels_changing_over_12']>.01
poster=args.out/'first-choice-opening.jpg'
if not poster.is_file():raise ValueError('Missing opening-frame JPEG')
encoded.replace(movie)
renderer=json.loads((args.frames/'hero-render.json').read_text())
report={'source_native_sha256':renderer['input_sha256'],
        'movie':{'file':movie.name,'sha256':sha(movie),'size':movie.stat().st_size,'codec':v['codec_name'],'pixel_format':v['pix_fmt'],
                 'dimensions':[v['width'],v['height']],'frame_count':int(v['nb_read_frames']),'fps':24,'duration_seconds':float(v['duration']),
                 'color':[v['color_space'],v['color_transfer'],v['color_primaries']],'audio_streams':0,'atoms':atoms,'full_decode':'success'},
        'opening_frame':{'native_frame':0,'file':poster.name,'jpeg_sha256':sha(poster),'source_png_sha256':sha(args.frames/'hero-0000.png'),'size':poster.stat().st_size},
        'camera':'Fixed single continuous full-height three-quarter view; original rigid animation, cinema lens and lighting changes only.',
        'cycles':renderer,
        'changed_pixels':{'comparison':'against decoded frame 0 in 960 × 540 view, includes encode/denoising and scene light variations','regions_xyxy':rects,'frames':changes}}
args.receipt.write_text(json.dumps(report,indent=2)+'\n')
print('Validated',movie.name,sha(movie),movie.stat().st_size,v['width'],v['height'],v['nb_read_frames'],v['duration'])
