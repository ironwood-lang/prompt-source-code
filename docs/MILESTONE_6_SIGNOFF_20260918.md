# Milestone 6 — 0.2.0 signoff, 2026-09-18

## Decision and authorization

**Milestone 6 is complete on an explicitly accepted combined-evidence basis.** After the
coordinator explained that the remaining gate required one full-validator pass or an
explicit acceptance of combined evidence, the owner declined further manual tests and
requested signoff and release 0.2.0 with new installation instructions. The owner then
confirmed: “Yes—publish 0.2.0 after checks pass.”

For this release, that decision replaces the original requirement for one successful
full Desktop validator run on the final candidate. It accepts the existing full run's
passing cases, the repaired cases' actual Desktop confirmation, and automated regression
checks. No additional manual acceptance is required by this signoff.

This is a release acceptance decision, not a change to captured evidence or a retroactive
validator pass. FULL_01's original result remains **Fail**. The focused retest remains a
focused **Pass**. Neither validator's assertions were loosened, and no histories or
exports were merged to manufacture an all-green run. Earlier reports record their
then-current status and remain unchanged.

## Accepted evidence

| Coverage | Evidence | Result |
| --- | --- | --- |
| S01–S14, including S04B and intentionally uncaptured S12 | [FULL_01 standard checkpoint](MILESTONE_6_FULL_01_STANDARD_20260918.md) | Standard validator passed; 145 supplemental checks passed; 14 entries and seven assets preserved. |
| S15, H01–H06, H09–H11, repeated H03, and final ordinary-file Git check | [FULL_01 full audit](MILESTONE_6_FULL_01_HOOKS_20260918.md) | These cases passed. The complete run contained 28 actual submissions, 27 entries, and ten assets; its only failed cases were H07/H08. |
| H07 correction and H08 envelope/artifacts after repair | [Focused Desktop validation](MILESTONE_6_H07_H08_VALIDATION_20260918.md) | Frozen focused validator passed; all 142 supplementary evidence checks passed; three actual submissions and two assets. |
| Repair behavior, text preservation, concurrency, atomic failure, and fallback | [Repair preparation](MILESTONE_6_H07_H08_REPAIR_20260918.md) | 143 unit tests, 16 system-Python regression tests, one explicit unmatched-interrupt check, and 80 stress invocations passed. |

All acceptance tasks used GPT-5.6 SOL, Medium; task-specific execution records confirm
the model and effort. The operator performed the actual UI sequence. Trust decisions and
Desktop restarts are operator-confirmed, while captured behavior, delivered messages,
helper calls, identities, artifacts, and ordinary outputs are present in the evidence.

The full run's five diagnostics arose only from H07's interaction/supersession and H08's
retained Desktop envelope/paths. The focused retest confirms the corrected behavior with
real same-turn delivery and actual attachment/paste sources. It does not merely compare
model-generated history with itself.

## Change-impact review

The original full candidate was `429e7689fc956f7929ed08f0a962e6afd869fe0b`. The tested
repair snapshot is identified by `preparation.json` in
`~/Vibe/PSC_M6_H07_H08_RETEST_20260918_01`.

| Changed component | Effect and coverage |
| --- | --- |
| Hook input handling | Recognized Desktop envelopes are separated before immutable capture and matching. H08 retested the actual envelope, both source-identical artifacts, portable context, and no-change result. Automated cases cover byte fidelity, malformed input, and repeated matching. |
| Hook completion | The agent supplies explicit interaction metadata to `--finish-hook`. H07 confirmed a correction superseding the preceding entry in the same active turn. Existing claim, identity, digest, terminal-state, and atomic replacement guards remain in use and have regression/race coverage. |
| Shared dedicated instructions | Correction rules now apply to both branches; normal hook completion uses the new helper. The standard instructions were shortened within unchanged budgets. Standard regression, installation, artifact, result, and recovery tests passed; the owner accepts the remaining model-behavior coverage gap from not repeating all Desktop cases on this exact text. |
| Root loader, installer, hook wrapper/definitions, schema, and full acceptance validator | Their bytes remain unchanged from the full candidate. No global configuration or new hook event is required. |
| Release preparation | Current-version documentation, installation/update guidance, and distribution metadata were updated. The runtime files remain byte-identical to the successful focused snapshot. |

Key repaired SHA-256 values:

- Dedicated instructions: `77bb47e62cdcb9eab2f498557aad1e73c2ef343dba40fae7c4648ab712815b1b`.
- Core helper: `1b85919cfc1f6ec6deacd9adc39d0590a50d02af86e0de391918d137afbedc42`.

No instruction budget was increased. The loader uses 196 words / 1,523 bytes; the complete
dedicated instructions use 766 / 6,129; together they use 962 / 7,652. This reduces the
18,250-byte inline baseline by approximately 58%, while keeping root and nested guidance
separate and preserved.

## Release checks and installation

The 0.2.0 release gate runs the full repository suite, the explicit unmatched-interrupt
check, and the four documented stress cases twenty times each. It also validates JSON,
Markdown links/fences, shell command syntax, whitespace, distribution hashes, and Git
state. A source archive is extracted outside the development repository and exercised
with the documented standard-library installer and checker under `/usr/bin/python3`.
This automated installation exercise does not substitute for Desktop evidence.

The final pre-commit run passed **143 tests** in 4.172 seconds, **one** explicit
unmatched-interrupt check, and all **80** stress invocations. All four repository JSON
files, Markdown fences and local links, reviewed shell blocks, and tracked/untracked
whitespace checks passed. Local `main` and `origin/main` had zero divergence before
publication. No runtime source changed after the successful focused Desktop retest.

Exact commands and results are recorded outside the repository in
`~/Vibe/PSC_M6_RELEASE_020_20260918/release-checks.json`, with the archive/install checks in
`package-checks.json`. Publication occurs only after these checks pass. GitHub supplies
source ZIP/tar archives for the immutable `v0.2.0` tag. The release body is intentionally
empty; [0.2.0 release notes](RELEASE_NOTES_0.2.0.md) and the [installation guide](INSTALLATION.md)
contain the user-facing explanations.

Standard capture remains `AGENTS.md`-driven. Its installer adds the small loader, dedicated
instructions, and local Python helper. Unlike 0.1.0, standard 0.2.0 capture requires the
tested system Python even when hooks are absent. No additional Python package, skill,
plugin, background service, or network capture service is required. Optional hooks remain
inert until the owner separately reviews, enables, and trusts them.

For 0.1.0 users, the guide explicitly removes only the old full-inline marked block before
installing the compact layout. Existing compact-loader installations use `update`.
Both procedures preserve existing valid history and artifact bytes. The installer does
not pretend to automatically remove the old inline block or repair historical failures.

## Preservation and remaining limits

FULL_01's preparation, inputs, installation, frozen assets, exports, checkpoints, and
results remain unchanged. The focused run's three entries, two assets, export, temporary
image copy, and execution record are likewise preserved. These local raw records are not
release assets; only factual repository reports are included in the source distribution.

The support claim remains the tested local Codex Desktop/macOS environment. Standard text
capture and semantic classification remain model-mediated. The recognized hook envelope
is specific to the observed Desktop serialization. Neither a pre-serialization text
guarantee nor identity with an unknown pre-clipboard image is claimed. No final-candidate
single full-run pass is claimed, and no additional platform or agent support is inferred.
