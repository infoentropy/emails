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
- Each block type's schema is declared as a **JSON Schema** document (fields as `properties`, with `type`, and whatever else JSON Schema offers — required fields, descriptions, etc.).
- Fields within a schema have a fixed **order**, and that order is meaningful: e.g. a "content card" block might define `title`, `body`, `cta` in that order. The order drives both how the authoring form lays out its inputs and the field order in the output. Order is declared explicitly via a `weight` property on each field; fields are sorted by `weight` ascending, rather than relying on `properties` key order (which JSON Schema doesn't guarantee across tooling).

## Authoring form

- Each field declares a `type`, and the form input it renders as is determined by that type. Field types: `integer`, `float`, `text` (single-line input), `paragraph` (multi-line textarea), `markdown` (textarea authored in markdown), `date`.
- Other field types (image picker, color picker, link picker, etc.) are explicitly deferred — not needed for a first version.

## Target shape

- **Schema layer**: describes the structure of an email — which blocks, in what order, and their field values, each per its code-defined block schema. This is the thing that's authored/edited and is theme-independent.
- **Output**: this tool's goal output is a JSON document/schema capturing the authored email (blocks, order, field values). It doesn't render HTML itself.
- **Render layer** (separate tool/idea): takes the JSON output + a theme and produces email HTML. Themes live outside this tool entirely (owned by the render layer, not authored or stored here). Out of scope for this tool.
- No server required to author — should work as a static/local tool.

## Open questions

- The field `type` values (`integer`/`float`/`text`/`paragraph`/`markdown`/`date`) aren't JSON Schema's own `type` vocabulary (`string`/`number`/`integer`/`boolean`/`array`/`object`/`null`) — needs deciding whether this `type` is a custom keyword alongside/instead of JSON Schema's native `type`, and how each maps to a JSON Schema `type`+`format` pair for validation.
- Exact shape of the output JSON (the authored email document) — likely validated against the block JSON Schemas, but shape not yet defined.

## Status

Early idea, not scoped. Needs a spec before implementation — see `../specs/README.md`.
