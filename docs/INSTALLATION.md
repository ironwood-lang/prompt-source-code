# Install and Operate PromptSourceCode 0.1.0

PromptSourceCode 0.1.0 captures Codex Desktop interactions in a local Git project and
implements storage schema 1.
Standard capture is the complete default. Optional hooks improve prompt matching and
record trusted interruptions, but they do not replace the standard instructions.

The root [`AGENTS.md`](../AGENTS.md) in this repository is development guidance. Do not
copy it into another project. Use the dedicated standard template below.

## 1. Install standard capture in a new project

1. Create or open a local Git repository as a project in Codex Desktop.
2. Copy the complete contents of
   [`templates/AGENTS.prompt-source-standard.md`](../templates/AGENTS.prompt-source-standard.md)
   to the new project's root `AGENTS.md`.
3. Keep `- Capture: enabled` unchanged.
4. Start a new Codex Desktop task in that project.

The first user submission should create the root `PROMPT_SOURCE.md` before requested
project work. Its first line must be:

```text
<!-- prompt-source-schema: 1 -->
```

`prompt_source_assets/` is created only when an artifact is preserved. Standard capture
requires no hook, skill, plugin, background service, Python process, or network service.

## 2. Add standard capture to an existing `AGENTS.md`

Append the entire template block to the existing root `AGENTS.md`. Preserve unrelated
project instructions. The copied block starts and ends with:

```text
<!-- prompt-source-standard-begin -->
<!-- prompt-source-standard-end -->
```

Do not copy this development repository's root `AGENTS.md`, and do not replace an
existing project's unrelated instructions.

## 3. Verify the first capture

After the first Desktop task completes, verify:

- `PROMPT_SOURCE.md` is at the repository root and begins with the exact schema-1 marker;
- Entry `000001` contains one `### User input` section and a completed factual result;
- a prompt that changed no task-work file says `Changed files: None.`;
- `git status --short` shows generated provenance as unstaged or untracked unless its
  inclusion was explicitly requested; and
- ordinary project files can still be staged and committed normally.

Do not describe standard model-mediated capture as independent verification of the
source message.

## 4. Update the standard instruction block

Replace the complete marked block, including both markers, with the block from the new
PromptSourceCode version. Preserve everything outside the markers. Do not rewrite,
renumber, or normalize existing `PROMPT_SOURCE.md` entries and do not recopy existing
assets.

If capture was disabled before the update, restore `- Capture: disabled` after copying
the new block unless the project owner also intends to re-enable it.

## 5. Disable and re-enable standard capture

Change only:

```text
- Capture: enabled
```

to:

```text
- Capture: disabled
```

Existing history and assets stay untouched. The Git restriction in the block remains
active. Change `disabled` back to `enabled` to resume; the next captured entry continues
after the greatest existing structural entry number.

Optional hooks run outside this control. Disable both hook definitions separately before
relying on the control line to suspend all capture.

## 6. Remove the standard instructions

Delete only the marked standard-capture block from the project-root `AGENTS.md`. This
stops future instruction-mediated capture without deleting history.

If the history itself is no longer wanted, first disable or remove every capture path,
then explicitly remove `PROMPT_SOURCE.md` and `prompt_source_assets/` together. Removing
only the assets leaves broken links. If provenance was committed previously, deleting
working-tree files does not erase Git history.

## 7. Optionally install the inert hook files

Review the final files in [`hooks/`](../hooks/) before copying them. In a project with no
existing hook configuration, run these commands from its root, substituting the reviewed
PromptSourceCode checkout path:

```sh
mkdir -p .codex/hooks
cp /path/to/PromptSourceCode/hooks/prompt_source_core.py .codex/hooks/
cp /path/to/PromptSourceCode/hooks/prompt_source_hook.py .codex/hooks/
cp /path/to/PromptSourceCode/hooks/hooks.json.example .codex/hooks.json
```

If `.codex/hooks.json` exists, merge only the example's `UserPromptSubmit` and `Interrupt`
groups. Do not overwrite unrelated definitions. Copying the files is inert: it neither
activates nor trusts the hooks.

## 8. Review and trust each hook explicitly

Use Codex CLI only for hook review and trust; Codex Desktop remains the capture
environment.

1. Open Codex CLI in the captured project and run `/hooks`.
2. Review, enable, and trust the exact `UserPromptSubmit` definition.
3. Separately review, enable, and trust the exact `Interrupt` definition.
4. Exit the CLI and fully restart Codex Desktop.
5. Reopen the project and begin a new Desktop task.

The tested CLI did not display raw trust hashes. Do not invent them. Trust is bound to
the exact definition's hash, so modifying a command or handler property invalidates the
prior decision. Never bypass hook trust. The current official
[Codex hooks documentation](https://developers.openai.com/codex/hooks) describes the
hash-bound review model and `/hooks` workflow.

## 9. Update, disable, re-enable, or remove the hooks

- **Update:** disable both definitions, replace both Python files and both configuration
  groups from a reviewed release, review and trust each changed definition again, then
  restart Desktop.
- **Disable:** disable both definitions through `/hooks`, then restart Desktop. Leave the
  standard block enabled for fallback capture.
- **Re-enable unchanged definitions:** enable both through `/hooks`, then restart Desktop
  before validating capture.
- **Remove:** disable both definitions, restart Desktop, remove only the two
  PromptSourceCode groups, and delete the two PromptSourceCode Python files. Preserve
  unrelated hooks and existing history.

## 10. Diagnose hook failures without losing the fallback

If a prompt is not hook-assisted:

1. Preserve the standard block and its `Capture: enabled` setting.
2. Inspect the visible hook error and local stderr diagnostic.
3. Confirm `/usr/bin/python3` exists and the two installed Python files match the reviewed
   release copies.
4. Use `/hooks` to confirm both exact definitions are enabled and trusted.
5. Confirm the project is a local Git repository opened in Codex Desktop and the event
   exposes a readable user-created Desktop transcript.
6. Re-review any changed definition and fully restart Desktop.

A guarded handler failure returns control to Desktop without hook matching context, so
the standard instructions can create an `Instruction-mediated` entry. Direct agent
claim/replacement failures remain nonzero to prevent unsafe enrichment. Never infer
`Interrupted` from an unfinished entry and never bypass trust while troubleshooting.

## 11. Understand Git behavior

By default, PromptSourceCode does not stage, commit, push, publish, or upload generated
`PROMPT_SOURCE.md` or `prompt_source_assets/`. This is an agent-behavior rule, not an
automatic `.gitignore` rule. The files normally remain visible for inspection.

The restriction applies only to generated provenance. Source, tests, documentation, and
other ordinary project files retain the project's normal Git workflow.

## 12. Upgrade an earlier installation

Read [`COMPATIBILITY.md`](COMPATIBILITY.md), replace only the marked standard block, and
leave existing schema-1 history and assets byte-for-byte intact. Update optional hook
files through the disable-copy-review-trust-restart sequence above.

If the history's first line is not the exact schema-1 marker, stop. Do not overwrite,
append, or silently migrate it. Preserve the file and use guidance for the schema it
declares. PromptSourceCode 0.1.0 does not ship an automatic migration tool.
