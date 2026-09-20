# Render layer tool

## Problem

The serverless email authoring tool (`serverless-email-authoring-tool.md`, in this folder) produces a JSON document describing an authored email: an ordered list of blocks, each with a `blockType` and `data` validated against that block's JSON Schema. That document needs to become actual email HTML. Rendering was explicitly kept out of scope for the authoring tool — this is that separate tool.

## Core idea

- Input: the authored email JSON document (blocks, in order, each with `id`, `blockType`, `data`) plus a **theme**.
- Each `blockType` maps to an HTML template/partial that knows how to render that block's `data` into email-safe markup (table layout, inline styles, MSO conditionals — see `../CLAUDE.md` for the HTML conventions already used in this repo's templates).
- The theme controls the visual styling applied on top (colors, fonts, spacing, etc.) without changing which blocks exist or their content — themes live entirely in this tool (per the authoring tool spec), not in the authored document.
- Output: a single HTML file/string for the email, ready to send or preview — same as `flipboard/techdigest.html` and `traction/index.html` in shape, but generated rather than hand-written.
- Medium is email only, matching the authoring tool's scope.
- No server required — should work as a static/local tool, same constraint as the authoring tool.

## Relationship to the authoring tool

- `blockType` → template mapping is **code-defined**, mirroring how the authoring tool's block schemas are code-defined — the same set of block types should be known to both tools.
- This tool trusts the input document (it was already validated against the block JSON Schemas by the authoring tool); it doesn't need to re-validate, though it may want to fail loudly on an unknown `blockType`.

## Open questions

- How is a theme structured/declared (a JSON/config document? a set of CSS variables? code)?
- Templating approach for turning `blockType` + `data` into HTML (a templating engine? plain string interpolation?) — needs to preserve the email-safe HTML patterns from `../CLAUDE.md`.
- How do `fieldType` values that need non-trivial rendering get handled — e.g. `markdown` (needs markdown→HTML conversion), `date` (needs a display format)?
- What happens when a block's schema evolves (new field added) but a template hasn't been updated yet — is there a compatibility/versioning story, or is it always assumed both tools ship in lockstep?
- Where do block templates live relative to themes — is a template theme-specific, or one template per `blockType` with the theme only supplying style values?

## Status

Early spec — core shape agreed, but the open questions above need answers before implementation starts.
