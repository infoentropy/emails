# Email block library

Split out of `serverless-email-authoring-tool.md`, which defines the document format and the authoring tool but deliberately doesn't commit to a set of block types. This file is where that set gets worked out.

Moved to `specs/` once every open question was settled; the schemas it describes are drafted in `../blocks/`.

## What this produces

A set of JSON Schema documents, one per block type, in the format the authoring tool spec defines: `$id` of `block:<name>`, a `title`, a `version` integer, `properties` with a `fieldType` and `weight` on each field, and a `required` list. Schemas follow the additive-only evolution rule in that spec.

**All four schemas exist in `../blocks/`** — `discount_header`, `content_feature_header`, `button` and `divider`. They are checked mechanically against the conventions above and against `content/weekly.json`: every surviving field is content, and no required field is empty in the source data.

Migrating the sample campaign under the content-only rule loses more than field names, and the losses are worth stating plainly:

- **The spacer instance disappears entirely.** Its block type no longer exists, so there is nothing to migrate it into. Whatever gap it was creating becomes the theme's problem.
- **`bg_image` held genuine CloudFront URLs** in both header blocks and now comes from the theme. That is a capability change rather than a relocation: a theme styles a *block type*, so every `discount_header` shares a background where each instance could previously differ. Nothing in the sample exercises this, since it has one of each header — but if per-campaign backgrounds matter, the answer is a theme per campaign, not restoring the field.
- **The feature header's avatar is gone**, taking the library's last image field with it. That leaves the image-dimensions convention in the authoring tool spec with no user, which is deliberate and recorded there.

Everything else dropped was either a styling value (`bg_color`, `bg_position`, `padding`, `width`) or empty in the source (`icon_image`, `icon_link`).

## Source material

`content/weekly.json` is a real campaign from the old Django app and contains the block types that actually shipped, with their real field names:

| Snippet name (old)              | New `blockType` | Fields |
|---------------------------------|-----------------|--------|
| `component - discount header`   | `discount_header` | `bg_color`, `bg_image`, `bg_position`, `body`, `coupon_code`, `cta_text`, `expires_text`, `icon_image`, `icon_link`, `padding`, `preheader` |
| `component - content feature header` | `content_feature_header` | `avatar_image`, `avatar_link`, `bg_color`, `bg_image`, `bg_position`, `feature_type`, `icon_image`, `icon_image_visible`, `icon_link`, `preheader` |
| `component - spacer`            | *(removed)* | `height` |
| `component - button`            | `button` | `color`, `link`, `text`, `width` |
| `component - large divider`     | `divider` | `color` |

Field names in that table are the **old** ones; `preheader` becomes `heading` and `color` becomes `variant`, per the sections below. Most of the rest do not survive the content-only rule.

Two block types changed identity. `spacer` is gone entirely: its only field was a measurement, and vertical rhythm is the theme's. `large divider` becomes `divider`, because `large` is a size descriptor smuggled into an identifier — the `variant` carries any weight distinction.

`flipboard/techdigest.html` and `traction/index.html` are the other reference points — the block types they'd decompose into may differ from the list above.

## Settled: field representation

The authoring tool keeps images, links and constrained values as `fieldType: text` for v1 — no image, colour, link or select widgets, and no `boolean` either. A `boolean` type was briefly added for `icon_image_visible`, then removed along with that field when the icons were reclassified as theme-owned; nothing in the library needs it now.

Consequences to design around rather than discover later:

- **Schemas should still declare `enum` and `format: uri`** even though the widget is a plain text box. The authoring tool's validator checks both, so constrained values and URLs are at least flagged when wrong — validation is the only guard rail here. This matters: the sample data contains `"bg_color": "##446740"`, a double-hash typo that shipped.
- **Authors hand-type CloudFront URLs.** Unpleasant but not blocking; the images are hosted externally already, and a serverless tool has nowhere to upload to regardless. Only `content_feature_header` still has URL fields — the avatar pair.
- **An empty optional field means "not filled in."** The validator skips `format` and `enum` checks on it, and the render layer omits whatever it would have produced. That rule now carries the visibility behaviour an explicit flag used to: a feature image with no URL simply does not render.

## Settled: `variant` replaces colour names

`button.color` and `large divider.color` both become **`variant`**, drawn from the shared `primary` / `secondary` scale the authoring tool spec defines. Colour names leave the document entirely; the theme resolves `(blockType, variant)` to an appearance.

The reasoning: the sample campaign uses two differently-coloured buttons (`calm-blue` and `blue`) in one email, so authors *do* differentiate and some selector has to stay in the document. But the existing vocabulary is already incoherent — `large divider` is also `blue`, and nothing says whether `blue` and `calm-blue` are the same token or two different ones.

Settled details:

- `button.variant` — `primary` / `secondary`, optional, defaults to `primary`.
- `divider.variant` — the same scale, same default. It is the block's only field.
- The names need no brand sign-off, because they name emphasis rather than colour. What the brand owner owns is the theme's mapping.

Worth noting how thin the evidence for a *divider* variant is: `flipboard/techdigest.html` contains ten dividers, all byte-identical (`1px solid #d8d8d8`), and `weekly.json` has exactly one. Buttons, by contrast, vary within a single campaign. In practice dividers may only ever use `primary` — which costs nothing, since the field is optional and the enum is shared rather than invented per block.

## Applying the content-only rule

The authoring tool spec now bans presentation values outright rather than judging field by field. Applied to the source material, almost nothing survives:

| Field | Verdict |
|---|---|
| `heading` (was `preheader`), `body`, `coupon_code`, `cta_text`, `expires_text`, `text`, `feature_type` | **Schema** — content |
| `variant` (was `color`, on button and divider) | **Schema** — a semantic selector, not styling |
| `bg_color`, `bg_image`, `bg_position`, `padding`, `width` | **Theme** — styling |
| `icon_image`, `icon_link`, `icon_image_visible` | **Theme** — an ornament carrying no message |
| `avatar_image`, `avatar_link` | **Removed** — the feature header no longer carries its own imagery |
| `height` (spacer) | **Removed with its block** — spacing is the theme's |

The result is four block types, all of them pure copy plus semantics:

- `discount_header` — heading, body, coupon_code, expires_text, cta_text
- `content_feature_header` — heading, feature_type
- `button` — text, link, variant
- `divider` — variant

`content_feature_header` is thin enough to question: with the avatar gone it is a heading plus a category. That is coherent if the theme keys its imagery off `feature_type`, which is a reasonable division of labour — but it makes `feature_type` load-bearing in a way it was not before, and sharpens the enum question below.

## Settled: naming

- **`blockType` values are snake_case identifiers** derived mechanically from the old snippet names, dropping the redundant `component` prefix — every block is a component. See the table above.
- **`preheader` becomes `heading` on every block that has one.** There is exactly one preheader in the system: the campaign-level metadata field, outside the blocks entirely. The name is reserved for it, and no block schema may define its own. What the old app called a block `preheader` is that block's heading text — and in both cases it is the *only* heading text the block has, so `heading` names it accurately rather than implying a headline it sits above.

## Settled: `body` stays `body`

`body` keeps its name and takes `fieldType: markdown`. Markdown is the notation an author fills the field in with, not a different kind of field — the same way `text` and `paragraph` are both just strings. The render layer converts it to HTML.

Raw HTML in a markdown field is **escaped, not passed through**. Standard markdown converters allow HTML through, which would leave the authoring tool's ban on raw HTML editing stated but unenforced.

That has one migration consequence: the legacy `body` in `weekly.json` is raw HTML (`"<p>THIS IS THE BEST I CAN DO</p>\n<p>wow it is great</p>"`). Under escaping it would render as visible literal angle brackets, so legacy values need converting to markdown as a one-off before any old campaign can round-trip through the new tools.

## Next step

Every decision this file was waiting on — the `boolean` gap, `button.color`, the `variant` vocabulary, `blockType` naming, `body`, and the `preheader` collision — is settled above, and the schemas are drafted in `../blocks/`.

Two things surfaced while writing them that are worth a decision:

- **`feature_type` is now enumerated** as `meditate` / `sleep`. Both values come from evidence in `content/weekly.json` and nowhere else: `sleep` appears as the literal `feature_type` and in the feature link, `meditate` as the destination of both buttons. The list was deliberately not padded out with plausible-looking product areas, because the evolution rule makes the risk asymmetric — *widening* an enum is permitted, so a missing value is a one-line change, while *narrowing* is forbidden, so a speculative value is stuck there for the life of the block type. Add values as real campaigns need them.

  This closes the last time-sensitive question: a field left free text could never have been constrained afterwards, and `feature_type` is load-bearing now that the theme selects imagery from it.

- ~~`spacer.height` declares a `minimum` nothing enforces~~ — moot: the spacer block is gone. The underlying gap remains, though, should any future field use a keyword outside the validator's `required` / `type` / `enum` / `format` subset.

Remaining work: confirm the block set is the right five, resolve the two points above, then this file and the schemas move on together.
