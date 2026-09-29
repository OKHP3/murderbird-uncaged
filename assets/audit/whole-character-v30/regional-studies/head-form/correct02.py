from pathlib import Path
P=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/scripts/regions/whole-character-v30-head-form.py');s=P.read_text();s=s.replace('outer=.056+.013*max(0,si)+.007*max(0,co)','outer=.054+.009*max(0,si)+.004*max(0,co)')
s=s.replace("capnames=['V27 fixed", "opticnames=[f'{p} {side}' for p in ('Seated passive optic housing','Seated Advanced optic','Recessed orbital bearing','Orbital passive retaining race') for side in (-1,1)]\n targets+=opticnames\n capnames=['V27 fixed")
s=s.replace("bpy.context.view_layer.update();front=None;frontname=None;dg=bpy.context.evaluated_depsgraph_get()",'''# A finite annular receiving cup carries the smaller actual lens aperture.
 # Coordinates here are CURRENT native world metres (not pre-mass profile).
 # The old passive housing remains passive; sensing eligibility stays on
 # the unchanged independently owned Advanced optic mesh.
 def current_install(n,v,f):
  install(n,[(oldpivot+(Vector(p)-pivot)/factor) for p in v],f)
 for side in (-1,1):
  lens=bpy.data.objects[f'Seated Advanced optic {side}'];points=[lens.matrix_world@v.co for v in lens.data.vertices]
  cy=(min(p.y for p in points)+max(p.y for p in points))/2;cz=(min(p.z for p in points)+max(p.z for p in points))/2
  inv=lens.matrix_world.inverted();lens.data=lens.data.copy()
  for v,p in zip(lens.data.vertices,points):
   p.y=cy+(p.y-cy)*.67;p.z=cz+(p.z-cz)*.67;p.x-=side*.025;v.co=inv@p
  lens.data.update();changed.append(lens.name)
  # Closed swept cup wall, with a deliberate lip and recessed inner seat.
  profile=[(.158,.069),(.153,.071),(.137,.050),(.130,.042),(.125,.042),(.133,.052),(.149,.067),(.153,.067)]
  v=[];f=[];n=72
  for x,r in profile:
   for k in range(n):a=math.tau*k/n;v.append((side*x,cy+r*math.cos(a),cz+r*math.sin(a)))
  for j in range(len(profile)):
   for k in range(n):f.append((j*n+k,j*n+(k+1)%n,((j+1)%len(profile))*n+(k+1)%n,((j+1)%len(profile))*n+k))
  current_install(f'Seated passive optic housing {side}',v,f)
  for prefix,scale in [('Recessed orbital bearing',.87),('Orbital passive retaining race',.85)]:
   o=bpy.data.objects[f'{prefix} {side}'];inv=o.matrix_world.inverted();o.data=o.data.copy()
   for vert in o.data.vertices:
    p=o.matrix_world@vert.co;p.y=cy+(p.y-cy)*scale;p.z=cz+(p.z-cz)*scale;vert.co=inv@p
   o.data.update();changed.append(o.name)
 bpy.context.view_layer.update();front=None;frontname=None;dg=bpy.context.evaluated_depsgraph_get()''')
s=s.replace("'foreheadProfile':PROFILE,'limits'", "'foreheadProfile':PROFILE,'opticContract':{'lensYZFactor':.67,'lensInwardSeatM':.025,'passiveCupOuterRadiusM':.071,'passiveCupInnerSeatRadiusM':.042,'raceYZFactor':.85,'bearingYZFactor':.87,'existingEraTagsPreserved':True},'limits'")
P.write_text(s)
study=Path('/tmp/v30-head-form/study01.py').read_text().replace('/tmp/v30-head-form/attempt01','/tmp/v30-head-form/attempt02');Path('/tmp/v30-head-form/study02.py').write_text(study)
