# Claude plugin: copy doc → email HTML

Now that the authoring tool exists, wrap the whole pipeline in a Claude plugin, a collection of skills used from Claude chat/Cowork, so a non-technical user can go from a loosely formatted copy document to finished email HTML without touching JSON.

## Flow

1. User loads the plugin/skill.
2. User provides a loosely formatted copy document: Google Doc, PDF, Word, pasted text.
3. **Skill A: pick the email type and structure the copy.**
   1. Offers a series of options: what kind of email is this (e.g. weekly digest, single feature announcement, newsletter).
   2. Parses the copy doc into the authored-email JSON document (see `../completed/serverless-email-authoring-tool.md`) for the chosen option: blocks in order, each `data` filled to its schema in `../blocks/`.
4. **Skill B: open the editor.** Opens the authoring tool (`../authoring/index.html`) loaded with Skill A's document. The user fixes typos and makes structural changes (reorder, add or drop blocks).
5. **Skill C: test in Iterable.** Translates the rulesets, has the user review them, renders the platform template, pushes it to Iterable and sends proofs (`../specs/render-layer-tool.md`, **Testing in Iterable**). The visual review happens earlier, in the editor's live preview.

## Email types

Email types are **hard-coded in Skill A**: each is a predefined set of blocks, in order. Skill A lists the types, the user picks one, and Claude fills that block set from the copy doc. Adding a type means editing the skill.

A starter set, using only the blocks that exist today (`../blocks/`):

| Type | Blocks |
|---|---|
| Digest | `content_feature_header`, one `primary` `article`, n `secondary` `article`s, `button` |
| Feature announcement | `content_feature_header`, `image_with_text`, `button` |
| Newsletter | `content_feature_header`, `image_with_text`, `divider`, n `secondary` `article`s, `button` |

"n" marks a repeating block: its count comes from the copy, not the type.

**Every block in the type is always emitted.** A block the copy has nothing for (e.g. a `button` when there's no call to action) is kept but marked **hidden**. The document's shape therefore always matches its type, and the user can unhide and fill the block in the editor rather than having to know it was ever an option.

`hidden` doesn't exist yet, and it touches all three tools:

- **Document format:** a block-level flag next to `id` and `blockType`, not inside `data`. It says whether the block is shown, not what it contains, so it doesn't belong to any block schema, and every block type gets it without a schema change. Optional, default `false`, so existing documents are unaffected.
- **Authoring tool:** a show/hide toggle per block, with hidden blocks visibly marked. Hidden blocks are still validated but their errors shouldn't nag, since an empty hidden block is the normal case.
- **Render layer:** skips hidden blocks entirely. That also means a hidden block's `data` never needs to be valid.

Conditional visibility (e.g. "US only") builds on this: `../completed/block-segmentation.md`.

The JSON document is the only thing passed between steps. Each skill reads it and writes it, so a user can also enter the flow partway (e.g. bring an existing JSON document straight to Skill C).

## Open questions

- **Skill A parsing:** extraction is Claude's job, done in the skill. The schemas give it the target shape, and validation catches misses. What happens to copy that doesn't fit the chosen type: drop it, flag it, or suggest another type? Images are required on `article`, but copy docs often won't have them. Leave placeholders and let the editor's advisory validation surface them?
- **Skill B in chat/Cowork:** the editor is a statically hosted page that loads from `localStorage` or a file import. How does Skill A's document get into it, and how does the edited document get back to Claude for Skill C: file export/import, or something smoother? (Also an open question in the render layer spec.)
- **Skill C depends on the render layer**, which isn't built yet (`../specs/render-layer-tool.md`). The renderer is a JavaScript module that runs under Node, and the skill can fetch it from the hosted site, so its copy can't drift from the editor's. It also needs Iterable API credentials in its environment.
- **Theme selection:** the document records its theme. Should Skill A set it from the email type, or leave the default for the user to change in the editor?
- **Relation to the existing campaign-strategy skill:** that skill covers the brief and the copywriting. This plugin could start where it stops, with its copy output as the "copy doc" input here.
- **Packaging:** one plugin with three skills, or one skill with three stages? Separate skills let users rerun one step (re-render after editing) without restarting the whole flow.

## Prerequisites

- Render layer tool (`../specs/render-layer-tool.md`).
- Block-level `hidden` flag: done in the authoring tool (with `../completed/block-segmentation.md`). The renderer still needs to skip hidden blocks.
