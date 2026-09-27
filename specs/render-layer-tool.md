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
- Basic shape: a render function takes the authored JSON document, a theme and an output flavor, and returns the rendered HTML (see **Entry point**).

### Theme structure

A theme is a directory, not a single file — `render/themes/<theme_name>/`, containing:

- `shell.html.j2` — the outer HTML document (doctype, `<head>`, MSO conditionals, media queries), wrapping a `{{ body }}` placeholder where the concatenated, rendered blocks go. The theme owns the shell rather than plugging values into one fixed shell: `flipboard/techdigest.html` and `traction/index.html` already diverge at the shell level (different meta tags, font stacks, breakpoints, doctype quirks), which is exactly the kind of brand-level variation a theme exists to own.
- `style.json` — the `(blockType, variant)` → appearance lookup (colors, fonts, spacing), plus two theme-wide settings:
  - `image_with_text.image_side`: `"left"` or `"right"`. Fixed per theme, not alternating — alternating would need each block template to know its position among same-type siblings, more context than the per-block rendering model in this spec provides. Worth revisiting only if a theme actually needs it.
  - `date_format`: a strftime pattern (e.g. `"%B %-d, %Y"`) applied to any `date`-formatted field at render time, with a repo-wide default pattern if a theme omits it. The document keeps storing ISO `YYYY-MM-DD` (already fixed by the block schema conventions); how it displays is presentation, same as `bg_color` or spacing.

Themes are code-defined and selected by name, looked up under `render/themes/`, not by arbitrary path — mirroring `blockType` → template being code-defined rather than user-supplied.

### Entry point

Marketers never run the renderer. Its callers are Skill C of the planned Claude plugin (`../ideas/claude-authoring-plugin.md`), which runs it in Claude's sandbox, and developers previewing templates and themes. So the interface is a function, not a CLI:

```python
render(document, theme, flavor, translations=None) -> str
```

- `document` — the parsed authored JSON document.
- `theme` and `flavor` — names, looked up under `render/themes/` and `render/flavors/`.
- `translations` — the approved ruleset translations. Needed only when the document contains a `ruleset`; a ruleset without an approved translation is still a hard error.
- Returns the rendered HTML as a string. No file I/O happens inside `render`.

A thin command wrapper in the same file reads the files, calls `render`, and prints the result, for callers that shell out:

```
python render/render.py DOC.json --theme NAME --flavor NAME [--translations FILE] > out.html
```

Nothing else lives in the wrapper.

### Delivery

The output is a template for the email platform, not a finished email, and getting it there is part of the flow:

- **v1: copy and paste** into the platform's template editor (Iterable first). No credentials, nothing to host.
- **Later: upload through the platform's API.** It needs an API key held somewhere (the skill, the sandbox, or a small service), which sits badly with the no-server constraint, so it waits until pasting is the actual bottleneck.

Opening the output in a browser is only a rough preview. With segmentation in play it contains the flavor's conditional syntax, so every branch of a switch group shows at once. A per-recipient preview is the platform's job.

Disk layout:

```
render/
  render.py
  blocks/<blockType>.html.j2      — one Jinja2 template per block type, code-defined
  themes/<theme_name>/            — shell.html.j2 + style.json, one dir per theme
  flavors/<flavor_name>.py        — conditional-wrapping + syntax-escaping logic per flavor
```

### Output flavors

The render layer is configured with an **output flavor**: which email platform's template language the HTML is written for. The rendered file goes to that platform as a template, not as final HTML, so anything decided per recipient at send time (currently: per-block rulesets, see `../completed/block-segmentation.md`) is emitted in the flavor's own syntax.

- **Iterable** is the first flavor: Handlebars as Iterable implements it, with Iterable's built-in helpers. SendGrid is expected to follow as its own flavor. It is also Handlebars-based, but its helpers differ, so "Handlebars" alone doesn't identify a flavor.
- A flavor owns: how conditionals are wrapped around blocks, and **escaping its own syntax** in rendered content (e.g. a literal `{{` in copy must not become a Handlebars tag). The conditions themselves are not the flavor's job. They are AI-translated per environment and handed to the render layer already approved (see the segmentation idea), because which recipient attributes exist can't be known generically.
- The authored document never names a flavor. The same document renders for any flavor.
- Block-level fields the render layer must honour (from `../completed/block-segmentation.md`, already produced by the authoring tool): `hidden: true` blocks are skipped entirely; a block with a `ruleset` is wrapped in its approved condition; adjacent blocks sharing a `switch` value render as one if / else-if / else chain, first match wins, with a last case lacking a `ruleset` as the `else`. A split switch group is a hard error.

### Ruleset translation (carried over from block segmentation)

Before rendering, each distinct `ruleset` needs an AI-translated and human-approved condition for the chosen flavor and environment. The design is in `../completed/block-segmentation.md` (**Translation: ruleset → conditional**). The parts that land here:

- A **translate step** (AI, run before this script: Claude inside the plugin's Skill C, or a small script calling the Claude API) that writes a translations file of ruleset text → condition, cached by (ruleset text, environment, flavor).
- A **review** of each ruleset, the AI's reading of it and the generated condition, before the file counts as approved.
- This script **reads approved translations and never calls an AI**. A ruleset with no approved translation is a hard error.
- Still open from that spec: where the translations file lives (inside the document or next to it), what form the environment context takes, and whether review should flag an audience left with no blocks.

## Open questions

Schema evolution and version skew are now settled — see **Compatibility with evolving schemas** above. Theme structure/shell ownership, the `image_with_text` image side, `date` display formatting, how the renderer is invoked, and how its output reaches the platform are now settled too — see **Theme structure**, **Entry point** and **Delivery** above.

`markdown` is settled: convert to HTML here (a Python markdown library called from the Jinja2 template), configured so that **raw HTML in the source is escaped, not passed through**. The default passthrough behaviour would quietly undo the authoring tool's ban on raw HTML editing. Note that the legacy `body` values in `content/weekly.json` are raw HTML and need converting to markdown as a one-off before they can round-trip.

Still open: where the ruleset translations file lives (inside the document or next to it), what form the environment context takes for translation, and whether translation review should flag an audience left with no blocks (carried over from `../completed/block-segmentation.md`, noted in **Ruleset translation** above).

## Status

Core shape, implementation approach (Python 3 + Jinja2), theme structure, entry point and delivery are now settled. The remaining open items are about ruleset translation tooling, not the render layer's own design — implementation can start.
