# Milestone 6 Focused Desktop Preflight — 2026-09-17

## Decision

**Do not start another full manual S01–S14 run yet.** The two previously recurring
failures passed this live preflight, but artifact handling produced two confirmed
contract failures. The existing validator accepted that artifact entry, so its checks
are incomplete. No product fix or evidence rewrite was made during this preflight.

Milestone 6 remains incomplete. This report supplements, without rewriting, the
[recovery audit](MILESTONE_6_RECOVERY_20260917.md).

## Candidate and execution boundary

- Source candidate: `cc961f450f97ffcab02623858851b19aadcdd7c8` on local `milestone-6`.
- Disposable workspace: `~/Vibe/PSC_M6_PREFLIGHT_20260917_01`.
- Installed project commit: `95e3008dae6afb942558180b8074a6294007a4a6`.
- Root project: `~/Vibe/PSC_M6_PREFLIGHT_20260917_01/project`.
- Nested project: `~/Vibe/PSC_M6_PREFLIGHT_20260917_01/project/packages/demo`.
- Root task: `Milestone 6 root preflight`, ID `01a0b18b-5e8f-7590-add1-d99f4555b3bd`.
- Nested task: `Milestone 6 nested preflight`, ID `01a0b192-f391-7ec0-a6e9-9d40498b5019`.

The operator added the two projects; the development agent created the two tasks and sent
six planned requests through Codex's app-task tools. These requests arrive as
`codex_delegation` tool messages, not manually submitted Desktop `userMessage` records.
They exercise live agent behavior but do not establish UI serialization, attachment,
clipboard-paste, steering, or Stop-button acceptance. The task-tool records did not expose
model or reasoning settings; this report does not invent them.

No hooks were installed, enabled, trusted, or tested. The coordinator changed only the
loader's capture control between completed turns and restored it afterward. The root
and nested instructions, dedicated contract, and helper match the initial installation.
No earlier acceptance workspace was reused or modified.

The complete task pages, without truncated command outputs, are preserved outside the
captured project in `app-task-export.json`. The workspace also contains
`preflight-plan.json`, `before-disabled-provenance.json`, and `preflight-checks.json`.
These are developer test evidence, not capture-runtime files. They are not inputs to a
claim that the complete UI-only acceptance validator passed.

## Observed results

| Request | Actual result |
| --- | --- |
| S01, initial root request | Passed. The agent checked live state, completely read the dedicated file, used `--begin-standard` before ordinary work, and used `--finish-standard`. Entry 1 retains the supplied complex text and is `Initial prompt`; both requested root outputs have the exact bytes. |
| P02, four filesystem artifacts | Failed contract audit. All four copies and SHA-256 values are correct; both differing same-name images survive. Naming and source-kind metadata are wrong, as detailed below. |
| P03, correction to the initial request | Passed. Entry 3 is `Correction`, supersedes Entry 000001, changes the ordinary file to `CORRECTED` plus LF, and leaves earlier captured entries unchanged. |
| S12, capture disabled in the same task | Passed. The agent observed `disabled`, did not read the dedicated file or call entry creation/completion, and created the ordinary output. All five provenance files remained byte-for-byte identical. No S12 entry exists. |
| S13, capture re-enabled in that task | Passed. The agent reread the enabled state, used the helper, appended Entry 4, and created the exact ordinary output. It did not backfill S12. |
| S14, first request in a separate nested task | Passed. The nested task resolved the Git root, read root and nested guidance, used `first_in_task: true`, and created Entry 5 as `Initial prompt` in the root history. The nested sentinel output is exact; no nested history/assets were created. |

All five captured entries are `Completed` and `Instruction-mediated`. Runtime session
IDs match the two actual tasks. Prompt comparison uses the observable supplied text,
allowing only the declared `Unknown` final-newline boundary. The nested task omitted one
final LF under that boundary; this is not a text-fidelity failure.

The failed artifact request was not retried or repaired in the evidence history. The
remaining independent cases continued against the same unchanged candidate.

## Confirmed defects

### 1. Asset entry numbers lost their required padding

The agent created `prompt-2-notes.txt`, `prompt-2-binary.dat`,
`prompt-2-R-sum-Final.png`, and `prompt-2-R-sum-Final-002.png`. Schema 1 requires the entry
number exactly as displayed, so these names should use `prompt-000002-`.

The compact instructions say `prompt-<entry>-...` without spelling out that requirement.
The helper returns an integer entry number, and artifact naming remains model-written.
The current validator checks flat links but does not reject this malformed number prefix.

### 2. External requested sources were labelled as repository snapshots

All four source files live under `../inputs/artifacts/`, outside the captured project.
The agent labelled them `Repository file snapshot`; the format defines that kind for
sources inside the project. These explicitly requested external sources should be
`Requested artifact`.

The compact instructions list the allowed kinds without their distinguishing semantics.
The validator accepts a listed kind without establishing that it matches the observed
source location. The copied bytes are correct; their classification is not.

## Additional assembly ambiguity, not counted as a third confirmed schema failure

The agent passed a complete `### Artifacts` section inside the `result` argument to
`--finish-standard`. Consequently the entry contains `### Result` before `### Artifacts`.
The helper accepts structural sections inside an otherwise free-form result string.

The documented layout describes artifacts after input/runtime context and examples place
results afterward, but the specification does not explicitly state that Result must be
the last section. This observation is recorded separately rather than manufacturing
another hard acceptance failure from an ambiguous rule. The helper interface and its
documentation should agree on a clear assembly path before another manual run.

## Integrity and topology checks

The history finished at 6,087 bytes with SHA-256
`c6e2592c5d93bd136d7a6a638605a9f67b92f724da5dfff452b5834d3d8d2ca6`.
It contains five chronological entries. The assets directory contains exactly four direct
children and no per-prompt directories.

| Preserved file | Bytes | SHA-256 |
| --- | ---: | --- |
| `prompt-2-notes.txt` | 34 | `28c0632356506034aba615a14939b0631f2f3ea9cdc2bc99abb3e9ec468b6b2f` |
| `prompt-2-binary.dat` | 1,024 | `785b0751fc2c53dc14a4ce3d800e69ef9ce1009eb327ccf458afe09c242c26c9` |
| `prompt-2-R-sum-Final.png` | 70 | `afab3cd49cf0a47b361ed2b78bd43febfa7fcfd0ab49fc065d5c36c505a4da98` |
| `prompt-2-R-sum-Final-002.png` | 70 | `3759a41b8b57aa59c46ce086048042297abed9ec54a540e85449a357a792ff20` |

Each destination was independently compared with its specific source file. Before and
after S12, the history was 4,898 bytes with SHA-256
`78b1a10cf0c93a220cce0d54993fa29ba1e658d3b6dd18b03cf7882833ea2253`; exact byte comparisons
also passed for the history and all four assets.

Generated history and assets remain untracked. The disposable project's `main` and local
bare `origin/main` remain synchronized. No network Git push was performed. The development
repository contains no live capture output and its product source is unchanged by this
preflight.

## Next action

Repair artifact naming and source-kind selection, and strengthen the validator and
regressions to catch the observed failures. Prefer a deterministic artifact-writing path
over another model-written naming recipe. Resolve the helper's artifact/result assembly
interface explicitly, without rewriting this evidence or treating ambiguous legacy
layout as a newly proven failure.

Then repeat only the affected artifact check against the repaired candidate before
preparing a fresh project for the operator's full S01–S14 run. Do not ask the operator to
repeat the full sequence to diagnose these already reproduced problems. Optional-hook
cases and complete Milestone 6 acceptance remain outstanding.
