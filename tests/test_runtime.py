from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'council/scripts/check_run.py'
spec = importlib.util.spec_from_file_location('check_run', SCRIPT)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
NOW = datetime(2026, 10, 12, 12, 20, tzinfo=timezone.utc)


def metadata(role):
    return {'source': 'host-runtime', 'evidence_ref': 'host-result/' + role,
            **{k: runtime.contract()[role][k] for k in ('model', 'effort')}}


def ledger():
    attempts = []
    for role in runtime.ROLES:
        brief = {field: 'Applicable evidence or a stated limitation.' for field in runtime.FIELDS}
        brief.update(role=role, status='complete')
        attempts.append({'role': role, 'thread_id': 'thread/' + role, 'attempt': 1,
                         'started_at': '2026-10-12T12:00:00Z', 'ended_at': '2026-10-12T12:01:00Z',
                         'terminal_state': 'complete', 'runtime': metadata(role), 'brief': brief})
    return {'phase': 'finished', 'started_at': '2026-10-12T12:00:00Z',
            'finished_at': '2026-10-12T12:03:00Z',
            'limits': {'overall_deadline': '2026-10-12T12:10:00Z', 'advisor_timeout_seconds': 120,
                       'max_search_calls': 10, 'max_verification_calls': 5},
            'usage': {'search_calls': 5, 'verification_calls': 2}, 'attempts': attempts,
            'synthesis': {'started_at': '2026-10-12T12:01:00Z', 'ended_at': '2026-10-12T12:02:00Z',
                          'terminal_state': 'complete', 'runtime': metadata('Synthesizer'), 'corrections': 0},
            'fidelity': {'status': 'passed', 'checked_at': '2026-10-12T12:03:00Z',
                         'evidence_ref': 'parent/fidelity-check'}}


class RuntimeTests(unittest.TestCase):
    def check(self, run):
        return runtime.check_run(run, now=NOW)

    def failed(self, run):
        result = self.check(run)
        self.assertEqual(result['process_status'], 'Failed Council')
        return result

    def test_normal_and_limited_briefs_complete(self):
        for status in ('complete', 'limited'):
            with self.subTest(status=status):
                run = ledger()
                run['attempts'][0]['brief']['status'] = status
                self.assertEqual(self.check(run)['process_status'], 'Full Council completed')

    def test_gate_is_not_full_until_synthesis_and_parent_check(self):
        run = ledger()
        run['phase'] = 'advisors'
        del run['synthesis']
        result = runtime.check_run(run, now=datetime(2026, 10, 12, 12, 2, tzinfo=timezone.utc))
        self.assertTrue(result['advisor_gate'])
        self.assertEqual(result['process_status'], 'In progress')
        run['phase'] = 'finished'
        self.failed(run)

    def test_required_fields_role_and_status_rejected(self):
        for change in ('missing', 'empty', 'wrong-role', 'wrong-status'):
            with self.subTest(change=change):
                run = ledger()
                brief = run['attempts'][0]['brief']
                if change == 'missing': del brief['risks']
                elif change == 'empty': brief['data limits'] = ' '
                elif change == 'wrong-role': brief['role'] = 'Creative'
                else: brief['status'] = 'success'
                self.assertIn('Strategist', self.failed(run)['missing_roles'])

    def test_missing_role_and_duplicate_thread_cannot_complete(self):
        run = ledger()
        run['attempts'].pop()
        result = self.failed(run)
        self.assertEqual(result['missing_roles'], ['Audience Advocate'])
        self.assertEqual(len(result['preserved_usable_briefs']), 4)
        run = ledger()
        run['attempts'][1]['thread_id'] = run['attempts'][0]['thread_id']
        self.failed(run)

    def test_unknown_wrong_and_self_reported_profiles(self):
        for target in ('advisor', 'synthesis'):
            for fault in ('absent', 'empty', 'self', 'model', 'effort', 'ref'):
                with self.subTest(target=target, fault=fault):
                    run = ledger()
                    record = run['attempts'][0] if target == 'advisor' else run['synthesis']
                    if fault == 'absent': record['runtime'] = None
                    elif fault == 'empty': record['runtime'] = {}
                    elif fault == 'self': record['runtime']['source'] = 'advisor'
                    elif fault == 'model': record['runtime']['model'] = 'wrong'
                    elif fault == 'effort': record['runtime']['effort'] = 'low'
                    else: record['runtime']['evidence_ref'] = ''
                    self.failed(run)

    def test_host_config_provenance_is_accepted(self):
        run = ledger()
        for item in [*run['attempts'], run['synthesis']]: item['runtime']['source'] = 'host-config'
        self.assertEqual(self.check(run)['process_status'], 'Full Council completed')

    def test_cancelled_late_brief_is_preserved_not_counted_and_retry_wins(self):
        run = ledger()
        first = run['attempts'][0]
        first.update(terminal_state='cancelled', ended_at='2026-10-12T12:00:30Z')
        retry = deepcopy(first)
        retry.update(thread_id='retry/Strategist', attempt=2, terminal_state='complete',
                     started_at='2026-10-12T12:00:31Z', ended_at='2026-10-12T12:01:00Z')
        run['attempts'].append(retry)
        first['result_received_at'] = '2026-10-12T12:04:00Z'
        result = self.check(run)
        self.assertEqual(result['process_status'], 'Full Council completed')
        self.assertEqual(result['accepted_results']['Strategist']['attempt'], 2)
        self.assertIn('Strategist/1', result['preserved_usable_briefs'])
        self.assertEqual(len(result['excluded_attempts']), 1)

    def test_retry_requires_previous_termination_and_new_thread(self):
        for fault in ('running', 'overlap', 'duplicate', 'after-valid', 'number'):
            with self.subTest(fault=fault):
                run = ledger()
                first = run['attempts'][0]
                retry = deepcopy(first)
                first['terminal_state'] = 'error'
                retry.update(thread_id='retry', attempt=2, started_at='2026-10-12T12:01:00Z')
                if fault == 'running': first.update(terminal_state='running', ended_at=None)
                elif fault == 'overlap': retry['started_at'] = '2026-10-12T12:00:30Z'
                elif fault == 'duplicate': retry['thread_id'] = first['thread_id']
                elif fault == 'after-valid': first['terminal_state'] = 'complete'
                else: retry['attempt'] = 1
                run['attempts'].append(retry)
                self.failed(run)

    def test_exhausted_retry_preserves_failures(self):
        run = ledger()
        run['phase'] = 'advisors'
        del run['synthesis']
        first = run['attempts'][0]
        first['terminal_state'] = 'error'
        retry = deepcopy(first)
        retry.update(thread_id='retry', attempt=2, started_at='2026-10-12T12:01:00Z',
                     ended_at='2026-10-12T12:01:30Z')
        run['attempts'].append(retry)
        result = runtime.check_run(run, now=datetime(2026, 10, 12, 12, 2, tzinfo=timezone.utc))
        self.assertEqual(result['process_status'], 'Failed Council')
        self.assertEqual(len(result['attempts']), 6)
        third = deepcopy(retry)
        third.update(thread_id='third', attempt=3)
        run['attempts'].append(third)
        self.failed(run)

    def test_deadlines_and_late_receipt(self):
        for fault in ('advisor', 'receipt', 'overall', 'synthesis', 'fidelity'):
            with self.subTest(fault=fault):
                run = ledger()
                if fault == 'advisor': run['attempts'][0]['ended_at'] = '2026-10-12T12:02:01Z'
                elif fault == 'receipt': run['attempts'][0]['result_received_at'] = '2026-10-12T12:02:01Z'
                elif fault == 'overall': run['finished_at'] = '2026-10-12T12:10:01Z'
                elif fault == 'synthesis': run['synthesis']['started_at'] = '2026-10-12T12:00:59Z'
                else: run['fidelity']['checked_at'] = '2026-10-12T12:01:59Z'
                self.failed(run)

    def test_finished_record_is_not_expired_by_later_inspection(self):
        self.assertEqual(self.check(ledger())['process_status'], 'Full Council completed')

    def test_per_role_timeout_is_preserved(self):
        run = ledger()
        run['limits']['advisor_timeout_seconds'] = {role: 120 for role in runtime.ROLES}
        run['limits']['advisor_timeout_seconds']['Strategist'] = 30
        self.failed(run)
        run['limits']['advisor_timeout_seconds']['Strategist'] = 60
        self.assertEqual(self.check(run)['process_status'], 'Full Council completed')

    def test_usage_caps_and_invalid_counts(self):
        for key in ('search_calls', 'verification_calls'):
            run = ledger()
            run['usage'][key] = run['limits']['max_' + key] + 1
            self.failed(run)
            for value in (-1, True, 1.5):
                run['usage'][key] = value
                with self.assertRaises(ValueError): self.check(run)

    def test_later_resource_failure_does_not_mislabel_the_advisor_gate(self):
        run = ledger()
        run['usage']['verification_calls'] = 6
        result = self.failed(run)
        self.assertTrue(result['advisor_gate'])
        self.assertEqual(result['missing_roles'], [])
        self.assertEqual(result['failed_stage'], 'limits')
        self.assertNotIn('synthesis before verified five-of-five gate', result['errors'])

    def test_fidelity_missing_failed_and_correction_limit(self):
        for change in ('missing', 'failed', 'self', 'corrections', 'error'):
            run = ledger()
            if change == 'missing': del run['fidelity']
            elif change == 'failed': run['fidelity']['status'] = 'failed'
            elif change == 'self': run['fidelity']['evidence_ref'] = ''
            elif change == 'corrections': run['synthesis']['corrections'] = 2
            else: run['synthesis']['terminal_state'] = 'error'
            self.failed(run)

    def test_duplicate_json_labels_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate JSON'):
            json.loads('{"role":"Strategist","role":"Creative"}', object_pairs_hook=runtime.no_duplicate_keys)

    def test_remaining_fidelity_failure_after_correction_is_terminal(self):
        run = ledger()
        run['phase'] = 'synthesis'
        run['synthesis']['corrections'] = 1
        run['fidelity']['status'] = 'failed'
        result = runtime.check_run(run, now=datetime(2026, 10, 12, 12, 3, tzinfo=timezone.utc))
        self.assertEqual(result['process_status'], 'Failed Council')

    def test_unknown_role_bad_terminal_and_timestamps(self):
        run = ledger()
        run['attempts'][0]['role'] = 'Other'
        self.failed(run)
        run = ledger()
        run['attempts'][0]['terminal_state'] = 'success'
        self.failed(run)
        run = ledger()
        run['attempts'][0]['ended_at'] = None
        self.failed(run)
        run = ledger()
        run['started_at'] = '2026-10-12T12:00:00'
        with self.assertRaises(ValueError): self.check(run)

    def test_not_started_and_aborted(self):
        run = ledger()
        run.update(phase='not_started', attempts=[])
        del run['synthesis']
        moment = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)
        self.assertEqual(runtime.check_run(run, now=moment)['process_status'], 'Not started')
        run['phase'] = 'aborted'
        self.failed(run)

    def test_cli_utf8_space_path_and_malformed_input(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / '한글 ledger.json'
            run = ledger()
            run['attempts'][0]['brief']['recommendation'] = '조건부 권고'
            # CLI uses the real clock; keep this completed fixture in the past.
            path.write_text(json.dumps(run, ensure_ascii=False).replace('2026-10-12', '2020-01-01'), encoding='utf-8')
            output = subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), str(path)], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(output.returncode, 0, output.stdout + output.stderr)
            result = json.loads(output.stdout)
            self.assertEqual(result['process_status'], 'Full Council completed')
            self.assertEqual(result['accepted_results']['Strategist']['brief']['recommendation'], '조건부 권고')
            path.write_text('{bad', encoding='utf-8')
            output = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(output.returncode, 2)
            self.assertEqual(json.loads(output.stdout)['process_status'], 'Failed Council')


if __name__ == '__main__':
    unittest.main()
