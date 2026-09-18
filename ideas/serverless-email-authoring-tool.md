# Serverless email authoring tool

## Problem

Building marketing emails today means hand-editing table-based HTML (see `flipboard/techdigest.html`, `traction/index.html`) or running a server-side app to manage them. Want something that runs without a server and still produces valid, email-client-safe HTML.

## Core idea

- An email is a sequence of **blocks** (e.g. header, discount banner, content card, CTA, footer).
- Each block type has a fixed **schema**: a defined set of fields (text, image URL, color, link, etc.) — not free-form HTML.
- Authoring an email = picking blocks, filling in their fields, and reordering them (move up/down). No raw HTML editing.
- Each block schema maps to an HTML template/partial that renders it. Swapping the HTML for a block (different theme, different medium — email vs. web) doesn't change the schema or the authored content, only the rendering.

## Target shape

- **Schema layer**: describes the structure of an email — which blocks, in what order, and their field values. This is the thing that's saved/edited and is theme-independent.
- **Render layer**: takes a schema + a theme/medium and spits out HTML. Swappable independently of the schema.
- No server required to author or render — should work as a static/local tool.

## Prior art in this repo

The old Django app (removed, see `CLAUDE.md`) had a similar shape: `hbemail` had `Template`/`TemplateRegion`/`Component`/`ComponentSchema` concepts, and `iterablegen` produced campaigns as an ordered list of snippets with per-snippet `data` — see `content/weekly.json` / `content/weekly.xml` for what that output looked like (a campaign with a `iterablecampaignsnippet_set` list, each snippet having a `data` dict of fields and a `snippet` name/type). That's close to the block+schema model described above, minus the server dependency.

## Open questions

- What format for the schema itself (JSON? something else)?
- How much of the old `hbemail`/`iterablegen` schema shapes are reusable vs. need rethinking for a serverless design?
- What counts as a "medium" beyond email — is web/landing-page rendering in scope now or later?
- Where do themes live, and how do they differ from mediums (a theme reskins a block, a medium may need a structurally different block)?

## Status

Early idea, not scoped. Needs a spec before implementation — see `../specs/README.md`.
