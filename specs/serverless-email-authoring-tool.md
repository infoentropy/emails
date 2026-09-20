# Serverless email authoring tool

## Problem

Building marketing emails today means hand-editing table-based HTML (see `flipboard/techdigest.html`, `traction/index.html`) or running a server-side app to manage them. Want something that runs without a server and still produces valid, email-client-safe HTML.

## Core idea

- An email is a sequence of **blocks** (e.g. header, discount banner, content card, CTA, footer).
- Each block type has a fixed **schema**: a defined set of fields (text, image URL, color, link, etc.) — not free-form HTML.
- Authoring an email = picking blocks, filling in their fields, and reordering them (move up/down). No raw HTML editing.
- Each block schema maps to an HTML template/partial that renders it. Swapping a block's HTML (a different theme) doesn't change the schema or the authored content, only the rendering.
- Medium is **email only** — no other output medium (e.g. web) is in scope.

## Tool shape

- The tool is a **single static HTML file** — one self-contained document with inline `<style>` and `<script>`, no build step, no package manager, no bundler.
- It must work when opened directly from disk (`file://`). That rules out `fetch()`ing sibling `.json` or `.js` files, since browsers block those requests under `file://`.
- Consequently, **block schemas are embedded in the file itself** as a JavaScript object literal (the JSON Schema documents, inlined). "Code-defined schemas" means a developer edits that literal in the source; there is no schema loader and no runtime schema fetching.
- No external dependencies, including CDN `<script>` tags — the tool must work offline. Anything it needs is vendored inline or hand-rolled.
- This matches how the rest of this repo works: standalone HTML files you open in a browser.

## Block schemas

- Block schemas are **code-defined**, not end-user-defined. The set of available block types and their fields is authored by developers (in the tool's source/config); end users choose from existing block types and fill in field values — they don't create new block types or add/remove fields.
- Each block type's schema is declared as a **JSON Schema** document (fields as `properties`, and whatever else JSON Schema offers — required fields, descriptions, etc.). `type` stays JSON Schema's own type (`string`, `number`, `integer`, ...); the widget/form-control choice is a separate custom `fieldType` keyword (see Authoring form), so schemas remain valid JSON Schema.
- Fields within a schema have a fixed **order**, and that order is meaningful: e.g. a "content card" block might define `title`, `body`, `cta` in that order. The order drives both how the authoring form lays out its inputs and the field order in the output. Order is declared explicitly via a `weight` property on each field; fields are sorted by `weight` ascending, rather than relying on `properties` key order (which JSON Schema doesn't guarantee across tooling).

### Schema evolution

Block schemas are code-defined, but authored documents are files on disk that outlive any particular copy of either tool — and the two tools share no distribution path (this one is a static HTML file users keep locally; the render layer is a Python script). Version skew is structural, so schemas evolve under a rule rather than a migration system.

- Each block schema carries a `version` integer, starting at `1`. It is a changelog aid for developers — **nothing validates against it**, and block instances do not record it.
- **Allowed** (bump `version`): add a new field, provided it is optional and declares a `default`; widen an `enum`; remove a field from `required`; edit `title`/`description`.
- **Forbidden**: renaming, removing or retyping a field; adding a field to `required`; narrowing an `enum`. Any of these is a new block type with a new `blockType`, not a revision of the existing one.
- Retiring a block type: set `"deprecated": true` on its schema. The authoring tool hides it from the add-block palette but still renders its form for existing instances, so old documents stay editable.

The point of the rule is that it makes migration unnecessary: a document authored against version *N* of a schema is valid against every later version **by construction**, because later versions only ever add optional fields. There is no migration machinery in v1 and none is planned.

Two companion rules give the render layer the other direction of compatibility — a stale template receiving a newer document:

- A field missing from a block's `data` takes the `default` declared in its schema.
- A field present in `data` that the schema doesn't know is **ignored**, never an error.

### What belongs in a block schema

The authored document is meant to be theme-independent, so presentation values generally belong to the theme, not the schema. But the line is drawn **per field, by asking whether the value carries meaning or only styling** — not by a blanket ban on anything that looks like a measurement:

- A spacer's `height` *is* the block's entire content; without it the block means nothing. It stays in the schema.
- A button's `width` or a header's `padding` are styling decisions the theme should own. They don't.

Applying this to each field of the real block set is the block library's job, not this spec's.

### Which block types ship

Deferred to a **separate spec** — this spec defines the document format and the tool, not the block library. The concrete set of block types (and their field definitions) is worked out in `../ideas/email-block-library.md`.

For development and testing, this tool ships with a small number of throwaway fixture schemas (e.g. the `content_card` below). They exist to exercise the form, reordering and export paths, and are expected to be replaced wholesale by the real library.

## Authoring form

- Each field declares a `fieldType`, and the form input it renders as is determined by that value: `integer`, `float`, `text` (single-line input), `paragraph` (multi-line textarea), `markdown` (textarea authored in markdown), `date`. `fieldType` is a custom keyword alongside JSON Schema's own `type`/`format` (used for validation), not a replacement for it. Suggested pairing:

  | `fieldType`  | JSON Schema `type` | JSON Schema `format` |
  |--------------|---------------------|------------------------|
  | `text`       | `string`            | —                      |
  | `paragraph`  | `string`            | —                      |
  | `markdown`   | `string`            | —                      |
  | `date`       | `string`            | `date`                 |
  | `integer`    | `integer`           | —                      |
  | `float`      | `number`            | —                      |

- Other field types (image picker, color picker, link picker, etc.) are explicitly deferred — not needed for a first version.
- A field's `title` is its form label; its `description`, if present, renders as help text under the input.

### Block operations

The authoring UI supports, per email:

- **Add** a block — pick a block type from a palette of the available types; the new block is appended to the end with empty/default field values.
- **Delete** a block.
- **Move up / move down** — reordering is one position at a time. Drag-and-drop is deferred.
- **Duplicate** a block — copies its field values into a new block instance with a fresh `id`.

### Block instance ids

- Ids are **incrementing and document-local**: `b1`, `b2`, `b3`, …
- The next id is derived on demand as `b` + (highest existing numeric suffix in the document + 1). No counter is stored in the document — that keeps the exported JSON clean, at the cost of an id being reusable after the last block is deleted.
- That's acceptable because ids are only used by the UI to key and reference blocks *within a single document*. They are **not stable identifiers** across exports, and nothing outside the document should reference them.

## Validation

- The JSON Schema serves two purposes: it drives form layout (via `fieldType`/`weight`/`title`) and it describes what valid data looks like.
- v1 does **not** bundle a full JSON Schema validator — vendoring one inline conflicts with the single-file, no-dependency constraint. Instead the tool hand-rolls a check over the subset it actually uses: `required`, `type`, `enum`, `format: date` and `format: uri`.
- `enum` and `format: uri` matter more than they look. Because v1 keeps the text-only `fieldType` set (see above), constrained values like brand colour tokens and every image and link URL are authored as free text — validation is the **only** guard rail on them, so the validator covers both even though no widget enforces them.
- Validation is **advisory, not blocking**: problems are surfaced next to the offending field and in a summary, but the author can still export a document that doesn't validate. Half-finished emails need to be saveable.

## Persistence

- **localStorage** holds the in-progress document, autosaved on every change, so a refresh or crashed tab doesn't lose work.
- **Export** writes the document out as a downloaded `.json` file. **Import** reads one back in via a file picker. The file is the real save format and the thing handed to the render layer; localStorage is only crash protection, not a document library.
- On load, the tool restores from localStorage if anything is there; otherwise it starts a new empty document.
- Import replaces the current document (with a confirmation prompt, since it discards unsaved work).

## Target shape

- **Schema layer**: describes the structure of an email — which blocks, in what order, and their field values, each per its code-defined block schema. This is the thing that's authored/edited and is theme-independent.
- **Output**: this tool's goal output is a JSON document/schema capturing the authored email (campaign metadata, blocks, order, field values). It doesn't render HTML itself.
- **Render layer** (separate tool/idea): takes the JSON output + a theme and produces email HTML. Themes live outside this tool entirely (owned by the render layer, not authored or stored here). Out of scope for this tool.
- No server required to author — should work as a static/local tool.

### Document format

The exported document wraps the block list in campaign-level metadata, mirroring the fields in the existing sample data at `content/weekly.json` (`name`, `subject`, `preheaderText`):

- `version` — integer format version, currently `1`. Lets the render layer reject documents it doesn't understand. This versions the *document format*, not individual block schemas.
- `name` — internal campaign name, not sent to recipients.
- `subject` — the email subject line.
- `preheader` — preview text shown after the subject in the inbox. (Note: renamed from `preheaderText` in `weekly.json`. Distinct from any per-block `preheader` field a block schema may define for its own heading text.)
- `blocks` — ordered array of block instances.

These four campaign fields are fixed in the tool's source, not schema-driven — they're part of the document format rather than a block type.

## Example

A "content card" block schema:

```json
{
  "$id": "block:content_card",
  "title": "Content Card",
  "type": "object",
  "properties": {
    "title": {
      "title": "Title",
      "type": "string",
      "fieldType": "text",
      "weight": 1
    },
    "body": {
      "title": "Body",
      "type": "string",
      "fieldType": "paragraph",
      "weight": 2
    },
    "cta": {
      "title": "Call to action",
      "type": "string",
      "fieldType": "text",
      "weight": 3
    }
  },
  "required": ["title", "body", "cta"]
}
```

An authored email using it, alongside another block (block order is array order — no `weight` needed at this level; each block instance has its own `id`, distinct from `blockType`, so the UI can reorder/reference a specific block even if the same `blockType` appears more than once):

```json
{
  "version": 1,
  "name": "Sample Campaign",
  "subject": "Big Sale This Week",
  "preheader": "Everything is 20% off through Friday.",
  "blocks": [
    {
      "id": "b1",
      "blockType": "content_card",
      "data": {
        "title": "Big Sale This Week",
        "body": "Everything is 20% off through Friday.",
        "cta": "Shop Now"
      }
    },
    {
      "id": "b2",
      "blockType": "footer",
      "data": {
        "unsubscribe_text": "Unsubscribe"
      }
    }
  ]
}
```

## Out of scope for v1

Called out explicitly so these read as decisions, not oversights:

- **No HTML preview.** Rendering belongs to the render layer, which this tool doesn't contain. The tool instead shows a live, read-only pane of the JSON document as it's authored — that pane is the only "preview".
- **No theme selection or storage.** Themes are the render layer's concern.
- **No multi-document library.** One document at a time; managing many emails is done with files on disk.
- **No image, color or link pickers** — see the deferred `fieldType` list above.
- **No drag-and-drop reordering** — move up/down only.
- **No collaboration, sharing or sync** of any kind. There's no server.

## Open questions

Both of the questions previously listed here are now settled — see **Schema evolution** above, and **Unknown block types** below.

## Unknown block types

If a document references a `blockType` this tool has no schema for, the tool **preserves the block**: it shows a read-only placeholder naming the unknown type, and writes the block back out on export with its `data` untouched. Opening a newer document in an older copy of the tool and saving must never silently destroy content.

The render layer takes the opposite line and fails loudly, since it cannot produce correct HTML for a block it has no template for.

## Status

Scoped, ready to implement. Move this file to `../completed/` via `git mv` once the work lands.
