"""Read only session metadata and token counters for the authorized CG team.

Counters include cached input. They are observed provider usage, not the
expired platform goal's accounting, API charges, or currency cost. No prompts,
tool output, secrets, or private production content are copied.
"""
import argparse
import datetime as dt
import json
import shutil
from pathlib import Path

ROOT_THREAD = '01a1050b-6c87-7c91-9d4f-56003ec98a76'
TEAM = {
    '/root', '/root/recursive_head', '/root/recursive_body',
    '/root/deadline22_coupled_construction', '/root/recursive_finish',
    '/root/pipeline_assessment', '/root/closeout21_record_qc',
    '/root/deadline23_independent_outcome', '/root/visual_assessment',
    '/root/recursive_disruptor', '/root/process_assessment',
}

def instant(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))

def readback(start, deadline, ceiling, session_root):
    rows = []
    for day in ('2026/10/03', '2026/10/04', '2026/10/05'):
        for path in (session_root / day).glob('*.jsonl'):
            with path.open() as stream:
                try:
                    first = json.loads(next(stream))
                except (ValueError, StopIteration):
                    continue
                meta = first.get('payload', {})
                agent = '/root' if meta.get('id') == ROOT_THREAD else meta.get('agent_path')
                if agent not in TEAM:
                    continue
                if agent != '/root' and meta.get('parent_thread_id') != ROOT_THREAD:
                    continue
                baseline = None
                latest = None
                model = None
                reasoning = None
                for line in stream:
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    payload = event.get('payload', {})
                    if event.get('type') == 'turn_context':
                        model = payload.get('model', model)
                        reasoning = payload.get('effort', payload.get('reasoning_effort', reasoning))
                    if event.get('type') != 'event_msg' or payload.get('type') != 'token_count':
                        continue
                    info = payload.get('info') or {}
                    usage = info.get('total_token_usage')
                    if not usage or not event.get('timestamp'):
                        continue
                    snapshot = {'timestamp': event['timestamp'], 'usage': usage}
                    latest = snapshot
                    if instant(event['timestamp']) < start:
                        baseline = snapshot
                if latest is None or instant(latest['timestamp']) < start:
                    continue
                baseline_usage = (baseline or {}).get('usage', {})
                delta = {key: max(0, int(value) - int(baseline_usage.get(key, 0)))
                         for key, value in latest['usage'].items()}
                rows.append({'agent': agent, 'session_id': meta.get('id'),
                             'model': model, 'reasoning_effort': reasoning,
                             'baseline': baseline, 'latest': latest,
                             'observed_delta': delta})
    now = dt.datetime.now(dt.timezone.utc)
    observed = sum(row['observed_delta'].get('total_tokens', 0) for row in rows)
    return {
        'schema_version': 1, 'read_at_utc': now.isoformat(),
        'start_utc': start.isoformat(), 'deadline_utc': deadline.isoformat(),
        'elapsed_seconds': max(0, int((now - start).total_seconds())),
        'remaining_seconds': max(0, int((deadline - now).total_seconds())),
        'authorized_ceiling': ceiling,
        'observed_provider_tokens_including_cached_input': observed,
        'observed_remaining_against_ceiling': max(0, ceiling - observed),
        'stop_for_deadline': now >= deadline,
        'stop_for_observed_ceiling': observed >= ceiling,
        'launch_reserve_guard': observed >= int(ceiling * .9),
        'planned_delegated_agent_limit': 10,
        'observed_agent_count_excluding_root': len({r['agent'] for r in rows} - {'/root'}),
        'scope_limits': [
            'Only named team sessions and available completed token-counter events are included.',
            'In-flight responses and delayed/missing session counters can lag this readback.',
            'Cached input is included; this is not platform goal accounting or billing.',
            'The platform goal still records the expired unfinished eight-hour run.',
        ],
        'sessions': rows,
    }

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--start', default='2026-10-04T14:20:42Z')
    p.add_argument('--deadline', default='2026-10-05T00:20:42Z')
    p.add_argument('--ceiling', type=int, default=1000000000)
    p.add_argument('--session-root', type=Path, default=Path('/Users/okh/.codex/sessions'))
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = readback(instant(args.start), instant(args.deadline), args.ceiling, args.session_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Report storage headroom alongside token/time guards. The architect must
    # obey these flags; this reader does not automatically terminate workers.
    storage = shutil.disk_usage(args.output.parent.resolve())
    result['storage_path'] = str(args.output.parent.resolve())
    result['storage_free_bytes'] = storage.free
    result['minimum_launch_storage_bytes'] = 8 * 1024 ** 3
    result['stop_for_low_storage'] = storage.free < result['minimum_launch_storage_bytes']
    result['scope_limits'].append('Guard flags require architect action; no automatic stop enforcement.')
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'sessions'}, indent=2))
