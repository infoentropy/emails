# Email block library

Split out of `../specs/serverless-email-authoring-tool.md`, which defines the document format and the authoring tool but deliberately doesn't commit to a set of block types. This file is where that set gets worked out.

Lives in `ideas/` rather than `specs/` because it isn't scoped yet — the block list and field definitions below are candidates, not decisions.

## What this needs to produce

A set of JSON Schema documents, one per block type, in the format the authoring tool spec defines: `$id` of `block:<name>`, a `title`, a `version` integer, `properties` with a `fieldType` and `weight` on each field, and a `required` list. Schemas must follow the additive-only evolution rule in that spec.

## Source material

`content/weekly.json` is a real campaign from the old Django app and contains the block types that actually shipped, with their real field names:

| Snippet name (old)              | Fields |
|---------------------------------|--------|
| `component - discount header`   | `bg_color`, `bg_image`, `bg_position`, `body`, `coupon_code`, `cta_text`, `expires_text`, `icon_image`, `icon_link`, `padding`, `preheader` |
| `component - content feature header` | `avatar_image`, `avatar_link`, `bg_color`, `bg_image`, `bg_position`, `feature_type`, `icon_image`, `icon_image_visible`, `icon_link`, `preheader` |
| `component - spacer`            | `height` |
| `component - button`            | `color`, `link`, `text`, `width` |
| `component - large divider`     | `color` |

`flipboard/techdigest.html` and `traction/index.html` are the other reference points — the block types they'd decompose into may differ from the list above.

## Settled: images, colours and links are text fields

The authoring tool keeps its text-only `fieldType` set for v1 (`text`, `paragraph`, `markdown`, `date`, `integer`, `float`). No image, colour, link, select or checkbox widgets. So every image URL, link URL and colour value in this library is modelled as `fieldType: text`, and widgets get upgraded in a later pass.

Consequences to design around rather than discover later:

- **Schemas should still declare `enum` and `format: uri`** even though the widget is a plain text box. The authoring tool's validator checks both, so constrained values and URLs are at least flagged when wrong — validation is the only guard rail here. This matters: the sample data contains `"bg_color": "##446740"`, a double-hash typo that shipped.
- **Authors hand-type CloudFront URLs.** Unpleasant but not blocking; the images are hosted externally already, and a serverless tool has nowhere to upload to regardless.
- **`icon_image_visible` has no representation.** It is a boolean, and there is no `boolean` fieldType. Options: drop the field, model it as a `text` enum of `"true"`/`"false"` (which lies about its JSON Schema `type`), or make `boolean` the first addition when the fieldType set is revisited. Unresolved — the only field in the source material that v1 genuinely cannot express.

## Applying the layout principle

The authoring tool spec keeps a presentation field only where the value *is* the content. Provisional verdicts:

| Field | Verdict |
|---|---|
| `height` (spacer) | **Schema** — the block's entire meaning |
| `body`, `preheader`, `coupon_code`, `cta_text`, `expires_text`, `text`, `feature_type` | **Schema** — content |
| `bg_image`, `icon_image`, `avatar_image`, `*_link` | **Schema** — content |
| `padding`, `width`, `bg_position`, `bg_color` | **Theme** — styling |

Two things fall out of this:

- **`large divider` becomes a zero-field block.** Its only field is `color`, which is styling. That's fine — it renders as a themed rule with nothing to author, like `<hr>` — but the authoring UI needs to handle a block whose form is empty.
- **`button.color` is the one case the principle doesn't settle.** `"calm-blue"` reads as a styling value, but in practice it is probably selecting a *variant* (primary vs. secondary), which is semantic and belongs in the schema. If so it should be renamed — `variant`, with an enum of semantic names rather than colour names, so the theme decides what "primary" looks like. Needs a decision from whoever owns the brand tokens.

## Other open questions

- **Naming.** Old names are prose (`component - discount header`). New `blockType` values should be identifier-shaped (`discount_header`). Straight rename, or reconsider the taxonomy?
- **`body` holds HTML.** In `weekly.json` the discount header's `body` is `"<p>THIS IS THE BEST I CAN DO</p>\n<p>wow it is great</p>"`. The authoring tool bans raw HTML editing, so this wants to be `fieldType: markdown` — meaning the render layer, not the tool, converts markdown to HTML. The render layer spec has this as an open question too.
- **Per-block `preheader`.** Several blocks have a `preheader` field that is heading text within the block, unrelated to the email-level `preheader` (inbox preview text). Worth renaming to avoid the collision.

## Next step

Settle the `boolean` gap and `button.color`, pick a first block set, then write the schemas out and move this to `../specs/`.
