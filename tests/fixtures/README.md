# Milestone 1 Fixtures

These files model canonical output; they do not enable PromptSourceCode capture in this
repository.

- `expected-history.md` is a deliberately named model rather than a live
  `PROMPT_SOURCE.md`. It covers complex text, follow-up and steering chronology, a
  superseding correction, same-entry artifact-name collision handling, a no-change result,
  unknown-cause incompletion, and a hook-confirmed interruption.
- `artifacts.json` stores Base64 fixture payloads and their verified sizes and SHA-256
  values. The two pasted-image comparison payloads decode to the same one-pixel scanline
  but have different bytes and digests.

There is intentionally no `prompt_source_assets/` fixture directory. The expected
history models its flat repository-relative references while the test suite checks the
payload data directly from the JSON manifest.
