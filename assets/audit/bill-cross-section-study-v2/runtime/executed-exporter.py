"""Export the hash-bound bill section study, without selecting it in the app."""
from pathlib import Path
import hashlib, json, runpy, shutil
import bpy

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'assets/models/uncaged-bill-cross-section-study-v2/murderbird-bill-cross-section-study-v2.blend'
NATIVE_SHA='33d001a7fdf7a025b1592b247dbbd5a97b56206211043e65e11a967d97c9f017'
HELPER=ROOT/'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA='39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
GLB=NATIVE.with_suffix('.glb')
AUDIT=ROOT/'assets/audit/bill-cross-section-study-v2/runtime'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}

def main():
    assert sha(NATIVE)==NATIVE_SHA and sha(HELPER)==HELPER_SHA
    assert not GLB.exists() and not AUDIT.exists()
    h=runpy.run_path(str(HELPER),run_name='export_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE));snapshot=h['scene_snapshot']()
    assert len(snapshot['meshes'])==699 and len(snapshot['empties'])==51 and len(snapshot['curves'])==462
    groups={}
    for o in bpy.data.objects:
        if o.type!='MESH':continue
        assert o.parent and all(o.get(k) for k in ('exteriorEras','region','surfaceRole')),o.name
        key=(o.parent.name,o['exteriorEras'],o['region'],o['surfaceRole'])
        groups.setdefault(key,[]).append(o.name)
    h['export_from_reopened_native'](NATIVE,GLB,snapshot,{})
    assert sha(NATIVE)==NATIVE_SHA
    AUDIT.mkdir(parents=True);shutil.copy2(__file__,AUDIT/'executed-exporter.py')
    receipt={'status':'diagnostic derivative only; app still selects V8','native':art(NATIVE),'glb':art(GLB),'helper':art(HELPER),'exporter':art(AUDIT/'executed-exporter.py'),'nativeCounts':{'meshes':699,'pivots':51,'guideCurves':462},'nativeBytesUnchanged':True,'batches':[{'owner':k[0],'eras':k[1],'region':k[2],'role':k[3],'members':v} for k,v in sorted(groups.items())],'limits':['Export helper checks preserved pivots and reopened authoring state. Independent native/export correspondence, browser review, movement and owner acceptance remain separate.']}
    (AUDIT/'export-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(art(GLB)))

if __name__=='__main__':main()
