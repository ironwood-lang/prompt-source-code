<!-- prompt-source-loader-begin -->

## PromptSourceCode loader

- Capture: enabled
- Instructions: `.prompt-source/instructions-v1.md`

For EVERY submission, including follow-ups and steering, resolve the Git root with
`git rev-parse --show-toplevel`; paths are relative to that root, never the current or
nested directory. Run `/usr/bin/python3 .prompt-source/validate.py --capture-state` there
before capture or requested work. This reads the current on-disk loader control; never
reuse an enabled/disabled value remembered from an earlier turn.

When the command reports enabled, read `.prompt-source/instructions-v1.md` completely
before creating a capture entry or doing requested work. Require its
first line to be
`<!-- prompt-source-instructions: 1 -->` and its final line to be
`<!-- prompt-source-instructions-end -->`. Follow it together with every applicable root
and nested `AGENTS.md`; it never replaces project instructions.

If either file is missing, unreadable, wrong-version, stale, conflicting, or truncated,
or the command fails, do not create or update `PROMPT_SOURCE.md` or
`prompt_source_assets/`. Preserve existing
provenance, report the capture problem, and continue requested work under the other
applicable project instructions.

When capture is disabled, do not read the dedicated file and do not create, update, or
delete provenance. In either state, never stage, commit, push, publish, or upload generated
provenance unless the user explicitly requests it.

<!-- prompt-source-loader-end -->
