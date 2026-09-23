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
- This tool **cannot** assume the input document is valid. The authoring tool's validation is advisory, not blocking (by design — half-finished emails need to be saveable), so a document that fails its block schemas can still be exported. Decide per case whether to validate on the way in or to render defensively; either way, "it was already validated" is not true.
- Unknown `blockType` is a hard error: this tool has no template for it and cannot produce correct HTML. (The authoring tool takes the opposite line and preserves unknown blocks, so that round-tripping a document through an older copy never destroys content.)

### Themes and variants

A block may carry a `variant` (`primary` or `secondary` — see the authoring tool spec). The theme owns what each one looks like, resolving `(blockType, variant)` to an appearance; the document never names a colour.

When a theme has no styling for a variant in use, **render the block as `primary` and emit a warning** naming the block type and the missing variant. Failing hard would be worse than it looks: widening the `variant` enum is an allowed schema change, so a hard error would turn every such widening into a breaking change for every existing theme. A warning keeps the email building while leaving the gap visible to whoever maintains the theme.

### Compatibility with evolving schemas

The authoring tool's **Schema evolution** section fixes the rules that make version skew survivable, and they impose two requirements on templates here:

- A field missing from a block's `data` takes the `default` declared in its schema. Old documents predate fields a newer template expects, and this is what fills the gap.
- A field present in `data` that the template doesn't use is **ignored**, never an error. This is what lets a stale template render a newer document.

Because schemas may only ever gain optional fields — renames and removals become a new `blockType` instead — a template written for version *N* of a schema keeps working against every later version. Lockstep shipping is not required, which matters because the two tools have no shared distribution path: this one is a Python script, the other a static HTML file users keep local copies of.

## Implementation

- A **Python 3** script, run locally/on demand — no server process.
- Templating via **Jinja2** (the standard, widely-used Python templating engine): one Jinja2 template per `blockType`, each block's `data` rendered through its template, then the rendered blocks concatenated into the final email HTML (wrapped in whatever outer document shell the theme provides).
- Basic shape: script takes the authored JSON document (and a theme selection) as input, and writes the rendered HTML as output.

### Output flavors

The render layer is configured with an **output flavor**: which email platform's template language the HTML is written for. The rendered file goes to that platform as a template, not as final HTML, so anything decided per recipient at send time (currently: per-block audience rules, see `../ideas/block-segmentation.md`) is emitted in the flavor's own syntax.

- **Handlebars** is the first flavor. SendGrid and Marketo are expected to follow, each as its own flavor. SendGrid's Handlebars dialect has different built-in helpers from plain Handlebars, so it isn't the same flavor.
- A flavor owns: its conditional syntax, the mapping from document field names (e.g. `country`) to the platform's recipient fields, and **escaping its own syntax** in rendered content (e.g. a literal `{{` in copy must not become a Handlebars tag).
- The authored document never names a flavor. The same document renders for any flavor.

## Open questions

Schema evolution and version skew are now settled — see **Compatibility with evolving schemas** above.

- How is a theme structured/declared (a JSON/config document? a set of CSS variables? code)? Also: does a theme supply its own outer document shell/Jinja2 template, or only style values plugged into a fixed shell?
- **Which side does an `image_with_text` image sit on?** The authoring document deliberately does not say — a `layout` field was drafted and removed to keep the schema content-only — so this is entirely the theme's call. A fixed side, or alternating down the email? Alternating needs the template to know a block's position among its siblings, which is more context than rendering one block in isolation provides.
- Exact CLI shape: input/output as file arguments vs. stdin/stdout, how the theme and output flavor are selected, where block templates and themes are located on disk.
- How should a `date` field be formatted for display? Still open.

`markdown` is settled: convert to HTML here (a Python markdown library called from the Jinja2 template), configured so that **raw HTML in the source is escaped, not passed through**. The default passthrough behaviour would quietly undo the authoring tool's ban on raw HTML editing. Note that the legacy `body` values in `content/weekly.json` are raw HTML and need converting to markdown as a one-off before they can round-trip.

## Status

Early spec — core shape and implementation approach (Python 3 + Jinja2) agreed, but the open questions above need answers before implementation starts.
