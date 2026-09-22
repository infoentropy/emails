# Email block library

Split out of `serverless-email-authoring-tool.md`, which defines the document format and the authoring tool but deliberately doesn't commit to a set of block types. This file is where that set gets worked out.

Moved to `specs/` once every open question was settled; the schemas it describes are drafted in `../blocks/`.

## What this produces

A set of JSON Schema documents, one per block type, in the format the authoring tool spec defines: `$id` of `block:<name>`, a `title`, a `version` integer, `properties` with a `fieldType` and `weight` on each field, and a `required` list. Schemas follow the additive-only evolution rule in that spec.

**All five schemas exist in `../blocks/`.** They are checked mechanically against the conventions above and against `content/weekly.json`: every surviving field is content, and no required field is empty in the source data.

Migrating the sample campaign under the content-only rule loses more than field names, and the losses are worth stating plainly:

- **Two instances disappear entirely** — the spacer and the discount header — because their block types no longer exist. There is nothing to migrate them into.
- **`bg_image` held genuine CloudFront URLs** and now comes from the theme. That is a capability change rather than a relocation: a theme styles a *block type*, so every instance of a type shares one background where each could previously differ. If per-campaign backgrounds matter, the answer is a theme per campaign, not restoring the field.
- **The feature header's avatar is gone**, taking the library's last image field with it. That leaves the image-dimensions convention in the authoring tool spec with no user, which is deliberate and recorded there.

Everything else dropped was either a styling value (`bg_color`, `bg_position`, `padding`, `width`) or empty in the source (`icon_image`, `icon_link`).

## Source material

`content/weekly.json` is a real campaign from the old Django app and contains the block types that actually shipped, with their real field names:

| Snippet name (old)              | New `blockType` | Fields |
|---------------------------------|-----------------|--------|
| `component - discount header`   | *(removed)* | `bg_color`, `bg_image`, `bg_position`, `body`, `coupon_code`, `cta_text`, `expires_text`, `icon_image`, `icon_link`, `padding`, `preheader` |
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
| `heading` (was `preheader`), `text`, `feature_type` | **Schema** — content |
| `body`, `coupon_code`, `cta_text`, `expires_text` | **Gone with `discount_header`** — content, but their block was dropped |
| `variant` (was `color`, on button and divider) | **Schema** — a semantic selector, not styling |
| `bg_color`, `bg_image`, `bg_position`, `padding`, `width` | **Theme** — styling |
| `icon_image`, `icon_link`, `icon_image_visible` | **Theme** — an ornament carrying no message |
| `avatar_image`, `avatar_link` | **Removed** — the feature header no longer carries its own imagery |
| `height` (spacer) | **Removed with its block** — spacing is the theme's |

The result is five block types:

- `content_feature_header` — heading, feature_type
- `image_with_text` — heading, body, image (+ alt, width, height)
- `article` — headline, link, image (+ alt, width, height), variant
- `button` — text, link, variant
- `divider` — variant

`content_feature_header` is thin enough to question: with the avatar gone it is a heading plus a category. That is coherent if the theme keys its imagery off `feature_type`, which is a reasonable division of labour — but it makes `feature_type` load-bearing in a way it was not before, and sharpens the enum question below.

## Settled: naming

- **`blockType` values are snake_case identifiers** derived mechanically from the old snippet names, dropping the redundant `component` prefix — every block is a component. See the table above.
- **`preheader` becomes `heading` on every block that has one.** There is exactly one preheader in the system: the campaign-level metadata field, outside the blocks entirely. The name is reserved for it, and no block schema may define its own. What the old app called a block `preheader` is that block's heading text — and in both cases it is the *only* heading text the block has, so `heading` names it accurately rather than implying a headline it sits above.

## Settled: `body` stays `body`

*(No block currently has a `body` field — `discount_header` was the only one. The decision below stands as the convention for whenever a body-copy block appears.)*

`body` keeps its name and takes `fieldType: markdown`. Markdown is the notation an author fills the field in with, not a different kind of field — the same way `text` and `paragraph` are both just strings. The render layer converts it to HTML.

Raw HTML in a markdown field is **escaped, not passed through**. Standard markdown converters allow HTML through, which would leave the authoring tool's ban on raw HTML editing stated but unenforced.

That has one migration consequence: the legacy `body` in `weekly.json` is raw HTML (`"<p>THIS IS THE BEST I CAN DO</p>\n<p>wow it is great</p>"`). Under escaping it would render as visible literal angle brackets, so legacy values need converting to markdown as a one-off before any old campaign can round-trip through the new tools.

## Newspaper-style articles

`article` is one block per article, carrying headline, link and an image. Prominence is the shared `variant`: `primary` is the lead feature, `secondary` a regular item. A newspaper front page is therefore one `article` with `primary` followed by several with `secondary` — no separate `feature_article` type, because emphasis is precisely what `variant` exists for.

`variant` defaults to `secondary` here rather than `primary`. That is a deliberate departure from the other blocks, now written into the authoring tool spec as "the vocabulary is shared, the default is not": a digest has one lead and many regulars, so defaulting every new article to a feature would be wrong in the common case.

Two consequences of taking the minimal field set:

- **Source and read time are not carried.** `flipboard/techdigest.html` shows both on all fourteen of its articles (`VICE •`, `3 min read`), and neither can come from the theme, because they are per-article facts a theme cannot know. Choosing minimal fields means that information is simply dropped. Adding them back later is cheap — a new optional field with a default is a permitted change — so this is a recoverable decision, unlike the enum case.
- **Every article must have an image.** `image`, `image_alt`, `image_width` and `image_height` are all required, which makes a text-only article impossible. That is the safe direction to start from: *removing* a field from `required` is a permitted change, while *adding* one is forbidden. Strict now, relaxable later.

## Gaps and limitations

Two earlier gaps are now closed. `image_with_text` restores body copy to the library, so an email can hold prose again, and between them the new blocks exercise `markdown` and `integer` alongside `text` — three of the six declared `fieldType` values rather than one. `paragraph`, `date` and `float` remain unused.

Two limitations are worth recording:

- **Conditional requirements are not expressible.** An article's `image_alt` and dimensions only make sense when `image` is filled. JSON Schema says this with `dependentRequired`, but the validator subset is `required` / `type` / `enum` / `format`, so it cannot check it. Here it does not bite, because the image fields are all required outright — but it will the moment an image becomes optional. This is the second keyword found wanting, after `minimum`.
- **No arrays.** The schema layer is flat scalars, so a block cannot hold a list. A digest of fourteen articles is fourteen blocks, which the existing move and duplicate operations handle but which is repetitive to author. A repeating-list block would need arrays of objects in the schema, the form renderer and the validator.

## Source material

`content/weekly.json` is a real campaign from the old Django app and contains the block types that actually shipped, with their real field names:

| Snippet name (old)              | New `blockType` | Fields |
|---------------------------------|-----------------|--------|
| `component - discount header`   | *(removed)* | `bg_color`, `bg_image`, `bg_position`, `body`, `coupon_code`, `cta_text`, `expires_text`, `icon_image`, `icon_link`, `padding`, `preheader` |
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
| `heading` (was `preheader`), `text`, `feature_type` | **Schema** — content |
| `body`, `coupon_code`, `cta_text`, `expires_text` | **Gone with `discount_header`** — content, but their block was dropped |
| `variant` (was `color`, on button and divider) | **Schema** — a semantic selector, not styling |
| `bg_color`, `bg_image`, `bg_position`, `padding`, `width` | **Theme** — styling |
| `icon_image`, `icon_link`, `icon_image_visible` | **Theme** — an ornament carrying no message |
| `avatar_image`, `avatar_link` | **Removed** — the feature header no longer carries its own imagery |
| `height` (spacer) | **Removed with its block** — spacing is the theme's |

The result is five block types:

- `content_feature_header` — heading, feature_type
- `image_with_text` — heading, body, image (+ alt, width, height)
- `article` — headline, link, image (+ alt, width, height), variant
- `button` — text, link, variant
- `divider` — variant

`content_feature_header` is thin enough to question: with the avatar gone it is a heading plus a category. That is coherent if the theme keys its imagery off `feature_type`, which is a reasonable division of labour — but it makes `feature_type` load-bearing in a way it was not before, and sharpens the enum question below.

## Settled: naming

- **`blockType` values are snake_case identifiers** derived mechanically from the old snippet names, dropping the redundant `component` prefix — every block is a component. See the table above.
- **`preheader` becomes `heading` on every block that has one.** There is exactly one preheader in the system: the campaign-level metadata field, outside the blocks entirely. The name is reserved for it, and no block schema may define its own. What the old app called a block `preheader` is that block's heading text — and in both cases it is the *only* heading text the block has, so `heading` names it accurately rather than implying a headline it sits above.

## Settled: `body` stays `body`

*(No block currently has a `body` field — `discount_header` was the only one. The decision below stands as the convention for whenever a body-copy block appears.)*

`body` keeps its name and takes `fieldType: markdown`. Markdown is the notation an author fills the field in with, not a different kind of field — the same way `text` and `paragraph` are both just strings. The render layer converts it to HTML.

Raw HTML in a markdown field is **escaped, not passed through**. Standard markdown converters allow HTML through, which would leave the authoring tool's ban on raw HTML editing stated but unenforced.

That has one migration consequence: the legacy `body` in `weekly.json` is raw HTML (`"<p>THIS IS THE BEST I CAN DO</p>\n<p>wow it is great</p>"`). Under escaping it would render as visible literal angle brackets, so legacy values need converting to markdown as a one-off before any old campaign can round-trip through the new tools.

## Gaps this leaves

Dropping `discount_header` removed the library's only body-copy field, and with it the last use of anything but one widget. Two consequences worth deciding on:

- **There is no way to put prose in an email.** The three remaining blocks offer a heading, a button label, and a divider. Nothing holds a paragraph. Whatever the library is meant to do, a content block with body copy looks like the obvious next addition — the authoring tool spec's `content_card` fixture (title, body, cta) is roughly its shape already.
- **Only `fieldType: text` is exercised.** `paragraph`, `markdown`, `date`, `integer` and `float` are all declared in the authoring tool spec and used by nothing. That is not the same situation as `boolean`, which was added specifically for one field and removed with it — these came from the original spec and predate any block library. But it is worth knowing that five of the six widgets are currently speculative, and that `markdown` in particular was settled in some detail (including the raw-HTML escaping rule) for a field that no longer exists.

## Status

Every decision this file was waiting on is settled, and all five schemas exist in `../blocks/`. They validate against the conventions in `serverless-email-authoring-tool.md`, and `content/weekly.json` still migrates into the ones that survived.

Settled since the first draft, for the record:

- The `boolean` gap, `button.color`, the `variant` vocabulary, `blockType` naming, `body`, and the `preheader` collision.
- **`feature_type` is enumerated** as `meditate` / `sleep`, both drawn from evidence in `content/weekly.json` and nowhere else. The list was deliberately not padded with plausible product areas: *widening* an enum is permitted, so a missing value is a one-line change, while *narrowing* is forbidden, so a speculative value is stuck for the life of the block type.
- **The block set was reshaped repeatedly** as the content-only rule tightened. `discount_header` and `spacer` were dropped, `large_divider` became `divider`, and `image_with_text` and `article` were added. The library is now `content_feature_header`, `image_with_text`, `article`, `button` and `divider`.

This file stays in `specs/` rather than moving to `../completed/`. The schemas are written, but nothing has shipped: no tool reads them yet. It moves once the render layer can consume them — and the theme work may reshape the set again before then, since arrangement, backgrounds and imagery all now depend on decisions the theme has not made.

Known limitations, carried rather than resolved:

- **Conditional requirements are not expressible.** `dependentRequired` would say that an image's alt text and dimensions matter only when the image is filled, but the validator subset is `required` / `type` / `enum` / `format`. It does not bite today, because the image fields are required outright — it will the moment one becomes optional. Second keyword found wanting, after `minimum`.
- **No arrays.** The schema layer is flat scalars, so a block cannot hold a list, and a fourteen-article digest is fourteen blocks. This is the limitation most likely to matter, given the newspaper-style content the library is now aimed at.
- **`paragraph`, `date` and `float` are declared but unused.** `text`, `markdown` and `integer` are exercised.
