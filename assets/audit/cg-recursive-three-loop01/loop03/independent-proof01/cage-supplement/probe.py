import bpy,json,hashlib,datetime,ast
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
C=R/'assets/audit/cg-recursive-three-loop01/loop03/saved-binding-final01/checker.py'
# Load only exact pure read-only definitions, never checker main or producer helpers.
a=ast.parse(C.read_text());defs=[n for n in a.body if isinstance(n,ast.FunctionDef) and n.name in ['sha_bytes','digest_json','uv_snapshot','cage_snapshot']]
ns={'bpy':bpy,'json':json,'hashlib':hashlib};exec(compile(ast.Module(body=defs,type_ignores=[]),str(C),'exec'),ns)
def serial(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def info(v):
 s=serial(v);return {'type':type(v).__name__,'dict_keys':list(v) if isinstance(v,dict) else None,'dictionary_count':len(v),'vertices':len(v.get('vertices',[])) if isinstance(v,dict) else None,'edges':len(v.get('edges',[])) if isinstance(v,dict) else None,'polygons':len(v.get('polygons',[])) if isinstance(v,dict) else None,'loops':len(v.get('loops',[])) if isinstance(v,dict) else None,'uv_layers':len(v.get('uv',{}).get('layers',[])) if isinstance(v,dict) else None,'serialized_bytes':len(s.encode()),'direct_sha256':hashlib.sha256(s.encode()).hexdigest(),'exact_checker_digest':ns['digest_json'](v)}
rows=[]
for era in ['builder','maker','mechanic']:
 src=R/f'assets/audit/cg-recursive-three-loop01/loop02/delivery/retained03/{era}/murderbird-recursive-{era}.blend';cand=R/f'assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/{era}/murderbird-recursive-{era}.blend'
 bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 original=ns['cage_snapshot'](bpy.data.objects['CGH17 frontal crown root']);before=info(original);frozen_serial=serial(original)
 Path(f'/tmp/cg-loop03-cage-supplement-2134/{era}-before.json').write_text(frozen_serial)
 bpy.ops.wm.open_mainfile(filepath=str(cand),load_ui=False,use_scripts=False)
 after_original=info(original);old=ns['cage_snapshot'](bpy.data.objects['CGH17 frontal crown root']);new=ns['cage_snapshot'](bpy.data.objects['CGRS04 source-scale frontal crown appearance'])
 oldinfo=info(old);newinfo=info(new)
 Path(f'/tmp/cg-loop03-cage-supplement-2134/{era}-retired.json').write_text(serial(old));Path(f'/tmp/cg-loop03-cage-supplement-2134/{era}-successor.json').write_text(serial(new))
 rows.append({'era':era,'before_source':before,'retained_python_dict_after_reopen':after_original,'retired_source':oldinfo,'successor':newinfo,'source_dict_survives_reopen':frozen_serial==serial(original),'retired_matches_before_serialization':serial(old)==frozen_serial,'successor_matches_before_serialization':serial(new)==frozen_serial,'original_checker_source_predicate':ns['digest_json'](old)==ns['digest_json'](original),'original_checker_successor_predicate':ns['digest_json'](new)==ns['digest_json'](old)})
 print(json.dumps(rows[-1]),flush=True)
Path('/tmp/cg-loop03-cage-supplement-2134/raw.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checker_sha256':hashlib.sha256(C.read_bytes()).hexdigest(),'results':rows},indent=2)+'\n')
