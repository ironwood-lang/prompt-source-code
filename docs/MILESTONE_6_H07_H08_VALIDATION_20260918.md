# Milestone 6 — focused H07/H08 Desktop validation, 2026-09-18

## Decision

**H07 and H08 passed on the repaired snapshot.** The operator completed the
[focused guide](MILESTONE_6_H07_H08_RETEST.md) using GPT-5.6 SOL, Medium. The frozen
focused validator passed with no errors, and all 142 supplementary evidence checks passed.
No further H07/H08 repeat is requested.

This result confirms the two [targeted repairs](MILESTONE_6_H07_H08_REPAIR_20260918.md).
It leaves the [FULL_01 standard checkpoint](MILESTONE_6_FULL_01_STANDARD_20260918.md)
and [original full-run failure](MILESTONE_6_FULL_01_HOOKS_20260918.md) unchanged.
**Milestone 6 remains in progress:** this focused validator does not constitute a passed
full acceptance validator, and the original full run was not changed or reclassified.

## Actual Desktop evidence

Workspace: `~/Vibe/PSC_M6_H07_H08_RETEST_20260918_01`.

Task: **Run PSC H00 acceptance hook**, `01a0b4a2-837e-7901-b4c7-00cfcd214a90`.
The complete Desktop export contains one page, two completed turns, and three actual
user submissions. No exported output is truncated. All 35 completed commands returned
exit code zero; no malformed helper request or failed retry appears in this run.

Task-specific execution records independently confirm `gpt-5.6-sol`, `medium` for
both turns. Three actual synthetic hook contexts match the three captured prompts and
their session/turn identities. Each submission has a complete dedicated-instruction
read before the agent's claim and work. No acceptance prompt was sent by the coordinator,
through CLI, or through task tools.

The CLI review, enable/trust, disable, and Desktop restart sequence is operator-confirmed
through completion of the guide. The retrieved records establish the resulting capture
behavior; they do not independently record those UI actions. No extra H11 submission was
requested or inferred.

## Outcomes

| Submission | Entry | Outcome |
| --- | --- | --- |
| H00 prerequisite | 1 | Pass. Initial request retained as a claimed, completed hook entry. The 120-second sleep ran, and the result accurately identifies the later correction. |
| H07 | 2 | Pass. Separate claimed, completed `Correction` in the same active turn, with `Supersedes: Entry 000001`. The original request remains intact. `hook-theme.txt` is exactly `GREEN` plus LF. |
| H08 | 3 | Pass. Claimed, completed follow-up in a later turn. Exact user text, separate path-free Desktop context, attached-file and pasted-image records, and `Changed files: None.` are present. |

The sleep call began at `13:10:09.284 UTC`; H07's matching context arrived at
`13:10:44.426 UTC`, approximately 35 seconds into the command's 119,862-millisecond
recorded execution. The GREEN file was created after the sleep. Both H00 and H07 belong
to turn `01a0b4a3-118d-7443-824e-8895a06a208b`; H08 belongs to the later turn
`01a0b4a6-8a25-7d01-901d-c92b80cba552`.

H08's stored user input is exactly the 197-byte delivered request, including its final
LF. The attachment envelope and its absolute paths are excluded from user input before
claiming; a separate context section identifies its runtime origin. The text attachment
is a 34-byte source-identical copy. The pasted image is a 236-byte source-identical copy
of the actual Desktop temporary image, which was still available and independently
preserved for this audit. It differs from the 70-byte pre-clipboard input fixture;
no identity with that pre-clipboard file is claimed.

There are exactly three history entries and two flat preserved assets. No duplicate
observation, extra submission, unexpected project file, or ordinary H08 file edit appears.

## Frozen validation and preserved files

Executed with the frozen script, without changing its assertions:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  ~/Vibe/PSC_M6_H07_H08_RETEST_20260918_01/candidate/scripts/hook_retest.py validate \
  ~/Vibe/PSC_M6_H07_H08_RETEST_20260918_01 \
  --desktop-export ~/Vibe/PSC_M6_H07_H08_RETEST_20260918_01/desktop-export.json
```

Exit code **0**; JSON result `passed: true`, `errors: []`; stderr empty. The exact
executable, argv, complete stdout, and stderr are in `focused-validation-result.json`.
No alternate source image or edited evidence was needed to pass.

New evidence beside the existing preparation/preflight records:

- `desktop-export.json`: the complete actual Desktop page.
- `focused-validation-result.json`: complete frozen-validator output.
- `audit_retest.py` and `retest-audit-result.json`: read-only supplementary checks.
- `retest-checkpoint/`: exact final history, two assets, ordinary file, actual Desktop
  temporary image, and the task-specific execution record.
- `retest-hygiene-result.json`: final documentation, JSON, whitespace, and Git checks.

SHA-256 values:

| Evidence | SHA-256 |
| --- | --- |
| History | `5b87d9891ceab790f4aaa7bffd1424c52a21188af04591fe8ad2301114014c1e` |
| Desktop export | `88c1346506070c883b1b91587d334d07a3a095f8021be35bbc7170615493b10f` |
| Text attachment | `28c0632356506034aba615a14939b0631f2f3ea9cdc2bc99abb3e9ec468b6b2f` |
| Desktop pasted image | `5d9eac1877263db08243aa70240e403f9c7abb6b5ada937ffc699e074c4733a5` |
| Execution record | `d5eb0a7bb4335e49a06bfc497a9173c86fad1333939c5bc8827a4cf621eef492` |

## Candidate, preservation, and Git

Every frozen source, input, standard installation, and installed hook still matches
`preparation.json`. The tested snapshot also matches the current development repair
source. It is the uncommitted repair snapshot documented in the repair report, not the
original FULL_01 candidate commit. Instruction sizes remain 196 words / 1,523 bytes for
the loader, 766 / 6,129 for dedicated instructions, and 962 / 7,652 combined; all frozen
budgets still pass.

The disposable project's HEAD remains its installation commit
`3148bf6c738c9cd77d9c9d60e58eeed8735baa03`. There is no remote, no staged or tracked change,
and no tracked provenance. Its only untracked paths are `.codex/`, `PROMPT_SOURCE.md`,
`hook-theme.txt`, and `prompt_source_assets/`.

Every FULL_01 evidence file in the saved preflight inventory still matches its hash,
including both exports, both checkpoints, all captured artifacts, inputs, frozen assets,
and previous validation results. The original standard and hook evidence reports are
byte-identical. No original acceptance task or captured file was modified, and the
S14-only supplemental audit was not rerun against the later hook state.

The unchanged implementation retains the earlier **143-test full-suite pass**, **16
system-Python regression passes**, **one explicit unmatched-interrupt pass**, and **80
stress-test passes**, recorded in the preparation evidence. This audit changed only
documentation and added evidence; it did not rerun those code tests without a source
change. Final Markdown/link, four-JSON-file, whitespace, and Git checks passed separately.

Development remains on `milestone-6` at
`d4576c5265edee7c321cd72f6122d890b19f6f86`. No development commit, push, tag, release,
branch switch, worktree, or PR was made. No live provenance or bytecode cache was created
inside the development repository.
