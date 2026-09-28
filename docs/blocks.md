# Blocks: developer guide

How blocks work **as the code stands today**. The specs in `../specs/` and `../completed/` record how each piece was decided and why, and later specs change earlier ones. This page is the current-state summary: when behaviour changes, update this page in the same change. For the reasoning behind a rule, follow the links to the specs.

## Overview

An email is a **document**: campaign metadata plus an ordered list of **blocks**. Each block is an instance of a **block type**, such as `article` or `button`. The block type's **schema** defines which content fields the block has.

```
authoring tool  ──►  document (.json)  ──►  render layer + theme  ──►  email HTML
(authoring/)                                 (render/: preview, and HTML with audience markers)
```

- **Block schemas** (`../blocks/*.json`) define the block types. They're JSON Schema documents with a few custom keywords.
- **The authoring tool** (`../authoring/index.html`) is a static page, served by GitHub Pages at `https://infoentropy.github.io/emails/authoring/`. It loads the schemas, builds a form from them, previews the email live and exports the document.
- **The render layer** (`../render/`) turns a document and a theme into email HTML, and checks documents. It never writes a sending platform's syntax: audiences go out as neutral `<!--audience …-->` markers that Claude converts when pushing. Plan and remaining steps: `../specs/render-layer-tool.md`.
- **Agents** editing documents read `agents.md`, not this page.

Blocks hold **content only**. Colour, spacing, sizing, backgrounds and arrangement all belong to the theme, and never to the document. The single exception is image pixel dimensions (see [Field conventions](#field-conventions)).

## The document

```json
{
  "version": 1,
  "name": "Sleep Stories — weekly",
  "subject": "Three new Sleep Stories for this week",
  "preheader": "Narrated by voices you'll actually drift off to",
  "theme": "sleep",
  "nextId": 3,
  "blocks": [
    { "id": "b1", "blockType": "content_feature_header",
      "data": { "heading": "New This Week", "feature_type": "sleep" } },
    { "id": "b2", "blockType": "button",
      "data": { "text": "Open tonight's story", "link": "https://www.calm.com/sleep" } }
  ]
}
```

| Key | Meaning |
|---|---|
| `version` | Document **format** version, currently `1`. It isn't a block schema version. |
| `name` | Internal campaign name, never sent. |
| `subject` | Subject line. |
| `preheader` | Inbox preview text. There's exactly one, and it lives here. No block may define a `preheader` field. |
| `theme` | Optional. A theme **name** from `../render/registry.js` (`spring`, `sleep`), never a style value. Missing means the registry's default theme. An unknown name is an error. |
| `nextId` | The number the next new block's id takes. It only ever goes up, so ids are never reused. Missing (older documents) means highest existing id + 1, and the tool adds it on export. |
| `blocks` | Ordered array of block instances. Array order is render order. |

These top-level keys are hard-coded in the tool, not driven by a schema. The tool writes them in the order above.

## A block instance

```json
{
  "id": "b7",
  "blockType": "button",
  "switch": "s1",
  "ruleset": "users in US, CA, GB. not a paying subscriber",
  "hidden": true,
  "data": { "text": "Start your free trial", "link": "https://www.calm.com/trial", "variant": "primary" }
}
```

| Key | Required | Meaning |
|---|---|---|
| `id` | yes | Document-local id: `b1`, `b2`, … A new block gets `b` + `nextId`, which then goes up by one, so an id is never reused, even after a delete. People and agents refer to blocks by id ("change b7"), and the tool shows it on each block. Ids are only meaningful within their document. |
| `blockType` | yes | Which schema `data` follows. snake_case, named for what the block is, never for how it looks. |
| `data` | yes | Field values, validated against the block type's schema. |
| `hidden` | no | `true`: kept in the document but never sent. See [Visibility](#visibility). |
| `ruleset` | no | Free text describing who sees the block. See [Visibility](#visibility). |
| `switch` | no | Group label that ties blocks into a switch group. See [Switch groups](#switch-groups). |

Everything **except `data`** is block-level and belongs to no schema. Every block type gets these keys for free, and adding a new block-level key never needs a schema change.

The tool writes keys in this order: `id`, `blockType`, `switch`, `ruleset`, `hidden`, any keys it doesn't recognise, then `data`. It omits `hidden` unless it's `true`, and omits `ruleset` when blank.

## Block schemas

One file per block type in `../blocks/`, named after the `blockType`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "block:button",
  "title": "Button",
  "version": 1,
  "type": "object",
  "properties": {
    "text":    { "title": "Label", "type": "string", "fieldType": "text", "weight": 1 },
    "link":    { "title": "Link",  "type": "string", "fieldType": "text", "weight": 2, "format": "uri" },
    "variant": { "title": "Variant", "type": "string", "fieldType": "text", "weight": 3,
                 "enum": ["primary", "secondary"], "default": "primary",
                 "description": "Emphasis, resolved to an appearance by the theme." }
  },
  "required": ["text", "link"]
}
```

Schema-level keywords:

| Keyword | Meaning |
|---|---|
| `$id` | `block:<blockType>`. The tool keys its schemas by `blockType`. |
| `title` | Shown in the palette and on block cards. |
| `version` | Integer changelog aid. **Nothing checks it**, and block instances don't record it. Bump it on every allowed change. |
| `required` | Fields that must be non-empty. |
| `deprecated` | `true` retires the type: the authoring tool leaves it out of the add-block palette and a switch's *Add case of another type* picker, but existing blocks of that type keep their form, validation and export, so old documents stay editable. See [Retiring a block type](#retiring-a-block-type). |

Field keywords:

| Keyword | Meaning |
|---|---|
| `title` | Form label. |
| `type` | JSON Schema type: `string`, `integer`, `number`. Used for validation. |
| `fieldType` | Custom keyword that picks the form control. See the table below. |
| `weight` | Sort order, ascending. It sets the order of form inputs **and** of keys in the exported `data`. Don't rely on `properties` key order. |
| `description` | Help text under the input. |
| `enum` | Allowed values. The control is still a plain text box, so validation is the only guard. |
| `format` | `uri` (must start with `http://` or `https://`) or `date` (`YYYY-MM-DD`). |
| `default` | Value for a new block, and the value the render layer must use when the field is missing from `data`. It must satisfy the field's own `enum`/`required`. |

| `fieldType` | `type` | `format` | Control |
|---|---|---|---|
| `text` | `string` | | single-line input |
| `paragraph` | `string` | | textarea |
| `markdown` | `string` | | textarea. The render layer converts it and **escapes** raw HTML. |
| `date` | `string` | `date` | date input |
| `integer` | `integer` | | number input, step 1 |
| `float` | `number` | | number input |

Add a `fieldType` only when a real field needs it. Image, colour and link pickers, selects and checkboxes are deliberately absent. Images, links and enums are authored as `text`.

## The block library

| `blockType` | Fields, in `weight` order (`*` = required) | Notes |
|---|---|---|
| `content_feature_header` | `heading*`, `feature_type*` (`meditate` \| `sleep`) | No imagery; the theme keys visuals off `feature_type`. |
| `image_with_text` | `heading*`, `body` (markdown), `image*`, `image_alt*`, `image_width*`, `image_height*` | Which side the image sits on is the theme's choice. |
| `article` | `headline*`, `link*`, `image*`, `image_alt*`, `image_width*`, `image_height*`, `variant` (default `secondary`) | One per article. `primary` = lead, `secondary` = regular item. |
| `button` | `text*`, `link*`, `variant` (default `primary`) | |
| `divider` | `variant` (default `primary`) | |

Why each block looks the way it does: `../completed/email-block-library.md`.

## Field conventions

- **`variant`** is the one shared vocabulary for emphasis: `enum: ["primary", "secondary"]`, `fieldType: text`, always optional with a default. The default is chosen per block type. The theme maps `(blockType, variant)` to an appearance, so a button's `primary` and a divider's `primary` needn't look alike. Use `variant` rather than inventing a size or colour field.
- **Image fields** come as four siblings: `<name>` (URL, `format: uri`), `<name>_alt`, `<name>_width`, `<name>_height` (integers, pixels). Email clients need explicit dimensions to reserve space while images are blocked. That's the only reason sizes are allowed in the document.
- **`body`** is `fieldType: markdown`.
- **Empty optional field = not filled in.** Validation skips `enum`/`format` checks on it, and the render layer omits whatever it would have produced.
- **Declare `enum` and `format: uri`** even though the widget is a text box. Validation is the only guard rail.
- **Schemas are flat.** There are no arrays or nested objects, so a list of articles is a list of blocks.

## Visibility

Three optional block-level keys control whether a block is sent, and to whom. Design and rationale: `../completed/block-segmentation.md`.

### `hidden`

`"hidden": true` keeps the block in the document and never sends it. It's the author's off switch and always wins over `ruleset` and `switch`. Hidden blocks aren't validated: they're never sent, and an empty hidden block is normal (e.g. an email type's block the copy had nothing for).

### `ruleset`

Free text saying who sees the block, in the author's own words:

```json
"ruleset": "users in US, CA, GB. not a paying subscriber"
```

- While drafting there's no grammar, and nothing in this repo knows which recipient attributes exist. Those depend on the sending platform and its setup.
- The authoring tool stores the text as typed (trimmed on export).
- **Settled form:** facet ids (`category.name`: lower-case letters, digits, hyphens) joined with ` + `, meaning *and*, e.g. `region.us-ca-gb + subscription.not-paying`. `parseRuleset()` in `../render/render.js` recognises it; anything else is unsettled free text. The preview understands both (see *Preview as* below).
- Before an email is sent, each free-text ruleset is **settled** into **facets**, in a conversation between Claude and the person: canned, approved conditions per category (region, subscription, behaviour), combined with ` + `, e.g. `region.us-ca-gb + subscription.not-paying`. `check` warns about an unsettled ruleset (`ruleset_unsettled`); converting markers into platform conditions stops on one. *(The settling and conversion procedures come in step 6. See the render layer spec, **Audiences**.)*
- No `ruleset`: the block goes to everyone.

### Switch groups

Several blocks where each recipient sees **at most one**. It's a switch statement over free-text rulesets.

```json
{ "id": "b7", "blockType": "button", "switch": "s1", "ruleset": "users in US, CA, GB. not a paying subscriber", "data": { … } },
{ "id": "b6", "blockType": "button", "switch": "s1", "data": { … } }
```

Semantics:

1. Blocks with the same `switch` value form one group. **Group members must be adjacent** in `blocks`, because the group renders in one place. A split group is a validation error in the tool and a hard error for the render layer.
2. Cases are checked **in array order; the first match wins.**
3. **If the last case has no `ruleset`, it's the fallback** ("Otherwise"). If the last case has a ruleset, the group has no fallback, and recipients no case matches see nothing.
4. An earlier case with no ruleset matches everyone and hides every case after it. That's valid, but it gets a warning.
5. Cases don't need to share a `blockType`, or to test the same attribute.
6. `hidden` on a case removes just that case. A hidden fallback means no fallback.
7. The `switch` value is only a label, unique per group within the document. The tool generates `s1`, `s2`, … and never shows it.

In the HTML for sending (`renderHtml`), a group becomes one marked chain:

```html
<!--audience if="users in US, CA, GB. not a paying subscriber"-->  …b7…
<!--audience else-->                                               …b6…
<!--audience end-->
```

Further cases with a ruleset add `<!--audience elseif="…"-->`, and a group with no fallback has no `else`. A single block with a ruleset is `if` … `end`. When the email is pushed, Claude replaces the markers with the platform's own conditionals (for Iterable, Handlebars), built from the facets' approved conditions.

## The authoring tool

`../authoring/index.html` is one page with an inline `<style>` and `<script>` and no dependencies. It must be served over http(s): GitHub Pages publishes `master` at `https://infoentropy.github.io/emails/authoring/`, and locally you run `python3 -m http.server` in the repo root and open `http://localhost:8000/authoring/`. Opening the file directly shows an error, because browsers block loading files from `file://`.

- **Schemas and renderer are loaded, not copied.** On start, `loadRenderer()` imports `../render/registry.js` and `../render/render.js`, then `registry.loadSchemas()` fetches `../blocks/<blockType>.json` for each registered type into `SCHEMAS`, in registry order. `../blocks/*.json` is the only copy.
- **Paths are relative** (`../render/…`, `../blocks/…`), never root-absolute: on Pages the site lives under `/emails/`.
- **The form is generated.** Each field renders through `control()`, chosen by `fieldType`, in `weight` order, labelled with `title` (plus `*` if required) and followed by the `description`/enum help text.
- **The theme picker** sits with the campaign fields and writes the document's `theme`.
- **Validation is advisory, and shared.** The Validation panel shows `check()` from `../render/render.js`: the same list agents get from `node render/check.js` (see [The render layer](#the-render-layer)). Errors show inline next to the field and mark the block; warnings are listed in grey. Nothing ever blocks export.
- **Live preview.** Every change re-renders the email with `renderPreview()` into a sandboxed `<iframe srcdoc>`, scaled to fit the panel, with a Desktop/Mobile width toggle. Hidden blocks are left out, and a block that can't render shows an inline error in its place.
- **Preview as.** Above the preview, when the email has rulesets, a picker lists the facets in use, one row per category, and each unsettled ruleset as a whole. Ticks say what the imagined recipient matches. A block shows when it has no ruleset, when all its facets are ticked, or when its unsettled text is ticked; a switch group shows its first matching case. Ticks are view state only (never saved), and the note under the preview says who it's showing. It tests nothing: real matching happens in the platform.
- **Copy HTML** (preview panel) copies `renderHtml()`'s output, or downloads it if the clipboard is blocked: every block that isn't hidden, audiences as `<!--audience …-->` markers. An email without rulesets can be pasted into a sending platform as it is; one with audiences needs its markers converted first (normally by Claude). Validation errors block it.
- **`serialise()`** builds the exported document: top-level keys as above, `data` keys in `weight` order, numeric strings from `integer`/`float` fields converted to numbers, block-level keys as described above. Validation and the preview both run on its output.
- **Nothing unknown is lost.** A block whose `blockType` has no schema shows as a read-only placeholder and is written back out untouched (it's still a `check` error, since it can't be rendered). Block-level keys the tool doesn't recognise are kept too. Opening a newer document in an older copy of the tool and saving must never destroy content.
- **Persistence:** every change autosaves to `localStorage` under `email-block-composer/doc`. That's crash protection only: the `.json` file is the real format. `docText()` writes it: 2-space indent, the tool's key order, a trailing newline.
- **File sync** (Chrome and Edge, via the File System Access API). *Open file* and *Save as…* attach the editor to that file, shown in a bar under the toolbar:
  - Every change is written to the file 400ms after the last edit.
  - While the tab is visible, the file is checked every 1.5s (and on focus). A change made elsewhere, by an agent say, loads and re-renders. The editor never writes back just because it loaded, so an agent's formatting survives until the person edits.
  - A file that isn't a valid document (caught mid-write, say) is left alone: nothing is written to it, edits here are kept, and the bar says why.
  - If the file changes while edits here haven't been written yet, the editor asks which version wins.
  - The file handle is kept in IndexedDB. After a reload the browser may need the person to click *Reconnect*. Then the file wins, unless edits were made here since the reload.
  - *Disconnect* and *New* detach; the file is left as it is.
  - In other browsers, *Open file* imports and *Save as…* downloads, as before. *Copy JSON* / *Paste JSON* work everywhere.
- **Deprecated types can't be added.** `addableTypes()` filters `deprecated: true` schemas out of the palette and the add-case select. Everything else still uses `SCHEMAS` directly, so existing blocks of a deprecated type render and export as before.
- **Structure in the UI:** `units()` splits the flat `blocks` array into plain blocks and switch groups. Groups move as one unit. A group can't be split from the UI, only by importing a document, and the *Regroup* fix then moves the cases back together.

## The render layer

Plain ES modules in `../render/`, with no dependencies. They run unchanged in the browser and under Node, and do no I/O: callers load the schemas with `registry.loadSchemas(readJson)` and pass them in.

| File | What it is |
|---|---|
| `registry.js` | Every block type (`templates`) and theme (`themes`, `defaultTheme`). Adding one means adding it here. Also `schemaUrl()` and `loadSchemas()`. |
| `render.js` | `check(doc, {schemas, theme})`, `renderHtml(doc, {schemas, theme})` (the email for sending, with audience markers; throws on `check` errors), `renderPreview(doc, {schemas, theme, as})` (`as`: facet ids, settled rulesets or unsettled ruleset texts the recipient matches), `parseRuleset()` and `audienceOptions()` (what *Preview as* offers). |
| `html.js` | The `html` tagged template (escapes every value unless wrapped in `raw()`), plus `safeUrl`, `fit`, `altText` and `paragraphs`. |
| `blocks/<blockType>.js` | One template per block type: `(data, style, theme)` → one table row. |
| `themes/<name>/theme.js` | A theme: `label`, `styles`, `imageSide`, `dateFormat`, `shell()`. |
| `themes/shell.js` | The email-safe outer document both themes use, plus `row()` and the width constants. |
| `check.js`, `preview.js`, `email.js` | Node wrappers: print `check()` as JSON; write `renderPreview()` HTML; write `renderHtml()` HTML (issues to stderr and exit 1 on errors). |

**Rendering one block:** a missing or empty field takes its schema `default`, and fields the schema doesn't know are ignored. Numeric strings become numbers and `date` fields are formatted with the theme's `dateFormat`. Then the theme resolves `(blockType, variant)` to a style, and a variant it doesn't style renders as `primary` with a warning. The template gets the data (with `variant` set to the one actually used), that style and the theme.

**Templates** build markup with `html\`…\``, so authored text is always escaped. Only `http(s)` URLs reach `href`/`src` (`safeUrl`). Markup follows the email conventions in `../CLAUDE.md`: tables, inline styles, 600px wide (`WIDTH`, and `CONTENT` inside the gutters), with classes `fluid` / `stack` that the shell's media query uses at narrow widths.

**`markdown` fields** aren't converted yet. They render as escaped plain text, with blank lines as paragraph breaks (`paragraphs()`). Real markdown is on the backlog.

**`check()`** returns `[{severity, block, field, code, message}]` (plus `switch` for switch issues). Hidden blocks aren't checked.

| Code | Severity | Meaning |
|---|---|---|
| `required`, `type`, `enum`, `format` | error | A field fails its schema. |
| `unknown_block_type` | error | No schema or template for `blockType`. |
| `unknown_theme` | error | `theme` isn't in the registry. |
| `theme_missing_type` | error | The theme has no styles for this block type. |
| `render_failed` | error | The block threw while rendering. |
| `duplicate_id` | error | Two blocks share an id. |
| `switch_split` | error | A switch group's cases aren't adjacent. |
| `not_a_document` | error | No `blocks` array. |
| `variant_unstyled` | warning | The theme doesn't style this variant; it renders as `primary`. |
| `ruleset_empty` | warning | A non-final switch case matches everyone. |
| `next_id` | warning | `nextId` isn't above every existing id. |
| `ruleset_unsettled` | warning | A ruleset is still free text; it must be settled into facets before sending. |
| `facet_category_repeated` | error | Two facets from one category in one ruleset. |

**HTML for sending** (`renderHtml`): every block that isn't hidden, audiences as `<!--audience if|elseif="…"-->` / `<!--audience else-->` / `<!--audience end-->` comments (ruleset text HTML-escaped, `--` as entities), and every `{` in content, subject and preheader written as `&#123;` so templating languages can't read authored text as a tag. No platform syntax: see *Switch groups* above for the markers and who converts them.

## Changing block types

Block schemas evolve **additively**. A document written against version *N* of a schema must stay valid against every later version, with no migration. Full rules: `../completed/serverless-email-authoring-tool.md`, **Schema evolution**.

| Allowed (bump `version`) | Forbidden (make a new `blockType` instead) |
|---|---|
| Add an **optional** field **with a `default`** | Rename, remove or retype a field |
| Widen an `enum` | Narrow an `enum` |
| Remove a field from `required` | Add a field to `required` |
| Edit `title` / `description` | |

The render layer's side of the contract: a field missing from `data` takes its schema `default`, and a field in `data` the schema doesn't know is ignored.

### Adding a block type

1. Write `../blocks/<blockType>.json`: `$id` `block:<blockType>`, `version: 1`, fields with `title`/`type`/`fieldType`/`weight`, and `required`. Content only.
2. Write its template, `../render/blocks/<blockType>.js` (see [The render layer](#the-render-layer)).
3. Import it in `../render/registry.js` and add it to `templates`. Its position there is its position in the palette.
4. Add styles for it to **every** theme under `../render/themes/`: a `primary` entry, plus one per other `variant` value. `check` reports an error for a type a theme doesn't style.
5. Serve the repo and open the tool, add the block from the palette, fill it in, and confirm the exported `data` is in `weight` order, validation behaves as expected, and the preview looks right in each theme at both widths.
6. Add a row to [The block library](#the-block-library) above, and to `../completed/email-block-library.md`.

### Changing an existing block type

Check the change against the table above. If it's allowed, edit the schema in `../blocks/`, bump `version`, and update the library table here.

### Retiring a block type

Set `"deprecated": true` on the schema and bump `version`. Keep it in the registry. The type disappears from the tool's add pickers, but existing blocks of that type stay editable and still export. *+ Add case* still copies an existing case, whatever its type. Don't delete the schema: documents that use the type would lose their form and fall back to the read-only unknown-type placeholder.

## Where things are decided

| Topic | Spec |
|---|---|
| Document format, schema keywords, evolution rules, the tool | `../completed/serverless-email-authoring-tool.md` |
| The block library and field conventions | `../completed/email-block-library.md` |
| `hidden`, `ruleset`, switch groups | `../completed/block-segmentation.md` |
| Rendering, themes, audience markers, settling rulesets into facets | `../specs/render-layer-tool.md` |
