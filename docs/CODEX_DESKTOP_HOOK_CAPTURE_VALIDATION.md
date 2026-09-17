# Codex Desktop Optional-Hook Capture Validation

This is the preserved Milestone 3 evidence for the optional path. The frozen 0.1.0
bundle was later rechecked in the separate
[`CODEX_DESKTOP_V1_RELEASE_READINESS.md`](CODEX_DESKTOP_V1_RELEASE_READINESS.md) run;
that later report does not alter the facts recorded here.

## Status

This report records the completed Milestone 3 validation performed on 2026-09-16 and
2026-09-17. Every required Desktop-only case below was completed. No raw Codex
transcript or full local session or turn identifier is published here; opaque labels
preserve only the identity relationships needed for the evidence.

## Environment and isolation

- Codex Desktop: 26.911.61220 (9647)
- macOS: 26.6.2 (25G83)
- System Python used by the hooks: 3.9.6
- Disposable project: `~/Vibe/PSC_Test`
- Disposable project's initial commit: `7f6dabad39b8a462b8474418b49d958495dfc600`
- Disposable local bare origin:
  `~/Vibe/PSC_M3_filtered_origin_20260917.git`
- Capture environment: Codex Desktop for every prompt; Codex CLI only for `/hooks`
  review, enablement, and trust.

The disposable project began with the final standard template as its root `AGENTS.md`.
It had no PromptSourceCode skill, plugin, service, or network dependency. The
PromptSourceCode development repository has no live `PROMPT_SOURCE.md` or
`prompt_source_assets/`.

A previously installed PromptSourceCode development-preview plugin exposed a skill and
global hook definitions, so the owner explicitly uninstalled it before the final
project-local validation. This removed an ambiguous external capture source; no plugin or
skill was used by the final run.

Earlier projects were not destroyed or silently reused:

- `~/Vibe/PSC_Test_M2_append_fix_20260916`
- `~/Vibe/PSC_Test_M3_activation_attempt_20260917`
- `~/Vibe/PSC_Test_M3_synthetic_prompt_defect_20260917`

The last project preserves the first live-hook defect exactly as observed. Its history
SHA-256 is
`ab19929b0ac94c7d1de02496502c9713575f2298d3b32893a7c89e907d9cabd7`.

## Trust evidence

The project-local definition contains only `UserPromptSubmit` and `Interrupt`. The owner
separately reviewed, enabled, and trusted them through Codex CLI `/hooks`, then fully
restarted Desktop. The initially trusted definition hashes, captured outside the CLI
before failure-fallback hardening changed the commands, were:

- `UserPromptSubmit`:
  `sha256:8c60dc3a2a73b9dec5961a8a7267f2b50c835d17c1fdfbfcccfd364a15668682`
- `Interrupt`:
  `sha256:e51ea33a26bbaf0e0a300aad54cd99c0c4939648a3290d7d682f8b7b13a5efab`

The tested CLI did not display raw hook-definition hashes, so no hash was inferred for
the final guarded definitions. The owner instead reviewed their exact commands, enabled
and trusted both definitions separately, and restarted Desktop. Before activation and
after each update, the installed Python and configuration files were byte-compared with
the reviewed development copies. No trust bypass was used.

## Case evidence

The main live session is labeled `S1`. Distinct completed turns are labeled `T1`, `T2`,
and so on; labels are not substituted identifiers in the captured history.

| # | Required case | Outcome and factual evidence |
|---:|---|---|
| 1 | Standard capture before installation | **Pass.** Entry 1 was created in Desktop as `Instruction-mediated` before hook files existed. |
| 2 | Installed but inactive/untrusted | **Pass.** Entry 2 remained `Instruction-mediated` after the inert files were installed and before both definitions were trusted and activated. |
| 3 | Separate `/hooks` review and trust | **Pass.** Both definitions were reviewed and trusted separately. The CLI did not expose their raw hashes; the hashes recorded above apply only to the initial pre-guard definitions and were not presented as final trust evidence. |
| 4 | Desktop restart after trust | **Pass.** Desktop was fully restarted before the first hook-assisted task. |
| 5 | Exact initial submission | **Pass.** Entry 3 was created before agent work as `Hook-assisted`, then claimed. Its known test prompt is 172 UTF-8 bytes, ends in LF, and has SHA-256 `d0cbeca098502bf0d9a6d2eba45b52fd250ec3867c4e6ad920d226c8243dffa0`. Stored bytes, newline state, and digest matched the delivered event string. Nonempty event identifiers map to `S1/T1`. |
| 6 | Ordinary follow-up | **Pass.** Entry 4 used `S1/T2`; `T2` differed from `T1`, and the entry was claimed and completed without duplication. |
| 7 | Two same-turn steering messages | **Pass after defect discovery.** Entries 9, 10, and 11 shared one event turn ID and remained separate in physical order. The initiating prompt and both steering messages were claimed and completed. The run exposed the digest-boundary defect described below. |
| 8 | Identical submissions | **Pass.** Entries 5 and 6 had identical prompt bytes and the same prompt SHA-256, `d2e7ea59a868fa5d14900a58ecd7e6946f1e06f988e4308dbc20a25220955949`, but distinct turn IDs. Both were separately created and claimed. |
| 9 | Agent enrichment without duplication | **Pass for completed live hook cases.** Entries 3 through 12 and 14 each contain one hook-created input observation, one successful claim, and one enriched result; no second entry was appended for agent observation. Entry 13 was claimed once before its trusted interruption. |
| 10 | Correction without rewriting | **Pass.** Entry 7 retained the ALPHA instruction. Entry 8 captured the later BETA correction, was refined to `Correction`, and points back with `Supersedes: Entry 000007`. |
| 11 | No task-work change | **Pass.** The completed hook-assisted prompts recorded `Changed files: None.` while leaving task-work files unchanged. |
| 12 | Attachment or pasted-image enrichment | **Pass.** After the post-update Desktop restart, Entry 12 captured the 437-byte LF-terminated delivered text as one claimed hook entry. Artifact metadata remained in its separate section. The attached image's Desktop-exposed source and flat preserved copy were both 577,924 bytes with SHA-256 `24c0df82228b155fd91db0d6599300eb2df760de19537bf845bf88e1a028963a`; an independent `cmp` succeeded. No claim was made that the prompt hook captured the binary. |
| 13 | Real Desktop Stop and trusted interrupt | **Pass with format hardening.** A real Stop interrupted the running Desktop turn after 23.1 seconds, well before its requested 120-second wait. Entry 13 had the event's same session and turn identifiers, retained its exact 151-byte LF-terminated input, became `Interrupted`, and used the exact reason `Hook-confirmed Interrupt event.` Entry 12 and all other completed entries remained completed. The first run exposed and then received the bounded metadata-spacing repair described below. |
| 14 | Unmatched or ambiguous interrupt | **Pass deterministically.** The unit test supplies unmatched identifiers, asserts `NoReliableMatch`, and verifies the history bytes are unchanged. |
| 15 | Hook failure with standard fallback | **Pass after defect resolution.** The first deliberate launch failure was correctly diagnosed but Desktop displayed `Hook blocked this message` and did not deliver it to the agent. After the definitions gained the reviewed local guard and were re-trusted, the identical missing-handler condition allowed the resent message to complete. Entry 15 is the sole exact-prompt observation, is `Instruction-mediated`, and has no hook identifiers or agent-claim metadata. The handler was restored byte-identically and no temporary failure file remained. Direct agent-helper failures remain nonzero. |
| 16 | Hook success plus agent observation | **Pass.** Exact identifier-and-byte claims produced one entry for every successful hook-assisted interaction; no agent observation appended a duplicate. |
| 17 | Concurrent submissions | **Pass deterministically.** Twelve released-at-once worker processes produced entries 1–12, unique ordered numbers, distinct event turn IDs, valid Markdown, and no extra persistent runtime output. Interrupt races with both agent replacement and prompt capture are also covered. |
| 18 | Failure injection | **Pass deterministically.** Injected failure after tempfile `fsync` but before `os.replace` retained the previous history byte-for-byte and removed the temporary file. |
| 19 | Final storage topology | **Pass.** The final project has one root history with structural Entries 1–16 in strictly increasing physical order and one flat assets directory containing the single preserved image. Fifteen entries are `Completed` and Entry 13 is `Interrupted`. No persistent lock, temporary, input, result, status, runtime-context, event-log, diagnostic, or bytecode-cache file exists. The installed hook source and inert configuration are opt-in assets, not runtime state. |
| 20 | Git behavior | **Pass.** Desktop created the exact 22-byte ordinary `ordinary-project.txt`. Only that file was staged, committed as disposable commit `913caacbb98d46864b2f3d57ed03691dd8b26a9a`, and pushed to the local bare origin. The resulting origin tree contains `AGENTS.md` and `ordinary-project.txt` only. `.codex/`, `PROMPT_SOURCE.md`, and `prompt_source_assets/` remained untracked, unstaged, uncommitted, unpushed, unpublished, and unuploaded. |
| 21 | Standard capture after hook disable/removal | **Pass.** Both definitions were disabled through `/hooks`, Desktop was fully restarted, and a new task produced Entry 16 as `Instruction-mediated`, with no hook identifiers or claim metadata. The hardened standard instructions detected that the initial append landed after repeated result text, moved only that new unfinished block to physical EOF before task work, and completed it there. Existing entries were unchanged. |

## Defects found during validation

### Desktop internal feature submissions also emit `UserPromptSubmit`

The first trusted run captured an internal ambient-suggestion prompt because it was a
root hook event without a subagent ID. This was not a user interaction. The project was
preserved unchanged, and the implementation now fails closed unless the event's
hook-provided transcript begins with matching `session_meta` for the same project and
session with `originator: Codex Desktop` and `thread_source: user`. Tests cover missing
metadata, ambient-suggestion metadata, CLI origin, and mismatched session and project.

### Appending steering changed an earlier optimistic digest

The first three-message steering run took 4 minutes 21 seconds although its deliberate
wait was only about 44.9 seconds and each hook claim completed below the trace timer's
resolution. Appending Entries 10 and 11 caused the parser to include a newly introduced
inter-entry separator in Entry 9's digest, so Entry 9's first enrichment was safely
rejected as stale. No partial or corrupt history was written, and the agent recovered.

The parser now keeps the single inter-entry separator outside each entry's content range,
so a later append cannot change an earlier entry digest. A regression test claims the
base entry, appends two same-turn steering entries, verifies the original digest is
unchanged, and enriches the base successfully. The fix was deployed with hooks disabled,
then re-reviewed, trusted, and exercised in the remaining live cases.

### Interrupt reason crossed the metadata separator

The real Stop correctly selected Entry 13 and applied the canonical state and reason, but
the first formatter placed a blank line before `Status reason` instead of after it. The
input, identifiers, and state were never altered incorrectly. The insertion now splits at
the complete blank-line-plus-`User input` boundary and emits the reason as the last
metadata field followed by one blank line. Exact-format regression assertions cover both
a normal interrupt and replacement of an earlier noncanonical reason.

The live Entry 13 was repaired only through the guarded atomic `--replace-entry`
interface. Its current digest, session ID, turn ID, and exact prompt bytes all had to
match; its input remained 151 bytes and its state remained `Interrupted`.

### Nonzero `UserPromptSubmit` failure blocked message delivery

For the first fallback test, the trusted command target was deliberately made
unavailable. Desktop displayed `Hook blocked this message` and Python's missing-file
diagnostic, and the user message never reached the agent. The handler was restored
immediately; the history SHA-256 was unchanged and no rejected interaction entry was
invented.

The final definitions run event handlers through a small `/bin/sh` guard. A failed local
handler keeps its stderr diagnostic but exits successfully without matching context, so
Desktop can deliver the message and the standard instructions can create an
`Instruction-mediated` entry. Direct `--claim` and `--replace-entry` calls do not use the
guard and still fail nonzero. An automated missing-handler test now asserts exit zero,
empty stdout, a useful stderr fallback diagnostic, no hook-created history, and a valid
standard-path history. After explicit review, trust, and Desktop restart, the live repeat
produced exactly one `Instruction-mediated` Entry 15 and completed successfully. The
handler was then restored byte-identically.

## Deterministic test result

The current standard-library test suite exercises parsing, exact UTF-8 preservation,
dynamic fences, all final-newline states, one-to-one repeated prompts, steering
association, agent claims and replacement, interruption matching, transcript-source
filtering, simultaneous processes, interruption races, atomic failure, malformed input,
wrong schema, truncation, duplicate or out-of-order headings, and failed-hook fallback.

The final command was:

```text
/usr/bin/python3 -m unittest discover -s tests -v
```

All 43 tests passed. Repeated stress runs of the concurrent-process, interruption-race,
and failure-injection tests also passed. JSON fixtures and the example hook definition
parsed successfully, the Markdown contract checks passed, and `git diff --check` reported
no errors.

## Final artifact and repository checks

The final disposable history SHA-256 is
`b47acb98e175f38771f6e6556f310447e5baceb2fea43d361dddad9f5600bb9d`.
Its single flat asset is 577,924 bytes with SHA-256
`24c0df82228b155fd91db0d6599300eb2df760de19537bf845bf88e1a028963a`
and independently compares byte-for-byte with Desktop's exposed source.

The ordinary project change was committed as
`913caacbb98d46864b2f3d57ed03691dd8b26a9a`. The final standard-template updates were
committed as `3713e2356ae53e1208fdd203a492d0f4786a93a9` and
`bd0710888f60d176f028dd343d90ad21bfd68032`; all were pushed in the disposable project.
The bare origin's final tree contains only `AGENTS.md` and `ordinary-project.txt`;
generated provenance and `.codex/` never entered its index or history. The
PromptSourceCode development repository contains no live `PROMPT_SOURCE.md` or
`prompt_source_assets/`.
