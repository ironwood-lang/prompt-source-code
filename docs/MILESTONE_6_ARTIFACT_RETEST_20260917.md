# Milestone 6 Focused Artifact Retest — 2026-09-17

## Result

**Passed: both reproduced artifact defects are resolved in this focused live retest.**
All 50 audit checks passed. No implementation change or evidence repair was made during
the run. This follows the [artifact repair](MILESTONE_6_ARTIFACT_REPAIR_20260917.md) and
preserves the [failed preflight](MILESTONE_6_PREFLIGHT_20260917.md) unchanged.

This result does not complete Milestone 6 or count as a full UI-only acceptance run.
No additional manual S01–S14 sequence was required to diagnose or retest these defects.

## Candidate and execution boundary

- Source candidate: `fc9af97991513687eca268f759bc3b107394891f`, local `milestone-6`.
- Disposable workspace: `~/Vibe/PSC_M6_ARTIFACT_RETEST_20260917_01`.
- Saved Desktop project: `PSC_M6_RETEST`, folder `project` inside that workspace.
- Installation commit: `36b7ea80706623499bf6aef4a5dcef3475fac492`.
- Task: `Milestone 6 artifact retest`, ID `01a0b230-42a7-7603-860c-fbcc2443d48a`.
- Turn: `01a0b230-4439-7b01-86e9-402f11ad0969`, completed without error.

The operator added the fresh project. The coordinator dispatched the exact four-source
P02 request from the failed preflight, without adding helper commands or expected names
to the request. All source fixtures came from `scripts/desktop_acceptance.py prepare`.
Because this was the new task's first request, the capture is Entry 000001 rather than
the failed preflight's Entry 000002.

Dispatch used the app-task tool. Its observable input is a `codex_delegation` tool message,
not a manually submitted Desktop `userMessage`. This exercises live instruction following
and filesystem artifact preservation, not UI attachment/paste serialization. No model or
reasoning setting was exposed by the task records, so neither is asserted here. No hooks
were installed, enabled, trusted, or exercised.

The complete task export, including all 15 command executions and untruncated outputs,
is saved as `app-task-export.json` outside the capture project. `retest-plan.json` contains
the exact request and expected mappings; `retest-checks.json` records the 50 checks and
file hashes. These are developer evidence, not capture-runtime dependencies or outputs.

## Observed behavior

The task checked live capture state and completely read the installed dedicated file
before creating its entry. It used `--begin-standard` with `first_in_task: true`, then
called `--preserve-artifact` once per source, omitting `kind` for all four filesystem
requests. It validated the unfinished history, used `--finish-standard`, and validated
the completed history. Every command returned success.

The intermediate output shows `In progress` before finalization. The final entry is
`Completed`, `Initial prompt`, and `Instruction-mediated`, with the actual runtime task
ID. Its text matches the supplied prompt body; the omitted final LF is covered by its
declared `Final newline: Unknown` boundary. This is not a claim about raw UI keystrokes.

All four records are correctly `Requested artifact`, because their sources are outside
the captured project. Each original name, link, destination byte count/digest, source
byte count/digest, and fidelity statement was checked. Artifacts precede the result;
no artifact Markdown was inserted into the free-form result argument.

| Preserved file | Bytes | SHA-256 |
| --- | ---: | --- |
| `prompt-000001-notes.txt` | 34 | `28c0632356506034aba615a14939b0631f2f3ea9cdc2bc99abb3e9ec468b6b2f` |
| `prompt-000001-binary.dat` | 1,024 | `785b0751fc2c53dc14a4ce3d800e69ef9ce1009eb327ccf458afe09c242c26c9` |
| `prompt-000001-R-sum-Final.png` | 70 | `afab3cd49cf0a47b361ed2b78bd43febfa7fcfd0ab49fc065d5c36c505a4da98` |
| `prompt-000001-R-sum-Final-002.png` | 70 | `3759a41b8b57aa59c46ce086048042297abed9ec54a540e85449a357a792ff20` |

The audit compared each destination's bytes directly with its specific original source,
not just with the model's report. The two same-named image sources have different hashes;
both survived under separate canonical names. No unavailable record or placeholder was
substituted. The installed read-only validator reports one valid entry.

Final history: 3,217 bytes, SHA-256
`c6f6be66c1bf5cb6649f0e303287414e4ba2039b0d79a6f8b3a1fd28e51c7fe4`.
Entry digest: `2a6676d2c731179ef66267f26f012f4a03b46c7b61e2c5e123f2ac9a12b93f17`.

## Regression, Git, and topology checks

During this retest the full 108-test suite passed again on `/usr/bin/python3` 3.9.6.
All ten selected race/failure tests passed 20 times each: the four required hook tests,
two standard-path tests, and four artifact tests. The explicit unmatched-interruption
test passed separately in the same 201-check run. The prior repair report records the
additional complete Python 3.14.7 suite pass; this live retest did not change product code.

The only new files inside the disposable project are the root history and four direct
children of the flat assets directory. All are untracked and unstaged. Ordinary tracked
files, root/nested instructions, installation files, and the installation commit are
unchanged. There are no hook files, per-prompt directories, or extra runtime sidecars.
The project's `main` remains synchronized with its local bare `origin/main`.

The development repository remains on local `milestone-6`, without live capture output.
Development `main`, `origin/main`, and the live remote main were checked at
`ef0cc942643e95b5405dc5ac72e30ae134718f53`. Nothing was pushed to GitHub; no tag, release,
release body, or published artifact was changed. Only this new report is added to source
control by the retest; prior reports and captures remain untouched.

## Remaining acceptance scope

The focused artifact check is complete and has no observed errors. There is no reason to
repeat S01–S14 merely to diagnose these two fixed defects. A complete acceptance claim
still requires the documented UI-only cases actually to be performed and the corresponding
validator to pass. This retest does not credit attachments, clipboard pastes, mid-turn
steering, Stop-button behavior, or optional-hook cases. Codex Desktop remains the only
supported capture environment; model-mediated text and UI-kind selection retain their
documented limitations. Milestone 6 is not marked complete.
