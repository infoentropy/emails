# Serverless email authoring tool

## Problem

Building marketing emails today means hand-editing table-based HTML (see `flipboard/techdigest.html`, `traction/index.html`) or running a server-side app to manage them. Want something that runs without a server and still produces valid, email-client-safe HTML.

## Core idea

- An email is a sequence of **blocks** (e.g. header, discount banner, content card, CTA, footer).
- Each block type has a fixed **schema**: a defined set of fields (text, image URL, color, link, etc.) — not free-form HTML.
- Authoring an email = picking blocks, filling in their fields, and reordering them (move up/down). No raw HTML editing.
- Each block schema maps to an HTML template/partial that renders it. Swapping the HTML for a block (different theme, different medium — email vs. web) doesn't change the schema or the authored content, only the rendering.

## Block schemas

- Block schemas are **code-defined**, not end-user-defined. The set of available block types and their fields is authored by developers (in the tool's source/config); end users choose from existing block types and fill in field values — they don't create new block types or add/remove fields.
- Fields within a schema have a fixed **order**, and that order is meaningful: e.g. a "content card" block might define `title`, `body`, `cta` in that order. The order drives both how the authoring form lays out its inputs and the field order in the output.

## Authoring form

- Each field renders as a form input based on its type. For now, only two are needed:
  - default: single-line text input
  - `textarea`: multi-line text box
- Other field types (image picker, color picker, link picker, etc.) are explicitly deferred — not needed for a first version.

## Target shape

- **Schema layer**: describes the structure of an email — which blocks, in what order, and their field values, each per its code-defined block schema. This is the thing that's authored/edited and is theme-independent.
- **Output**: this tool's goal output is a JSON document/schema capturing the authored email (blocks, order, field values). It doesn't render HTML itself.
- **Render layer** (separate tool/idea): takes the JSON output + a theme/medium and produces HTML. Swappable independently of the schema, and out of scope for this tool.
- No server required to author — should work as a static/local tool.

## Prior art in this repo

The old Django app (removed, see `CLAUDE.md`) had a similar shape: `hbemail` had `Template`/`TemplateRegion`/`Component`/`ComponentSchema` concepts, and `iterablegen` produced campaigns as an ordered list of snippets with per-snippet `data` — see `content/weekly.json` / `content/weekly.xml` for what that output looked like (a campaign with a `iterablecampaignsnippet_set` list, each snippet having a `data` dict of fields and a `snippet` name/type). That's close to the block+schema model described above, minus the server dependency.

## Open questions

- How are code-defined block schemas declared (a config file per block type? a schema language? plain code)?
- How much of the old `hbemail`/`iterablegen` schema shapes are reusable vs. need rethinking for a serverless design?
- What counts as a "medium" beyond email — is web/landing-page rendering in scope now or later?
- Where do themes live, and how do they differ from mediums (a theme reskins a block, a medium may need a structurally different block)?
- Exact shape of the output JSON — is it closer to the old `iterablecampaignsnippet_set` list shape, or something new?

## Status

Early idea, not scoped. Needs a spec before implementation — see `../specs/README.md`.
