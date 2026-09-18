# Optional Hook-Assisted Capture

PromptSourceCode's root loader, dedicated project instructions, and project-local validator
remain the complete default. The optional assets in [`../hooks/`](../hooks/) are inert until
a project owner deliberately copies the two hook Python files and installs, reviews,
enables, and trusts the hook definition.
The optional path targets Codex Desktop on macOS and uses only `UserPromptSubmit` and
`Interrupt`.

The hooks are local standard-library Python. They make no network requests and run no Git
commands. Event handlers write only the canonical root `PROMPT_SOURCE.md`; the agent
invokes the project-local [artifact helper](ARTIFACT_CAPTURE.md) for copies under the
dedicated instructions. Temporary atomic-write files exist only while
a replacement is active. Serialization locks the existing project directory itself, so
there is no persistent lock, event log, status file, or diagnostic file.

The reviewed copyable files and their exact byte counts and SHA-256 digests are frozen in
[`../tests/fixtures/distribution-manifest.json`](../tests/fixtures/distribution-manifest.json).
Copying them into `.codex/` does not enable either definition and does not grant trust.

## Install explicitly

First complete the standard installation in [`INSTALLATION.md`](INSTALLATION.md), including
the root loader, `.prompt-source/instructions-v1.md`, and `.prompt-source/validate.py`.
The standard helper now creates and finalizes instruction-mediated entries as well as
validating history. Its runtime-supplied `Session ID`, when available, does not make an
entry hook-assisted. Only hook matching context activates the hook claim path. The
standard loader control and explicit hook enablement remain separate controls.
Then, from a trusted local PromptSourceCode checkout, review these exact optional files:

- `hooks/prompt_source_core.py`
- `hooks/prompt_source_hook.py`
- `hooks/hooks.json.example`

For a project that has no existing hook configuration, explicitly copy them as follows,
substituting the path to the reviewed PromptSourceCode checkout:

```sh
mkdir -p .codex/hooks
cp /path/to/PromptSourceCode/hooks/prompt_source_core.py .codex/hooks/
cp /path/to/PromptSourceCode/hooks/prompt_source_hook.py .codex/hooks/
cp /path/to/PromptSourceCode/hooks/hooks.json.example .codex/hooks.json
```

If `.codex/hooks.json` already exists, do not overwrite it. Merge only the example's
`UserPromptSubmit` and `Interrupt` groups after reviewing both the existing definitions
and the merge. The supplied command assumes `/bin/sh` and `/usr/bin/python3`, executes
from the captured project's root, and points to
`.codex/hooks/prompt_source_hook.py`. The local shell guard preserves a handler's stderr
diagnostic but returns control to Desktop successfully so the standard instruction path
can receive the message. Agent `--claim` and `--replace-entry` commands call Python
directly and therefore retain nonzero safety failures.

Copying these files does not grant trust. Do not submit capture-sensitive prompts until
the review, trust, and restart steps below are complete if deterministic hook capture is
required. While the files are untrusted, standard instruction-mediated capture remains
active.

## Review and trust each definition

Codex Desktop ran trusted repository hooks in the completed feasibility experiment, but
the tested Desktop workflow did not expose hook trust management. Use Codex CLI only for
the explicit review-and-trust operation:

1. Open Codex CLI in the captured project.
2. Run `/hooks`.
3. Review the discovered `UserPromptSubmit` definition, including its exact command and
   source path, then explicitly enable and trust it.
4. Separately review, enable, and trust the `Interrupt` definition.
5. Exit the CLI.
6. Fully restart Codex Desktop after the trust changes, reopen the project, and begin a
   new Desktop task.

The CLI version used for Milestone 3 validation showed the exact discovered definitions
and their enabled/trusted state but did not display raw definition hashes. Review those
exact definitions; do not invent a hash or treat a missing hash display as a reason to
bypass trust.

Trust is bound to each exact hook definition. Editing the command, handler properties, or
other definition content changes its hash and invalidates the prior decision. Review and
trust the changed definition again, then restart Desktop. Never use
`--dangerously-bypass-hook-trust`, never alter managed trust data directly, and never
recommend a trust bypass. Codex CLI is not a supported PromptSourceCode capture
environment; it is used here only because `/hooks` supplies the required review-and-trust
workflow.

The current official [Codex hooks documentation](https://developers.openai.com/codex/hooks)
describes project-local discovery, hash-bound trust, and `/hooks` review. These release
instructions remain limited to behavior exercised by PromptSourceCode's Desktop
validation.

## Runtime behavior

`UserPromptSubmit` validates the event object and requires a matching project `cwd`, the
exact event name, a non-empty session ID, a non-empty turn ID, a string prompt, and the
hook-provided transcript path. It reads only the transcript's first `session_meta` record
and requires matching identifiers and project path, `originator: Codex Desktop`, and
`thread_source: user`. This fail-closed boundary excludes subagents and Desktop feature
tasks such as ambient suggestion generation even when they also emit the event. Missing,
unreadable, non-user, or mismatched metadata causes a diagnostic and standard fallback.
The hook then encodes the prompt in the canonical dynamic fence, records its final-newline
state, UTF-8 byte count, and SHA-256, and atomically appends a `Hook-assisted`, `In
progress` entry before agent work. Every invocation is a distinct observation; identical
prompt content is never a global deduplication key.

The hook returns synthetic matching context to the agent. That context contains the
entry number, session ID, turn ID, and Base64 of the exact UTF-8 prompt. It is not
user-authored input and is not copied into `### User input` or mislabeled as Codex Desktop
runtime context. The agent passes the claim object unchanged to:

```text
/usr/bin/python3 .codex/hooks/prompt_source_hook.py --claim
```

The claim helper matches the earliest `Pending` entry having the same session ID, turn
ID, and exact prompt bytes, then changes only `Agent observation: Pending` to `Claimed`.
This makes matching one-to-one and observation-ordered: two deliberately identical
submissions create and claim two entries. A hash can help inspection but never replaces
the exact-byte and identifier match.

The agent enriches the claimed entry instead of appending a duplicate. Hook-derived
classification is `Initial prompt` for the first event in a session, `Steering` for later
events with the same turn ID, and `Follow-up` for a later turn. The agent may refine a
claimed entry to `Correction`, add `Supersedes`, attach runtime context or artifact
metadata, and complete it. It must preserve the hook-captured input and identifiers.
Use `.prompt-source/validate.py --preserve-artifact` with the current entry digest for
artifact copies and metadata. Its returned digest replaces the prior digest for subsequent
enrichment. Keep previously recorded artifact facts unchanged; stale digests are rejected.

Hook-assisted entry replacements use the same core's `--replace-entry` interface. Its
stdin JSON contains `entry_number`, `session_id`, `turn_id`, `prompt_utf8_base64`, the
current `expected_entry_sha256`, and `replacement_entry_base64`. The helper acquires the
same project-directory lock, requires the expected entry digest, checks immutable input
and identifiers, rejects an agent-created `Interrupted` transition, validates the entire
history, and atomically replaces the file. If `Interrupt` wins a race, a stale agent
replacement fails instead of overwriting the interruption. If agent completion wins,
the later `Interrupt` preserves the completed entry.

If identity cannot be established safely, do not guess or delete either observation. The
agent preserves the hook entry and adds a separate `Instruction-mediated` entry with:

```text
- Deduplication note: Identity with a hook-created observation could not be established safely; both observations were preserved.
```

An instruction-created entry is never relabeled `Hook-assisted`.

`Interrupt` accepts only the exact trusted event name from the same validated Desktop
user-session boundary and locates entries by both supplied identifiers. For one active
turn containing an initiating prompt plus steering or
correction entries, it changes every matching `Hook-assisted` entry still `In progress`
to `Interrupted`, in physical order, with the exact reason `Hook-confirmed Interrupt
event.` It preserves completed entries and all captured input. No match, malformed
history, wrong schema, or uncertain identity produces no history rewrite and a diagnostic
on stderr.

## Concurrency and failure behavior

Every hook and agent-helper mutation follows the same transaction:

1. lock the already-existing project directory;
2. read and validate the whole UTF-8 schema-1 history;
3. reject malformed fences, a wrong schema marker, duplicate or non-increasing structural
   entry headings, or a stale expected entry digest;
4. calculate the update while holding the lock;
5. write and `fsync` a temporary file in the history's directory;
6. atomically replace `PROMPT_SOURCE.md` and `fsync` the directory; and
7. remove any temporary file on failure.

The writer does not silently repair unrelated corruption. If a replacement fails before
the atomic rename, the previous complete history remains in place. Successful text-only
capture creates no assets directory and leaves no persistent runtime file other than the
canonical history.

The blank line between two entries is treated as a structural separator rather than part
of the earlier entry's digest. Appending a steering or follow-up entry therefore does not
make an unchanged earlier entry appear stale during agent enrichment.

## Failure and standard fallback

Hook validation and I/O failures produce a concise stderr diagnostic and no persistent
diagnostic log. The trusted definition's local guard converts a handler failure to host
success without emitting matching context, so a failed `UserPromptSubmit` hook does not
block the message or replace standard capture. When no valid hook matching
context accompanies the user interaction—because hooks are absent, unavailable,
disabled, untrusted, or failed—the agent follows the ordinary
`Instruction-mediated` path and records the interaction before task work. Direct agent
helper failures remain nonzero so unsafe enrichment is never silently accepted.

If a hook wrote an entry but its matching context did not reach the agent, identity is
uncertain. Preserve both observations with the deduplication note rather than suppressing
one by content. Standard capture remains model-mediated and uses its existing unfinished
entry rules. It must never infer `Interrupted` without a reliable `Interrupt` event.

For diagnosis, inspect the hook's visible failure and stderr, confirm both files and the
exact definitions through `/hooks`, confirm `/usr/bin/python3` exists, and confirm the
event exposes a readable user-created Codex Desktop transcript. Then re-review changed
definitions and restart Desktop. Do not bypass trust. The deterministic repository tests
exercise parsing, Desktop-session filtering, matching, concurrency, interruption,
structural conflicts, and failed atomic replacement without requiring live hooks.

## Disable, update, re-enable, or remove

To disable the enhancement, use `/hooks` to disable both reviewed definitions (or remove
only these two groups from the project's `.codex/hooks.json`), then restart Desktop.
Leave the standard loader, dedicated file, and validator installed. Existing history and
assets remain unchanged, and new interactions use standard capture.

To update, disable both definitions, replace the two Python files and the two reviewed
configuration groups from a trusted PromptSourceCode version, review and trust the new
hash-bound definitions separately through `/hooks`, and restart Desktop. Re-enabling
without a definition change still requires a Desktop restart before validation.

Before an update writes to an existing history, confirm that its first line is the exact
schema-1 marker. A missing, malformed, incompatible, or future marker is not upgraded by
the hook; preserve the history and follow [`COMPATIBILITY.md`](COMPATIBILITY.md).

To remove the enhancement, disable both definitions, restart Desktop, remove only the
PromptSourceCode `UserPromptSubmit` and `Interrupt` groups from `.codex/hooks.json`, and
delete `.codex/hooks/prompt_source_hook.py` and
`.codex/hooks/prompt_source_core.py`. Do not delete unrelated hook definitions. Removal
does not delete `PROMPT_SOURCE.md` or `prompt_source_assets/`; standard capture continues
until its separately marked loader is disabled or removed.
