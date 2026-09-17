<!-- prompt-source-loader-begin -->

## PromptSourceCode loader

- Capture: enabled
- Instructions: `.prompt-source/instructions-v1.md`

When capture is enabled, before creating a capture entry or doing requested work, read
that file completely. Require its first line to be
`<!-- prompt-source-instructions: 1 -->` and its final line to be
`<!-- prompt-source-instructions-end -->`. Follow it together with every applicable root
and nested `AGENTS.md`; it never replaces project instructions.

If the file is missing, unreadable, wrong-version, stale, conflicting, or truncated, do
not create or update `PROMPT_SOURCE.md` or `prompt_source_assets/`. Preserve existing
provenance, report the capture problem, and continue requested work under the other
applicable project instructions.

When capture is disabled, do not read the dedicated file and do not create, update, or
delete provenance. In either state, never stage, commit, push, publish, or upload generated
provenance unless the user explicitly requests it.

<!-- prompt-source-loader-end -->
