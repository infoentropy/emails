# Render layer

## Problem

The authoring tool (`../completed/serverless-email-authoring-tool.md`) produces a JSON document describing an email: campaign metadata plus an ordered list of blocks, each with a `blockType` and `data` validated against that block's JSON Schema. That document has to become email HTML, and the person authoring it has to be able to see the result while they work.

## The workflow it serves

1. A writer produces the email copy. Some parts are meant for particular audiences only.
2. The copy becomes a JSON document. An AI takes the first pass (the planned Claude plugin, `../ideas/claude-authoring-plugin.md`), or a person builds it in the block editor, which is slower.
3. The email is rendered and its visuals reviewed.
4. The author fine-tunes it in the block editor, re-rendering as they go. The audience logic (if/else per recipient) can only be tested reliably in the sending platform (Iterable), so rendering has to connect to it.
5. The author can switch the whole email to a different theme and see it straight away: summer vs. spring, anxiety vs. sleep.

Steps 3 to 5 form one loop: edit, look, tweak, switch theme, look again. **Rendering is part of the editor, not a separate batch step.** A script run outside the editor would break the loop on every pass.

## What this changes in earlier specs

Later specs change earlier ones. This one overrides:

| Earlier decision | Where | Now |
|---|---|---|
| The render layer is a Python 3 + Jinja2 script. | earlier drafts of this spec | A **JavaScript** renderer, used by the editor in the browser and by Claude under Node. |
| The authoring tool is a single file that works from `file://`, with no `fetch()` and no build step, so the block schemas are copied into it by hand. | `../completed/serverless-email-authoring-tool.md`, **Tool shape** | The editor is **statically hosted** and loads the schemas, templates and themes as files. Still no build step and no server-side code. |
| No theme selection or storage in the authoring tool. Themes live outside the document. | same spec, **Target shape** and **Out of scope for v1** | The **document records its theme**, and the editor has a theme picker. |
| No "view as segment" preview, since the editor can't evaluate free-text rulesets. | `../completed/block-segmentation.md`, **Switch groups in the authoring tool** | A **"preview as" picker** where the author chooses which rulesets count as true. It still evaluates nothing, so the platform remains the only real test of the logic. |
| Block ids are derived as highest + 1, so an id can be reused after the last block is deleted, and ids aren't stable. | `../completed/serverless-email-authoring-tool.md`, **Block instance ids** | **Ids are never reused**, and the editor shows them. The document stores the next id (see **Working with agents**). |
| Each ruleset's text gets its own AI-written condition ("translation"), cached by exact text, stored inside or next to the document. | `../completed/block-segmentation.md`, **Translation: ruleset → conditional** | Rulesets are **settled into facets**, reusable approved conditions, in a conversation with the person. The facet library lives in a private campaign repo (see **Audiences** and **Campaign storage**). |
| Validation lives inside the editor page. | same spec, **Validation** | Validation moves into the shared `check`, used by the editor and by agents. It stays advisory. |

Everything else in those specs stands: content-only blocks, `variant`, schema evolution, `hidden` / `ruleset` / `switch` semantics, output flavors, and the principle that a person approves every condition before it's used (the "translation" step, now **Audiences: settling rulesets into facets**).

## Hosting

- The site is this repo served as static files: **GitHub Pages**, deployed from the `master` branch at the repo root. It's a project site at `https://infoentropy.github.io/emails/`, so the editor is at `https://infoentropy.github.io/emails/authoring/`. Only what's merged to `master` is live.
- The editor is `authoring/index.html`, and it loads `../blocks/*.json` and `../render/…` with `fetch()` and ES module imports. The JavaScript runs in the visitor's browser. Pages runs nothing on the server, which matches the design: no build step, and no secrets on the page.
- **All paths between files are relative** (`../blocks/button.json`, never `/blocks/button.json`). The site lives under `/emails/`, so a root-absolute path would resolve to `infoentropy.github.io/blocks/…` and fail. Relative paths also work unchanged on a local server, which serves the repo at `/`.
- **The repo root has an empty `.nojekyll` file.** Without it, Pages runs the repo through Jekyll, which drops files and folders starting with `_` and processes Markdown.
- Pages serves over HTTPS, which **File sync** needs: the browser only offers file access on secure pages. IndexedDB and localStorage work as usual.
- Pages' limits (1 GB per site, a soft 100 GB of bandwidth a month) are far above what this needs.
- Nothing authored is sent to the host. Documents stay in the browser (localStorage autosave, file export/import, as now), so a public site exposes only schemas, templates and themes.
- Opening the editor from `file://` is no longer supported. Locally, serve the repo root with any static server (e.g. `python3 -m http.server`) and open `http://localhost:8000/authoring/`.
- **The hand-inlined schemas in the editor go away.** `../blocks/*.json` becomes the only copy, which removes the "edit both copies" step from `../docs/blocks.md`.
- Everyone uses the same deployed version, so the editor and renderer always ship together. Version skew now matters only for documents saved by older versions, and for Claude's copy of the renderer (see **The renderer**).

## The document records its theme

A new optional top-level key, next to `subject` and `preheader`:

```json
{ "version": 1, "name": "…", "subject": "…", "preheader": "…", "theme": "sleep", "blocks": [ … ] }
```

- The value is a theme **name** from the registry, never a colour or style value. The content-only rule still holds: the document says which look to use, and the theme owns what that look is.
- Missing `theme` (every existing document) means the registry's default theme. No format version bump is needed.
- An unknown theme name is a **hard error** when producing a platform template, since sending in the wrong look isn't a safe fallback. The editor shows the problem and asks the author to pick a theme.
- The editor's theme picker sits with the campaign fields. Changing it re-renders the preview immediately.

## The renderer

One dependency-free JavaScript module, `render/render.js`, that runs unchanged in the browser and under Node. It exposes a check and two render functions sharing the same per-block rendering:

```js
check(document, { schemas, theme, flavor, facets })                 // → list of issues (see Working with agents)
renderPreview(document, { schemas, theme, rulesets })                // → plain HTML for the preview pane
renderTemplate(document, { schemas, theme, flavor, facets })        // → a template for the sending platform
```

- `schemas` are the block schemas, loaded by the caller with `registry.loadSchemas(readJson)`: a `fetch` in the browser, a file read in Node.
- `theme` defaults to the document's `theme`.
- **`renderPreview`** resolves audience logic locally, from the author's "preview as" choice (`rulesets`: the ruleset texts treated as true). It emits no platform syntax and needs no facet library, so steps 3 to 5 work before any AI or platform is involved.
- **`renderTemplate`** wraps blocks in the flavor's conditional syntax, using the approved conditions of each ruleset's facets (see **Audiences**). This is what goes to Iterable.
- Neither function does I/O or calls an AI. The caller loads the files.

Claude runs the same module under Node, fetched from the hosted site or from a checkout of this repo, so its output matches the editor's. That settles the plugin's worry about its copy of the renderer drifting from this repo.

### Per block, in order

1. `hidden: true`: skip.
2. Unknown `blockType`: **hard error**, since there's no template for it. (The editor still preserves unknown blocks, so round-tripping never destroys content.)
3. Fill missing fields from the schema's `default`, and ignore fields the template doesn't use (see **Compatibility with evolving schemas**). The document may be invalid, because the editor's validation is advisory, so templates render defensively. An empty optional field produces nothing.
4. Resolve `(blockType, variant)` against the theme (see **Themes and variants**).
5. Convert `markdown` fields (see **Markdown**: for now, escaped plain text), and format `date` fields with the theme's date format.
6. Render through the block's template.

Audience handling then differs by function:

- **Preview:** a block with a `ruleset` shows only if the author ticked that ruleset. A switch group shows its first case whose ruleset is ticked, otherwise its final case without a `ruleset` if it has one, otherwise nothing. The picker lists each distinct ruleset text in the document, and ticking none shows what someone matching no ruleset gets.
- **Template:** as in `../completed/block-segmentation.md`. A block with a `ruleset` is wrapped in the conditions of its facets, and a switch group becomes one if / else-if / else chain. A split switch group, an unsettled ruleset, or an unknown facet is a **hard error**.

Finally, the rendered blocks go into the theme's shell.

### Templates

One module per block type, `render/blocks/<blockType>.js`, exporting a function from `(data, style, theme)` to one table row of markup. Templates are written with an `html` tagged template literal (in `render/html.js`) that **escapes every interpolated value by default**. That gives the same autoescaping safety as Jinja2 without a dependency, and anything already safe (converted markdown, the rendered block list) is passed through explicitly with `raw()`. Only `http(s)` URLs are written into `href` and `src`.

The escaper also applies the flavor's own escaping in `renderTemplate`, so a literal `{{` in copy can't become an Iterable tag. `renderPreview` escapes HTML only.

Markup follows the repo's email conventions (table layout, inline styles, MSO conditionals; see `../CLAUDE.md`).

### Themes

A theme is a module, `render/themes/<name>/theme.js`, exporting:

- `label`: display name for the picker, e.g. "Sleep".
- `styles`: the `(blockType, variant)` → appearance lookup (colours, fonts, spacing, background images).
- `imageSide`: `"left"` or `"right"` for `image_with_text`. Fixed per theme, not alternating, because alternating needs each block to know its position among its siblings. Revisit only if a theme actually needs it.
- `dateFormat`: `Intl.DateTimeFormat` options, e.g. `{ month: "long", day: "numeric", year: "numeric" }`. Parse the document's `YYYY-MM-DD` as UTC so the day can't shift with the viewer's timezone. There's a default if the theme omits it.
- `shell({ subject, preheader, body })`: the outer HTML document (doctype, `<head>`, Outlook settings, media queries, the hidden preheader). The theme owns its shell: `flipboard/techdigest.html` and `traction/index.html` already differ at that level, and that's exactly the brand-level variation a theme exists for. The first two themes share one, `render/themes/shell.js`, with their own colours and fonts; a theme can replace it.

Themes can also add assets (e.g. background images) under their directory, referenced by absolute URL from the hosted site or an image host.

### Registry

A static site can't list a directory, so `render/registry.js` names everything available: the block types (each has a schema in `../blocks/` and a template in `render/blocks/`), the themes, the default theme, and the flavors. Adding a block type, theme or flavor means adding one line there. This keeps templates, themes and flavors code-defined, the same way block schemas are.

### Disk layout

```
blocks/<blockType>.json            schemas (unchanged)
authoring/index.html               editor + preview pane
docs/agents.md                     the one page agents read
render/
  render.js                        check, renderPreview, renderTemplate
  html.js                          html/raw and small markup helpers
  check.js                         Node wrapper: prints check's issues as JSON
  preview.js                       Node wrapper: writes renderPreview's HTML
  registry.js                      block types, themes, default theme, flavors, schema loading
  package.json                     { "type": "module" } only, so Node treats render/ as ES modules
  blocks/<blockType>.js            one template per block type
  themes/shell.js                  the email shell the current themes share
  themes/<name>/theme.js           styles, imageSide, dateFormat, shell
  flavors/<name>.js                conditional wrapping + syntax escaping per platform
```

## The editor

The authoring tool grows a preview pane next to the form:

- It re-renders on every change with `renderPreview`, so you see the email while you edit it.
- A **theme picker** writes the document's `theme`.
- A **"preview as" picker** lists the document's rulesets as checkboxes. Its label must make clear that it chooses what to *show* and tests nothing: whether a real recipient matches "US only" is decided by the facets' approved conditions, in the platform.
- A **width toggle** (desktop / mobile) is cheap and worth having, since email layouts collapse at narrow widths.
- The preview is rendered into an `<iframe srcdoc>`, so the email's styles can't leak into the editor or the other way round.
- Validation stays advisory. The validation panel shows `check`'s issues, the same list an agent sees. A block that fails to render shows an inline error in the preview in place of that block, and the rest of the email still renders.
- Each block shows its id (`b7`), so a person and an agent can refer to the same block.
- The editor can work on a file on disk directly (see **File sync** below).

### File sync

The editor can **open a file on disk and stay attached to it**, so a person and an agent can take turns on the same `campaign.json` without exporting and importing:

- **Open file** uses the browser's file picker and keeps the file handle. Every change is autosaved to the file (debounced), as well as to localStorage.
- **Save as…** attaches too, to the file it just wrote.
- The editor **watches the file** while the tab is visible, checking its modified time every second or two (1.5s, plus on focus). It compares the text with what it last read or wrote, so its own writes aren't mistaken for outside changes, and loading a file never writes it back. When it changes on disk, the editor reloads it and re-renders the preview, so an agent's edit shows up without the person doing anything.
- **If the file on disk isn't valid JSON** (for example, caught mid-write), the editor keeps what it has, shows a notice, and doesn't write to the file until it parses again, so it never overwrites an agent's work with a stale copy.
- **If both sides changed** (an edit is still waiting to autosave when the file changes on disk), the editor asks: take the file's version, or keep the editor's and overwrite the file.
- The editor writes the same format as Save: 2-space indent, keys in the tool's order, trailing newline. A one-field change is a one-line diff.
- The handle is remembered across reloads (stored in IndexedDB). The browser may ask the person to confirm access again after a reload (a *Reconnect* button). Then the file wins, unless edits were made in the tab since the reload, in which case the editor asks.
- **Disconnect** and **New** detach, leaving the file as it is. A file that disappears (moved, deleted) detaches with a message; the work stays in the editor.
- This needs the File System Access API, which is **Chrome and Edge only**. Other browsers, and Claude environments without local files (chat), keep using Open/Save and paste, as now.

## Working with agents

Agents (Claude in the plugin, or Claude Code) do the first draft and many small changes. People do the visual review and the fine-tuning. The design aims to keep each agent turn cheap in tokens.

**The principle: agents work on the JSON and get text feedback. People judge the visuals.** A rendered email is large: `flipboard/techdigest.html` is 2,281 lines of table markup, while the JSON for a similar email is a few dozen lines. Screenshots are costly too, and need a headless browser. So in an agent's normal loop it reads and edits only the document, and learns whether the document is right from `check`, never from reading the rendered HTML.

### `check`

`check(document, options)` returns every problem with the document as a list, and an empty list means it's good:

```json
[
  { "severity": "error",   "block": "b7", "field": "image_alt", "code": "required",
    "message": "Image alt text is required." },
  { "severity": "warning", "block": "b3", "field": "variant",   "code": "variant_unstyled",
    "message": "Theme \"sleep\" has no style for button/secondary; rendering as primary." }
]
```

- It covers everything the editor's validation covers today (`required`, `type`, `enum`, `format`), plus split switch groups, empty rulesets on non-final cases, an unknown `blockType`, an unknown `theme`, variants the theme doesn't style, and a trial render of every block that isn't hidden.
- With a `flavor` and `facets`, it also checks rulesets against the facet library (see **Audiences**). So a clean `check` guarantees `renderTemplate` won't fail.
- `block` and `field` pin each issue to one place, so the fix is a targeted edit. `code` is stable and machine-readable. `message` is for people.
- Hidden blocks aren't checked, as now.

Agents run it through a thin Node wrapper (`render/preview.js` is the only other one, for the milestone screenshots below):

```
node render/check.js campaign.json [--flavor iterable]
```

It prints the list as JSON and exits non-zero if there are errors. Warnings alone don't fail it.

### Stable block ids

Agents and people refer to blocks by id ("change b7's button text"), so an id must keep meaning the same block:

- **Ids are never reused.** The document gains an optional top-level `nextId` (e.g. `"nextId": 12`) that only ever goes up. New blocks take it and increment it. When it's missing (existing documents), it's derived as today, from the highest existing id + 1.
- An agent adding blocks does the same: take `nextId`, then increment it.
- The editor shows each block's id.

### Small edits

- An agent changes only what it was asked to, editing the fields in place rather than rewriting the document. The fixed format makes that a one-line change for a one-field edit.
- It then runs `check`, and hands back to the person, whose preview has already updated through **File sync**.
- Switching theme is a one-key change (`"theme": "spring"`).

### Visual checks by agents

Only at milestones: after the first draft of a new email, or when trying a new theme. The agent renders the preview HTML to a file and takes one screenshot with whatever headless browser its environment has. It never does this after routine edits. Visual judgement is the person's job, in the editor.

### What an agent reads

An agent authoring or editing an email doesn't read the specs. It reads:

- `docs/agents.md`: one page covering the document shape, the block-level keys (`hidden`, `ruleset`, `switch`), `nextId`, the theme names, `check`, and the rules above.
- The schemas in `blocks/*.json` for the block types it uses.
- The document itself, and `check`'s output.

`docs/agents.md` is kept current in the same change as anything it describes, like `docs/blocks.md`.

## Testing in Iterable

The audience logic can only be trusted once it has run in the platform, against real or test user profiles. That needs Iterable credentials, and **the hosted page holds none**: a public static page has nowhere safe to keep an API key.

So Claude does this part, in the plugin (Skill C) or in Claude Code with an Iterable API key in its environment:

1. **Settle audiences:** turn each free-text ruleset into facets, with the author, in conversation (see **Audiences**).
2. **Render** with `renderTemplate` under Node.
3. **Push** the template to Iterable through its template API, and **send proofs** to test users, or point the author at Iterable's preview with test user data. Confirm the exact endpoints against Iterable's API docs.

This is only needed after the rulesets change, not after every copy edit.

**Fallback without Claude:** the editor has a "Copy template" action that runs `renderTemplate` and copies the result for pasting into Iterable's template editor. It works only once every ruleset in the document is settled and the editor can read the facet library (which needs folder access; see **Campaign storage**). For a document without rulesets it always works.

## Output flavors

The rendered template goes to the platform as a template, not as final HTML, so anything decided per recipient at send time is written in the platform's own syntax.

- **Iterable** is the first flavor: Handlebars as Iterable implements it, with Iterable's helpers. SendGrid should follow as its own flavor. It's also Handlebars-based but its helpers differ, so "Handlebars" alone doesn't identify a flavor.
- A flavor owns how conditionals wrap blocks, and **escaping its own syntax** in content. The conditions themselves come from the facet library (see **Audiences**).
- The document never names a flavor. The same document renders for any flavor.

## Audiences: settling rulesets into facets

Writers describe audiences in their own words, and nobody will phrase "US, Canada or UK users who don't pay" the same way twice. So a free-text `ruleset` is a **draft**. Before an email goes to the platform, each one is **settled** into a combination of **facets**: small, canned, approved conditions that are reused across campaigns. This replaces the "translation" step of `../completed/block-segmentation.md` (**Translation: ruleset → conditional**), where each ruleset's text got its own condition, looked up by exact text.

### Facets

A facet is one reusable condition, in a **category**: `region`, `subscription`, `behavior`, and more as needed. Its id is `category.name`, e.g. `region.us-ca-gb`, `subscription.not-paying`, `behavior.sleep-story-30d`.

- Any **or** and **not** inside a category live in the facet's own definition: `region.us-ca-gb` is "US or CA or GB", and `subscription.not-paying` is "anything but paying, including empty".
- A **settled ruleset** is facet ids joined with ` + `, meaning **and**. It uses **at most one facet per category**, written in the library's category order, so the same audience always produces the same text:

  ```json
  { "id": "b6", "blockType": "button", "ruleset": "region.us-ca-gb + subscription.not-paying", … }
  ```

- An **or** across categories ("in the US, *or* a paying subscriber anywhere") isn't a ruleset. Express it as a switch group (first match wins) or as two blocks.
- A ruleset that isn't in this form is unsettled free text. That's normal while drafting.

### Where they live

In the private campaign repo (see **Campaign storage**), one folder per sending platform:

- **`iterable/fields.md`**, written by a person: which user fields Iterable holds, how their values are coded, and how copy words map to them ("subscriber" means `subscriptionStatus` is `paying`; "UK" means `GB`). It's the environment context that `../completed/block-segmentation.md` left open. Claude never uses a field that isn't described here; it asks.
- **`iterable/facets.json`**, maintained by Claude with the person's approval:

  ```json
  {
    "region": {
      "us-ca-gb": {
        "description": "Country is US, Canada or the UK.",
        "fields": ["country"],
        "condition": "…Iterable code; exact form settled in step 5…",
        "approved": "2026-09-28",
        "examples": ["users in US, CA, GB", "US/Canada/UK folks"]
      }
    },
    "subscription": {
      "not-paying": {
        "description": "Subscription status is anything but paying, including empty.",
        "fields": ["subscriptionStatus"],
        "condition": "…",
        "approved": "2026-09-28",
        "examples": ["not a paying subscriber", "haven't paid yet"]
      }
    },
    "behavior": {}
  }
  ```

  Key order is category order. `fields` says which facets to re-check when `fields.md` changes. `examples` keeps the phrasings that settled to the facet, so the next writer's wording is easier to match.

Facet ids are platform-neutral names. A second platform gets its own folder (`sendgrid/fields.md`, `sendgrid/facets.json`) with the same ids and its own conditions, so documents don't change.

### Settling: a conversation, not a lookup

Claude runs it (in the plugin, or in Claude Code) before building a platform template, and a person takes part. It's a documented agent procedure in `docs/agents.md`, not code. For each unsettled ruleset in the campaign:

1. **Decompose** it into categories: "US/Canada/UK folks who haven't paid yet" is region + subscription.
2. **Match** each part to an existing facet by meaning, using `description` and `examples`, and confirm it: "region → `region.us-ca-gb` (country US, CA or GB)?"
3. **Propose** a new facet only when none fits. It gets an id, a description and a condition, uses only fields from `fields.md`, and comes with questions about anything ambiguous ("does 'haven't paid' include lapsed users?"). Claude points out near-duplicates first.
4. On confirmation, **rewrite the block's `ruleset`** to the settled form, and add new facets and example phrasings to `facets.json`.

Rules that keep the library consistent:

- **Nothing settles without the person.** Claude proposes and the person confirms, facet by facet.
- **New facets are approved** (`approved` records when). An unapproved facet can't be used.
- **Changing an approved facet** affects every campaign that uses it. Claude lists them (by searching `campaigns/`) before the change is approved.
- **When `fields.md` changes**, Claude re-checks the facets whose `fields` include the changed field.

### Rendering and checking

- **`renderPreview`** needs no library. The "preview as" picker shows the document's facets grouped by category, and a block shows when all its facets are ticked. Unsettled rulesets appear as whole-ruleset checkboxes, as now.
- **`renderTemplate`** combines a ruleset's facet conditions with **and**, which is nesting in Handlebars. For a switch group, each case's **else** leads on to the remaining cases. The exact output depends on the shape of Iterable's conditions, which step 5 settles.
- **`check`** warns about an unsettled ruleset (`ruleset_unsettled`). With the facet library loaded, it reports an unknown or unapproved facet (`unknown_facet`) and two facets from one category in a ruleset (`facet_category_repeated`) as errors. The renderer never calls an AI.

## Campaign storage

This repo is **public**, and GitHub Pages publishes every file in it. So it holds only the tool: the editor, the render layer, schemas, themes and docs. Campaign content goes in a **separate private repo** (e.g. `infoentropy/email-campaigns`):

```
email-campaigns/
  campaigns/
    2026-10-sleep-stories.json    one document per email
  iterable/
    fields.md                      the platform's user fields (a person writes it)
    facets.json                    the facet library (Claude maintains it; a person approves)
```

- Git gives every agent edit a reviewable, revertible diff.
- The editor opens `campaigns/….json` with **File sync**. The private repo doesn't need Pages.
- Agents run this repo's `render/check.js` and `render/preview.js` against those files: from a checkout of this repo alongside the campaign repo, or fetched from the hosted site.
- The editor reads one file at a time, so it can't see `facets.json`. Until it can open the whole campaign folder (Chrome/Edge, a later extension of **File sync**), templates with audiences come from Claude, and "Copy template" covers emails without rulesets.

## Themes and variants

A block may carry a `variant` (`primary` or `secondary`). The theme resolves `(blockType, variant)` to an appearance, and the document never names a colour.

When a theme has no styling for a variant in use, **render the block as `primary` and warn**, naming the block type and the missing variant. In the editor the warning shows in the validation panel. Failing hard would turn every allowed widening of the `variant` enum into a breaking change for every existing theme.

## Compatibility with evolving schemas

From the authoring tool's **Schema evolution** rules:

- A field missing from `data` takes the `default` declared in its schema. Old documents predate fields that newer templates expect.
- A field in `data` that the template doesn't use is **ignored**, never an error.

Schemas may only gain optional fields; renames and removals become a new `blockType`. So a template written for version *N* of a schema works against every later version, and documents saved by older versions keep rendering.

## Markdown

**Deferred (backlog).** For now `markdown` fields render as escaped plain text, with blank lines as paragraph breaks and single newlines as line breaks (`paragraphs()` in `render/html.js`). That's safe and needs no library; it just doesn't format.

The intended design, when it's picked up: convert to HTML with **raw HTML in the source escaped, not passed through**, since passing it through would quietly undo the editor's ban on raw HTML. The plan was **markdown-it** with `html: false`, vendored as a single file under `render/vendor/` (no package manager), running in both the browser and Node. It was deferred because the npm registry and CDNs weren't reachable from the build environment; vendoring it needs a machine that can download it, or a small hand-written converter for the subset email copy needs. The legacy `body` values in `content/weekly.json` are raw HTML and need a one-off conversion to markdown before they can round-trip.

## Open questions

- **The exact Iterable form of a facet's condition** (a wrapping block helper, or an expression usable in an else-if), and whether Iterable can combine conditions in one place. It decides how nesting and switch groups render (see **Audiences**). To confirm against Iterable's Handlebars reference in step 5.
- **Behavioural facets** ("played a Sleep Story in the last 30 days") can only use what Iterable can evaluate at send time: a user field, possibly precomputed, or list membership. Which ones exist is for `fields.md` to say.
- **Should review flag an audience left with no blocks?** The "preview as" picker makes such an audience visible by hand; review could catch it automatically. (Carried over.)
- **Theme vs. `feature_type`.** "Anxiety theme vs. sleep theme" overlaps with `content_feature_header.feature_type` (`meditate` / `sleep`), which the library spec says a theme keys its visuals off. Is the category content (a field), the look (a theme), or both, with the theme free to use the field?
- **How the plugin hands a document to the hosted editor in chat**, where there's no shared file for **File sync**: file import (works today), or something smoother such as a URL fragment. With Claude Code and local files, File sync covers it.

## Build order

1. **Hosting.** *Done.* GitHub Pages is on (deploying from `master`), and `.nojekyll` is in place. The editor loads `../blocks/*.json` through `render/registry.js` using relative paths, and the inlined schemas are gone.
2. **Shared check and renderer, with preview.** *Done.*
   - The editor's validation moved into `check`; `check.js` and `preview.js` are the Node wrappers.
   - `render.js` and `html.js`, templates for the five block types, and two themes, `spring` (default) and `sleep`, sharing a shell ported from the existing templates.
   - The preview pane (Desktop/Mobile), the document `theme` key and the theme picker.
   - `nextId`, so ids are never reused (ids were already shown in the editor).
   - `docs/agents.md`.
3. **File sync.** *Done.* Open file and Save as… attach; edits autosave to the file; outside changes reload; invalid files and conflicts are handled as in **File sync**.
4. **"Preview as".** Add the picker to the editor: facets grouped by category for settled rulesets, whole-ruleset checkboxes for unsettled ones, and facet-aware matching in `renderPreview` (a block shows when all its facets are ticked). `renderPreview` already resolves free-text `rulesets` and switch groups, and `preview.js --as` exposes it.
5. **Iterable flavor.** Add `renderTemplate`, the Iterable flavor, facet parsing and checks in `check` (`ruleset_unsettled`, `unknown_facet`, `facet_category_repeated`), and the "Copy template" action.
6. **Claude + Iterable.** Set up the private campaign repo, the settling conversation (as a documented agent procedure), then push and send proofs through Iterable's API.

`../CLAUDE.md`, `../docs/blocks.md` and `../docs/agents.md` are updated in the same change as each step that alters what they describe (hosting, the `theme` and `nextId` keys, the renderer, `check`).

**Backlog:**

- **Markdown rendering** (see **Markdown**).

## Status

Design settled apart from the open questions above, none of which block steps 1 to 4. Steps 1 to 3 are done. Next is step 4.
