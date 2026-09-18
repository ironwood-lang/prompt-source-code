# Milestone 6 — standard-capture smoke check, 2026-09-18

## Decision and scope

Freeze the standard-capture candidate at
`429e7689fc956f7929ed08f0a962e6afd869fe0b`. Both focused live checks passed, with
correct structured completion reports and no product changes needed. This follows the
[result-reporting repair](MILESTONE_6_RESULT_REPAIR_20260918.md) and the earlier
[manual S06/S08 context confirmation](MILESTONE_6_CONTEXT_RETEST_20260917.md).
No repeat of S01–S14 is requested by this report.

This is a live model-driven smoke check in an existing Codex Desktop task, **not a new
Desktop UI acceptance run**. Requests were sent through `send_message_to_thread`; the
execution record identifies their delivery as `codex_delegation` tool output, not UI
user submissions. No attachment picker or clipboard operation was repeated. The task
controls exercised model interpretation and the installed completion flow; they do not
establish the UI delivery boundary. They are test orchestration, not a new capture
dependency or an expansion of the supported environment.

Direct computer-use control of the Codex window was unavailable. Task-tool evidence was
not converted into a fabricated Desktop `userMessage` export or submitted as S06/S08
acceptance evidence. The full Desktop acceptance validator was not claimed to pass.

## Preparation and execution

The existing project label `PSC_RETEST_01` resolves to
`~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/project`. The existing task was
`Preserve attached files exactly`, ID `01a0b26b-a599-7612-be3f-b161b214cfcc`.
No new project, task, folder-trust action, or hook installation was required.

Before updating, the entire project, original inputs, preparation manifest, validation
result, and Desktop export were backed up under the new sibling directory
`~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/standard-smoke-20260918-01/`.
Only `.prompt-source/instructions-v1.md` and `.prompt-source/validate.py` changed during
installation. Root and nested guidance were preserved. Exact prompts and expectations
were recorded before execution in the new directory's `preparation.json`.

Both turns used `gpt-5.6-sol` with `medium` effort, verified from the task-specific
execution record. R01 completed before R02 started. Each turn read the complete current
instructions, began capture before work, and successfully used the structured completion
API on its first attempt. No completion override was supplied.

| Case | Verified outcome |
| --- | --- |
| R01: preserve four existing local sources | Entry 000003 is Completed; all four copies match their sources byte-for-byte. Differing same-named images have separate collision-safe names. Sources are correctly classified as Requested artifact, without invented Desktop attachment context. Result: `Changed files: None.` |
| R02: ordinary file creation | Entry 000004 is Completed; `standard-smoke.txt` contains exactly `STANDARD_OK` plus one LF, 12 bytes. Its Result lists only that task-work file, with no history, assets, or installation files. |

The two requests are separate chronological Follow-up entries with correct backward
associations and the existing session ID. Their captured text matches the exact task-tool
request body; final-newline state remains Unknown. This is not a claim of verbatim UI
submission capture for these two requests.

## Independent audit and retained evidence

All 68 final focused audit checks passed. The installed history validator reports four
valid entries, and the installation checker matches the frozen candidate. Independent
source/copy byte comparisons passed for all four new assets. The original two-entry
history remains an exact byte prefix, including its historical reporting defects; the
original five assets and prior evidence files are unchanged.

Storage is one root history and nine files in one flat assets directory. The only new
ordinary file is `standard-smoke.txt`. No project hook installation, extra capture
runtime files, or staged changes exist. Project HEAD, `origin/main`, and the sibling
local bare origin remain `8b47e527ade09c5fcd7322f05af9b3891e91ed1c`.

The new evidence directory retains `audit.py`, `audit-result-final.json`, and
`task-tool-evidence-final.json`, plus preparation and backups. The task evidence contains
the relevant delivery and command records, not a UI export. An initial audit assertion
mistook injected environment context for a UI request because both use the user role.
The audit was corrected to check its explicit environment-context metadata; the initial
failed audit is retained. No capture code or captured evidence was changed to resolve it.

SHA-256 values:

- Final history: `23f564ec2624086eb71136595c0f8195b54e40dd34de4c5eae309027632d0bf2`.
- Ordinary file: `027ead22ca896b6802b5bd46c731456c8a9696c1723d64f1229cb46b58c958c6`.
- Final task-tool evidence: `ab8ded77e775386467888c1ba18650f299b63f3d15dc47512da54cbbb27af89e`.

## Automated and repository checks

With bytecode generation disabled, the complete 127-test suite passed. The explicit
unmatched-interruption test passed, and each of the four required concurrency/failure
tests passed 20 repetitions, 80 invocations total. JSON validation, Markdown fences and
internal links, and whitespace checks passed. Hook assets remain inert and the automated
checks find no hook network/Git operations or global capture configuration dependency.
Standard installed commands work without hooks, including from nested Git directories.

Instruction sizes remain 196 words / 1,523 UTF-8 bytes for the loader, 767 / 6,085 for
the dedicated instructions, and 963 / 7,608 combined. Maximums remain 300 / 2,048,
900 / 6,144, and 1,200 / 8,192 respectively. Architecture remains the marked root loader,
canonical `.prompt-source/instructions-v1.md`, and local `.prompt-source/validate.py`.

This report is the only development-repository change. No source, test, template,
release asset, or earlier evidence report changed. No live provenance or bytecode caches
exist in the development repository. Local `main`, `origin/main`, and a read-only remote
check resolve to `ef0cc942643e95b5405dc5ac72e30ae134718f53`. Work remains local on
`milestone-6`; no push, tag, release, or release-body modification was made.

## Remaining boundary

The repaired happy-path completion flow now has live model confirmation without hooks.
The standard implementation is frozen for the next phase, not declared infallible:
request interpretation, artifact classification, and summary/path selection remain
model-mediated. These checks complement, rather than replace or rewrite, earlier manual
evidence. There is no fresh UI S06/S08 run of the repaired structured completion contract.
Optional-hook Desktop acceptance remains unperformed on this candidate, and Milestone 6
is **not complete**. Codex Desktop remains the only supported capture environment.
