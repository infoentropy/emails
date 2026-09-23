# Claude plugin: copy doc → email HTML

Now that the authoring tool exists, wrap the whole pipeline in a Claude plugin, a collection of skills used from Claude chat/Cowork, so a non-technical user can go from a loosely formatted copy document to finished email HTML without touching JSON.

## Flow

1. User loads the plugin/skill.
2. User provides a loosely formatted copy document: Google Doc, PDF, Word, pasted text.
3. **Skill A: pick the email type and structure the copy.**
   1. Offers a series of options: what kind of email is this (e.g. weekly digest, single feature announcement, newsletter).
   2. Parses the copy doc into the authored-email JSON document (see `../completed/serverless-email-authoring-tool.md`) for the chosen option: blocks in order, each `data` filled to its schema in `../blocks/`.
4. **Skill B: open the editor.** Opens the authoring tool (`../authoring/index.html`) loaded with Skill A's document. The user fixes typos and makes structural changes (reorder, add or drop blocks).
5. **Skill C: render.** Runs the render script to output the HTML email.

The JSON document is the only thing passed between steps. Each skill reads it and writes it, so a user can also enter the flow partway (e.g. bring an existing JSON document straight to Skill C).

## Open questions

- **What is an "email type"?** Nothing in the repo defines one yet. The likely shape is a named recipe: an allowed or suggested sequence of block types (digest = `content_feature_header`, one `primary` `article`, n `secondary` `article`s, `button`), maybe paired with a default theme. Where do recipes live? Next to `blocks/` as data, so Skill A and the editor can share them?
- **Skill A parsing:** extraction is Claude's job, done in the skill. The schemas give it the target shape, and validation catches misses. What happens to copy that doesn't fit the chosen type: drop it, flag it, or suggest another type? Images are required on `article`, but copy docs often won't have them. Leave placeholders and let the editor's advisory validation surface them?
- **Skill B in chat/Cowork:** the editor is a static page that loads from `localStorage` or a file import. In chat it would probably be published as an Artifact with the document injected as its starting state. The edited document then has to get back to Claude for Skill C: by export/paste, or through an artifact capability that lets Claude read the page's state. This needs checking against what artifacts can actually do.
- **Skill C depends on the render layer**, which isn't built yet (`../specs/render-layer-tool.md`: Python 3 + Jinja2). Chat/Cowork can run Python in its sandbox, so the script and templates would ship inside the skill. The skill's copy of the schemas and templates can drift from this repo. Build a packaging step, or have the skill fetch them from here?
- **Theme selection:** the render layer takes a theme. Ask the user in Skill C, or tie it to the email type chosen in Skill A?
- **Relation to the existing campaign-strategy skill:** that skill covers the brief and the copywriting. This plugin could start where it stops, with its copy output as the "copy doc" input here.
- **Packaging:** one plugin with three skills, or one skill with three stages? Separate skills let users rerun one step (re-render after editing) without restarting the whole flow.

## Prerequisites

- Render layer tool (`../specs/render-layer-tool.md`).
- A definition of email types/recipes (new; could be its own spec).
