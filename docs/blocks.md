# Blocks: developer guide

How blocks work **as the code stands today**. The specs in `../specs/` and `../completed/` record how each piece was decided and why, and later specs change earlier ones. This page is the current-state summary: when behaviour changes, update this page in the same change. For the reasoning behind a rule, follow the links to the specs.

## Overview

An email is a **document**: campaign metadata plus an ordered list of **blocks**. Each block is an instance of a **block type**, such as `article` or `button`. The block type's **schema** defines which content fields the block has.

```
authoring tool  ──►  document (.json)  ──►  render layer + theme  ──►  email HTML
(authoring/)                                 (not built yet)
```

- **Block schemas** (`../blocks/*.json`) define the block types. They're JSON Schema documents with a few custom keywords.
- **The authoring tool** (`../authoring/index.html`) is a single static page. It builds a form from the schemas and exports the document.
- **The render layer** turns a document and a theme into email HTML. It's specified in `../specs/render-layer-tool.md` but **not built yet**. Everything below about rendering is what it must do, not what exists.

Blocks hold **content only**. Colour, spacing, sizing, backgrounds and arrangement all belong to the theme, and never to the document. The single exception is image pixel dimensions (see [Field conventions](#field-conventions)).

## The document

```json
{
  "version": 1,
  "name": "Sleep Stories — weekly",
  "subject": "Three new Sleep Stories for this week",
  "preheader": "Narrated by voices you'll actually drift off to",
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
| `blocks` | Ordered array of block instances. Array order is render order. |

These top-level keys are hard-coded in the tool, not driven by a schema.

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
| `id` | yes | Document-local id: `b1`, `b2`, … A new block gets `b` + (highest numeric suffix + 1). Ids aren't stable across exports, so nothing outside the document should reference them. After a delete, an id can be reused. |
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
| `deprecated` | Specified, but **not implemented yet**: the plan is to hide the type from the add-block palette while keeping existing instances editable. The tool ignores it today. |

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

Why each block looks the way it does: `../specs/email-block-library.md`.

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

- There's no grammar, and nothing in this repo knows which recipient attributes exist. Those depend on the sending platform and its setup.
- The authoring tool stores the text as typed (trimmed on export) and doesn't parse it.
- Before rendering, an AI translates each distinct ruleset into the platform's condition syntax, using context about the user's environment. A person reviews the translation, and the render layer uses only approved translations. A ruleset with no approved translation is a hard error, never an unconditional block. *(Not built. See the render layer spec.)*
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

The render layer outputs a group as one conditional chain in the platform's syntax. For Iterable:

```handlebars
{{#if <condition for b7>}}
  …b7…
{{else}}
  …b6…
{{/if}}
```

It adds a `{{else if …}}` for each further case, and omits `{{else}}` when there's no fallback.

## The authoring tool

`../authoring/index.html` is one file with an inline `<style>` and `<script>`, no dependencies, and no `fetch()`, so it works from `file://`.

- **Schemas are inlined.** The `SCHEMAS` object literal near the top of the script is a hand-copied version of `../blocks/*.json`, keyed by `blockType`. The two must match exactly; see [Changing block types](#changing-block-types).
- **The form is generated.** Each field renders through `control()`, chosen by `fieldType`, in `weight` order, labelled with `title` (plus `*` if required) and followed by the `description`/enum help text.
- **Validation is advisory.** `issuesFor()` checks `required`, `type` (integer/number), `enum`, `format: uri` and `format: date` for each block. `structureIssues()` checks split switch groups and empty rulesets on non-final cases. Problems show inline and in the Validation panel, but never block export.
- **`serialise()`** builds the exported document: `data` keys in `weight` order, numeric strings from `integer`/`float` fields converted to numbers, block-level keys as described above.
- **Nothing unknown is lost.** A block whose `blockType` has no schema shows as a read-only placeholder and is written back out untouched. Block-level keys the tool doesn't recognise are kept too. Opening a newer document in an older copy of the tool and saving must never destroy content.
- **Persistence:** every change autosaves to `localStorage` under `email-block-composer/doc`. That's crash protection only: the `.json` file (via *Save as…* / *Copy JSON*) is the real format, and *Open file* / *Paste JSON* load one back in.
- **Structure in the UI:** `units()` splits the flat `blocks` array into plain blocks and switch groups. Groups move as one unit. A group can't be split from the UI, only by importing a document, and the *Regroup* fix then moves the cases back together.

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
2. Paste the same JSON into `SCHEMAS` in `../authoring/index.html` under the key `<blockType>`.
3. Check that the two copies match:

   ```sh
   python3 - <<'EOF'
   import json, glob
   s = open('authoring/index.html').read()
   a = s.index('const SCHEMAS = ') + len('const SCHEMAS = ')
   inline = json.loads(s[a:s.index('\n};', a) + 2])
   for f in sorted(glob.glob('blocks/*.json')):
       d = json.load(open(f)); k = d['$id'].split(':', 1)[1]
       print(k, 'ok' if inline.get(k) == d else 'MISMATCH')
   print('inline only:', set(inline) - {json.load(open(f))['$id'].split(':', 1)[1] for f in glob.glob('blocks/*.json')} or 'none')
   EOF
   ```

4. Open the tool, add the block from the palette, fill it in, and confirm the exported `data` is in `weight` order and validation behaves as expected.
5. Add a row to [The block library](#the-block-library) above, and to `../specs/email-block-library.md`.
6. Once the render layer exists: add the block's template, and theme styling for each `variant` it uses.

### Changing an existing block type

Check the change against the table above. If it's allowed, edit both copies, bump `version`, run the check in step 3, and update the library table here.

## Where things are decided

| Topic | Spec |
|---|---|
| Document format, schema keywords, evolution rules, the tool | `../completed/serverless-email-authoring-tool.md` |
| The block library and field conventions | `../specs/email-block-library.md` |
| `hidden`, `ruleset`, switch groups | `../completed/block-segmentation.md` |
| Rendering, themes, output flavors, ruleset translation | `../specs/render-layer-tool.md` |
