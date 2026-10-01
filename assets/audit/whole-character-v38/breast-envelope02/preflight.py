import bpy,runpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/lower-support02/murderbird-v38-lower-support02.blend'))
c=runpy.run_path(str(ROOT/'scripts/regions/v38-breast-envelope02.py'))['apply']()
p={k:c[k] for k in ('modelEnvelopeMeasurements','actualInspectedReceivingFrameBounds','actualSurfaceFallbackSamples','finitePlateRootSeating')}
(Path(__file__).parent/'pre-save-proof.json').write_text(json.dumps(p,indent=2))
print('PREFLIGHT',json.dumps({'measurements':c['modelEnvelopeMeasurements'],'fallbacks':c['actualSurfaceFallbackSamples'],'plates':len(c['finitePlateRootSeating']),'maximumRootGap':max(p['maximumSampledRootDistanceM']for p in c['finitePlateRootSeating'])}))
