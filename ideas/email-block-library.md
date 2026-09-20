# Email block library

Split out of `../specs/serverless-email-authoring-tool.md`, which defines the document format and the authoring tool but deliberately doesn't commit to a set of block types. This file is where that set gets worked out.

Lives in `ideas/` rather than `specs/` because it isn't scoped yet — the block list and field definitions below are candidates, not decisions.

## What this needs to produce

A set of JSON Schema documents, one per block type, in the format the authoring tool spec defines: `$id` of `block:<name>`, a `title`, `properties` with a `fieldType` and `weight` on each field, and a `required` list.

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

## Tension to resolve

The authoring tool's v1 `fieldType` set is `text`, `paragraph`, `markdown`, `date`, `integer`, `float` — no image picker, no color picker, no link picker. But **most fields above are images, colors or links**. Options:

1. Model them as `text` fields holding a URL or hex string for now, and upgrade the widgets later. Ugly to author, but unblocks everything.
2. Pull image/color/link pickers forward into the tool's v1, contradicting its current "explicitly deferred" line.
3. Pick a first block set that avoids them — which, looking at the table, means roughly `spacer` and `divider`. Not enough to be useful.

This is the main thing to settle before this becomes a spec.

## Other open questions

- **Naming.** Old names are prose (`component - discount header`). New `blockType` values should be identifier-shaped (`discount_header`). Straight rename, or reconsider the taxonomy?
- **`body` holds HTML.** In `weekly.json` the discount header's `body` is `"<p>THIS IS THE BEST I CAN DO</p>\n<p>wow it is great</p>"`. The authoring tool bans raw HTML editing, so this wants to be `fieldType: markdown` — meaning the render layer, not the tool, converts markdown to HTML. Needs confirming with whoever owns the render layer.
- **Enum-ish fields.** `color: "calm-blue"`, `feature_type: "sleep"`, `bg_position: "bottom center"` are clearly constrained value sets, not free text. JSON Schema `enum` covers this, but no `fieldType` maps to a select/dropdown widget yet. Probably needs one.
- **Layout fields.** `padding: "10px 20px 10px 20px"` and `width: 220` are presentation, and the authoring tool's premise is that content is theme-independent. Do these belong in the schema layer at all, or are they the render layer's job?
- **`icon_image_visible`** is a boolean — another `fieldType` the v1 list doesn't have.
- **Per-block `preheader`.** Several blocks have a `preheader` field that is heading text within the block, unrelated to the email-level `preheader` (inbox preview text). Worth renaming to avoid the collision.

## Next step

Decide the tension above, pick a first block set, then write the schemas out and move this to `../specs/`.
