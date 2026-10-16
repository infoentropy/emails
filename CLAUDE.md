# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository contents

This repository holds an email authoring tool, its render layer, and sample campaign data. The repo root is also a Claude plugin (`emails`) and a one-plugin marketplace (`infoentropy`), so the skills and the render layer they run ship together. There is no build system, package manager, linter, or test suite; `render/package.json` exists only to mark `render/` as ES modules for Node.

- `authoring/index.html` — the block authoring tool: a dependency-free page that loads the block schemas and the render layer, and produces the campaign JSON document with a live preview. In Chrome/Edge it can stay attached to a file on disk that an agent edits too (file sync). It must be served over http(s), not opened from `file://` (see below).
- `blocks/*.json` — the block schema library: one JSON Schema document per block type. The only copy: the authoring tool fetches them at startup.
- `render/` — the render layer: dependency-free ES modules shared by the browser and Node. `registry.js` lists every block type (template) and theme; `render.js` has `check()`, `renderPreview()` and `renderHtml()` (the email for sending, with audiences as neutral `<!--audience …-->` markers; the render layer never writes a platform's syntax); `blocks/` holds one template per block type and `themes/` the themes. `check.js`, `preview.js` and `email.js` are the Node commands agents run.
- `docs/blocks.md` — developer guide to how blocks work *today*: document format, schema keywords, the block library, visibility (`hidden`/`ruleset`/`switch`), the render layer, and how to add or change a block type. Specs record how behaviour was decided and change over time; keep this doc current in the same change whenever block behaviour changes.
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` — the plugin manifest and the marketplace listing it (`source: "./"`, the repo root). Users install with `/plugin marketplace add infoentropy/emails` then `/plugin install emails@infoentropy`. Validate with `claude plugin validate .` after changing either, or any skill. Bump `version` in `plugin.json` when a change should reach installed copies.
- `skills/*/SKILL.md` — the plugin's skills, the procedures agents follow: `email-document` (draft and edit documents, `check`, previews), `settle-audiences` (rulesets → facets), `send-to-iterable` (build HTML, convert markers to Handlebars), `campaign-setup` (scaffold a private campaign repo). Skills run the render layer as `node "${CLAUDE_PLUGIN_ROOT}/render/…"`, so everything a skill needs must stay inside this repo, at paths relative to the root. Keep each skill current in the same change as anything it describes (e.g. a new block type goes in `email-document`'s table).
- `docs/agents.md` — an index of the skills, for agents working without the plugin.
- `skills/campaign-setup/template/` — starter files for a user's **private** campaign repo (example campaign, `iterable/fields.md`, `iterable/facets.json`, a `CLAUDE.md`, a `.claude/settings.json` that enables the plugin, and a README). Example data only: real campaign content never goes in this public repo. Keep it working with the current tool (its example must pass `check`) and in step with the skills.
- `README.md` — the entry point for people cloning this repo.

To check a document, run `node render/check.js <doc.json>` (prints issues as JSON; exits 1 on errors). Test render-layer changes by running it against a sample document and by loading the authoring tool, whose Validation panel and preview use the same code.
- `content/weekly.json` / `content/weekly.xml` — the same sample campaign data (a snippet-based email campaign structure: name, subject, preheader, and a list of content snippets with per-snippet data like background image/color, copy, and CTA text) expressed in JSON and XML respectively.

Rendered email markup (templates in `render/blocks/`, the shell in `render/themes/shell.js`) uses classic email-safe patterns: XHTML transitional doctype, inline `<style>` blocks, table layouts, and Outlook (`mso`)/`ExternalClass` conditional CSS. When editing it, preserve these email-client compatibility patterns rather than modernizing to standard responsive/CSS-grid techniques, which many email clients don't support. The authoring tool needs a server: run `python3 -m http.server` in the repo root and open `http://localhost:8000/authoring/`. All paths between files must be relative (never `/blocks/…`), because on Pages the site lives under `/emails/`.

The repo is published as-is by GitHub Pages from `master` at `https://infoentropy.github.io/emails/` (e.g. the authoring tool at `/emails/authoring/`). Keep the empty `.nojekyll` file at the root: without it Pages runs Jekyll, whose Liquid templating fails on the Handlebars `{{` examples in the skills and docs and breaks the deploy.

## Project management

`feedback/` holds refinements requested for already-launched features (see its README).
