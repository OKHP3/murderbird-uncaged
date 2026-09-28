"""Write-once bill section study: preserve YZ contour and all attachments."""
from pathlib import Path
import hashlib, json, math, runpy, shutil
import bpy

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend'
OUT=ROOT/'assets/models/uncaged-bill-cross-section-study-v1'
AUDIT=ROOT/'assets/audit/bill-cross-section-study-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}

def main():
    assert sha(BASE)=='b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478'
    assert not OUT.exists() and not AUDIT.exists()
    h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
    names=['Profiled upper bill blade 0','Profiled upper bill blade 1'];changes=[]
    for name in names:
        obj=bpy.data.objects[name];assert len(obj.data.vertices)==57*40
        old=[tuple(v.co) for v in obj.data.vertices];changed=[]
        for j in range(57):
            t=.245*j/56 if name.endswith('0') else .25+.75*j/56
            # Retain the exact root seam and distal apex. A flatter lateral
            # field is strongest in the main plate; YZ silhouette is fixed.
            blend=min(1,max(0,t/.08))*min(1,max(0,(.91-t)/.10))
            blend=blend*blend*(3-2*blend)
            width=max(abs(obj.data.vertices[j*40+k].co.x) for k in range(40))
            for k in range(40):
                v=obj.data.vertices[j*40+k];u=abs(v.co.x)/max(width,1e-9)
                new_u=(1-blend)*u+blend*u**.38
                v.co.x=math.copysign(width*new_u,v.co.x)
                if tuple(v.co)!=old[j*40+k]:changed.append(j*40+k)
        assert all(tuple(v.co)[1:]==p[1:] for v,p in zip(obj.data.vertices,old))
        changes.append({'name':name,'changedVertexCount':len(changed),'method':'Flatten lateral section using exponent 0.38; exact YZ, maximum row width, root and distal apex retained.'})
    after=h['scene_snapshot']();assert before['empties']==after['empties'] and before['curves']==after['curves']
    for n,b in before['meshes'].items():
        a=after['meshes'][n]
        assert a==b if n not in names else all(a[k]==b[k] for k in a if k!='mesh'),n
    OUT.mkdir(parents=True);AUDIT.mkdir(parents=True)
    native=OUT/'murderbird-bill-cross-section-study-v1.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
    shutil.copy2(__file__,AUDIT/'executed-generator.py')
    receipt={'status':'isolated bill section proposal; not selected','base':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'changes':changes,'referenceScope':'July head only; proposed formed plate cross-section, not recovered dimensions.','preservation':{'other697MeshesExact':True,'51PivotsAnd462GuideCurvesExact':True,'ownersTransformsMaterialsExact':True,'saveReloadExact':True},'limits':['Side silhouette is unchanged; this alone cannot resolve a wrong YZ profile.','No export, motion clearance or artistic acceptance.']}
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    renderer=runpy.run_path(str(ROOT/'scripts/study-v8-bill-envelope.py'),run_name='renderer')['renders'];renderer.__globals__['AUDIT']=AUDIT
    receipt['views']=renderer(BASE,'before')+renderer(native,'after')
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(art(native)))

if __name__=='__main__':main()
