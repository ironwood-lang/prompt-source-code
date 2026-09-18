#!/usr/bin/env python3
"""Prepare and validate only H07/H08, with one same-turn correction prerequisite."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import desktop_acceptance as acceptance

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_FILES = (
    'templates/AGENTS.prompt-source-loader.md', 'templates/prompt-source-instructions-v1.md',
    'hooks/prompt_source_core.py', 'hooks/prompt_source_hook.py', 'hooks/hooks.json.example',
    'scripts/instruction_contract.py', 'scripts/desktop_acceptance.py', 'scripts/hook_retest.py',
    'tests/fixtures/artifacts.json',
)
HOOK_FILES = {
    '.codex/hooks/prompt_source_core.py': 'hooks/prompt_source_core.py',
    '.codex/hooks/prompt_source_hook.py': 'hooks/prompt_source_hook.py',
    '.codex/hooks.json': 'hooks/hooks.json.example',
}
SETUP = ('PSC acceptance H00. Run `/bin/sleep 120`, then create `hook-theme.txt` containing '
         'exactly `AMBER` followed by one LF. Remain responsive to steering while the command runs.\n')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(workspace: Path) -> None:
    workspace = workspace.resolve()
    if workspace == ROOT or ROOT in workspace.parents:
        raise ValueError('retest must be outside the development repository')
    if workspace.exists():
        raise ValueError('refusing to reuse an existing retest workspace')
    acceptance.instruction_contract.validate_pair(
        (ROOT / SNAPSHOT_FILES[0]).read_text(), (ROOT / SNAPSHOT_FILES[1]).read_text())
    workspace.mkdir(parents=True)
    candidate = workspace / 'candidate'
    for relative in SNAPSHOT_FILES:
        target = candidate / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    project, inputs = workspace / 'project', workspace / 'inputs'
    project.mkdir()
    (inputs / 'prompts').mkdir(parents=True)
    (project / 'AGENTS.md').write_text('# Focused hook retest project\n\nKeep ordinary task files in this project.\n')
    subprocess.run([sys.executable, '-B', str(candidate / 'scripts/instruction_contract.py'),
                    'install', str(project)], check=True, stdout=subprocess.PIPE)
    cases = {c['id']: c['prompt'] for c in acceptance._acceptance_cases('unused')}
    for identifier, prompt in [('H00', SETUP), ('H07', cases['H07']), ('H08', cases['H08'])]:
        (inputs / 'prompts' / (identifier + '.txt')).write_bytes(prompt.encode())
    fixture = json.loads((candidate / 'tests/fixtures/artifacts.json').read_bytes())
    artifacts = {a['id']: a for a in fixture['artifacts']}
    (inputs / 'notes.txt').write_bytes(base64.b64decode(artifacts['attached-text']['payload_base64']))
    (inputs / 'paste-source.png').write_bytes(base64.b64decode(artifacts['pasted-image']['pre_clipboard_payload_base64']))
    git = acceptance._run_git
    git(project, 'init', '-b', 'main')
    git(project, 'config', 'user.name', 'PromptSourceCode Acceptance')
    git(project, 'config', 'user.email', 'acceptance@example.invalid')
    git(project, 'add', 'AGENTS.md', '.prompt-source')
    git(project, 'commit', '-m', 'test: install focused H07 H08 candidate')
    record = {
        'schema': 1, 'scope': 'H00 prerequisite, H07 correction, H08 artifacts; no Desktop prompts submitted',
        'project': str(project), 'repository_head_at_preparation': git(ROOT, 'rev-parse', 'HEAD'),
        'repository_status_at_preparation': git(ROOT, 'status', '--short'),
        'candidate_sha256': {name: digest(candidate / name) for name in SNAPSHOT_FILES},
        'input_sha256': {p.relative_to(inputs).as_posix(): digest(p) for p in inputs.rglob('*') if p.is_file()},
        'installation_sha256': {p.relative_to(project).as_posix(): digest(p)
            for p in project.rglob('*') if p.is_file() and '.git' not in p.parts},
        'installation_commit': git(project, 'rev-parse', 'HEAD'),
        'hooks_installed': False, 'hooks_trusted': False,
        'model': 'gpt-5.6-sol', 'effort': 'medium',
    }
    (workspace / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n')
    print(f'Prepared focused retest: {workspace}\nProject: {project}\nNo hooks installed or trusted; no prompts submitted.')


def validate(workspace: Path, export: Path, pasted_source: Path | None = None) -> dict:
    workspace = workspace.resolve()
    project, inputs, candidate = workspace / 'project', workspace / 'inputs', workspace / 'candidate'
    prep = json.loads((workspace / 'preparation.json').read_bytes())
    errors = []
    def check(condition, message):
        if not condition: errors.append(message)
    check(prep['schema'] == 1 and Path(prep['project']) == project, 'preparation belongs to a different project')
    for group, base in [('candidate_sha256', candidate), ('input_sha256', inputs), ('installation_sha256', project)]:
        for name, expected in prep[group].items():
            check((base / name).is_file() and digest(base / name) == expected, f'{group} changed: {name}')
    for installed, frozen in HOOK_FILES.items():
        check((project / installed).is_file() and (project / installed).read_bytes() == (candidate / frozen).read_bytes(),
              'installed hook differs from snapshot: ' + installed)
    pages = json.loads(export.read_bytes())
    observations = acceptance.read_desktop_export(export, project)
    turns = {(p['thread']['id'], t['id']): t for p in pages for t in p['turns']}
    messages = [i for t in turns.values() for i in t['items'] if i['type'] == 'userMessage']
    check(len({p['thread']['id'] for p in pages}) == 1, 'use one new Desktop task')
    check(all(Path(p['thread']['cwd']).resolve() == project for p in pages), 'task must use the root project')
    check(len(messages) == 3 and set(observations) == {'H00', 'H07', 'H08'}
          and all(len(v) == 1 for v in observations.values()), 'need exactly setup, H07, and H08 once each')
    entries = acceptance.core.validate_history_file(project)
    records = []
    check(len(entries) == 3, 'need exactly three history entries')
    expected_interactions = ['Initial prompt', 'Correction', 'Follow-up']
    for number, (identifier, interaction) in enumerate(zip(['H00', 'H07', 'H08'], expected_interactions), 1):
        if len(entries) < number or len(observations.get(identifier, [])) != 1:
            continue
        entry, observed = entries[number - 1], observations[identifier][0]
        check(entry.number == number and entry.prompt == observed['prompt'], identifier + ': exact delivered user text differs')
        check(entry.fields['Interaction'] == interaction, identifier + ': interaction differs')
        check(entry.fields['Status'] == 'Completed' and observed['turn_status'] == 'completed', identifier + ': not completed')
        check(entry.fields['Capture method'] == 'Hook-assisted' and entry.fields.get('Agent observation') == 'Claimed', identifier + ': not a claimed hook entry')
        check(entry.fields.get('Session ID') == json.dumps(observed['session_id']) and entry.fields.get('Turn ID') == json.dumps(observed['turn_id']), identifier + ': identity differs')
        check(entry.final_newline == acceptance.core._split_final_newline(observed['prompt'])[1], identifier + ': newline differs')
    if all(len(observations.get(key, [])) == 1 for key in ['H00', 'H07', 'H08']):
        first, correction, artifact = [observations[key][0] for key in ['H00', 'H07', 'H08']]
        check(first['first_in_task'], 'setup was not the first submission')
        check(first['turn_id'] == correction['turn_id'] != artifact['turn_id'], 'H07 must correct setup in the same active turn; H08 must follow')
        check(any(i['type'] == 'commandExecution' and '/bin/sleep 120' in i['command']
                  for t in turns.values() if t['id'] == first['turn_id'] for i in t['items']), 'setup sleep was not executed')
    if len(entries) == 3:
        check(entries[1].fields.get('Supersedes') == 'Entry 000001', 'H07 must supersede the setup entry')
        check(acceptance.reports_no_task_changes(entries[2]), 'H08 must report no task-work changes')
        context = acceptance.core.desktop_runtime_context(entries[2].text)
        check(context is not None and bool(context[0].strip()), 'H08 runtime context missing')
        records = acceptance.core._validate_artifacts(entries[2].text)
        check(sorted(r['Kind'] for r in records) == ['Attached file', 'Pasted image'], 'H08 must contain exactly its attachment and paste')
        check(acceptance.PASTED_FIDELITY in entries[2].text.splitlines(), 'pasted-image fidelity boundary missing')
    history = (project / acceptance.core.HISTORY_NAME).read_text()
    check(str(Path.home()) not in history and '/var/folders/' not in history, 'runtime absolute path leaked into history')
    check((project / 'hook-theme.txt').is_file() and (project / 'hook-theme.txt').read_bytes() == b'GREEN\n', 'H07 ordinary output differs')
    assets = sorted((project / 'prompt_source_assets').iterdir()) if (project / 'prompt_source_assets').is_dir() else []
    check(len(assets) == 2 and all(p.is_file() for p in assets), 'need two flat preserved assets')
    references = re.findall(r'\]\(<(prompt_source_assets/[^>]+)>\)', history)
    check(len(references) == 2 and set(references) == {p.relative_to(project).as_posix() for p in assets}, 'asset references differ')
    for asset in assets:
        if not asset.is_file(): continue
        check(f'- Byte count: {asset.stat().st_size}' in history and f'- SHA-256: {digest(asset)}' in history, 'asset metadata differs: ' + asset.name)
    check(any(p.is_file() and p.read_bytes() == (inputs / 'notes.txt').read_bytes() for p in assets), 'attached bytes differ')
    raw = next((part['text'] for i in messages for part in i['content']
                if part['type'] == 'text' and 'PSC acceptance H08.' in part['text']), '')
    if pasted_source is None:
        match = re.search(r'^## codex-clipboard-[^:]+: (.+)$', raw, re.M)
        pasted_source = Path(match[1]) if match else None
    check(pasted_source is not None and pasted_source.is_file(), 'actual Desktop pasted-source evidence unavailable')
    if pasted_source is not None and pasted_source.is_file():
        check(any(p.is_file() and p.read_bytes() == pasted_source.read_bytes() for p in assets), 'Desktop pasted bytes differ')
    for record in records:
        match = re.search(r'\]\(<(prompt_source_assets/[^>]+)>\)', record.get('Preserved copy', ''))
        if not match:
            check(False, 'artifact lacks its preserved copy'); continue
        asset = project / match[1]
        source = inputs / 'notes.txt' if record['Kind'] == 'Attached file' else pasted_source
        if source is not None and source.is_file():
            check(asset.read_bytes() == source.read_bytes(), record['Kind'] + ': classified artifact bytes differ')
    git = acceptance._run_git
    check(git(project, 'rev-parse', 'HEAD') == prep['installation_commit'], 'unexpected project commit')
    check(not git(project, 'remote'), 'focused project must have no remote')
    check(not git(project, 'ls-files', 'PROMPT_SOURCE.md', 'prompt_source_assets', '.codex'), 'capture files are tracked')
    check(not git(project, 'diff', '--cached', '--name-only') and not git(project, 'diff', '--name-only'), 'staged or tracked changes present')
    expected = set(prep['installation_sha256']) | set(HOOK_FILES) | {'PROMPT_SOURCE.md', 'hook-theme.txt'} | set(references)
    actual = {p.relative_to(project).as_posix() for p in project.rglob('*') if p.is_file() and '.git' not in p.parts}
    check(actual == expected, 'unexpected project files or missing expected files')
    result = {'passed': not errors, 'errors': errors, 'scope': 'Focused H07/H08 only; not full Milestone 6 acceptance',
              'history_sha256': digest(project / 'PROMPT_SOURCE.md'), 'export_sha256': digest(export),
              'asset_sha256': {p.name: digest(p) for p in assets if p.is_file()}}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    setup = sub.add_parser('prepare'); setup.add_argument('workspace', type=Path)
    audit = sub.add_parser('validate'); audit.add_argument('workspace', type=Path)
    audit.add_argument('--desktop-export', type=Path, required=True)
    audit.add_argument('--pasted-source', type=Path, help='previously preserved actual Desktop temporary image, if needed')
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            prepare(args.workspace); return 0
        result = validate(args.workspace, args.desktop_export, args.pasted_source)
        print(json.dumps(result, indent=2)); return 0 if result['passed'] else 1
    except (OSError, ValueError, KeyError, TypeError, acceptance.core.PromptSourceError) as exc:
        print(f'Focused retest failed: {exc}', file=sys.stderr); return 1


if __name__ == '__main__':
    raise SystemExit(main())
