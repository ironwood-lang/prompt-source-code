# Install and Operate PromptSourceCode

PromptSourceCode captures Codex Desktop interactions in a local Git project using storage
schema 1. Standard capture consists of a small root loader plus one project-local dedicated
instruction file. Optional hooks improve prompt matching and trusted interruption capture;
they never replace the standard path.

The root [`AGENTS.md`](../AGENTS.md) in this repository is development guidance. Never copy
it into another project.

## Canonical standard layout

The installed files are:

```text
AGENTS.md                              # existing project guidance plus the marked loader
.prompt-source/instructions-v1.md      # complete operational capture contract
.prompt-source/validate.py             # schema-1 validator invoked in read-only mode
```

The path `.prompt-source/instructions-v1.md` is frozen for instruction version 1. The
loader uses exactly:

```text
<!-- prompt-source-loader-begin -->
<!-- prompt-source-loader-end -->
```

No user-specific Codex configuration or fallback filename is part of this layout.

## 1. Install in a new or existing project

From an unpacked PromptSourceCode checkout or release, run:

```text
python3 scripts/instruction_contract.py install /path/to/project
```

The standard-library installer:

- creates `.prompt-source/instructions-v1.md` from the canonical template;
- installs `.prompt-source/validate.py` from the reviewed standard-library validator;
- creates a root `AGENTS.md` when none exists;
- otherwise preserves every existing byte and appends the loader after a blank line;
- refuses partial, duplicate, reversed, or conflicting loader markers; and
- refuses to overwrite a differing dedicated file or validator.

It does not touch nested `AGENTS.md` files, history, artifacts, Git configuration, the Git
index, or any global Codex setting. Review the resulting files before opening a new Codex
Desktop task.

For a manual installation, create `.prompt-source/`, copy
[`templates/prompt-source-instructions-v1.md`](../templates/prompt-source-instructions-v1.md)
to `.prompt-source/instructions-v1.md`, copy
[`hooks/prompt_source_core.py`](../hooks/prompt_source_core.py) to
`.prompt-source/validate.py`, then append the complete
[`AGENTS.prompt-source-loader.md`](../templates/AGENTS.prompt-source-loader.md) block to the
root `AGENTS.md`. Preserve everything outside the loader markers. If the existing file has
no final newline, add a newline and one blank line before the loader. Never append when
either marker already exists; inspect and update the one bounded block instead.

Root and nested project instructions continue to apply. The loader explicitly makes the
dedicated capture contract supplemental rather than a replacement. Its canonical path is
relative to the Git root, not the current directory, so a task opened at a nested project
directory still reads the one root installation and writes one root history.

## 2. Verify the first capture

Start a new Codex Desktop task and send a harmless prompt. After it completes, verify:

- `PROMPT_SOURCE.md` is at the Git root and starts with
  `<!-- prompt-source-schema: 1 -->`;
- Entry `000001` contains the submitted text, was created before requested work, and ends
  in a factual terminal state;
- a no-change prompt records `Changed files: None.`;
- `prompt_source_assets/` exists only when an artifact was preserved; and
- generated provenance is unstaged while ordinary project files can be staged normally.

From the project root, run:

```sh
cd "$(git rev-parse --show-toplevel)" && \
  /usr/bin/python3 .prompt-source/validate.py --validate-history
```

A successful first capture reports one valid entry and changes no files. Resolving and
changing to the Git root first makes the same command work from a nested project directory.

Standard text capture is model-mediated. Do not describe read-back as independent source
verification.

## 3. Update the loader and dedicated instructions

From the new reviewed PromptSourceCode checkout, run:

```text
python3 scripts/instruction_contract.py update /path/to/project
```

The update replaces only the bounded loader, canonical dedicated file, and project-local
validator. It preserves all root content outside the loader, every nested instruction,
`PROMPT_SOURCE.md`, and `prompt_source_assets/`. It never renumbers, normalizes, or migrates
schema-1 history.

If capture was disabled, the canonical update restores `Capture: enabled`; change that
single control back to `disabled` before the next Desktop task unless re-enabling was
intentional. Run `python3 scripts/instruction_contract.py check /path/to/project` to verify
markers, path, version, validator identity, and enforced instruction budgets.

## 4. Disable and re-enable standard capture

In the marked loader, change only:

```text
- Capture: enabled
```

to:

```text
- Capture: disabled
```

While disabled, Codex does not read the dedicated file or update/delete history and
assets. The generated-provenance Git restriction remains active. Change only `disabled`
back to `enabled` to resume; the next valid entry appends after the greatest structural
number without rewriting older entries.

Optional hooks operate separately. Disable both hook definitions and restart Desktop
before relying on this control to suspend every capture path.

## 5. Remove standard capture without deleting history

First disable optional hooks. Delete only the complete root loader block, including its
two markers, then remove `.prompt-source/instructions-v1.md` and
`.prompt-source/validate.py`. Remove `.prompt-source/` only if it is empty. Leave
`PROMPT_SOURCE.md` and `prompt_source_assets/` untouched; removal stops future standard
capture but preserves history.

Deleting captured history is a separate, explicit choice. Disable all capture paths first,
then remove `PROMPT_SOURCE.md` and `prompt_source_assets/` together. Deleting working-tree
copies cannot erase provenance already committed to Git.

## 6. Troubleshoot the instruction layout

Run:

```text
python3 scripts/instruction_contract.py check /path/to/project
```

The loader deliberately fails closed for standard capture when the dedicated file is
missing, unreadable as UTF-8, uses the wrong version or path, lacks its final marker,
exceeds a budget, or conflicts with other applicable instructions. A missing, unreadable,
stale, or conflicting `.prompt-source/validate.py` also stops capture. Codex must preserve
existing provenance, report the capture problem, and continue ordinary requested work
under the remaining project guidance.

Repair from a reviewed copy. Do not guess at a partial file, silently fall back to a
global filename, rewrite history, or remove root/nested project guidance. A stale
installation is one whose canonical path or version markers differ from the reviewed
release; use the documented update operation. If the loader has partial or duplicate
markers, repair it manually only after identifying the exact intended block boundaries.

## 7. Optionally install the inert hook files

Review [`hooks/`](../hooks/) before copying anything. In a project without hook
configuration, run from its root, substituting the reviewed checkout path:

```sh
mkdir -p .codex/hooks
cp /path/to/PromptSourceCode/hooks/prompt_source_core.py .codex/hooks/
cp /path/to/PromptSourceCode/hooks/prompt_source_hook.py .codex/hooks/
cp /path/to/PromptSourceCode/hooks/hooks.json.example .codex/hooks.json
```

If `.codex/hooks.json` exists, merge only the example `UserPromptSubmit` and `Interrupt`
groups; never overwrite unrelated definitions. Copied files are inert: they do not enable
the hooks or grant trust.

## 8. Review and trust each hook explicitly

Codex Desktop remains the capture environment. Use Codex CLI only for hook review and
trust:

1. Open the captured project in Codex CLI and run `/hooks`.
2. Review, enable, and trust the exact `UserPromptSubmit` definition.
3. Separately review, enable, and trust the exact `Interrupt` definition.
4. Exit the CLI and fully restart Codex Desktop.
5. Reopen the project and start a new Desktop task.

The tested CLI did not display raw trust hashes. Do not invent one. Trust is bound to the
exact definition; modifying a command or handler property invalidates the prior decision. Never
bypass hook trust. See the current official
[Codex hooks documentation](https://developers.openai.com/codex/hooks).

## 9. Update, disable, re-enable, or remove hooks

- **Update:** disable both definitions, replace both Python files and both reviewed
  configuration groups, re-review and trust each changed definition, then restart Desktop.
- **Disable:** disable both definitions through `/hooks`, restart Desktop, and leave the
  standard loader enabled for fallback capture.
- **Re-enable:** enable both unchanged definitions through `/hooks` and restart Desktop.
- **Remove:** disable both, restart Desktop, remove only their two configuration groups,
  and delete the two PromptSourceCode Python files. Preserve unrelated hooks and history.

## 10. Diagnose hook failures without losing fallback

Keep the standard loader enabled. Inspect the visible hook error and local stderr, confirm
`/usr/bin/python3` and both copied files, verify both exact definitions in `/hooks`, and
confirm the project is a local Git repository opened as a user-created Desktop task.
Re-review changed definitions and restart Desktop. Never bypass trust.

A guarded event-handler failure returns control without matching context, allowing one
instruction-mediated entry. Direct claim or replacement failures remain nonzero to avoid
unsafe enrichment. Never infer `Interrupted` from an unfinished standard entry.

## 11. Generated-provenance Git behavior

By default, PromptSourceCode does not stage, commit, push, publish, or upload generated
`PROMPT_SOURCE.md` or `prompt_source_assets/`. This is agent behavior, not an automatic
`.gitignore` rule, so the files stay visible for review.

The loader, `.prompt-source/instructions-v1.md`, and `.prompt-source/validate.py` are
installation files and may be tracked like other project guidance. The restriction applies
only to generated provenance; ordinary source, tests, documentation, and other project
files retain normal Git behavior.

## 12. Existing histories and other schemas

The full-inline 0.1.0 experiment does not need to remain installed. Replace it with the
new loader, dedicated file, and validator while leaving valid schema-1 history and verified
assets byte-for-byte intact. See [`COMPATIBILITY.md`](COMPATIBILITY.md).

If the history does not begin with the exact schema-1 marker, stop capture. Never
overwrite, prepend, append, or silently migrate it; preserve the file and use guidance for
the schema it declares.
