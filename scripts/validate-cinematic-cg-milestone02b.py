"""Verify retained source geometry/stance and pinned binaries; no artistic score."""
from pathlib import Path
import bpy, sys, argparse, json, hashlib, re, array
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--era',default='builder');p.add_argument('--out',default='assets/audit/cinematic-cg-milestone02b/validation-shape.json');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def signature(o):
    d=o.data;h=hashlib.sha256()
    verts=array.array('f',[0])*(len(d.vertices)*3);d.vertices.foreach_get('co',verts);h.update(verts.tobytes())
    loops=array.array('i',[0])*len(d.loops);d.loops.foreach_get('vertex_index',loops);h.update(loops.tobytes())
    polys=array.array('i',[0])*len(d.polygons);d.polygons.foreach_get('loop_total',polys);h.update(polys.tobytes())
    for uv in d.uv_layers:
        v=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',v);h.update(v.tobytes())
    return {'mesh':h.hexdigest(),'world':[float(v) for row in o.matrix_world for v in row],'region':o.get('cg1cRegion'),'hidden':o.hide_render}
source=ROOT/f'assets/models/cinematic-cg-milestone02a/murderbird-cg-2a-{a.era}.blend'
candidate=ROOT/f'assets/models/cinematic-cg-milestone02b/murderbird-cg-2b-{a.era}.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));original={o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(candidate));current={o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH'}
missing=[n for n in original if n not in current]
geometry=[n for n,v in original.items() if n in current and v['mesh']!=current[n]['mesh']]
transforms=[n for n,v in original.items() if n in current and v['world']!=current[n]['world']]
stance=[n for n,v in original.items() if v['region'] in ('leg','foot')]
pin_pattern=r'`([^`]+\.(?:jpg|png|mp4))` — `([a-f0-9]{64})`'
pins=[]
for path,expected in re.findall(pin_pattern,(ROOT/'goal.md').read_text()):
    actual=sha(ROOT/path);pins.append({'path':path,'sha256':actual,'expected':expected,'pass':actual==expected})
record={'era':a.era,'source_sha256':sha(source),'candidate_sha256':sha(candidate),'source_mesh_count':len(original),'retained_source_mesh_count':len(original)-len(missing),'missing_sources':missing,'changed_source_geometry_or_uv':geometry,'changed_source_transforms':transforms,'stance_meshes_preserved':len(stance),'pins':pins,'artistic_acceptance':'Not established by this check'}
record['status']='PASS' if not (missing or geometry or transforms) and all(x['pass'] for x in pins) else 'FAIL'
(ROOT/a.out).write_text(json.dumps(record,indent=2)+'\n');print('CG2B_VALIDATION',record['status'],len(original),len(stance));assert record['status']=='PASS',record
