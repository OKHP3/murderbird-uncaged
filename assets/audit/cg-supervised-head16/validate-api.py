"""Error/atomicity checks on disposable scene; zero renders/saves/exports."""
from pathlib import Path
import bpy, importlib.util, json
ROOT=Path(__file__).resolve().parents[3]
sp=importlib.util.spec_from_file_location('h16',ROOT/'scripts/cg-supervised-head16.py')
h16=importlib.util.module_from_spec(sp);sp.loader.exec_module(h16)
bpy.ops.wm.open_mainfile(filepath=str(h16.INPUT))
scene=bpy.context.scene
objects=[scene.objects[n] for n in h16.NAMES]
slots=lambda:[[m.name for m in o.data.materials] for o in objects]
before=slots();checks={}
def reject(label, era='builder'):
    try:h16.apply(scene,ROOT,era)
    except (ValueError,RuntimeError) as e:checks[label]={'status':'PASS','error':str(e)}
    else:raise AssertionError(label+' must reject')
    assert slots()==before
reject('unknown-era','unknown')
reject('mismatched-existing-era','maker')
objects[1].name='temporary head16 missing far test'
reject('missing-far-atomic-no-near-mutation')
objects[1].name=h16.NAMES[1]
objects[1]['cgSupervisedHead15']=False
reject('invalid-object-marker')
objects[1]['cgSupervisedHead15']=True
original=[o.data.materials[0] for o in objects]
route=h16.apply(scene,ROOT,'builder')
try:h16.apply(scene,ROOT,'builder')
except RuntimeError as e:checks['second-apply-rejected']={'status':'PASS','error':str(e)}
else:raise AssertionError('second apply must reject')
for obj,mat in zip(objects,original):obj.data.materials[0]=mat
assert slots()==before
checks['restored-slot-bindings']={'status':'PASS'}
(ROOT/'assets/audit/cg-supervised-head16/api-validation.json').write_text(json.dumps({'checks':checks,'renders':0,'native_saves':0,'exports':0},indent=2)+'\n')
print('HEAD16_API_VALIDATION_PASS')
