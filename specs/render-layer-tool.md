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
| Validation lives inside the editor page. | same spec, **Validation** | Validation moves into the shared `check`, used by the editor and by agents. It stays advisory. |

Everything else in those specs stands: content-only blocks, `variant`, schema evolution, `hidden` / `ruleset` / `switch` semantics, output flavors, and the translate-and-review step.

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
check(document, { flavor, translations })                  // → list of issues (see Working with agents)
renderPreview(document, { theme, rulesets })                // → plain HTML for the preview pane
renderTemplate(document, { theme, flavor, translations })  // → a template for the sending platform
```

- `theme` defaults to the document's `theme`.
- **`renderPreview`** resolves audience logic locally, from the author's "preview as" choice (`rulesets`: the ruleset texts treated as true). It emits no platform syntax and needs no translations, so steps 3 to 5 work before any AI or platform is involved.
- **`renderTemplate`** wraps blocks in the flavor's conditional syntax, using approved translations. This is what goes to Iterable.
- Neither function does I/O or calls an AI. The caller loads the files.

Claude runs the same module under Node, fetched from the hosted site or from a checkout of this repo, so its output matches the editor's. That settles the plugin's worry about its copy of the renderer drifting from this repo.

### Per block, in order

1. `hidden: true`: skip.
2. Unknown `blockType`: **hard error**, since there's no template for it. (The editor still preserves unknown blocks, so round-tripping never destroys content.)
3. Fill missing fields from the schema's `default`, and ignore fields the template doesn't use (see **Compatibility with evolving schemas**). The document may be invalid, because the editor's validation is advisory, so templates render defensively. An empty optional field produces nothing.
4. Resolve `(blockType, variant)` against the theme (see **Themes and variants**).
5. Convert `markdown` fields to HTML with raw HTML escaped (see **Markdown**), and format `date` fields with the theme's date format.
6. Render through the block's template.

Audience handling then differs by function:

- **Preview:** a block with a `ruleset` shows only if the author ticked that ruleset. A switch group shows its first case whose ruleset is ticked, otherwise its final case without a `ruleset` if it has one, otherwise nothing. The picker lists each distinct ruleset text in the document, and ticking none shows what someone matching no ruleset gets.
- **Template:** as in `../completed/block-segmentation.md`. A block with a `ruleset` is wrapped in its approved condition, and a switch group becomes one if / else-if / else chain. A split switch group, or a ruleset with no approved translation, is a **hard error**.

Finally, the rendered blocks go into the theme's shell.

### Templates

One module per block type, `render/blocks/<blockType>.js`, exporting a function from `(data, style)` to markup. Templates are written with an `html` tagged template literal that **escapes every interpolated value by default**. That gives the same autoescaping safety as Jinja2 without a dependency, and anything already safe (converted markdown, the rendered block list) is passed through explicitly with `raw()`.

The escaper also applies the flavor's own escaping in `renderTemplate`, so a literal `{{` in copy can't become an Iterable tag. `renderPreview` escapes HTML only.

Markup follows the repo's email conventions (table layout, inline styles, MSO conditionals; see `../CLAUDE.md`).

### Themes

A theme is a module, `render/themes/<name>/theme.js`, exporting:

- `label`: display name for the picker, e.g. "Sleep".
- `styles`: the `(blockType, variant)` → appearance lookup (colours, fonts, spacing, background images).
- `imageSide`: `"left"` or `"right"` for `image_with_text`. Fixed per theme, not alternating, because alternating needs each block to know its position among its siblings. Revisit only if a theme actually needs it.
- `dateFormat`: `Intl.DateTimeFormat` options, e.g. `{ month: "long", day: "numeric", year: "numeric" }`. Parse the document's `YYYY-MM-DD` as UTC so the day can't shift with the viewer's timezone. There's a default if the theme omits it.
- `shell({ subject, preheader, body, styles })`: the outer HTML document (doctype, `<head>`, Outlook settings, media queries, the hidden preheader). The theme owns its shell: `flipboard/techdigest.html` and `traction/index.html` already differ at that level, and that's exactly the brand-level variation a theme exists for.

Themes can also add assets (e.g. background images) under their directory, referenced by absolute URL from the hosted site or an image host.

### Registry

A static site can't list a directory, so `render/registry.js` names everything available: the block types (each has a schema in `../blocks/` and a template in `render/blocks/`), the themes, the default theme, and the flavors. Adding a block type, theme or flavor means adding one line there. This keeps templates, themes and flavors code-defined, the same way block schemas are.

### Disk layout

```
blocks/<blockType>.json            schemas (unchanged)
authoring/index.html               editor + preview pane
docs/agents.md                     the one page agents read
render/
  render.js                        check, renderPreview, renderTemplate, html/raw
  check.js                         Node wrapper: prints check's issues as JSON
  registry.js                      block types, themes, default theme, flavors
  blocks/<blockType>.js            one template per block type
  themes/<name>/theme.js           styles, imageSide, dateFormat, shell
  flavors/<name>.js                conditional wrapping + syntax escaping per platform
  vendor/                          the markdown library (see Markdown)
```

## The editor

The authoring tool grows a preview pane next to the form:

- It re-renders on every change with `renderPreview`, so you see the email while you edit it.
- A **theme picker** writes the document's `theme`.
- A **"preview as" picker** lists the document's rulesets as checkboxes. Its label must make clear that it chooses what to *show* and tests nothing: whether a real recipient matches "US only" is decided by the approved translation, in the platform.
- A **width toggle** (desktop / mobile) is cheap and worth having, since email layouts collapse at narrow widths.
- The preview is rendered into an `<iframe srcdoc>`, so the email's styles can't leak into the editor or the other way round.
- Validation stays advisory. The validation panel shows `check`'s issues, the same list an agent sees. A block that fails to render shows an inline error in the preview in place of that block, and the rest of the email still renders.
- Each block shows its id (`b7`), so a person and an agent can refer to the same block.
- The editor can work on a file on disk directly (see **File sync** below).

### File sync

The editor can **open a file on disk and stay attached to it**, so a person and an agent can take turns on the same `campaign.json` without exporting and importing:

- **Open file** uses the browser's file picker and keeps the file handle. Every change is autosaved to the file (debounced), as well as to localStorage.
- The editor **watches the file** while the tab is visible, checking its modified time every second or two. When it changes on disk, the editor reloads it and re-renders the preview, so an agent's edit shows up without the person doing anything.
- **If the file on disk isn't valid JSON** (for example, caught mid-write), the editor keeps what it has, shows a notice, and doesn't write to the file until it parses again, so it never overwrites an agent's work with a stale copy.
- **If both sides changed** (an edit is still waiting to autosave when the file changes on disk), the editor asks: take the file's version, or keep the editor's and overwrite the file.
- The editor writes the same format as Save: 2-space indent, keys in the tool's order. A one-field change is a one-line diff.
- The handle is remembered across reloads (stored in IndexedDB). The browser asks the person to confirm access again after a reload.
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
- With a `flavor` and `translations`, it also reports each ruleset without an approved translation. So a clean `check` guarantees `renderTemplate` won't fail.
- `block` and `field` pin each issue to one place, so the fix is a targeted edit. `code` is stable and machine-readable. `message` is for people.
- Hidden blocks aren't checked, as now.

Agents run it through a thin Node wrapper, the one command in the design:

```
node render/check.js campaign.json [--flavor iterable --translations FILE]
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

1. **Translate** each distinct ruleset into an Iterable condition, then have the author **review** them (see **Ruleset translation**).
2. **Render** with `renderTemplate` under Node.
3. **Push** the template to Iterable through its template API, and **send proofs** to test users, or point the author at Iterable's preview with test user data. Confirm the exact endpoints against Iterable's API docs.

This is only needed after the rulesets change, not after every copy edit.

**Fallback without Claude:** the editor has a "Copy template" action that runs `renderTemplate` and copies the result for pasting into Iterable's template editor. It works only once every ruleset in the document has an approved translation available to the editor. For a document without rulesets it always works.

## Output flavors

The rendered template goes to the platform as a template, not as final HTML, so anything decided per recipient at send time is written in the platform's own syntax.

- **Iterable** is the first flavor: Handlebars as Iterable implements it, with Iterable's helpers. SendGrid should follow as its own flavor. It's also Handlebars-based but its helpers differ, so "Handlebars" alone doesn't identify a flavor.
- A flavor owns how conditionals wrap blocks, and **escaping its own syntax** in content. The conditions themselves come from the translate step.
- The document never names a flavor. The same document renders for any flavor.

## Ruleset translation (carried over from block segmentation)

The design is in `../completed/block-segmentation.md` (**Translation: ruleset → conditional**):

- A **translate step** (AI: Claude in the plugin, or Claude Code) writes ruleset text → condition, cached by (ruleset text, environment, flavor).
- A **review** of each ruleset, the AI's reading of it, and the generated condition, before it counts as approved.
- The renderer only **reads approved translations** and never calls an AI. A ruleset with no approved translation is a hard error in `renderTemplate`. `renderPreview` never needs one.

## Themes and variants

A block may carry a `variant` (`primary` or `secondary`). The theme resolves `(blockType, variant)` to an appearance, and the document never names a colour.

When a theme has no styling for a variant in use, **render the block as `primary` and warn**, naming the block type and the missing variant. In the editor the warning shows in the validation panel. Failing hard would turn every allowed widening of the `variant` enum into a breaking change for every existing theme.

## Compatibility with evolving schemas

From the authoring tool's **Schema evolution** rules:

- A field missing from `data` takes the `default` declared in its schema. Old documents predate fields that newer templates expect.
- A field in `data` that the template doesn't use is **ignored**, never an error.

Schemas may only gain optional fields; renames and removals become a new `blockType`. So a template written for version *N* of a schema works against every later version, and documents saved by older versions keep rendering.

## Markdown

`markdown` fields are converted to HTML with **raw HTML in the source escaped, not passed through**. Passing it through would quietly undo the editor's ban on raw HTML.

Use **markdown-it** with `html: false`, vendored as a single file under `render/vendor/` (no package manager). It runs in both the browser and Node. The legacy `body` values in `content/weekly.json` are raw HTML and need a one-off conversion to markdown before they can round-trip.

## Open questions

- **Where do approved translations live?** Next to the document, or inside it? This now matters to the editor too: the "Copy template" fallback needs them, and inside the document is the only place a static page can reliably find them. The cost is platform-specific code in a document that's meant to be platform-neutral. (Carried over from block segmentation.)
- **What form does the environment context take** for translation: a notes file, a sample user profile, or pulled from Iterable's API? (Carried over.)
- **Should review flag an audience left with no blocks?** The "preview as" picker makes such an audience visible by hand; review could catch it automatically. (Carried over.)
- **Theme vs. `feature_type`.** "Anxiety theme vs. sleep theme" overlaps with `content_feature_header.feature_type` (`meditate` / `sleep`), which the library spec says a theme keys its visuals off. Is the category content (a field), the look (a theme), or both, with the theme free to use the field?
- **How the plugin hands a document to the hosted editor in chat**, where there's no shared file for **File sync**: file import (works today), or something smoother such as a URL fragment. With Claude Code and local files, File sync covers it.

## Build order

1. **Hosting.** GitHub Pages is on (deploying from `master`), and `.nojekyll` is in place. Switch the editor to load `../blocks/*.json` through the registry, using relative paths, and delete the inlined schemas.
2. **Shared check and renderer, with preview.**
   - Move the editor's validation into `check` and add `check.js`.
   - Add `render.js` with `html`/`raw`, templates for the five block types, and one theme (ported from an existing template).
   - Add the preview pane, the document `theme` key and the theme picker. Add a second theme to prove switching works.
   - Add `nextId`, and show ids in the editor.
   - Write `docs/agents.md`.
3. **File sync.** Open a file, autosave to it, and reload when it changes on disk.
4. **"Preview as".** Add the ruleset picker and switch-group resolution in `renderPreview`.
5. **Iterable flavor.** Add `renderTemplate`, the Iterable flavor, translation coverage in `check`, and the "Copy template" action.
6. **Claude + Iterable.** Translate, review, push and send proofs through Iterable's API.

`../CLAUDE.md`, `../docs/blocks.md` and `../docs/agents.md` are updated in the same change as each step that alters what they describe (hosting, the `theme` and `nextId` keys, the renderer, `check`).

## Status

Design settled apart from the open questions above, none of which block steps 1 to 4. Implementation can start at step 1.
