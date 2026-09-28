"""Compare preserved inner annular seat and outer span with its paired-V2 source."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
V6=ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
V6_SHA='cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
SOURCE=ROOT/'assets/models/uncaged-paired-bill-mandible-study-v2/murderbird-paired-bill-mandible-study-v2.blend'
SOURCE_SHA='7ba7c996fbcffc118217ad4fcd0c1c1316a3e0a6b0cefa77be4794e6f5a4df15'
V3=ROOT/'scripts/study-orbital-saddle-v3.py'
OUT=Path(__file__).resolve().parent/'source-seat-radial-profile.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def profile(path,expected):
    assert sha(path)==expected
    bpy.ops.wm.open_mainfile(filepath=str(path));rows=[]
    for side in (-1,1):
        o=bpy.data.objects[f'Forged orbital mounting plate {side}'];m=o.matrix_world.copy()
        pts=[m@v.co for v in o.data.vertices]
        for i in range(20,28):
            skins=[]
            for skin in (0,1):
                p=[pts[skin*448+i*7+j] for j in range(7)]
                radii=[math.hypot(q.y+.369,q.z-1.786) for q in p]
                skins.append({'skin':skin,'innerJ0WorldM':[float(c) for c in p[0]],'outerJ6WorldM':[float(c) for c in p[6]],
                    'innerJ0RadiusM':radii[0],'outerJ6RadiusM':radii[6],'radialSpanM':radii[6]-radii[0],
                    'allRadiiM':radii})
            rows.append({'side':'left' if side==1 else 'right','station':i,'skins':skins})
    return rows

def main():
    assert not OUT.exists()
    source=profile(SOURCE,SOURCE_SHA); v6=profile(V6,V6_SHA)
    key=lambda x:(x['side'],x['station'])
    source_map={key(r):r for r in source};v6_map={key(r):r for r in v6}
    differences=[]
    for k in source_map:
        a,b=source_map[k],v6_map[k]
        for sa,sb in zip(a['skins'],b['skins']):
            differences.append({'side':k[0],'station':k[1],'skin':sa['skin'],
                'innerSeatJ0MaxPositionDeltaM':max(abs(x-y) for x,y in zip(sa['innerJ0WorldM'],sb['innerJ0WorldM'])),
                'sourceRadialSpanM':sa['radialSpanM'],'currentV6RadialSpanM':sb['radialSpanM'],
                'sourceOuterRadiusM':sa['outerJ6RadiusM'],'currentOuterRadiusM':sb['outerJ6RadiusM']})
    result={'status':'read-only source profile complete','inputs':{'sourcePairedV2':{'path':str(SOURCE.relative_to(ROOT)),'sha256':sha(SOURCE)},
        'currentV6':{'path':str(V6.relative_to(ROOT)),'sha256':sha(V6)},'v3Recipe':{'path':str(V3.relative_to(ROOT)),'sha256':sha(V3)},
        'script':{'path':str(Path(__file__).resolve().relative_to(ROOT)),'sha256':sha(Path(__file__).resolve())}},
        'method':'Direct native mesh coordinates; station mapping i*7+j and skin offset 448 as defined by V3 recipe. YZ radii use its documented optical center (-.369,1.786). No geometry edits.',
        'sourceProfiles':source,'currentV6Profiles':v6,'comparison':differences,
        'limits':['Radial spans are inherited mesh dimensions around the annular loop, not a verified engineering tolerance or solved clearance envelope.','The source comparison identifies preserved seat position and historical widths; it does not say the full outer V6 surface is valid.']}
    OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'output':str(OUT),'v6InnerSeatMaxDeltaM':max(r['innerSeatJ0MaxPositionDeltaM'] for r in differences),'stations':[{'station':i,'sourceSpanM':source_map[('right',i)]['skins'][0]['radialSpanM'],'v6SpanM':v6_map[('right',i)]['skins'][0]['radialSpanM']} for i in range(20,28)]},indent=2))
if __name__=='__main__':main()
