# PromptSourceCode Fixtures

These files model canonical output; they do not enable PromptSourceCode capture in this
repository.

- `expected-history.md` is a deliberately named model rather than a live
  `PROMPT_SOURCE.md`. It covers complex text, follow-up and steering chronology, a
  superseding correction, same-entry artifact-name collision handling, a no-change result,
  unknown-cause incompletion, and a hook-confirmed interruption.
- `artifacts.json` stores Base64 fixture payloads and their verified sizes and SHA-256
  values. The two pasted-image comparison payloads decode to the same one-pixel scanline
  but have different bytes and digests.
- `hook-events.json` contains non-sensitive representative `UserPromptSubmit` and
  `Interrupt` objects for deterministic parser and identifier-association tests.
- `release-manifest.json` preserves the exact 0.1.0 release-asset record, including the
  superseded full-inline template hash.
- `distribution-manifest.json` freezes the current loader, dedicated instructions,
  standard-library installer, shared capture/validation helper, and optional hook assets.

There is intentionally no `prompt_source_assets/` fixture directory. The expected
history models its flat repository-relative references while the test suite checks the
payload data directly from the JSON manifest.
