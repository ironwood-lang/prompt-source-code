# Milestone 6 Validation Evidence — 2026-09-17

## Status

Milestone 6 is **not yet complete**. The final candidate passes the deterministic suite
and a focused automated Codex app-task smoke, but the complete 28-case UI-only runbook was
not completed successfully against this exact candidate. Optional hooks were intentionally
not tested in this milestone run.

No additional manual repetition is requested. The two earlier manual workspaces remain
preserved as evidence; neither history was rewritten.

## Candidate architecture and size

The standard installation consists of:

- a bounded loader in the project-root `AGENTS.md`;
- `.prompt-source/instructions-v1.md`, the canonical operational contract; and
- `.prompt-source/validate.py`, a project-local standard-library schema validator invoked
  before work and finalization.

The loader supplements rather than replaces root and nested project guidance. Standard
capture uses no global Codex configuration, enabled hook, skill, plugin, background
service, or network access.

| Always-read file | Lines | Words | UTF-8 bytes | Maximum words | Maximum bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Loader file | 23 | 138 | 1,052 | 300 | 2,048 |
| Enforced loader block | — | 138 | 1,051 | 300 | 2,048 |
| Dedicated instructions | 125 | 801 | 6,058 | 900 | 6,144 |
| Enforced combined blocks | — | 939 | 7,109 | 1,200 | 8,192 |

The one-byte loader difference is its trailing file newline, which is outside the bounded
marker block measured by the installer. The validator is executable support code, not
always-read project instruction text.

## Problems found in the manual attempts

The first attempt exposed noncanonical dynamic fences, unfinished steering entries, and
an incorrect nested-task interaction classification. The second attempt exposed one
remaining fence error, active-turn messages classified as corrections, an invented
standard Stop reason, noncanonical artifact field names and links, and absolute
operator-specific paths in artifact metadata.

A final pre-run audit found that the validator command was relative to the current working
directory and therefore failed when invoked from `packages/demo`. The command now resolves
and changes to the Git root first. A deterministic nested-directory regression and a
separate app-level nested-project task both pass.

These were treated as product defects rather than reasons to ask for repeated manual
runs. The instructions now define the distinctions directly, and deterministic validation
rejects every observed malformed form.

## Deterministic validation

`python3 -m unittest discover -s tests -v` passed all **68 of 68** tests. New or tightened
coverage includes:

- the canonical loader, instruction, and validator paths;
- missing, unreadable, stale, conflicting, or truncated installation files;
- validator installation, update, and removal behavior;
- active-turn steering versus later-turn correction;
- canonical dynamic fences and newline states;
- the conservative standard incomplete reason;
- numbered artifact records, allowed kinds, exact field names and ordering, angle-bracket
  flat links, byte counts, digests, pasted-image fidelity, and unavailable artifacts;
- preservation of existing root/nested instructions, histories, and assets; and
- the existing concurrency, interruption, atomic-failure, inert-hook, no-network, and
  no-Git hook checks.

The unmatched-interrupt test also passed explicitly. Each of the four required
concurrency/failure-injection cases passed 20 consecutive invocations: **80 of 80** stress
invocations passed.

## Automated Codex app-task smoke

A fresh disposable project was prepared at
`/Users/Shared/PSC_M6_ACCEPTANCE_AUTOMATED_20260917/project`. Its installed candidate was
committed and pushed only to its local bare origin. Local `main` and `origin/main` matched
at `0f9b0a18aff68cbfd826b3ccacc6450a62679335` after the final candidate update.

The smoke produced twelve valid instruction-mediated entries and covered:

| Behavior | Outcome |
| --- | --- |
| Initial capture and ordinary follow-up | Passed |
| No-change result | Passed |
| Backtick-containing text requiring a tilde fence | Passed |
| One active turn with two steering updates | Passed; both updates were `Steering` |
| Later explicit correction | Passed; it was `Correction` with `Supersedes` |
| Existing root guidance | Passed; the expected ordinary output was created |
| Separate nested project | Passed; Entry 000012 was `Initial prompt`, nested guidance ran, and root validation succeeded |
| Four requested artifacts | Passed; bytes and SHA-256 values matched sources |
| Same-name collision | Passed; the second differing payload used `-002` |
| Unavailable artifact | Passed without invented copy, size, or digest |
| Final project-local validation | Passed with twelve entries |
| Storage topology | Passed; one history and four flat asset files |
| Generated-provenance Git behavior | Passed; history/assets remained untracked |
| Local Git synchronization | Passed; `main` and local `origin/main` were `0 0` |

The final history was 8,590 bytes with SHA-256
`bcf799faee4ac87e502354484fa6b6bde4f480e55a8731736b45fc5f79ae27a1`.

This smoke used the Codex app task API after the folder was trusted. It was not a UI-only
run and therefore does not replace the complete Desktop acceptance gate.

## Remaining acceptance gaps

- No real Stop-button action was performed against the exact final candidate. The
  canonical standard recovery rule is covered deterministically and the earlier manual
  attempts remain preserved.
- No attachment or clipboard paste was performed through the UI against the exact final
  candidate. Source-file artifact bytes and collision handling passed in the automated
  smoke; prior Desktop evidence remains separate.
- The optional-hook cases were not performed. Hooks remain optional, inert, and covered by
  deterministic tests, but no new Milestone 6 live-hook support claim is made.
- The app-task smoke cannot establish UI serialization behavior or substitute for the
  runbook's complete validator.

## Conclusion

The repeated-manual-loop failure mode has been addressed: the agent now runs the same
project-local parser before work and finalization, so the known structural defects fail
inside the task that creates them. The implementation is ready for normal development and
targeted future acceptance, but Milestone 6 must remain open until the remaining Desktop
acceptance scope is either performed once against the final candidate or explicitly
waived by the project owner.
