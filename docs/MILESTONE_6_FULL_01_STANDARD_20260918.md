# Milestone 6 — FULL_01 standard Desktop acceptance, 2026-09-18

## Decision

**The S01–S14 standard-capture checkpoint passed.** No repeat of this phase is
required. Continue with S15 and H01–H11 in the same workspace, following the
[complete runbook](MILESTONE_6_CODEX_DESKTOP_ACCEPTANCE.md#install-inert-optional-hooks-s15).
Full Milestone 6 acceptance remains incomplete until the optional-hook phase and final
Git checks have actually been performed and validated.

The candidate remains frozen at `429e7689fc956f7929ed08f0a962e6afd869fe0b`.
No source, template, test, installation, captured entry, or artifact was repaired during
this audit. No acceptance criteria were relaxed. Earlier evidence reports are unchanged.

## Run and evidence boundary

The operator completed the UI-only sequence in
`~/Vibe/PSC_M6_ACCEPTANCE_20260918_FULL_01/project`, opening `packages/demo` as a
separate Desktop project for S14. Both tasks used `gpt-5.6-sol`, `medium` effort,
verified for all 12 turns from their task-specific execution records.

- Root task: `Create PSC acceptance test files`,
  `01a0b432-d3f6-7132-b528-e94a7a77df9f`.
- Nested task: `Exercise nested instructions`,
  `01a0b446-f327-7141-b7e8-4d4fc1a5663a`.

Three complete task-export pages retain 15 actual Desktop user submissions, including
S04B and the intentionally uncaptured S12. These are UI user messages, not delegated
test prompts reconstructed as user messages. The history contains 14 chronological
schema-1 entries and seven preserved assets. Captured text was compared with the actual
Desktop-delivered representation, not assumed identical to the clipboard fixture.
Final-newline uncertainty remains explicit where applicable.

The command record shows complete dedicated-instruction reads before enabled capture
and requested work. S12 observed disabled capture and performed its ordinary work
without reading the dedicated instructions or creating an entry. S14 resolved the
root installation from the nested project and retained both instruction scopes.

## Required cases and factual outcomes

| Case | Entry | Outcome |
| --- | --- | --- |
| S01 | 1 | Completed. Delivered whitespace, Unicode, embedded heading, and code fence preserved; root sentinel and ordinary file have exact expected bytes. |
| S02 | 2 | Completed follow-up. Exact contents reported; `Changed files: None.`; one valid repository snapshot also retained. |
| S03 | 3 | Completed. Sleep ran; DARK request retained and superseded before task-file changes. |
| S04 | 4 | Completed steering entry. BLUE request retained separately and superseded before task-file changes. |
| S04B | 5 | Completed steering entry. AMBER request retained separately and superseded by S05. |
| S05 | 6 | Completed correction superseding Entry 5. `ui-theme.txt` contains exactly GREEN plus LF. |
| S06 | 7 | Completed. All four attached files have correct classification, separate context, and byte-identical copies; differing same-named images have collision-safe names. Result: `Changed files: None.` |
| S07 | 8 | Completed. Correct repository-source link and byte-identical snapshot. Result: `Changed files: None.` |
| S08 | 9 | Completed. Correct pasted-image classification, separate context, no invented filename, and a byte-identical copy of Desktop's 236-byte temporary image. Result: `Changed files: None.` |
| S09 | 10 | Completed. Missing requested source marked unavailable, without invented bytes, hash, or preserved copy. Result: `Changed files: None.` |
| S10 | 11 | Incomplete, as required. Desktop records an interrupted turn; the work marker does not exist; no interruption reason was invented. |
| S11 | 12 | Completed. Conservative recovery retained Entry 11 as incomplete; recovery file has exact expected bytes. |
| S12 | None | Capture disabled. Ordinary disabled-check file created; no entry; prior history and all seven assets remain unchanged. |
| S13 | 13 | Completed after re-enabling, with the uncaptured-predecessor condition acknowledged and exact ordinary output. |
| S14 | 14 | Completed initial entry in the separate nested task, appended only to root history. Nested sentinel has exact expected bytes; root and nested guidance unchanged. |

## Non-blocking observations

1. S02 initially supplied an array instead of a scalar continuation number. S04 initially
   used a correction-only supersedes field for steering. Both requests were rejected
   without changing history and corrected automatically before task-file work; neither
   produced a duplicate entry. These were recovered model-call mistakes, not silent
   successful requests.
2. S06–S09 unnecessarily supplied `provenance_changes_requested: true`, contrary to the
   routine-capture instruction. Every request also supplied `changed_files: []`, so this
   flag had no effect: all four results correctly report no task-work changes. This is
   an instruction-following deviation, not a recurrence of the earlier reporting defect.
3. S02 captured an additional valid eight-byte repository snapshot. This explains seven
   assets rather than the standard phase's minimum six; it did not change the source
   file or falsely report a task-work change.

These observations do not invalidate the required output checks, but prevent claiming
perfect model compliance. No repair or additional manual run is requested for them.

## Validation and preservation

The unmodified `scripts/desktop_acceptance.py validate` command with `--standard-only`,
the actual Desktop export, and the frozen candidate reference returned exit code 0:
`Desktop standard-capture acceptance validation PASSED`. Its complete output is retained.
The installed history validator also reported 14 valid entries. All 145 supplemental
audit checks passed, including independent source/copy byte comparisons for all seven
assets, exact ordinary outputs, unchanged preparation inputs and installation hashes,
and matching frozen candidate files.

The S12 baseline history hash matches the exact current prefix through Entry 12, and
all seven baseline asset hashes still match. S13 and S14 only append later entries.
The temporary pasted source was independently compared and copied into the external
checkpoint before it could disappear; no claim is made about unknown pre-paste bytes.

Local evidence under `~/Vibe/PSC_M6_ACCEPTANCE_20260918_FULL_01/` includes:

- `desktop-standard-export.json`: complete original task pages.
- `standard-validation-result.json`: validator command, exit status, complete output.
- `audit_standard.py` and `standard-audit-result.json`: supplemental checks and results.
- `standard-checkpoint/`: exact history, assets, disable baseline, and pasted-source copy.

SHA-256 values:

- History: `446a12c22ac025e41283554032974fc6afb936ab6d86c9ec2c16dc68322be240`.
- Desktop export: `0f8bad5897f0b7b3e353391fd2d1436177f3741a05c7e8cfe3529a0fd9b3c086`.

## Architecture, Git, and remaining scope

The marked root loader still resolves `.prompt-source/instructions-v1.md`, with the
local `.prompt-source/validate.py` helper. Sizes remain 196 words / 1,523 UTF-8 bytes
for the loader, 767 / 6,085 for dedicated instructions, and 963 / 7,608 combined.
All enforced maximums pass: 300 / 2,048, 900 / 6,144, and 1,200 / 8,192 respectively.

There is exactly one root history and one flat assets directory; no nested histories,
extra capture runtime files, or project hook installation exist. Ordinary outputs are
limited to the seven expected files. Provenance is untracked, and nothing is staged.
Project HEAD, `origin/main`, and the sibling local bare origin remain synchronized at
`44197b1a57442fc93c53ce82a38799d490f7e203`.

Development work remains local on `milestone-6`. This report is the only repository
change; no code, release asset, or previous report changed. Local development `main`
and `origin/main` still resolve to `ef0cc942643e95b5405dc5ac72e30ae134718f53`.
No generated provenance or bytecode caches exist in the development repository.
No commit, push, release, tag, or hook-trust change was made during this audit.

The preflight's 127-test suite, explicit unmatched-interruption test, and 80 repeated
concurrency/failure checks are recorded in `preflight-result.json`; this audit did not
rerun them or change the tested implementation. Standard capture now has fresh full
S01–S14 Desktop UI confirmation without hooks. It remains model-mediated, supported
only in Codex Desktop. S15 and H01–H11 have not run on FULL_01, so **Milestone 6 is not
yet complete**.
