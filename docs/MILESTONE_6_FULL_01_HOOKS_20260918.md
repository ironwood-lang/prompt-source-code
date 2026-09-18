# Milestone 6 — FULL_01 optional-hook acceptance, 2026-09-18

## Decision

**Full acceptance failed. Milestone 6 remains incomplete.** The operator reports completing
S15, H01–H11, and the final ordinary-file Git check with GPT-5.6 SOL, Medium. Complete
Desktop evidence contains every required submission. H07 failed correction metadata;
H08 failed separation of user text from the Desktop attachment envelope. These two
cases produced five diagnostics from the unmodified full validator.

The [S01–S14 standard checkpoint](MILESTONE_6_FULL_01_STANDARD_20260918.md) remains valid
and unchanged. No full manual rerun is requested. No captured entry, artifact, installation,
input fixture, frozen asset, previous report, or checkpoint was repaired or regenerated.
No implementation or acceptance criterion was changed during this audit.

The candidate remains `429e7689fc956f7929ed08f0a962e6afd869fe0b`. Development remains on
`milestone-6` at `d4576c5265edee7c321cd72f6122d890b19f6f86`; this new report is the only
additional development-repository file from the final audit. The intentional untracked
standard-checkpoint report is preserved. No commit, push, tag, release, branch, worktree,
PR, acceptance-task mutation, or hook-trust change was performed by the coordinator.

## Evidence and execution boundary

Workspace: `~/Vibe/PSC_M6_ACCEPTANCE_20260918_FULL_01`.

All pages were retrieved again through Desktop `read_thread`, following pagination for
the original root task. The resulting `desktop-export.json` contains six complete pages,
22 turns, and 28 actual user submissions from these five tasks:

| Task | Scope |
| --- | --- |
| Create PSC acceptance test files | S01–S13, including S04B and uncaptured S12 |
| Exercise nested instructions | S14 |
| Create inert hook check file | S15 |
| Create hook active marker | H01–H10, including H03A/H03B and same-turn steering |
| Create ordinary git check file | H11 |

No returned command output was truncated. The original root/nested turns are identical
to those in the preserved standard export. Task-specific execution records independently
confirm `gpt-5.6-sol` and `medium` for every one of the 22 turns. Ten actual synthetic
hook matching contexts correspond one-to-one to Entries 16–25; every decoded claim
prompt matches its stored hook input exactly, including H08's incorrectly retained
envelope. These records are observed execution evidence, not generated test submissions.

The CLI review, enable/trust, disable, and Desktop restart sequence is operator-confirmed.
The exported tasks establish the resulting capture behavior; they are not an independent
recording of those UI actions. H10's unavailable-handler setup is likewise covered by the
operator's completion confirmation; its task records the delivered message and successful
standard fallback, without a separate structured hook-stderr event in the export.

## Full validator result

Executed from the development repository, without `--standard-only`:

```sh
python3 -B scripts/desktop_acceptance.py validate \
  "$PSC_RUN_ROOT/project" \
  "$PSC_RUN_ROOT/inputs/manifest.json" \
  --instructions-relative .prompt-source/instructions-v1.md \
  --desktop-export "$PSC_RUN_ROOT/desktop-export.json" \
  --candidate-ref 429e7689fc956f7929ed08f0a962e6afd869fe0b
```

Exit code: **1**. Complete stdout was empty. Complete stderr:

```text
Desktop acceptance validation FAILED:
- unexpected or duplicate capture at Entry 000024: unlabelled
- missing captured case H08
- H07 has interaction 'Steering'
- H07 does not supersede H06
- history exposes the operator home path instead of a portable boundary
```

The exact argv, exit code, stdout, and stderr are retained in
`full-validation-result.json`. The validator was neither patched nor rerun with relaxed
conditions. A separate final-state audit produced 269 checks: 264 passed and five failed,
all associated with the same two case failures. Its diagnostic identification of Entry 24
does not convert H08 into a canonical match or waive its failure.

## Failure diagnosis

1. **H07 — wrong interaction.** Entry 23 remains `Steering` although the delivered message
   explicitly corrects H06. The actual agent replacement request retained that value;
   this was not a dropped prompt or an incorrect final task file.
2. **H07 — missing supersession.** The same replacement retained `Continues: Entry 000022`
   and omitted `Supersedes: Entry 000022`. The helper permits correction enrichment, but
   the agent did not request it; the correction rule is currently placed under the
   standard-branch heading in the compact instructions.
3. **H08 — envelope stored as user text.** Entry 24 contains the complete 586-byte Desktop
   envelope, including file notices, the safety instruction, and the request heading.
   Its first bytes therefore do not identify H08 to the case matcher, producing both the
   unexpected/unlabelled-entry and missing-H08 diagnostics. Exactly one H08 entry exists;
   there was no lost submission or duplicate H08 capture.
4. **H08 — nonportable paths.** The envelope includes an absolute home path and a temporary
   clipboard path inside `User input`. Adding a separate path-free context section later
   did not remove those runtime details from user-authored text.

The H08 synthetic matching context already contained the entire envelope before the
agent's claim. In the frozen implementation, `capture_prompt` takes `payload['prompt']`
directly into `render_entry` and the claim object. `replace_entry` correctly refuses to
change those captured bytes. The defect therefore originates at the hook's authorship
boundary; instructing the agent to rewrite this evidence would violate the immutable-input
contract. The two H08 artifacts themselves are correct and were independently compared
with their available sources.

The local schema validator accepted the history because it validates structure, integrity,
and state transitions; it does not establish whether a hook prompt includes a Desktop
envelope or whether a natural-language correction was classified correctly. The existing
correction unit test explicitly supplies corrected metadata. Passing it does not establish
that a Desktop agent will supply that metadata in practice.

## Case outcomes

The standard cases below retain their earlier results and byte-preservation checks.
`Pass` for a remaining case does not imply that full acceptance passed.

| Case | Entry | Result | Observation |
| --- | --- | --- | --- |
| S01 | 1 | Pass | Original delivered text and exact ordinary/sentinel files retained. |
| S02 | 2 | Pass | No-change result and valid repository snapshot retained. |
| S03 | 3 | Pass | Initial DARK request retained in the active steering turn. |
| S04 | 4 | Pass | BLUE steering retained separately. |
| S04B | 5 | Pass | AMBER steering retained separately. |
| S05 | 6 | Pass | Correction supersedes S04B; exact GREEN file retained. |
| S06 | 7 | Pass | Four source-identical attachments and separate context retained. |
| S07 | 8 | Pass | Source-identical repository snapshot retained. |
| S08 | 9 | Pass | Desktop-materialized pasted image and context retained. |
| S09 | 10 | Pass | Unavailable source retained without invented bytes or metadata. |
| S10 | 11 | Pass | Explicit incomplete state and absent work marker retained. |
| S11 | 12 | Pass | Conservative recovery and exact output retained. |
| S12 | None | Pass | Ordinary work exists; no capture; saved disable baseline unchanged. |
| S13 | 13 | Pass | Re-enabled capture and exact output retained. |
| S14 | 14 | Pass | Separate nested task, root history, exact nested sentinel retained. |
| S15 | 15 | Pass | One instruction-mediated initial entry; exact INERT output. |
| H01 | 16 | Pass | One claimed/completed hook entry and exact ACTIVE output. |
| H02 | 17 | Pass | Separate hook turn; no-change result; additional valid snapshot. |
| H03A | 18 | Pass | First identical submission claimed and completed separately. |
| H03B | 19 | Pass | Second identical submission claimed separately with a distinct turn ID. |
| H04 | 20 | Pass | Sleep ran; initiating request retained in the steering turn. |
| H05 | 21 | Pass | BLUE steering claimed separately in the same turn. |
| H06 | 22 | Pass | AMBER steering claimed separately in the same turn. |
| H07 | 23 | Fail | Correct GREEN output, but wrong interaction and missing supersession. |
| H08 | 24 | Fail | Both artifacts correct; complete Desktop envelope misclassified as user input. |
| H09 | 25 | Pass | Actual interrupted turn; claimed entry has trusted reason; marker absent. |
| H10 | 26 | Pass | One instruction-mediated fallback entry and exact FALLBACK output. |
| H11 | 27 | Pass | New task; one instruction-mediated initial entry and exact ORDINARY output. |
| Final Git check | N/A | Pass | Only ordinary-git-check.txt committed and pushed to the sibling bare origin. |

H01 was delivered by Desktop with a final LF, despite the clipboard fixture lacking one.
The hook preserved the actual delivered LF. H03A/H03B both arrived with two trailing LFs
and preserve those identical bytes separately. These comparisons concern Desktop's
delivered representation, not pre-serialization editor or clipboard state.

H11 initially invoked the helper without required stdin; it was rejected and retried
before task work, producing no extra entry. H02 retained an additional valid seven-byte
snapshot of `hook-active.txt` while correctly reporting `Changed files: None.`. Together
with the seven standard-phase assets and H08's two artifacts, this explains ten assets.

## Preservation, topology, and Git

The entire standard history remains an exact prefix of the final history. All seven
standard assets, the standard export, validation output, supplemental script/result,
preparation record, preflight result, and disable baseline remain unchanged. Every input,
baseline installation file, and frozen asset matches its recorded size and SHA-256.
Installed hook files match the frozen candidate byte-for-byte; H10's handler was restored.
The S14-only supplemental script was read for context and was not rerun.

Final storage is one root history with 27 entries and one flat directory with ten assets.
All ten assets were independently compared byte-for-byte with available original sources
or the preserved standard pasted-source checkpoint. H08's 236-byte temporary source was
still available, compared directly, and copied into the new final checkpoint. No identity
with an unknown pre-clipboard source is claimed.

All twelve expected ordinary files have exact bytes; both interrupted-work markers are
absent. The project contains only expected baseline files, ordinary outputs, provenance,
and the three optional hook files. No persistent extra runtime outputs exist.

Project `main`, `origin/main`, and the sibling bare origin all resolve to
`abaeb354ba69c3f52d26d0abcf51fb9073a2845d`. The only commit after installation adds
`ordinary-git-check.txt`; divergence is `0 0`. Nothing is staged. Provenance and `.codex/`
remain untracked. The origin URL remains exactly `../origin.git`. Development `main` and
`origin/main` remain at `ef0cc942643e95b5405dc5ac72e30ae134718f53`.

Instruction sizes are unchanged: loader 196 words / 1,523 UTF-8 bytes; dedicated
instructions 767 / 6,085; combined 963 / 7,608. All existing budgets remain satisfied.
Root guidance remains 188 to 220 lines, 1,661 to 1,857 words, and 12,419 to 13,944 bytes;
nested guidance remains 3 lines, 22 words, and 213 bytes. These were read from the
preserved successful checkpoint and confirmed against unchanged installation bytes;
the failed full validator did not emit a success-size summary.

Final SHA-256 values:

- History: `b14a6e06b1d657a430deab73d9b0d0400df805227de5be61d73e3ab1dd15ab46`.
- Full Desktop export: `6b9f0ba2cf73ddc912281c2e5cb129b75691ed21a77d83693b3c384d82762d2c`.

| Asset | SHA-256 |
| --- | --- |
| prompt-000002-ordinary-project.txt | `da68f54607d5f5644954096ce1597c006c5bb9f2497e07441bf064b81003ef8a` |
| prompt-000007-notes.txt | `28c0632356506034aba615a14939b0631f2f3ea9cdc2bc99abb3e9ec468b6b2f` |
| prompt-000007-binary.dat | `785b0751fc2c53dc14a4ce3d800e69ef9ce1009eb327ccf458afe09c242c26c9` |
| prompt-000007-R-sum-Final.png | `afab3cd49cf0a47b361ed2b78bd43febfa7fcfd0ab49fc065d5c36c505a4da98` |
| prompt-000007-R-sum-Final-002.png | `3759a41b8b57aa59c46ce086048042297abed9ec54a540e85449a357a792ff20` |
| prompt-000008-repository-source.txt | `cb91e693f3aba07b9b71123b44fd97a549dc0b3d4135c1d4f72f2a24cbcb9b60` |
| prompt-000009-image-001.png | `5d9eac1877263db08243aa70240e403f9c7abb6b5ada937ffc699e074c4733a5` |
| prompt-000017-hook-active.txt | `883d3bff9a26459c06c2dae4b4993c3f6bf4059f8abefb81bef9985f280237ff` |
| prompt-000024-notes.txt | `28c0632356506034aba615a14939b0631f2f3ea9cdc2bc99abb3e9ec468b6b2f` |
| prompt-000024-image-001.png | `5d9eac1877263db08243aa70240e403f9c7abb6b5ada937ffc699e074c4733a5` |

New evidence beside `project/`, separate from the preserved standard checkpoint:

- `desktop-export.json`: every actual page from all five tasks.
- `full-validation-result.json`: complete failed validator invocation/output.
- `audit_full.py` and `full-audit-result.json`: final-state checks, failures, and hashes.
- `full-checkpoint/`: final history/assets, H08 pasted-source bytes, and exact copies of
  all five task execution records.
- `full-automated-checks.json`: complete automated-test argv, exit codes, and outputs.
- `full-hygiene-result.json`: JSON, Markdown, whitespace, Git, and preservation checks.

## Automated checks and limitations

The documented full suite passed **127 tests**:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
```

The explicit unmatched-interruption test passed **1 test**:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest \
  tests.test_hooks.HookCaptureTests.test_unmatched_interrupt_is_conservative_and_byte_preserving
```

All **80 stress invocations** passed (four tests, twenty repetitions):

```sh
for iteration in $(seq 1 20); do
  PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest \
    tests.test_hooks.HookCaptureTests.test_simultaneous_prompt_processes_produce_unique_ordered_entries \
    tests.test_hooks.HookCaptureTests.test_interrupt_racing_agent_update_never_overwrites_terminal_state \
    tests.test_hooks.HookCaptureTests.test_interrupt_racing_prompt_capture_is_serialized_without_corruption \
    tests.test_hooks.HookCaptureTests.test_atomic_failure_retains_last_complete_history_and_removes_tempfile \
    || exit 1
done
```

After adding this report, all 25 format/documentation tests passed, including Markdown
fences and internal links. Repository hygiene also passed for all four repository JSON
files, whitespace including both untracked evidence reports, Git status/divergence, and
unchanged captured evidence. The untracked-file `git diff --no-index --check` commands
returned 1 because files differ from `/dev/null`, with no whitespace diagnostics; this
is not a whitespace failure. Detailed commands, raw exit codes, and their assessment are
in the separate hygiene record. No commit is included in this audit.

The recorded preparation environment is Codex Desktop 26.915.31029 build 9771,
macOS 26.6.2 build 25G83, Codex CLI 0.155.0-alpha.9, Python 3.14.7 for development,
system Python 3.9.6 for installed helpers, and Git 2.54.0 (Apple Git-157). Capture support
remains limited to Codex Desktop; CLI was used by the operator only for hook management.
Standard capture remains model-mediated. Automated helper tests do not substitute for
failed Desktop cases.

## Narrow follow-up scope

No fixes were applied. The next repair should address the hook's recognized Desktop
envelope boundary before immutable capture, retaining exact user-text bytes and safe
one-to-one claim matching. Correction classification and backward supersession also need
an explicit hook-enrichment path that does not depend on interpreting rules located under
the standard-branch heading.

Add deterministic regressions from the observed envelope shape and the correction
finalization behavior, then seek focused Desktop confirmation of the affected hook
steering/correction and attachment/paste cases in a separate disposable project. Preserve
FULL_01 as failed evidence. Do not rerun S01–S14 or prescribe another full manual run
without a demonstrated need. Neither those proposed fixes nor a future focused test can
retroactively turn this frozen candidate's full validation into a pass.
