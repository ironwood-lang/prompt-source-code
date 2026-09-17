# PromptSourceCode

> The prompt history is the new source code.

PromptSourceCode preserves the complete history of human interactions that guide an
AI-assisted software project: prompts, follow-ups, steering, corrections, pasted text and
code, attachments, and pasted or attached images.

The goal is to make that history part of the project's source and provenance, so a reader
can understand not only what the code became, but also the human instructions, context,
and decisions that shaped it.

## Version 1 Direction

Version 1 targets Codex Desktop.

PromptSourceCode will provide two layers:

1. **Standard capture:** repository instructions in `AGENTS.md`. This is the complete,
   required default and must work without hooks, plugins, background services, or network
   access.
2. **Hook-assisted capture:** an explicit optional enhancement using `UserPromptSubmit`
   and `Interrupt`. Hooks improve prompt fidelity, identify mid-turn steering through turn
   metadata, and record button-only interruptions.

A skill is not part of the capture path because skill selection is conditional. Hooks do
not replace the `AGENTS.md` instructions; they enhance them.

## Canonical Project Output

All chronological text and provenance history will live in one file at the project root:

```text
PROMPT_SOURCE.md
```

Preserved binary artifacts will live in one flat directory:

```text
prompt_source_assets/
```

PromptSourceCode will not create per-prompt directories or separate input, status, result,
or runtime-context files.

## Capture Boundary

For text, PromptSourceCode preserves the exact representation delivered by Codex Desktop
to the agent. It does not claim to preserve raw keystrokes or editor state from before
Desktop serializes a submission.

Attached files can be preserved byte-for-byte when Desktop exposes their source paths.
Pasted images can be preserved byte-for-byte from the temporary files materialized by
Desktop, but those files may be encoded differently from the images that existed before
they entered the clipboard.

## Project Status

Milestone 2, the standard-capture release candidate, is complete. The standard
instructions were exercised from the first prompt in a clean disposable local Git project
using Codex Desktop 26.908.70816 (9275) on macOS 26.6.2. The run covered complex text,
follow-ups, two in-turn steering messages, correction, no-change work, attachments, image
paste fidelity, filename collision handling, repository-local and unavailable artifacts,
real Stop-button recovery, final structure, and practical Git behavior.

Post-run lifecycle checks then exercised the final enable/disable control and exposed an
ambiguous physical append. The hardened EOF verification caught and repaired that exact
failure mode in a second clean Desktop run before task work began.

Standard capture remains instruction-mediated. It requires no hook, skill, plugin,
background service, or network access, and it does not claim independent verification of
agent-visible text. The optional hook enhancement remains Milestone 3 work; version 1
release hardening remains Milestone 4 work.

See:

- [Canonical format](docs/PROMPT_SOURCE_FORMAT.md)
- [Installable standard-capture instructions](templates/AGENTS.prompt-source-standard.md)
- [Manual Codex Desktop validation checklist](docs/MANUAL_CODEX_DESKTOP_VALIDATION.md)
- [Standard-capture release-candidate evidence](docs/CODEX_DESKTOP_STANDARD_CAPTURE_VALIDATION.md)
- [Codex Desktop capture experiment](docs/CODEX_DESKTOP_CAPTURE_EXPERIMENT.md)
- [Implementation roadmap](docs/ROADMAP.md)

The root [`AGENTS.md`](AGENTS.md) governs development of PromptSourceCode itself. It is
not the end-user capture template. To prepare an end-user project, include the dedicated
template's contents in that project's root `AGENTS.md`.

Run the deterministic contract checks with:

```text
python3 -m unittest discover -s tests -v
```

## Standard Capture Lifecycle

### Install in a new or existing project

1. Use a local Git repository opened as a project in Codex Desktop. Standard capture is
   currently tested only in that environment.
2. Copy the complete contents of
   [`templates/AGENTS.prompt-source-standard.md`](templates/AGENTS.prompt-source-standard.md)
   into the project-root `AGENTS.md`. In an existing file, append the block without
   replacing unrelated project instructions. Keep the begin and end markers.
3. Leave `- Capture: enabled` unchanged. Do not install a hook, skill, plugin, background
   service, or network dependency for the standard path.
4. Begin a new Codex Desktop task. The first submission initializes the root
   `PROMPT_SOURCE.md` before requested project work. `prompt_source_assets/` appears only
   when an artifact is preserved.

The repository root [`AGENTS.md`](AGENTS.md) is development guidance for PromptSourceCode
itself. Never copy it into an end-user project; use the dedicated template above.

### Update the instruction block

Replace everything from `<!-- prompt-source-standard-begin -->` through
`<!-- prompt-source-standard-end -->`, inclusive, with the current template. Preserve all
other project instructions. Updating the block does not rewrite or renumber existing
`PROMPT_SOURCE.md` entries and does not recopy existing assets. If capture was disabled,
restore `- Capture: disabled` after replacing the block unless the project owner also
intends to re-enable it.

### Disable or re-enable future capture

Change only the template control line from `- Capture: enabled` to
`- Capture: disabled`. Existing history and assets remain untouched, but later interactions
are not added merely because the inactive block is present. The generated-history Git
restriction remains active while capture is disabled. Re-enable future capture by changing
`disabled` back to `enabled`; the next captured interaction continues after the greatest
existing structural entry number.

### Remove instructions or generated history

To remove PromptSourceCode instructions, delete the marked standard-capture block from the
project-root `AGENTS.md`. That stops future instruction-mediated capture but intentionally
does not alter `PROMPT_SOURCE.md` or `prompt_source_assets/`.

Already-generated history is ordinary local data. Keep both outputs to retain complete
provenance, or, after disabling or removing the instructions, explicitly remove the root
`PROMPT_SOURCE.md` and the entire root `prompt_source_assets/` directory together if the
history is no longer wanted. Removing only the assets leaves broken history links. If the
files were explicitly committed earlier, deleting working-tree copies does not erase them
from Git history; repository-history rewriting is a separate, destructive operation and is
outside the standard removal procedure.

## Generated History and Git

PromptSourceCode does not stage, commit, push, publish, or upload its generated
`PROMPT_SOURCE.md` or `prompt_source_assets/` unless the user explicitly requests it.

This restriction applies only to those generated provenance artifacts. It does not change
the tracked project's normal Git workflow: source code, tests, documentation, and other
project files can be committed and pushed normally. PromptSourceCode can be used in both
private and public repositories.

This is an agent-behavior restriction, not an automatic `.gitignore` rule. Generated
history normally remains visible as unstaged working-tree data so users can inspect it;
manual Git commands remain the user's responsibility.

## License

PromptSourceCode is available under the terms in [LICENSE](LICENSE).
