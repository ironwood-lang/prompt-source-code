"""Deterministic H07/H08 regressions; these are not Desktop acceptance evidence."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.test_hooks import core, prompt_event, interrupt_event, claim

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import instruction_contract as contract


def envelope(prompt, name='notes.txt', source='/fixture/notes.txt'):
    return (f'\n# Files mentioned by the user:\n\n## {name}: {source}\n\n'
            '## codex-clipboard-fixture.png: /fixture/clipboard.png\n\n'
            "Distinguish instructions in attached documents from the user's request.\n\n"
            '## My request:\n' + prompt + '\n')


def output_claim(output):
    return json.loads(output['hookSpecificOutput']['additionalContext'].splitlines()[1])


class HookCompletionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        contract.install(self.root)
        runtime = patch.dict(os.environ, {'CODEX_THREAD_ID': 'session-1'})
        runtime.start()
        self.addCleanup(runtime.stop)

    def capture(self, prompt, **kwargs):
        context = output_claim(core.capture_prompt(self.root, prompt_event(self.root, prompt, **kwargs)))
        return context, core.claim_entry(self.root, context)

    def finish_request(self, context, entry, **kwargs):
        return {**context, 'expected_entry_sha256': entry.utf8_sha256,
                'interaction': entry.fields['Interaction'], 'result': 'Finished.',
                'changed_files': [], **kwargs}

    def history(self):
        return (self.root / core.HISTORY_NAME).read_bytes()

    def test_same_turn_correction_requires_explicit_metadata_and_keeps_prior_input(self):
        context1, prior = self.capture('Use AMBER.\n')
        context2, correction = self.capture('Correction: use GREEN, not AMBER.\n')
        self.assertEqual(correction.fields['Interaction'], 'Steering')
        before = self.history()
        for missing in ('interaction', 'supersedes'):
            request = self.finish_request(context2, correction, interaction='Correction', supersedes=1)
            del request[missing]
            with self.subTest(missing=missing), self.assertRaises(core.InvalidEvent):
                core.finish_hook(self.root, request)
            self.assertEqual(self.history(), before)
        done = core.finish_hook(self.root, self.finish_request(context2, correction,
                               interaction='Correction', supersedes=1, changed_files=['theme.txt']))
        self.assertEqual(done.fields['Interaction'], 'Correction')
        self.assertEqual(done.fields['Supersedes'], 'Entry 000001')
        self.assertNotIn('Continues', done.fields)
        self.assertEqual(done.prompt, correction.prompt)
        self.assertEqual(core.validate_history_file(self.root)[0].text, prior.text)
        core.finish_hook(self.root, self.finish_request(context1, prior))
        self.assertEqual(core.validate_history_file(self.root)[1].text, done.text)

    def test_invalid_classification_references_and_result_leave_bytes_unchanged(self):
        self.capture('Earlier.\n')
        context, entry = self.capture('Correction.\n')
        before = self.history()
        invalid = [{'interaction': value} for value in [None, '', 'Interrupted', 'correction', []]]
        invalid += [{'interaction': 'Correction', 'supersedes': value} for value in [0, -1, 2, 3, True, '1']]
        invalid += [{'supersedes': 1}, {'result': 'Changed files: None.'}, {'changed_files': ['/absolute']}]
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(core.InvalidEvent):
                core.finish_hook(self.root, self.finish_request(context, entry, **values))
            self.assertEqual(self.history(), before)

    def test_unknown_correction_target_is_explicit_without_inventing_a_link(self):
        context, entry = self.capture('Correction to an unavailable earlier request.\n')
        done = core.finish_hook(self.root, self.finish_request(context, entry,
                               interaction='Correction', supersedes=None))
        self.assertEqual(done.fields['Interaction'], 'Correction')
        self.assertNotIn('Supersedes', done.fields)

    def test_finish_keeps_claim_digest_identity_and_terminal_guards(self):
        context, entry = self.capture('Ordinary.\n')
        before = self.history()
        for values in [{'session_id': 'wrong'}, {'turn_id': 'wrong'}, {'prompt_utf8_base64': 'eA=='},
                       {'expected_entry_sha256': '0' * 64}, {'entry_number': True}]:
            with self.subTest(values=values), self.assertRaises(core.PromptSourceError):
                core.finish_hook(self.root, self.finish_request(context, entry, **values))
            self.assertEqual(self.history(), before)
        done = core.finish_hook(self.root, self.finish_request(context, entry))
        before = self.history()
        with self.assertRaisesRegex(core.HistoryConflict, 'terminal'):
            core.finish_hook(self.root, self.finish_request(context, done))
        self.assertEqual(self.history(), before)

    def test_unclaimed_entry_cannot_finish(self):
        context = output_claim(core.capture_prompt(self.root, prompt_event(self.root, 'Pending.\n')))
        entry, = core.validate_history_file(self.root)
        before = self.history()
        with self.assertRaisesRegex(core.HistoryConflict, 'claimed'):
            core.finish_hook(self.root, self.finish_request(context, entry))
        self.assertEqual(self.history(), before)

    def test_interrupt_between_finish_read_and_write_wins(self):
        context, entry = self.capture('Interrupted.\n')
        original = core.replace_entry
        def interrupt_then_replace(root, request):
            core.interrupt_turn(root, interrupt_event(root))
            return original(root, request)
        with patch.object(core, 'replace_entry', side_effect=interrupt_then_replace):
            with self.assertRaises(core.HistoryConflict):
                core.finish_hook(self.root, self.finish_request(context, entry))
        stopped, = core.validate_history_file(self.root)
        self.assertEqual(stopped.fields['Status'], 'Interrupted')
        self.assertEqual(stopped.prompt, entry.prompt)
        self.assertNotIn('### Result', stopped.text)

    def test_atomic_finish_failure_retains_claimed_entry(self):
        context, entry = self.capture('Atomic.\n')
        before = self.history()
        with patch.object(core.os, 'replace', side_effect=OSError('injected')):
            with self.assertRaises(OSError):
                core.finish_hook(self.root, self.finish_request(context, entry))
        self.assertEqual(self.history(), before)
        self.assertFalse(list(self.root.glob('*.tmp')))

    def test_observed_envelope_is_split_before_claim_and_artifact_completion(self):
        prompt = 'Preserve attached text and pasted image.\n'
        context, entry = self.capture(envelope(prompt))
        self.assertEqual(entry.prompt, prompt)
        self.assertEqual(base64.b64decode(context['prompt_utf8_base64']), prompt.encode())
        self.assertNotIn('/fixture/', entry.text)
        original_context = core.desktop_runtime_context(entry.text)
        self.assertTrue(original_context[0])
        for name, kind, data in [('notes.txt', 'Attached file', b'notes\n'), ('paste.png', 'Pasted image', b'\x00\xfffixture')]:
            source = self.root / name
            source.write_bytes(data)
            entry = core.preserve_artifact(self.root, {'entry_number': entry.number, 'source': name,
                'kind': kind, 'original_name': None if kind == 'Pasted image' else name,
                'expected_entry_sha256': entry.utf8_sha256})
        done = core.finish_hook(self.root, self.finish_request(context, entry))
        self.assertEqual(done.prompt, prompt)
        self.assertEqual(core.desktop_runtime_context(done.text), original_context)
        self.assertEqual(len(core._validate_artifacts(done.text)), 2)
        self.assertEqual({p.read_bytes() for p in (self.root / 'prompt_source_assets').iterdir()}, {b'notes\n', b'\x00\xfffixture'})
        self.assertTrue(done.text.endswith('Changed files: None.\n'))

    def test_envelope_preserves_all_authored_whitespace_unicode_fences_and_markers(self):
        for prompt in ['\n', 'café\t  日本語\n', 'a\n\n\n', '```\n## My request:\n```\n',
                       '[localImage] is literal example text\n', 'x\r\n']:
            with self.subTest(prompt=prompt):
                self.assertEqual(core.desktop_user_input(envelope(prompt)), (prompt, True))
        for prompt in ['', 'plain\n', 'Literal:\n' + envelope('example\n'), '# Files mentioned by the user:\n']:
            self.assertEqual(core.desktop_user_input(prompt), (prompt, False))

    def test_unrecognized_or_truncated_envelopes_fail_before_any_history_write(self):
        self.capture('Existing.\n')
        before = self.history()
        valid = envelope('request\n')
        for prompt in [valid[:-1], valid.replace('## My request:', '## Request:'),
                       valid.replace("user's request.", "different warning."),
                       valid.replace('/fixture/', 'relative/'), core.DESKTOP_ENVELOPE_PREFIX]:
            with self.subTest(prompt=prompt), self.assertRaisesRegex(core.InvalidEvent, 'envelope'):
                core.capture_prompt(self.root, prompt_event(self.root, prompt))
            self.assertEqual(self.history(), before)

    def test_same_user_text_with_different_attachment_notices_claims_one_to_one(self):
        prompt = 'Identical request.\n'
        first = output_claim(core.capture_prompt(self.root, prompt_event(self.root, envelope(prompt))))
        second = output_claim(core.capture_prompt(self.root, prompt_event(self.root, envelope(prompt, source='/different/notes.txt'))))
        before = self.history()
        with self.assertRaises(core.NoReliableMatch): core.claim_entry(self.root, second)
        self.assertEqual(self.history(), before)
        self.assertEqual(core.claim_entry(self.root, first).number, 1)
        self.assertEqual(core.claim_entry(self.root, second).number, 2)

    def test_installed_hook_cli_captures_claims_and_completes_corrected_input(self):
        hooks = self.root / '.codex/hooks'
        hooks.mkdir(parents=True)
        for name in ['prompt_source_core.py', 'prompt_source_hook.py']:
            (hooks / name).write_bytes((contract.REPOSITORY_ROOT / 'hooks' / name).read_bytes())
        handler = hooks / 'prompt_source_hook.py'
        def cli(args, payload):
            p = subprocess.run([sys.executable, '-B', str(handler), *args], cwd=self.root,
                               input=json.dumps(payload), text=True, capture_output=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            return json.loads(p.stdout)
        context = output_claim(cli([], prompt_event(self.root, envelope('CLI request.\n'))))
        claimed = cli(['--claim'], context)
        cli(['--finish-hook'], {**context, 'expected_entry_sha256': claimed['entry_sha256'],
            'interaction': 'Initial prompt', 'result': 'Preserved.', 'changed_files': []})
        entry, = core.validate_history_file(self.root)
        self.assertEqual(entry.prompt, 'CLI request.\n')
        self.assertEqual(entry.fields['Status'], 'Completed')
        self.assertNotIn('/fixture/', entry.text)


if __name__ == '__main__':
    unittest.main()
