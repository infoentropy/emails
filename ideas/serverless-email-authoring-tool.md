# Serverless email authoring tool

## Problem

Building marketing emails today means hand-editing table-based HTML (see `flipboard/techdigest.html`, `traction/index.html`) or running a server-side app to manage them. Want something that runs without a server and still produces valid, email-client-safe HTML.

## Core idea

- An email is a sequence of **blocks** (e.g. header, discount banner, content card, CTA, footer).
- Each block type has a fixed **schema**: a defined set of fields (text, image URL, color, link, etc.) — not free-form HTML.
- Authoring an email = picking blocks, filling in their fields, and reordering them (move up/down). No raw HTML editing.
- Each block schema maps to an HTML template/partial that renders it. Swapping a block's HTML (a different theme) doesn't change the schema or the authored content, only the rendering.
- Medium is **email only** — no other output medium (e.g. web) is in scope.

## Block schemas

- Block schemas are **code-defined**, not end-user-defined. The set of available block types and their fields is authored by developers (in the tool's source/config); end users choose from existing block types and fill in field values — they don't create new block types or add/remove fields.
- Each block type's schema is declared as a **JSON Schema** document (fields as `properties`, and whatever else JSON Schema offers — required fields, descriptions, etc.). `type` stays JSON Schema's own type (`string`, `number`, `integer`, ...); the widget/form-control choice is a separate custom `fieldType` keyword (see Authoring form), so schemas remain valid JSON Schema.
- Fields within a schema have a fixed **order**, and that order is meaningful: e.g. a "content card" block might define `title`, `body`, `cta` in that order. The order drives both how the authoring form lays out its inputs and the field order in the output. Order is declared explicitly via a `weight` property on each field; fields are sorted by `weight` ascending, rather than relying on `properties` key order (which JSON Schema doesn't guarantee across tooling).

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

## Target shape

- **Schema layer**: describes the structure of an email — which blocks, in what order, and their field values, each per its code-defined block schema. This is the thing that's authored/edited and is theme-independent.
- **Output**: this tool's goal output is a JSON document/schema capturing the authored email (blocks, order, field values). It doesn't render HTML itself.
- **Render layer** (separate tool/idea): takes the JSON output + a theme and produces email HTML. Themes live outside this tool entirely (owned by the render layer, not authored or stored here). Out of scope for this tool.
- No server required to author — should work as a static/local tool.

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

An authored email using it, alongside another block (block order is array order — no `weight` needed at this level):

```json
{
  "blocks": [
    {
      "blockType": "content_card",
      "data": {
        "title": "Big Sale This Week",
        "body": "Everything is 20% off through Friday.",
        "cta": "Shop Now"
      }
    },
    {
      "blockType": "footer",
      "data": {
        "unsubscribe_text": "Unsubscribe"
      }
    }
  ]
}
```

## Open questions

- Exact shape of the output JSON (the authored email document) — the example above is a first pass, not yet settled (e.g. does a block need its own `id`? Is `blockType` the right key name?).

## Status

Early idea, not scoped. Needs a spec before implementation — see `../specs/README.md`.
