"""Explicit companion:10changedcup/frozen-shell pairs, neutral+7actualsnapshots only."""
from pathlib import Path
P=Path(__file__).resolve().parent
# Reuse exact captured basis/finite predicates; execute no prior screening/Boolean loops.
code=(P/'finite-screen.py').read_text().split("result={'method'")[0].replace("shutil.copy2(packetSource,P/'source-runtime-poses.json')",'')
exec(code,globals())
def cupscreen(path,sample):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();errors=[]
 if sample:
  for name,n in sample['nodes'].items():
   o=bpy.data.objects[name];original=basis.inverted()@trs(gltf[name])@basis;error=max(abs(o.matrix_local[i][j]-original[i][j])for i in range(4)for j in range(4));assert error<2e-6;errors.append(error)
  for name,n in sample['nodes'].items():o=bpy.data.objects[name];o.matrix_basis=o.matrix_parent_inverse.inverted()@basis.inverted()@trs(n)@basis;bpy.context.view_layer.update()
 items={n:shape(bpy.data.objects[n])for n in SOCKET+SHELL};rows=[]
 for cup in SOCKET:
  for shell in SHELL:rows.append({'cup':cup,'shell':shell,'owners':[items[cup]['owner'],items[shell]['owner']],**crossing(items[cup],items[shell])})
 return {'basisRestMaxErrorM':max(errors,default=0),'checkedPairCount':len(rows),'strictCrossingPairCount':sum(x['strictTrianglePairs']>0 for x in rows),'pairs':rows}
out={'method':'Standaloneexplicitcoverage2changedcup halves×5frozen shells=10pairs, strict finiteedge-through-face; coplanar/grazing/containment/sweeps omitted. No bow/Booleanchecks repeated.','note':'These pairs were already executed by finalfinite-screen loop BOW+SOCKET+[STEM] with SOCKET target=SHELL; its method prose stale. Frozen priorJSON unchanged.','sourceNativeSHA256':hashlib.sha256(S.read_bytes()).hexdigest(),'candidateNativeSHA256':hashlib.sha256(C.read_bytes()).hexdigest(),'runtimePacketSHA256':hashlib.sha256(packetSource.read_bytes()).hexdigest(),'poseQualification':packet['scope'],'poses':{}}
for sample in [None]+packet['samples']:
 label='neutral'if sample is None else sample['label'];a=cupscreen(S,sample);b=cupscreen(C,sample);out['poses'][label]={'source':a,'candidate':b};print('CUP_SHELL',label,a['strictCrossingPairCount'],b['strictCrossingPairCount'],flush=True)
(P/'cup-shell-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('CUP_SHELL_READY',flush=True)
