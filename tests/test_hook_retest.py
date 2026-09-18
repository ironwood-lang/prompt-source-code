"""Synthetic fixtures test the focused validator, not Desktop acceptance."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import hook_retest as retest
from tests.test_hook_completion import core, envelope, output_claim
from tests.test_hooks import prompt_event


class HookRetestTests(unittest.TestCase):
    def prepared(self, directory):
        workspace = Path(directory) / 'focused'
        with contextlib.redirect_stdout(io.StringIO()): retest.prepare(workspace)
        return workspace

    def complete_fixture(self, workspace):
        project, inputs = workspace / 'project', workspace / 'inputs'
        for installed, frozen in retest.HOOK_FILES.items():
            path = project / installed
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((workspace / 'candidate' / frozen).read_bytes())
        turns = [dict(id='turn-1', startedAt=1, status='completed', items=[]),
                 dict(id='turn-2', startedAt=2, status='completed', items=[])]
        for number, identifier in enumerate(['H00', 'H07', 'H08'], 1):
            prompt = (inputs / 'prompts' / (identifier + '.txt')).read_text()
            turn = turns[0 if number < 3 else 1]
            raw = envelope(prompt, source=str(inputs / 'notes.txt')).replace('/fixture/clipboard.png', str(inputs / 'paste-source.png')) if number == 3 else prompt
            turn['items'].append({'id': str(number), 'type': 'userMessage', 'content': [{'type': 'text', 'text': raw}]})
            if number == 1:
                turn['items'].append({'id': 'sleep', 'type': 'commandExecution', 'command': '/bin/sleep 120'})
            claim = output_claim(core.capture_prompt(project, prompt_event(project, raw, turn=turn['id'])))
            entry = core.claim_entry(project, claim)
            if number == 3:
                for source, kind in [(inputs / 'notes.txt', 'Attached file'), (inputs / 'paste-source.png', 'Pasted image')]:
                    entry = core.preserve_artifact(project, {'entry_number': 3, 'source': str(source),
                        'kind': kind, 'original_name': None if kind == 'Pasted image' else 'notes.txt',
                        'expected_entry_sha256': entry.utf8_sha256})
            request = {**claim, 'expected_entry_sha256': entry.utf8_sha256, 'result': 'Fixture result.',
                       'changed_files': [], 'interaction': ['Initial prompt', 'Correction', 'Follow-up'][number - 1]}
            if number == 2: request['supersedes'] = 1
            core.finish_hook(project, request)
        shutil.rmtree(project / '.test-transcripts')
        (project / 'hook-theme.txt').write_bytes(b'GREEN\n')
        export = workspace / 'desktop-export.json'
        export.write_text(json.dumps([{'thread': {'id': 'session-1', 'cwd': str(project)},
                                     'page': {'hasMore': False}, 'turns': turns}]))
        return export

    def test_preparation_is_fresh_isolated_inert_and_snapshotted(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = self.prepared(directory)
            self.assertFalse((workspace / 'project/.codex').exists())
            self.assertFalse((workspace / 'project/PROMPT_SOURCE.md').exists())
            self.assertEqual(len(list((workspace / 'inputs/prompts').iterdir())), 3)
            with self.assertRaises(ValueError): retest.prepare(workspace)
            with self.assertRaises(ValueError): retest.prepare(retest.ROOT / 'forbidden-retest')
            self.assertFalse((retest.ROOT / 'forbidden-retest').exists())

    def test_validator_accepts_only_complete_focused_case_evidence(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'CODEX_THREAD_ID': 'session-1'}):
            workspace = self.prepared(directory)
            export = self.complete_fixture(workspace)
            result = retest.validate(workspace, export)
            self.assertTrue(result['passed'], result['errors'])
            self.assertIn('not full Milestone 6', result['scope'])

    def test_validator_rejects_actual_h07_metadata_failure_and_extra_submission(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'CODEX_THREAD_ID': 'session-1'}):
            workspace = self.prepared(directory)
            export = self.complete_fixture(workspace)
            path = workspace / 'project/PROMPT_SOURCE.md'
            original = path.read_bytes()
            path.write_bytes(original.replace(b'- Interaction: Correction', b'- Interaction: Steering')
                             .replace(b'- Supersedes: Entry 000001\n', b''))
            result = retest.validate(workspace, export)
            self.assertIn('H07: interaction differs', result['errors'])
            self.assertIn('H07 must supersede the setup entry', result['errors'])
            path.write_bytes(original)
            pages = json.loads(export.read_bytes())
            pages[0]['turns'][1]['items'].append({'type': 'userMessage', 'id': 'extra', 'content': [{'type': 'text', 'text': 'Extra greeting.'}]})
            export.write_text(json.dumps(pages))
            self.assertFalse(retest.validate(workspace, export)['passed'])

    def test_validator_rejects_wrong_turn_changed_installation_and_artifact_bytes(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'CODEX_THREAD_ID': 'session-1'}):
            workspace = self.prepared(directory)
            export = self.complete_fixture(workspace)
            (workspace / 'project/.codex/hooks/prompt_source_hook.py').write_text('changed')
            pages = json.loads(export.read_bytes())
            pages[0]['turns'][0]['id'] = 'wrong-turn'
            export.write_text(json.dumps(pages))
            result = retest.validate(workspace, export)
            self.assertFalse(result['passed'])
            self.assertIn('H07: identity differs', result['errors'])
            self.assertTrue(any('installed hook differs' in e for e in result['errors']))
            next((workspace / 'project/prompt_source_assets').iterdir()).write_bytes(b'changed')
            with self.assertRaisesRegex(core.HistoryConflict, 'preserved copy differs'):
                retest.validate(workspace, export)


if __name__ == '__main__':
    unittest.main()
