# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository contents

This repository holds static HTML email templates and sample campaign data — there is no build system, package manager, linter, or test suite.

- `flipboard/techdigest.html` — standalone HTML email template (table-based layout with MSO/Outlook conditional comments for email client compatibility).
- `traction/index.html` — standalone HTML email template ("Traction coding sample"), plus `traction/smallpaw.png`, an image it references.
- `content/weekly.json` / `content/weekly.xml` — the same sample campaign data (a snippet-based email campaign structure: name, subject, preheader, and a list of content snippets with per-snippet data like background image/color, copy, and CTA text) expressed in JSON and XML respectively.

The HTML files use classic email-safe markup: XHTML transitional doctype, inline `<style>` blocks, table layouts, and Outlook (`mso`)/`ExternalClass` conditional CSS. When editing them, preserve these email-client compatibility patterns rather than modernizing to standard responsive/CSS-grid techniques, which many email clients don't support.

There is no local server or renderer in this repo — preview the HTML files by opening them directly in a browser or an email client testing tool.

Note: a previous version of this repository contained a Django app (`app/`) with models named `calm`, `hbemail`, and `iterablegen` that generated the campaign JSON/XML seen in `content/`. That app has been removed; `content/weekly.json` and `content/weekly.xml` remain as static examples of its output format.

## Project management

Work is tracked as markdown files moving through four folders (see each folder's README for details):

1. `ideas/` — early, unscoped ideas.
2. `feedback/` — refinements requested for already-launched features.
3. `specs/` — scoped work ready to implement. Pull work from here.
4. `completed/` — finished specs, moved from `specs/` via `git mv` (not deleted) once the work lands, as part of the same commit/PR that finishes it.

