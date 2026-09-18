# Milestone 6 — H07/H08 repair preparation, 2026-09-18

## Outcome and boundary

The two defects identified in the [FULL_01 hook audit](MILESTONE_6_FULL_01_HOOKS_20260918.md)
have local implementation fixes and automated regression coverage. **Desktop confirmation
of the repaired candidate is pending. Milestone 6 remains incomplete.** FULL_01 still has
its original failed result; no captured evidence or previous report was repaired.

The [focused operator guide](MILESTONE_6_H07_H08_RETEST.md) repeats H07 and H08 with one
prerequisite submission, H00. H00 requests AMBER after a running sleep so H07 can correct
it to GREEN in the same active turn. This is three submissions in one new Local task,
using GPT-5.6 SOL, Medium. It does not repeat or claim new results for the other cases.

## Repairs

**H07:** Correction classification now appears before both capture branches in the
dedicated instructions. Hook completion uses `--finish-hook`, which requires an explicit
interaction type and, for a correction, an explicit earlier entry number or `null` when
the target is unknown. A known correction target replaces the provisional continuation
with `Supersedes`. Result rendering uses the existing structured result contract.

The helper does not infer natural-language intent; classification remains agent-mediated.
It makes that decision explicit and rejects missing or malformed completion metadata.
Existing identity, claim, digest, immutable-input, atomic-write, and interruption guards
remain enforced by the guarded replacement path. Lower-level replacement remains
available; the normal instructions now direct completion through the structured helper.

**H08:** The hook separates the observed Desktop attachment/paste envelope before
creating immutable user input and its matching claim. File/path notices and the runtime
heading become a path-free context summary. User text retains its whitespace, Unicode,
fences, and literal markers; only the recognized envelope separator is removed.

The parser accepts the observed envelope shape. A changed or truncated envelope with
the recognized prefix fails before a history write, leaving standard capture available.
This is not a claim to support every future Desktop serialization. Artifact preservation
still requires the actual delivered source paths and retains the existing fidelity rules.

The README, optional-hook guide, format specification, technical reference, roadmap, and
current distribution manifest are aligned. The historical release manifest and the full
Desktop acceptance validator were not changed.

## New regression coverage

Twelve completion tests cover explicit correction metadata, unknown targets without
fabrication, invalid inputs without mutation, identity/digest/claim enforcement,
interruption races, atomic failure, envelope separation before claim, exact text bytes,
artifact preservation, malformed-envelope fallback, repeated matching, and the installed
hook command path.

Four focused-run tests cover fresh inert preparation, complete evidence validation,
rejection of the original H07 metadata defect and extra submissions, wrong turn IDs,
changed installed hooks, and artifact tampering. These use explicitly synthetic temporary
fixtures to test the validator; they are not Desktop acceptance evidence.

## Automated checks

The complete repository suite passed **143 tests** in 4.229 seconds:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
```

The installed command's system Python also passed all **16 new regression tests**:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m unittest \
  tests.test_hook_completion tests.test_hook_retest -v
```

The explicit unmatched-interrupt check passed **1 test**:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest \
  tests.test_hooks.HookCaptureTests.test_unmatched_interrupt_is_conservative_and_byte_preserving
```

All **80 required stress invocations** passed: twenty repetitions of these four tests,
with `PYTHONDONTWRITEBYTECODE=1` and `python3 -B -m unittest`:

```text
tests.test_hooks.HookCaptureTests.test_simultaneous_prompt_processes_produce_unique_ordered_entries
tests.test_hooks.HookCaptureTests.test_interrupt_racing_agent_update_never_overwrites_terminal_state
tests.test_hooks.HookCaptureTests.test_interrupt_racing_prompt_capture_is_serialized_without_corruption
tests.test_hooks.HookCaptureTests.test_atomic_failure_retains_last_complete_history_and_removes_tempfile
```

The focused workspace retains `automated-checks.json` (the full-suite completion segment
and complete system-Python regression output) and `stress-checks.json` (every exact argv,
exit code, stdout, and stderr for the unmatched and stress runs). Final documentation,
JSON, shell syntax, whitespace, installation, Git, and preservation checks are recorded
separately in `preflight-result.json`. No automated fixture counts as a performed UI case.

## Prepared retest candidate

Workspace: `~/Vibe/PSC_M6_H07_H08_RETEST_20260918_01`.

The preparation script froze nine source files under `candidate/`, installed only
standard capture into `project/`, and created H00/H07/H08 prompt files plus the text and
image inputs. It initialized an isolated disposable Git repository with one local
installation commit, `3148bf6c738c9cd77d9c9d60e58eeed8735baa03`, and no remote. No project
hooks, history, or preserved-assets directory exist at handoff. No trust change or
acceptance submission was performed by the coordinator.

This is a snapshot of uncommitted repairs on development HEAD
`d4576c5265edee7c321cd72f6122d890b19f6f86`, not the original candidate commit. Its exact
source, input, installation hashes, and development status are in `preparation.json`.
Key SHA-256 values:

- Dedicated instructions: `77bb47e62cdcb9eab2f498557aad1e73c2ef343dba40fae7c4648ab712815b1b`.
- Core and installed validator: `1b85919cfc1f6ec6deacd9adc39d0590a50d02af86e0de391918d137afbedc42`.
- Focused preparation/validator: `40f9a28ae471453ff859692d1dd14f1a5b80af088bd5b47ca854948ff79a9dd9`.

Instruction budgets remain unchanged. The loader is 196 words / 1,523 bytes; dedicated
instructions are 766 words / 6,129 bytes; combined, 962 words / 7,652 bytes. All maximums
pass, including the 6,144-byte dedicated-instruction limit. The frozen installation check
passes against the new project.

## Preservation and remaining work

FULL_01's final history and ten assets still match its full checkpoint and audit hashes.
The standard checkpoint history and its seven assets, both Desktop exports, preparation,
inputs, frozen candidate, installed capture files, prior audits, and results remain
untouched. The standard-only supplemental audit was not rerun against the later state.
The original five acceptance tasks were not changed.

The development repository remains on `milestone-6` at its handoff HEAD. No development
commit, push, tag, release, PR, worktree, or branch switch was made. Local development
`main` and `origin/main` still have zero divergence. No live provenance or bytecode caches
exist in the development repository.

After the operator completes the guide, retrieve the complete actual Desktop task and
execution evidence, preserve the Desktop-materialized H08 image, and run the frozen
focused validator. Require a real same-turn correction with a backward supersession,
exact separately captured user text, distinct runtime context, correct artifacts, and
no duplicate entries. Report failures before any repair. A focused pass does not change
FULL_01's historical result or by itself satisfy full Milestone 6 signoff.
