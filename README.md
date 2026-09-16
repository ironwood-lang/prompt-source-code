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

The Codex Desktop feasibility experiments are complete. The canonical history format and
standard `AGENTS.md` template are the next implementation milestone, followed by the
optional hook enhancement and release hardening.

See:

- [Codex Desktop capture experiment](docs/CODEX_DESKTOP_CAPTURE_EXPERIMENT.md)
- [Implementation roadmap](docs/ROADMAP.md)

## Generated History and Git

PromptSourceCode does not stage, commit, push, publish, or upload its generated
`PROMPT_SOURCE.md` or `prompt_source_assets/` unless the user explicitly requests it.

This restriction applies only to those generated provenance artifacts. It does not change
the tracked project's normal Git workflow: source code, tests, documentation, and other
project files can be committed and pushed normally. PromptSourceCode can be used in both
private and public repositories.

## License

PromptSourceCode is available under the terms in [LICENSE](LICENSE).
