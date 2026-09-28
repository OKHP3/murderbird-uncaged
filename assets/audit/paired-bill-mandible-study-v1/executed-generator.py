"""Isolated rigid bill/mandible proportion study; inherited hinge stays fixed."""
from pathlib import Path
import hashlib,json,math,runpy,shutil
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-bill-cross-section-study-v2/murderbird-bill-cross-section-study-v2.blend'
BASE_SHA='33d001a7fdf7a025b1592b247dbbd5a97b56206211043e65e11a967d97c9f017'
OUT=ROOT/'assets/models/uncaged-paired-bill-mandible-study-v1'
AUDIT=ROOT/'assets/audit/paired-bill-mandible-study-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

def main():
    assert sha(BASE)==BASE_SHA and not OUT.exists() and not AUDIT.exists()
    h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='helpers')
    g=runpy.run_path(str(ROOT/'scripts/study-head-continuous-plates-v2.py'),run_name='profile_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
    bill_names=['Profiled upper bill blade 0','Profiled upper bill blade 1']
    jaw_names=['Forked forged mandible -1','Forked forged mandible 1','Distal mandible bridge']
    # A monotonic cutting edge rather than a local sinusoidal bulge. These
    # authored stations are a qualitative reference interpretation only.
    inner_y=[(-.420,),(-.482,),(-.525,),(-.552,),(-.580,),(-.608,),(-.623,),(-.622,)]
    changes=[]
    for name in bill_names:
        o=bpy.data.objects[name];matrix=o.matrix_world.copy();inverse=matrix.inverted()
        old=[matrix@v.co for v in o.data.vertices];assert len(old)==57*40
        offsets=[];new_inner=[]
        for j in range(57):
            t=.245*j/56 if name.endswith('0') else .25+.75*j/56
            delta=(g['lerp_rows'](inner_y,t)[0]-old[j*40+20].y)*smooth((t-.18)/.09)
            # Preserve the contact apex and the distal tip's complete section.
            delta*=smooth((.96-t)/.065)
            new_inner.append(old[j*40+20].y+delta)
            for k in range(40):
                i=j*40+k;a=k*math.tau/40
                cross=1-2*abs((a+math.pi)%math.tau-math.pi)/math.pi
                p=old[i].copy();p.y+=delta*(1-cross)/2
                o.data.vertices[i].co=inverse@p;offsets.append((p-old[i]).length)
            assert (matrix@o.data.vertices[j*40].co-old[j*40]).length<1e-7
        changes.append({'name':name,'maximumDisplacementM':max(offsets),'innerYByRow':new_inner})
    for name in jaw_names:
        o=bpy.data.objects[name];matrix=o.matrix_world.copy();inverse=matrix.inverted();offsets=[]
        for v in o.data.vertices:
            p=matrix@v.co;delta=.035*smooth((-p.y-.400)/.200)
            p.y+=delta;v.co=inverse@p;offsets.append(delta)
        changes.append({'name':name,'maximumRetractionM':max(offsets),'proximalYAtLeastMinus0400Unchanged':True})
    after=h['scene_snapshot']();names=set(bill_names+jaw_names)
    assert before['empties']==after['empties'] and before['curves']==after['curves']
    for n,b in before['meshes'].items():
        a=after['meshes'][n]
        assert a==b if n not in names else all(a[k]==b[k] for k in a if k!='mesh'),n
    OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);native=OUT/'murderbird-paired-bill-mandible-study-v1.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
    shutil.copy2(__file__,AUDIT/'executed-generator.py')
    receipt={'status':'isolated head proportion proposal; not selected','base':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'changes':changes,'innerYStations':inner_y,'preservation':{'other694MeshesExact':True,'51PivotsAnd462GuidesExact':True,'ownersTransformsMaterialsExact':True,'outerBillProfileAndApexExactWithinFloatTolerance':True,'saveReloadExact':True},'referenceScope':'July head only; deeper constructed upper bill and shorter lower jaw are authored proposals, not measured dimensions.','limits':['No export, clearance or owner approval yet.','Inherited construction curves predate these mesh edits and have not been promoted as updated shape authority.','Orbital housing and crown remain unresolved.']}
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    renderer=runpy.run_path(str(ROOT/'scripts/study-v8-bill-envelope.py'),run_name='renderer')['renders'];renderer.__globals__['AUDIT']=AUDIT
    receipt['views']=renderer(BASE,'before')+renderer(native,'after');(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(art(native)))

if __name__=='__main__':main()
