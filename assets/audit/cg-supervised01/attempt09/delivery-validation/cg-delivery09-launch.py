import subprocess,json,time,datetime,sys,signal,os
from pathlib import Path
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');BLENDER='/Applications/Blender.app/Contents/MacOS/Blender';mode=sys.argv[1];deadline=datetime.datetime(2026,10,4,11,19,45,tzinfo=datetime.timezone.utc).timestamp();jobs={}
for era in ('builder','maker','mechanic'):
 log=Path(f'/tmp/cg-delivery09-{mode}-{era}.log');f=log.open('w')
 if mode=='render':cmd=[BLENDER,'--background','--threads','2','--python',str(ROOT/'scripts/build-cg-supervised09.py'),'--','--mode','candidate','--era',era,'--attempt','attempt09','--final','--export','--readable-lighting','--stage','--resolution','1280','--samples','12']
 else:cmd=[BLENDER,'--background','--threads','2','--python','/tmp/cg-delivery09-native-check.py','--']+(['--preflight'] if mode=='preflight' else ['--early'] if mode=='early' else [])+[era]
 p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);f.close();jobs[era]={'process':p,'pid':p.pid,'log':str(log),'command':cmd};print('STARTED',mode,era,p.pid,flush=True)
Path(f'/tmp/cg-delivery09-{mode}-pids.json').write_text(json.dumps({k:{i:v for i,v in q.items() if i!='process'} for k,q in jobs.items()},indent=2))
while any(q['process'].poll() is None for q in jobs.values()):
 if time.time()>=deadline:
  for q in jobs.values():
   if q['process'].poll() is None:os.killpg(q['pid'],signal.SIGTERM)
  break
 time.sleep(2)
result={era:{'pid':q['pid'],'exit_code':q['process'].poll(),'log':q['log'],'traceback': 'Traceback (most recent call last)' in Path(q['log']).read_text(),'runtime_error': 'RuntimeError:' in Path(q['log']).read_text(),'assertion_error':'AssertionError' in Path(q['log']).read_text(),'completion_marker':('SUPERVISED09_COMPLETE' if mode=='render' else 'DELIVERY09_PREFLIGHT_PASS' if mode=='preflight' else 'DELIVERY09_EARLY_PASS' if mode=='early' else 'DELIVERY09_NATIVE_PASS') in Path(q['log']).read_text()} for era,q in jobs.items()}
Path(f'/tmp/cg-delivery09-{mode}-processes.json').write_text(json.dumps(result,indent=2));print('PROCESSES_DONE',json.dumps(result),flush=True)
