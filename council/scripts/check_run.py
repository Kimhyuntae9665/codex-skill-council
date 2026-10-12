"""Check a Council host ledger offline; never dispatch, cancel, or modify files."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys

SKILL = Path(__file__).resolve().parents[1] / 'SKILL.md'
ROLES = ('Strategist', 'Skeptic', 'Creative', 'Operator', 'Audience Advocate')
FIELDS = ('role', 'status', 'recommendation', 'key reasons', 'risks', 'assumptions',
          'facts vs inference', 'evidence/sources', 'confidence',
          'what would change my mind', 'skills/tools used', 'data limits')
TERMINAL = {'complete', 'error', 'timeout', 'cancelled'}


def contract(skill: Path = SKILL) -> dict:
    """Reuse the entrypoint table rather than another list of model IDs."""
    rows = re.findall(r'^\| ([^|]+?) \| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \|$',
                      skill.read_text(encoding='utf-8'), re.M)
    if len(rows) != 6 or {row[0] for row in rows} != {*ROLES, 'Synthesizer'}:
        raise ValueError('Model table must contain five unique roles and Synthesizer')
    return {role: {'model': model, 'effort': effort, 'agent': agent}
            for role, model, effort, agent in rows}


def instant(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamps must include a timezone')
    return result


def count(value, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f'{name} must be a nonnegative integer')
    return value


def profile(metadata, expected: dict) -> str:
    # Only host-supplied metadata/configuration is usable; brief text is irrelevant.
    if not isinstance(metadata, dict) or metadata.get('source') not in {'host-runtime', 'host-config'}:
        return 'unverified'
    if not isinstance(metadata.get('evidence_ref'), str) or not metadata['evidence_ref'].strip():
        return 'unverified'
    if not metadata.get('model') or not metadata.get('effort'):
        return 'unverified'
    return 'verified' if all(metadata.get(k) == expected[k] for k in ('model', 'effort')) else 'mismatch'


def usable(brief, role: str) -> bool:
    return (isinstance(brief, dict) and all(isinstance(brief.get(k), str) and brief[k].strip() for k in FIELDS)
            and brief['role'] == role and brief['status'] in {'complete', 'limited'})


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON field: {key}')
        result[key] = value
    return result


def check_run(run: dict, *, now: datetime | None = None, skill: Path = SKILL) -> dict:
    """The caller is the trust boundary: this does not authenticate host records."""
    now = now or datetime.now(timezone.utc)
    expected = contract(skill)
    phase = run['phase']
    if phase not in {'not_started', 'advisors', 'synthesis', 'finished', 'aborted'}:
        raise ValueError('Unknown phase')
    started = instant(run['started_at'])
    limits = run['limits']
    deadline = instant(limits['overall_deadline'])
    timeout_spec = limits['advisor_timeout_seconds']
    timeouts = {role: count(timeout_spec[role] if isinstance(timeout_spec, dict) else timeout_spec,
                            'advisor_timeout_seconds') for role in ROLES}
    if any(value == 0 for value in timeouts.values()) or deadline <= started:
        raise ValueError('Positive advisor timeout and overall deadline after start required')
    end = instant(run['finished_at']) if phase in {'finished', 'aborted'} else now
    if end < started or end > now:
        raise ValueError('Invalid run time interval')
    errors, exclusions, accepted, preserved, profiles = [], [], {}, {}, {}
    if end > deadline:
        errors.append('overall deadline exceeded')
    for key in ('search_calls', 'verification_calls'):
        used = count(run['usage'][key], key)
        cap = count(limits['max_' + key], 'max_' + key)
        if used > cap:
            errors.append(f'{key} limit exceeded')
    limit_errors = tuple(errors)
    attempts = run['attempts']
    if not isinstance(attempts, list):
        raise ValueError('attempts must be a list')
    seen, groups = set(), {role: [] for role in ROLES}
    for attempt in attempts:
        role, thread = attempt['role'], attempt['thread_id']
        if role not in groups or not isinstance(thread, str) or not thread.strip():
            errors.append('unknown role or missing thread_id')
            continue
        if thread in seen:
            errors.append(f'duplicate thread_id: {thread}')
        seen.add(thread)
        groups[role].append(attempt)
    for role, items in groups.items():
        items.sort(key=lambda a: count(a['attempt'], 'attempt'))
        previous_end, previous_valid = None, False
        if len(items) > 2:
            errors.append(f'{role}: retry limit exceeded')
        for number, attempt in enumerate(items, 1):
            label = f"{role}/{attempt['attempt']}"
            start = instant(attempt['started_at'])
            state = attempt['terminal_state']
            if state not in TERMINAL | {'running'}:
                errors.append(f'{label}: invalid terminal state')
            if attempt['attempt'] != number or attempt['attempt'] > 2:
                errors.append(f'{label}: invalid attempt sequence')
            if start < started or start > end:
                errors.append(f'{label}: invalid start time')
            if number > 1 and (previous_end is None or previous_end > start or previous_valid):
                errors.append(f'{label}: retry before termination or after a valid result')
            finish = instant(attempt['ended_at']) if attempt.get('ended_at') else None
            if state in TERMINAL and (finish is None or finish < start or finish > end):
                errors.append(f'{label}: terminal result lacks a valid end time')
            if state == 'running' and finish is not None:
                errors.append(f'{label}: running attempt has an end time')
            receive = instant(attempt['result_received_at']) if attempt.get('result_received_at') else finish
            if receive is not None and (receive < start or receive > now):
                errors.append(f'{label}: invalid result receipt time')
            role_deadline = min(start + timedelta(seconds=timeouts[role]), deadline)
            timed_out = (finish or end) > role_deadline or (receive is not None and receive > role_deadline)
            identity = profile(attempt.get('runtime'), expected[role])
            profiles[label] = identity
            brief = attempt.get('brief')
            valid_brief = usable(brief, role)
            if valid_brief:
                preserved[label] = brief
            valid = state == 'complete' and finish is not None and not timed_out and valid_brief and identity == 'verified'
            if valid:
                accepted[role] = {'thread_id': attempt['thread_id'], 'attempt': attempt['attempt'], 'brief': brief}
            else:
                exclusions.append({'attempt': label, 'state': state, 'profile': identity,
                                   'timed_out': timed_out, 'usable_brief': valid_brief})
            previous_end, previous_valid = finish, valid
    gate = len(accepted) == len(ROLES) and len(errors) == len(limit_errors)
    synthesis = run.get('synthesis')
    complete = False
    if synthesis is not None:
        if not gate:
            errors.append('synthesis before verified five-of-five gate')
        else:
            synth_start = instant(synthesis['started_at'])
            gate_end = max(instant(groups[role][-1]['ended_at']) for role in ROLES)
            gate_receipt = max(instant(groups[role][-1].get('result_received_at') or groups[role][-1]['ended_at']) for role in ROLES)
            if synth_start < max(gate_end, gate_receipt) or synth_start > end:
                errors.append('synthesis started before all accepted results or after run end')
            identity = profile(synthesis.get('runtime'), expected['Synthesizer'])
            profiles['Synthesizer'] = identity
            corrections = count(synthesis.get('corrections', 0), 'corrections')
            if corrections > 1:
                errors.append('synthesis correction limit exceeded')
            if synthesis['terminal_state'] == 'complete':
                synth_end = instant(synthesis['ended_at'])
                if not synth_start <= synth_end <= end or synth_end > deadline:
                    errors.append('invalid synthesis end time or deadline exceeded')
                fidelity = run.get('fidelity', {})
                fidelity_ok = fidelity.get('status') == 'passed' and isinstance(fidelity.get('evidence_ref'), str) and bool(fidelity['evidence_ref'].strip())
                if fidelity_ok:
                    checked = instant(fidelity['checked_at'])
                    fidelity_ok = synth_end <= checked <= end
                complete = identity == 'verified' and fidelity_ok and not errors
            elif synthesis['terminal_state'] not in {'running', 'error', 'timeout', 'cancelled'}:
                errors.append('invalid synthesis terminal state')
    if phase == 'not_started' and attempts:
        errors.append('not_started phase contains dispatch attempts')
    if phase == 'synthesis' and not gate:
        errors.append('synthesis phase without verified five-of-five gate')
    missing = [role for role in ROLES if role not in accepted]
    exhausted = any(len(groups[role]) >= 2 and all(a['terminal_state'] in TERMINAL for a in groups[role]) for role in missing)
    synthesis_failed = synthesis is not None and (synthesis.get('terminal_state') in {'error', 'timeout', 'cancelled'}
                         or (synthesis.get('corrections') == 1 and run.get('fidelity', {}).get('status') == 'failed'))
    if phase == 'finished' and not complete:
        errors.append('finished without verified five-role gate, Sol synthesis, and passed parent fidelity check')
    if errors or exhausted or synthesis_failed or phase == 'aborted' or (phase == 'finished' and not complete):
        status = 'Failed Council'
    elif phase == 'finished' and complete:
        status = 'Full Council completed'
    elif phase == 'not_started':
        status = 'Not started'
    else:
        status = 'In progress'
    return {'process_status': status, 'advisor_gate': gate, 'accepted_results': accepted,
            'phase': phase, 'failed_stage': ('limits' if limit_errors else 'advisor gate' if not gate else 'synthesis/fidelity') if status == 'Failed Council' else None,
            'missing_roles': missing, 'preserved_usable_briefs': preserved,
            'attempts': attempts, 'synthesis': synthesis, 'profiles': profiles,
            'excluded_attempts': exclusions, 'errors': errors,
            'limits': limits, 'usage': run['usage'],
            'verification_limits': ['Host records are not authenticated; tool sandbox/isolation and claim truth are not checked.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path, help='UTF-8 parent-maintained host ledger JSON')
    args = parser.parse_args()
    try:
        run = json.loads(args.ledger.read_text(encoding='utf-8'), object_pairs_hook=no_duplicate_keys)
        result = check_run(run)
    except (ValueError, KeyError, TypeError, AttributeError, OSError, OverflowError) as exc:
        print(json.dumps({'process_status': 'Failed Council', 'input_error': str(exc),
                          'verification_limits': ['Malformed input; retain the original ledger.']}, ensure_ascii=True))
        return 2
    # ASCII JSON also works with legacy Windows console encodings; values stay intact.
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 1 if result['process_status'] == 'Failed Council' else 0


if __name__ == '__main__':
    sys.exit(main())
