# Codex Desktop Version 1 Release Readiness

## Status

The final Milestone 4 clean-project acceptance run passed on 2026-09-17. The
schema-1 format and release bundle are frozen, the final Desktop cases passed, and the
repository is ready for an explicitly authorized version 1 tag. No version tag, GitHub
release, or package publication was created, and no other release artifact was created.

## Tested environment and dates

The final run used:

- Codex Desktop / ChatGPT app 26.911.61220 (9647);
- macOS 26.6.2 (25G83);
- `/usr/bin/python3` 3.9.6 for the optional hooks;
- Git 2.54.0 (Apple Git-157); and
- Codex CLI 0.155.0-alpha.2.6 only for `/hooks` review, trust, enablement, and
  disablement.

All Milestone 4 Desktop cases were performed on 2026-09-17. Earlier Milestone 2 and 3
evidence remains separately dated in the linked reports and was not rewritten.

## Disposable project isolation

The run used the fresh local Git project
`/Users/soliveira/Vibe/PSC_M4_V1_ACCEPTANCE_20260917` and the separate bare origin
`/Users/soliveira/Vibe/PSC_M4_V1_ACCEPTANCE_origin_20260917.git`. The previously used
Milestone 3 project was inspected before being preserved at a distinct path; it was not
reset, destroyed, or silently reused.

The fresh project began with the final standard template as its root `AGENTS.md`, the
optional hooks absent, and no PromptSourceCode skill, plugin, background service, or
network service. Its initial ordinary project commit was pushed before capture began.
Codex Desktop was the capture environment from the first prompt. Codex CLI was used only
for explicit hook review and lifecycle controls.

## Case-by-case outcomes

| Case | Factual outcome |
| --- | --- |
| Initial standard capture | Passed. Entry 000001 was created before task work; arbitrary Markdown required a five-backtick dynamic fence and `Final newline: None` was preserved. |
| Ordinary follow-up and no-change completion | Passed. Entry 000002 remained a separate completed interaction and recorded `Changed files: None.` |
| Same-turn steering | Passed. The initiating request and steering message were preserved separately as Entries 000003 and 000004. |
| Correction and supersession | Passed. Entry 000005 continued Entry 000004 and superseded Entry 000003 without rewriting either earlier interaction. |
| Artifact preservation and topology | Passed. Entry 000006 copied one 93-byte text artifact byte-for-byte into the flat assets directory with distinct metadata. |
| Standard capture disabled and re-enabled | Passed. A Desktop interaction while disabled made no history or task-work change; after re-enablement, Entry 000007 appended at physical EOF. |
| Optional files inert before trust | Passed. Installed but untrusted files produced no hook observation; Entry 000008 used standard capture. |
| Separate review, trust, and restart | Passed. `UserPromptSubmit` and `Interrupt` were reviewed and trusted separately through CLI `/hooks`; the tested CLI exposed definitions and trust state but not raw trust hashes. Desktop was fully restarted. |
| Exact hook-assisted capture and one-to-one matching | Passed in a manually created Desktop task. Entry 000011 preserved hook bytes, SHA-256, and LF state, then the agent claimed and completed that single entry without duplication. |
| Repeated identical prompts | Passed for two separate standard follow-ups as Entries 000012 and 000013. Hook-specific repeated-prompt behavior remains covered by the Milestone 3 Desktop evidence and deterministic final-bundle tests. |
| Trusted interruption | Passed. A real Desktop Stop changed only the matching Hook-assisted Entry 000014 from `In progress` to `Interrupted` with the exact canonical hook-confirmed reason and no invented result. |
| Guarded hook failure | Passed. Making the unchanged wrapper temporarily unreadable caused the configured shell guard to continue; Entry 000015 used the standard fallback. Original permissions were restored and all hook bytes still matched the release manifest. |
| Hooks disabled and standard fallback | Passed. Both events showed one installed and zero active definitions in `/hooks`; after a full Desktop restart, Entry 000016 completed through standard capture. |
| Final history validation | Passed. The final parser found Entries 000001 through 000016 in increasing physical order: 15 `Completed`, one `Interrupted`, 14 Instruction-mediated, and two Hook-assisted. |
| Persistent runtime outputs | Passed. Only `PROMPT_SOURCE.md`, one flat `prompt_source_assets/` file, and the explicitly installed `.codex/` source/config files existed; there was no status, input, result, event-log, runtime-context, or persistent lock file. |
| Generated-provenance Git isolation | Passed. `.codex/`, `PROMPT_SOURCE.md`, and `prompt_source_assets/` remained untracked, unstaged, uncommitted, and unpushed. |
| Ordinary project Git behavior | Passed. Two ordinary task outputs were explicitly staged, committed as `ffbb2f2b34790524cdeee16934aaaf857df09ce2`, and pushed; local `main` and its bare origin then matched. |

Entries 000009 and 000010 record two conservative standard fallbacks encountered while
setting up the final hook case. One task used a legacy saved-project alias whose earlier
hook configuration was disabled; the other was created through Desktop automation and
correctly identified as an agent-created task. Opening the fresh project directly and
using a manually created Desktop task resolved the setup mismatch. Neither case produced a
false hook observation or duplicate.

## Relevant hashes and byte counts

The frozen copyable release assets are recorded in
[`../tests/fixtures/release-manifest.json`](../tests/fixtures/release-manifest.json) and
verified by the automated suite. Significant acceptance outputs were:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Final root `AGENTS.md` | 18,250 | `ef276c69b7f2f1f61811d10003bcde0195365719d8c163ef82d8438302db777b` |
| Final `PROMPT_SOURCE.md` | 15,531 | `64bd34e6285b1790e9b580baf3f57c1032cf81cf58b4029a316bb86b29575e71` |
| Source artifact | 93 | `72211a0ad186a1ce14c3e100fe1ffa057a14d11aa02cb7198573db5d51a791c5` |
| Preserved asset | 93 | `72211a0ad186a1ce14c3e100fe1ffa057a14d11aa02cb7198573db5d51a791c5` |
| Ordinary initial output | 25 | `5128fc8a438bd1ff7290faf07c1063ed12ce79591f298b9d884687e54e8f14f1` |
| Ordinary steering output | 34 | `dbcf12d6634d2e15f4f0e656ff9fa378d93d57cd2f222b000152bc2621fa63c7` |

The report deliberately omits raw local transcripts, full session/turn identifiers, and
managed trust data.

## Automated validation

The final pre-commit run passed all 49 `unittest` cases. Four concurrency and
failure-injection tests covering simultaneous prompt processes, prompt/interrupt races,
agent/interrupt races, and pre-replacement atomic failure were then repeated 20 times
each: 80 of 80 stress invocations passed. The suite also validated Markdown fences and
internal links, frozen release-asset hashes and byte counts, malformed and non-version-1
history rejection, inert event scope, and the absence of network or Git operations in
hook code. Every JSON file parsed with the standard library, Python sources compiled,
`git diff --check` passed, and independent repository-boundary checks found no live
generated provenance in the development repository.

## Final storage topology

The acceptance project ended with one root `PROMPT_SOURCE.md` and one direct file inside
the flat `prompt_source_assets/` directory. There were no per-prompt directories and no
separate input, result, status, runtime-context, event-log, or lock files. The optional
`.codex/` directory contained only the deliberately installed hook definition and two
Python source files; both hook events were disabled for the final fallback case.

## Git behavior

Generated provenance never entered the acceptance repository index or either commit and
was never pushed, published, or uploaded. Ordinary files retained normal Git behavior and
were pushed successfully. The PromptSourceCode development repository itself contains no
live generated provenance.

## Defects found and resolutions

- Strict replacement validation initially considered the replacement entry in isolation,
  which rejected valid backward `Continues` and `Supersedes` references. Replacement now
  validates the complete candidate history, and regression tests cover the association.
- A saved-project alias selected an older disabled hook lifecycle record during acceptance.
  The exact project state was preserved; the fresh project was opened directly in Desktop
  and the final user-created-task cases passed.
- Agent-created Desktop automation is intentionally excluded by the hook boundary. The
  attempted case failed closed and used standard capture; the required hook case was then
  performed in a manually created Desktop task.

No unresolved release-bundle defect remained after the final validation cases.

## Supported scope and remaining limitations

Version 1 supports the tested local Codex Desktop on macOS workflow. Standard capture is
model-mediated and does not independently verify its own output. Hook capture remains an
explicit local enhancement requiring separate review, trust, enablement, and a Desktop
restart. Version 1 does not claim live capture support for Codex CLI, the IDE extension,
cloud tasks, Windows, Linux, network filesystems, other agents, or automatic provenance
publication. Detailed distinctions and upgrade rules are in
[`COMPATIBILITY.md`](COMPATIBILITY.md).

## Release decision

### Ready for an explicitly authorized tag?

Yes. The source, documentation, frozen assets, automated checks, and final Desktop
acceptance evidence are ready for an explicitly authorized version 1 tag and publication.
Tagging and publishing remain intentionally pending a separate explicit instruction.
