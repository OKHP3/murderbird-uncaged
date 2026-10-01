"""Read-only stock/transition assessment; no hybrid shape saved or rendered."""
import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4];AUDIT=Path(__file__).resolve().parent
src=ROOT/'assets/models/whole-character-v38/lower-support02/murderbird-v38-lower-support02.blend';cand=ROOT/'assets/models/whole-character-v38/breast-support01/murderbird-v38-breast-support01.blend'
def collect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();names=['V30 continuous tapered breast liner']+[f'V34 formed breast course {r} plate {i}'for r,n in[(3,7),(4,6),(5,5),(6,4)]for i in range(1,n+1)];out={}
 for n in names:
  o=bpy.data.objects[n];v=[o.matrix_world@p.co for p in o.data.vertices];o.data.calc_loop_triangles();out[n]={'points':v,'tree':BVHTree.FromPolygons(v,[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True,epsilon=0),'bounds':[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)]}
 return out
s=collect(src);c=collect(cand);records=[]
for n,d in s.items():
 if not any(f'course {r} 'in n for r in(4,5,6)):continue
 roots=sorted(d['points'],key=lambda p:-p.z)[:20];scores=[c['V30 continuous tapered breast liner']['tree'].find_nearest(p)[3]-s['V30 continuous tapered breast liner']['tree'].find_nearest(p)[3]for p in roots];records.append({'sourceLowerPlate':n,'sourceBoundsWorldM':d['bounds'],'sourceVerticesAboveChangedBackingThreshold':sum(p.z>1.005 for p in d['points']),'upper20SourceVertexNearestBackingDistanceDeltaRangeM':[min(scores),max(scores)],'limits':'Source skin/root stock can remain separated or intersecting; nearest-distance change does not establish seating'})
# Compare only actual source row4 against actual candidate row3 surfaces; no replacement.
transition=[]
for a in [n for n in c if'course 3 'in n]:
 for b in [n for n in s if'course 4 'in n]:
  h=c[a]['tree'].overlap(s[b]['tree'])
  if h:transition.append({'candidateUpperPlate':a,'sourceLowerPlate':b,'crossingTrianglePairs':len(h),'candidateTriangles':len({i for i,j in h})})
out={'status':'Coherent region boundary proposal, not accepted stock fit','assessment':'Source rows4–6 lie at/below high-sternum field onset except reported vertices; preserving their exact stock would avoid two newly introduced row4/return pairs and row5 inherited increases caused solely by reconstruction. New row3/source row4 finite contacts still need bounded seam/seat proof. This does not resolve inherited source fit warnings.','fieldBoundaryNativeWorldZ':1.005,'lowerCourseEvidence':records,'candidateRow3SourceRow4TransitionCrossings':transition,'limits':['Read-only pair assessment, no hybrid geometry changed/saved/rendered.','Returned surface contacts include coincident/penetrating triangles; absence cannot certify gap-free seam or supporting stock.','At a future boundary choice, keep source-exact lower course roots and verify new upper free margins, not just object checksums.']};(AUDIT/'lower-course-assessment.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'aboveThreshold':[(p['sourceLowerPlate'],p['sourceVerticesAboveChangedBackingThreshold'])for p in records],'transitionPairs':len(transition)}))
