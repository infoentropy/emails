# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository contents

This repository holds an email authoring tool, its render layer, and static HTML email templates and sample campaign data. There is no build system, package manager, linter, or test suite; `render/package.json` exists only to mark `render/` as ES modules for Node.

- `flipboard/techdigest.html` — standalone HTML email template (table-based layout with MSO/Outlook conditional comments for email client compatibility).
- `traction/index.html` — standalone HTML email template ("Traction coding sample"), plus `traction/smallpaw.png`, an image it references.
- `authoring/index.html` — the block authoring tool: a dependency-free page that loads the block schemas and the render layer, and produces the campaign JSON document with a live preview. In Chrome/Edge it can stay attached to a file on disk that an agent edits too (file sync). It must be served over http(s), not opened from `file://` (see below).
- `blocks/*.json` — the block schema library: one JSON Schema document per block type, authored per `completed/serverless-email-authoring-tool.md`. The only copy: the authoring tool fetches them at startup.
- `render/` — the render layer: dependency-free ES modules shared by the browser and Node. `registry.js` lists every block type (template) and theme; `render.js` has `check()`, `renderPreview()` and `renderHtml()` (the email for sending, with audiences as neutral `<!--audience …-->` markers; the render layer never writes a platform's syntax); `blocks/` holds one template per block type and `themes/` the themes. `check.js`, `preview.js` and `email.js` are the Node commands agents run. Plan and remaining build steps: `specs/render-layer-tool.md`.
- `docs/blocks.md` — developer guide to how blocks work *today*: document format, schema keywords, the block library, visibility (`hidden`/`ruleset`/`switch`), the render layer, and how to add or change a block type. Specs record how behaviour was decided and change over time; keep this doc current in the same change whenever block behaviour changes.
- `docs/agents.md` — the one page an agent reads to draft or edit an email document. Keep it current in the same change as anything it describes.

To check a document, run `node render/check.js <doc.json>` (prints issues as JSON; exits 1 on errors). Test render-layer changes by running it against a sample document and by loading the authoring tool, whose Validation panel and preview use the same code.
- `content/weekly.json` / `content/weekly.xml` — the same sample campaign data (a snippet-based email campaign structure: name, subject, preheader, and a list of content snippets with per-snippet data like background image/color, copy, and CTA text) expressed in JSON and XML respectively.

The HTML files use classic email-safe markup: XHTML transitional doctype, inline `<style>` blocks, table layouts, and Outlook (`mso`)/`ExternalClass` conditional CSS. When editing them, preserve these email-client compatibility patterns rather than modernizing to standard responsive/CSS-grid techniques, which many email clients don't support.

Rendered email markup (templates in `render/blocks/`, the shell in `render/themes/shell.js`) follows the same email-safe patterns. Preview the hand-written email templates by opening them directly in a browser or an email client testing tool. The authoring tool needs a server: run `python3 -m http.server` in the repo root and open `http://localhost:8000/authoring/`. All paths between files must be relative (never `/blocks/…`), because on Pages the site lives under `/emails/`.

The repo is published as-is by GitHub Pages from `master` at `https://infoentropy.github.io/emails/` (e.g. the authoring tool at `/emails/authoring/`). Keep the empty `.nojekyll` file at the root: without it Pages runs Jekyll, whose Liquid templating fails on the Handlebars `{{` examples in the specs and breaks the deploy.

## Project management

Work is tracked as markdown files moving through four folders (see each folder's README for details):

1. `ideas/` — early, unscoped ideas.
2. `feedback/` — refinements requested for already-launched features.
3. `specs/` — scoped work ready to implement. Pull work from here.
4. `completed/` — finished specs, moved from `specs/` via `git mv` (not deleted) once the work lands, as part of the same commit/PR that finishes it.

