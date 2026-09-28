"""Validate the isolated v6 head and cervical-clearance proposal against inherited rigid contracts."""
from pathlib import Path
import importlib.util
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('v5_checks', ROOT / 'scripts/verify-alignment-v5-assets.py')
v5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v5)
base = v5.base
for version in ('v4', 'v5'):
    previous = json.loads((ROOT / f'assets/models/uncaged-alignment-{version}/alignment-inventory.json').read_text())
    for row in previous['generatedFiles']:
        base.validate_record(row)
base.MODEL_DIR = 'assets/models/uncaged-alignment-v6'
base.INVENTORY_PATH = base.MODEL_DIR + '/alignment-inventory.json'
base.MODEL_PATH = base.MODEL_DIR + '/murderbird-alignment-v6.glb'
base.SOURCE_PATH = base.MODEL_DIR + '/murderbird-alignment-v6.blend'
report = base.validate()
inventory = json.loads((ROOT / base.INVENTORY_PATH).read_text())
gltf, _ = base.parse_glb(base.source_file(base.MODEL_PATH))
v5.verify_exported_pivots(gltf, inventory['pivots'])
report['checks'].append('All v4/v5 generated files retain recorded hashes; every exported rest pivot matches the reconstructed v5 jaw and inherited rig at 1e-6 tolerance')
report['checks'] = [check.replace('Saved native v4 Empty local/world joint positions match preserved v3 inventory except bill-contact; unit scales retained', 'Native and recorded joint transforms match the declared reconstruction: jaw world (0,-0.300,1.704); other joints preserve v3 except the surface bill-contact landmark; unit scales retained') for check in report['checks']]
report['scope'] = 'v6 head and local cervical-clearance proposal; v5 jaw pivot retained; not artistic approval'
report['validatorSources'] = [{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [Path(__file__),ROOT/'scripts/verify-alignment-v5-assets.py',ROOT/'scripts/verify-alignment-v4-assets.py']]
print(json.dumps(report,indent=2))
