"""Replay the named regional panel clearance tests in a built copy of the study."""
from argparse import ArgumentParser
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
REGIONS = {
    (era, region) for era in ('maker', 'mechanic', 'advanced')
    for region in ('head', 'breast', 'left-wing', 'right-wing')
}


def by_region(rows):
    indexed = {(row['era'], row['region']): row for row in rows}
    if len(rows) != len(REGIONS) or set(indexed) != REGIONS:
        raise ValueError("The replay must contain all 12 expected era and region combinations")
    return indexed


def verify(analytic, frozen, surfaces):
    if analytic['portable'] != frozen['portable'] or analytic['errors']:
        raise ValueError("Viewer identity or browser errors differ from the recorded study")
    current, expected = by_region(analytic['rows']), by_region(frozen['rows'])
    for region, row in current.items():
        if row['axis'] != expected[region]['axis'] or abs(row['lowerBound'] - expected[region]['lowerBound']) > 1e-8:
            raise ValueError(f"Continuous separation changed for {region}")
        if row['maxHingeDrift'] > 1e-10 or row['reassemblyMatrixError'] > 1e-12:
            raise ValueError(f"Hinge placement or reassembly changed for {region}")
    if surfaces is not None:
        for key in ('portable', 'script', 'model'):
            if surfaces[key] != analytic[key]:
                raise ValueError(f"Triangle sweep used a different {key}")
        for region, row in by_region(surfaces['checks']).items():
            if len(row['poses']) != 51 or any(p['crossing_triangle_pairs'] for p in row['poses']):
                raise ValueError(f"Missing or intersecting triangle poses for {region}")
    print(f"Verified {len(current)} continuous clearance bounds from "
          f"{sum(r['sampledOpeningPositions'] for r in current.values())} panel positions.")
    print(f"Minimum separation: {min(r['lowerBound'] for r in current.values()):.9f} model units.")
    if surfaces is not None:
        print("Blender found zero transverse triangle crossings in the 612 sampled pairs.")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--app', type=Path, default=Path(os.environ.get('MB_QA_APP', HERE.parents[1])),
                        help='Independent study directory containing the built web/ and portable HTML')
    parser.add_argument('--output', type=Path, default=HERE.parent / '.results' / 'panels')
    parser.add_argument('--blender', help='Also replay the independent triangle tests using this Blender executable')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Keep frozen expectations beside the harness, even when testing a different build directory.
    reference = HERE.parents[1] / 'verification' / 'panels-continuous.json'
    environment = dict(os.environ, MB_QA_APP=str(args.app.resolve()), OPENBLAS_NUM_THREADS='1')

    def run(*command):
        subprocess.run([str(arg) for arg in command], env=environment, check=True)

    with TemporaryDirectory(prefix='murderbird-panel-replay-') as capture:
        run('node', HERE / 'capture.cjs', capture)
        run(sys.executable, HERE / 'continuous.py', capture, output / 'continuous.json')
        if args.blender:
            run(args.blender, '--background', '--factory-startup', '--python-exit-code', '1',
                '--python', HERE / 'analyze.py', '--', capture, output / 'sweeps.json')
    surfaces = json.loads((output / 'sweeps.json').read_bytes()) if args.blender else None
    verify(json.loads((output / 'continuous.json').read_bytes()), json.loads(reference.read_bytes()), surfaces)


if __name__ == '__main__':
    main()
