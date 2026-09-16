# PromptSourceCode

Include the instructions below in you AGENTS.md or CLAUDE.md file, before starting your project:

```markdown
## Prompt History

Maintain `docs/PROMPT_HISTORY.md` as a chronological, append-only record of every user input
received while working on this repository. The prompt history is part of the project's
source and provenance.

For every user input, update `docs/PROMPT_HISTORY.md` before performing the requested work.
This includes normal prompts, follow-ups, steering while a task is running, corrections,
questions, prompts that produce no code changes, pasted text or code, attached files, pasted
or attached images/screenshots, and other user-supplied artifacts.

### Rules

- Preserve the user's text verbatim. Do not summarize, rewrite, correct, clean up, or
combine prompts.
- Record each distinct user input as a separate sequential entry, including steering,
corrections, and changes of direction.
- Never delete or rewrite previous prompts because they were later corrected, contradicted,
abandoned, or superseded.
- Preserve user-supplied files and images when possible under `docs/prompt_history_assets/` and
reference them from the corresponding history entry.
- If an artifact already exists in the repository, record its repository-relative path instead
of duplicating it.
- If an original artifact cannot be copied, record its filename and type when available, plus
a concise factual description of what was supplied.
- Include an ISO 8601 timestamp with timezone when reliably available. Never invent timestamps
or other metadata.
- After completing the work, update the same history entry with a short factual `Result`
describing what happened, including important files changed or that no repository changes
were required.
- Before appending a new entry, re-read the end of `docs/PROMPT_HISTORY.md` and use the next
available sequence number. Preserve entries written by other sessions or agents.
- Do not omit sensitive input from the local history. If an apparent secret may be newly exposed
by a commit, push, or other remote action, warn the user before exposing it.
- These rules apply to any coding agent or harness working in this repository, not only Codex.
- Do not modify this section of `AGENTS.md` when recording prompts. All prompt records belong
in `docs/PROMPT_HISTORY.md`.

### `docs/PROMPT_HISTORY.md` Entry Format

Use the following format when appending entries to `docs/PROMPT_HISTORY.md`:

```markdown
## Prompt 000001

**Timestamp:** `2026-09-16T10:14:23-03:00`
**Agent:** Codex
**Model:** Astra 6
**Effort:** Extra High

### User Input

[verbatim user input]

### Attachments

- [paths to attached, referenced, pasted images or preserved artifacts, if any]

### Result

[short factual description of what the agent did in response]

Omit `Attachments` when there are no attachments or user-supplied artifacts.

The text inside square brackets above is instructional placeholder text. Do not copy those
placeholders literally into `docs/PROMPT_HISTORY.md`. Replace them with the actual user input,
artifact references, and result.

The guiding principle is: **prompts are part of the source.**
```
