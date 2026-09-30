import bpy,json,sys,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[4];out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists();models=[];source={}
for label,folder in [('source','jaw-fit02'),('01','cranial-transition01'),('02','cranial-transition02')]:
 path=r/f'assets/models/whole-character-v38/{folder}/murderbird-v38-{folder}.blend';bpy.ops.wm.open_mainfile(filepath=str(path));allpoints=[];errors=[];lengths=[]
 for o in bpy.data.objects:
  if not o.name.startswith('V38 swept crown course'):continue
  p=[o.matrix_world@v.co for v in o.data.vertices];n=len(p)//2;assert n==169;allpoints+=p
  vectors=[p[n+i]-p[i]for i in range(n)];lengths+=[v.length for v in vectors]
  if label=='source':source[o.name]=vectors
  else:errors.extend((v-source[o.name][i]).length for i,v in enumerate(vectors))
 seat=bpy.data.objects['V31 frontal cranial cap receiving seat'];sp=[seat.matrix_world@v.co for v in seat.data.vertices]
 models.append({'model':label,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'actualCrownBoundsNative':[[min(p[k]for p in allpoints),max(p[k]for p in allpoints)]for k in range(3)],'actualPairedStockVectorLengthRangeM':[min(lengths),max(lengths)],'maxPairedStockVectorDifferenceFromSourceM':max(errors)if errors else 0,'actualFixedFrontalSeatBoundsNative':[[min(p[k]for p in sp),max(p[k]for p in sp)]for k in range(3)],'frontalSeatOwner':seat.parent.name,'frontalSeatEraTags':seat.get('exteriorEras')})
out.write_text(json.dumps({'models':models,'scope':'Actual saved native crown/seat bounds and paired-vector fidelity; source stock variation inherited. No lap/self/moving-fit or uniform normal-thickness certificate.'},indent=2)+'\n')
