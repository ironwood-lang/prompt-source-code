# Artifact capture helper

The installed `.prompt-source/validate.py --preserve-artifact` command preserves one
observed source for an unfinished entry. It runs without enabled hooks or global
configuration. Run it at the Git root, before ordinary work can change the source.
The installed helper also locates that root when called by absolute path from a nested
directory. All relative source paths are relative to that root, not the caller's cwd.

Send one JSON object on stdin; no persistent request file is needed:

```json
{"entry_number": 2, "source": "../inputs/artifacts/notes.txt"}
```

`entry_number` comes from entry creation or hook claiming. For filesystem sources, omit
`kind`: a resolved source inside the project is `Repository file snapshot`; an external
source is `Requested artifact`. Symlinks are classified by their resolved target. The
helper accepts an explicit kind only for an observed `Attached file`, `Attached image`,
or `Pasted image`; being an image file alone does not make a source a Desktop attachment.

For those three observed Desktop kinds, the helper automatically adds one fenced,
path-free `Codex Desktop runtime context` summary before the artifact records. It states
that the agent observed an attachment/paste and keeps Desktop notices separate from user
input. This is a summary of the agent's reported observation, not a verbatim envelope or
independent proof of what Desktop delivered. Filesystem-only requests do not get invented
Desktop context. An unavailable attachment/paste still gets context, without claiming its
bytes were preserved.

The summary and artifact record are written together under the same lock and atomic
history replacement. Repeated preservation calls retain one context section, including
when filesystem artifacts came first. Existing valid context is retained unchanged;
malformed context stops enrichment. Completion refuses attachment/paste entries with
missing or empty context. These writer guards do not rewrite or invalidate old schema-1
histories when they are read.

`original_name` optionally carries an observed filename. The default is the source
basename. Supply null for an unnamed paste; its generated name uses `image-001` and the
actual materialized file's safe extension. When no source path is exposed, omit `source`
and optionally supply a factual, single-line, path-free `unavailable_reason`; the default
is `Unknown`. Do not guess a path to obtain a more specific error. Missing, non-file, or
unreadable sources produce an unavailable record without a copy, size, hash, or placeholder.

The helper implements the [frozen schema-1 rules](PROMPT_SOURCE_FORMAT.md): displayed
entry numbers (`prompt-000002-...`), basename sanitization, lowercased safe extensions,
flat collision suffixes, byte-for-byte comparison, destination size/SHA-256, source
verification, fidelity boundaries, ordered metadata, and local artifact numbering. A
matching existing candidate is reused; differing bytes are never overwritten. A source
already in the flat assets directory with a canonical name can be reused across entries.
Other sources receive a canonical name. Repository source links are percent-encoded;
external absolute paths are not put in artifact metadata.

The same command can enrich a claimed hook entry. Supply its current
`expected_entry_sha256`, then use the returned digest for later enrichment or
`--replace-entry`. The runtime task must match a recorded Session ID. Unclaimed, foreign,
changed, and terminal entries are rejected. This command does not install or activate
hooks; hook event enablement/trust remains separate from the loader control.

The helper rechecks the live loader and dedicated instructions under the project-directory
lock. Disabled capture makes no changes. It appends artifact records to the unfinished
entry before `--finish-standard` adds a result. Results may contain ordinary Markdown,
but not reserved capture section headings outside fences. Existing histories are not
rewritten to impose this new writer interface.

## Failure boundaries and validation

Publication uses a temporary file and a no-overwrite atomic link, followed by atomic
history replacement. Cooperating writers share the directory lock; no persistent lock
file is created. Temporary files are removed on handled failures. This is **not** a
cross-file transaction: a crash or history-write failure after asset publication can
leave a complete, unreferenced copy. It is retained, not deleted speculatively, because
history replacement may already have succeeded. A retry can verify and reuse that copy.
Report the failure; do not silently claim that the entry contains the artifact.

An observed source change during comparison aborts recording. Sources are read into
memory; very large files may fail for resource reasons. Noncooperating external edits
cannot be made transactional by this directory lock.

`--validate-history` is read-only. Besides the schema it verifies every referenced local
copy, rejecting symlinked asset storage, missing copies, and mismatched bytes/digests.
The schema parser rejects malformed padded prefixes. Neither check can reconstruct an
unrecorded source location, prove model-supplied UI classifications, or independently
verify model-mediated text. Historical failures remain evidence; validation does not
repair or rename their files.
