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

## Settled: field representation

The authoring tool keeps images, links and constrained values as `fieldType: text` for v1 — no image, colour, link or select widgets. One exception was carved out: **`boolean` was added to the fieldType set** (see the authoring tool spec), because `icon_image_visible` is a real boolean and every text-based encoding of it would make the schema misdescribe its own data.

Consequences to design around rather than discover later:

- **Schemas should still declare `enum` and `format: uri`** even though the widget is a plain text box. The authoring tool's validator checks both, so constrained values and URLs are at least flagged when wrong — validation is the only guard rail here. This matters: the sample data contains `"bg_color": "##446740"`, a double-hash typo that shipped.
- **Authors hand-type CloudFront URLs.** Unpleasant but not blocking; the images are hosted externally already, and a serverless tool has nowhere to upload to regardless.
- **`icon_image_visible` needs a precedence rule.** The sample has `icon_image_visible: true` sitting next to `icon_image: ""` — the flag says show it, with nothing to show. Define it as: the icon renders **iff `icon_image` is non-empty *and* `icon_image_visible` is true.** Emptiness alone is not enough to hide an icon, and the flag alone cannot conjure one.
- **`discount header` has no visibility flag** despite carrying the same `icon_image` / `icon_link` pair. Either it gains one for consistency — permitted at zero cost by the additive-only rule, provided it is optional and defaults to `true` — or the inconsistency is deliberate and should be written down as such.

## Settled: `variant` replaces colour names

`button.color` and `large divider.color` both become **`variant`**: a semantic selector with an `enum`, where the theme decides what each value looks like. Colour names leave the document entirely.

The reasoning: the sample campaign uses two differently-coloured buttons (`calm-blue` and `blue`) in one email, so authors *do* differentiate and some selector has to stay in the document. But the existing vocabulary is already incoherent — `large divider` is also `blue`, and nothing says whether `blue` and `calm-blue` are the same token or two different ones. Semantic names fix that and keep the document theme-independent.

- `button.variant` — provisionally `primary` / `secondary`.
- `large_divider.variant` — provisionally `subtle` / `strong`. This reverses the earlier finding that the divider would be a zero-field block; it now has exactly one field.

Both enums are **provisional vocabulary**, not decisions: whoever owns the brand tokens should confirm the value names before the schemas are written. The shape is settled; the words are not.

## Applying the layout principle

The authoring tool spec keeps a presentation field only where the value *is* the content. Provisional verdicts:

| Field | Verdict |
|---|---|
| `height` (spacer) | **Schema** — the block's entire meaning |
| `body`, `preheader`, `coupon_code`, `cta_text`, `expires_text`, `text`, `feature_type` | **Schema** — content |
| `variant` (was `color`, on button and divider) | **Schema** — a semantic selector, not styling |
| `icon_image_visible` | **Schema** — an authoring decision, now a `boolean` field |
| `bg_image`, `icon_image`, `avatar_image`, `*_link` | **Schema** — content |
| `padding`, `width`, `bg_position`, `bg_color` | **Theme** — styling |

Both questions this originally raised are now resolved above: `large divider` is not a zero-field block after all (it keeps a `variant`), and `button.color` becomes `button.variant`. No block in the library now has an empty form, so the authoring UI does not strictly need to handle that case — still worth building defensively, since the additive-only rule leaves a field-free block possible in future.

## Other open questions

- **Naming.** Old names are prose (`component - discount header`). New `blockType` values should be identifier-shaped (`discount_header`). Straight rename, or reconsider the taxonomy?
- **`body` holds HTML.** In `weekly.json` the discount header's `body` is `"<p>THIS IS THE BEST I CAN DO</p>\n<p>wow it is great</p>"`. The authoring tool bans raw HTML editing, so this wants to be `fieldType: markdown` — meaning the render layer, not the tool, converts markdown to HTML. The render layer spec has this as an open question too.
- **Per-block `preheader`.** Several blocks have a `preheader` field that is heading text within the block, unrelated to the email-level `preheader` (inbox preview text). Worth renaming to avoid the collision.

## Next step

The two blockers are cleared. What remains before this becomes a spec:

1. Confirm the provisional `variant` vocabularies with whoever owns the brand tokens.
2. Decide the three open questions above (naming, markdown `body`, `preheader` collision) — all smaller than the two just settled.
3. Pick the first block set, write the schemas out, and `git mv` this to `../specs/`.
