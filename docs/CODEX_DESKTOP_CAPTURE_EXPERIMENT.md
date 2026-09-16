# Codex Desktop Capture Experiment

## Status

Completed on 2026-09-16 using a disposable local project in Codex Desktop, with Codex
CLI used only to review and trust the experimental hooks.

The experiment first evaluated whether repository-level `AGENTS.md` instructions could
preserve the user interaction history needed by PromptSourceCode. A subsequent disposable
hook experiment evaluated deterministic prompt and interruption capture in Desktop.

## Scope

The experiment covered:

1. Text containing misspellings, repeated spaces, blank lines, Unicode, Markdown, and
   nested code fences.
2. A normal follow-up after task completion.
3. Two steering messages sent while a turn was active.
4. An attached PDF with a known source file.
5. An attached PNG with a known source file.
6. The same image pasted through the clipboard.
7. A turn interrupted by the user before completion.
8. `UserPromptSubmit` delivery for an initial prompt and a mid-turn steering message.
9. `Interrupt` delivery when the user pressed Stop during an active turn.
10. Repository-local hook discovery, review, trust, and execution in Desktop.

The experiment did not test Codex CLI as a coding environment, the Codex IDE extension,
cloud execution, or other coding agents. Codex CLI was used only for `/hooks` trust
management because Desktop did not expose an equivalent workflow in this experiment.

## Results

| Case | Result | Conclusion |
| --- | --- | --- |
| Complex text | Passed with an accepted fidelity boundary | Codex preserved the exact text representation delivered to the agent. |
| Follow-up | Passed | The follow-up was preserved as a separate entry. |
| Mid-turn steering | Passed | Both steering messages were recorded separately and in order before the turn completed. |
| Attached PDF | Passed | The copied PDF was byte-identical to the source file. |
| Attached PNG | Passed | The copied PNG was byte-identical to the source file. |
| Pasted image | Passed with an accepted fidelity boundary | Codex copied the PNG materialized by Codex Desktop byte-for-byte. The materialized PNG was pixel-identical but not binary-identical to the original file. |
| User interruption | Partially passed | The initiating prompt was recorded, but the button-only interruption was not. |
| Hook prompt capture | Passed after CLI trust | Desktop emitted `UserPromptSubmit` for both the initial prompt and the mid-turn steering message. |
| Hook interruption capture | Passed after CLI trust | Desktop emitted `Interrupt` when the user pressed Stop. |
| Desktop hook onboarding | Failed as a Desktop-only workflow | Desktop ran trusted hooks but did not provide a discovered review-and-trust interface; `/hooks` in Codex CLI was required. |

## Detailed Findings

### Text fidelity

Codex preserved the agent-visible text, including spelling errors, whitespace, tabs,
Unicode characters, Markdown, code fences, and the final newline.

Codex Desktop had already serialized some user input before delivering it to the agent.
Observed examples included an HTML space entity and a transformed Markdown link. The
agent copied that serialized representation faithfully.

PromptSourceCode therefore defines text fidelity as:

> The exact text representation delivered by Codex Desktop to the Codex agent.

PromptSourceCode does not claim to preserve raw keystrokes or editor state from before
Codex Desktop processes the submission.

Text capture performed through `AGENTS.md` remains model-mediated. Reading the resulting
file back and hashing it proves the integrity of the stored file, but does not independently
prove equality with the source message. Result records must not describe model read-back as
independent verification.

### Follow-ups and steering

The initial instruction and two steering messages were stored as three distinct entries.
Their file timestamps showed that the steering messages were written during the active turn
and before the result records were produced.

This demonstrates that repository instructions can preserve corrections, superseded
directions, and changes of intent without rewriting earlier history.

### Attached files

Codex Desktop exposed filesystem paths for the attached PDF and PNG. Codex copied both
artifacts into the project and verified the source and destination with SHA-256.

The PDF source and captured copy were both 1,266,984 bytes with SHA-256:

```text
b536084ff3cb9348e6a4a2f3fbb18eeab643ae2c50295dacedb2591e53665ac6
```

The attached PNG source and captured copy were both 1,192,930 bytes with SHA-256:

```text
987021540010256dbc2ee5f722ff21b75657744d5f40cbee3c8dd049cb34eb4a
```

Both binary comparisons succeeded.

### Pasted images

Codex Desktop materialized the pasted image as a temporary PNG under `/var/folders/`.
Codex copied that temporary file into the project before it disappeared.

The temporary PNG and captured project copy were both 1,433,435 bytes with SHA-256:

```text
d11aff3b59211a894e7e28f45df59e24de960f563e43e317931f83c2b3e5c8f6
```

The clipboard-materialized PNG was not binary-identical to the original attached PNG. It
had a different byte count, a different SHA-256 value, and an explicit sRGB profile.
Decoding both images produced identical dimensions and identical pixel-channel values.

PromptSourceCode therefore distinguishes:

- **Attached file:** preserve the original file byte-for-byte.
- **Pasted image:** preserve the file materialized and delivered by Codex Desktop
  byte-for-byte. Do not claim that it retains the unknown pre-paste encoding.

If original encoding, metadata, signatures, animation, layers, steganographic content, or
file hashes matter, the user should attach the image as a file instead of pasting it.

### Codex Desktop runtime context

For attachments, Codex Desktop added an agent-visible envelope containing the file name,
source path, a safety instruction, and a `My request` section. This material was not wholly
authored by the user.

For images, the experimental agent also wrote synthetic `<image>` tags that were not part
of the textual user-message field. Those tags must not be represented as verbatim user
input in the final format.

The implementation must distinguish, within the same history entry:

- User-authored input.
- Codex Desktop runtime context, when it differs.
- Artifact metadata and preservation details.

### Interruption

The prompt that began the interrupted turn was stored successfully. After the user stopped
the turn, no result or interruption record was written.

Repository instructions cannot make an already stopped agent record the stop action. An
unfinished entry can indicate that work did not complete, but it cannot distinguish a user
interruption from an application exit, crash, shutdown, or other failure.

The instructions-only implementation will use an explicit status lifecycle:

1. Create the entry with `In progress` before acting on the prompt.
2. Change it to `Completed` and add the factual result when work finishes.
3. Leave it `In progress` if the turn ends unexpectedly.
4. On a later interaction, an unfinished prior entry may be marked `Incomplete`, with the
   reason stated as unavailable rather than invented.

The successful `Interrupt` experiment confirms that an optional hook can record a user
interruption explicitly.

### Hook feasibility experiment

A disposable repository-local hook logged the raw JSON received on standard input for
`UserPromptSubmit` and `Interrupt`. Each record also stored the raw byte count, SHA-256,
and Base64 so the captured bytes could be checked independently of JSON parsing.

The first attempt did not run because the disposable directory was not yet a Git
repository. Codex uses `.git` as the default project-root marker, so the repository-local
`.codex/hooks.json` was not in an active project configuration layer. After initializing
the disposable repository, the hooks were discoverable but still skipped because their
exact definitions had not been trusted.

Codex Desktop did not expose a hook review-and-trust interface during the experiment.
Using `/hooks` in Codex CLI created separate hash-bound trust records for
`UserPromptSubmit` and `Interrupt`. After restarting Desktop and opening a new task, both
hooks executed successfully. Changing either hook definition will invalidate the matching
trust decision and require another review.

The final Desktop run produced four records in chronological order:

1. `UserPromptSubmit` for the initial prompt.
2. `UserPromptSubmit` for a steering message sent while the same turn was active.
3. `UserPromptSubmit` for a prompt that began a new turn.
4. `Interrupt` when the user pressed Stop during that new turn.

The initial prompt and steering message shared the same `session_id` and `turn_id`. The
next prompt had a new `turn_id`, and the `Interrupt` event used that same new turn ID. This
provides deterministic linkage between steering messages, ordinary turns, and the turn
that was interrupted.

Every event contained:

- `session_id`
- `transcript_path`
- `cwd`
- `hook_event_name`
- `model`
- `permission_mode`
- `turn_id`

`UserPromptSubmit` additionally contained `prompt`. `Interrupt` did not contain a prompt
or user-authored explanation. The three prompt values matched the Desktop task transcript,
including their final newline. All raw byte counts, SHA-256 values, Base64 round trips, and
parsed JSON comparisons succeeded.

The hook therefore solves two limitations of model-mediated `AGENTS.md` capture:

1. It receives the agent-visible prompt string deterministically before submission.
2. It records a button-only interruption and identifies the affected turn explicitly.

The hook does not capture pre-serialization editor state or raw keystrokes. Its fidelity
boundary remains the text representation Codex Desktop submits to the Codex runtime.
This hook run tested text prompts and interruption only. It did not establish that the
`prompt` string contains structured attachment or pasted-image data, so binary artifact
preservation still depends on the separately tested Desktop file access and capture logic.

### Hook product implications

The Desktop hook runtime itself passed. The onboarding experience did not pass the
Desktop-only, out-of-the-box requirement because the user had to open Codex CLI and trust
each hook through `/hooks`. Packaging the hook in a plugin would not remove this issue:
plugin hooks use the same trust review process and are not trusted automatically.

Consequently, hooks should not be mandatory for the first Desktop release unless Desktop
adds an accessible hook trust interface. They remain valuable as an optional advanced
enhancement for deterministic prompt capture and explicit interruption records.

## Agreed Storage Format

All chronological text and provenance history will be maintained in one canonical file at
the repository root:

```text
PROMPT_SOURCE.md
```

Each numbered entry will contain the user input, optional Codex Desktop runtime context,
artifact metadata, capture-fidelity statement, status, and result. Follow-ups, corrections,
and steering messages will be separate sequential entries.

Binary artifacts cannot be embedded in Markdown without undesirable encoding and size
overhead. They will be preserved in one assets directory and referenced from
`PROMPT_SOURCE.md`:

```text
prompt_source_assets/
├── prompt-000006-voucher_surf.pdf
├── prompt-000007-IronwoodWrench.png
└── prompt-000008-image-001.png
```

The implementation will not create per-prompt directories or separate `input.md`,
`status.md`, `result.md`, or runtime-context files.

## Generated History Git Policy

PromptSourceCode may create and update `PROMPT_SOURCE.md` and
`prompt_source_assets/` locally. It must not stage, commit, push, publish, or upload those
generated provenance artifacts unless the user explicitly requests it.

This default applies only to PromptSourceCode's generated history and assets. It does not
restrict normal Git operations for source code, tests, documentation, or other files in the
tracked project.

## Conclusions

An `AGENTS.md`-based implementation is viable as the first Codex Desktop version. It
successfully preserved ordinary prompts, follow-ups, steering, attached files, and pasted
images under the fidelity definitions above.

Trusted hooks work in Codex Desktop and improve two areas:

1. Deterministic capture of the prompt string without asking the model to reproduce it.
2. Explicit recording of button-only interruption events.

However, the tested Desktop build did not offer a complete hook trust workflow. Requiring
Codex CLI solely for `/hooks` would violate the intended Desktop-first, straightforward
onboarding experience. PromptSourceCode v1 should therefore keep hooks optional and must
remain useful without them. Hook-based capture can become the preferred path if Desktop
later provides a direct, understandable trust interface.
