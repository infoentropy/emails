# Email block library

Split out of `../specs/serverless-email-authoring-tool.md`, which defines the document format and the authoring tool but deliberately doesn't commit to a set of block types. This file is where that set gets worked out.

Lives in `ideas/` rather than `specs/` because it isn't scoped yet — the block list and field definitions below are candidates, not decisions.

## What this needs to produce

A set of JSON Schema documents, one per block type, in the format the authoring tool spec defines: `$id` of `block:<name>`, a `title`, a `version` integer, `properties` with a `fieldType` and `weight` on each field, and a `required` list. Schemas must follow the additive-only evolution rule in that spec.

## Source material

`content/weekly.json` is a real campaign from the old Django app and contains the block types that actually shipped, with their real field names:

| Snippet name (old)              | New `blockType` | Fields |
|---------------------------------|-----------------|--------|
| `component - discount header`   | `discount_header` | `bg_color`, `bg_image`, `bg_position`, `body`, `coupon_code`, `cta_text`, `expires_text`, `icon_image`, `icon_link`, `padding`, `preheader` |
| `component - content feature header` | `content_feature_header` | `avatar_image`, `avatar_link`, `bg_color`, `bg_image`, `bg_position`, `feature_type`, `icon_image`, `icon_image_visible`, `icon_link`, `preheader` |
| `component - spacer`            | `spacer` | `height` |
| `component - button`            | `button` | `color`, `link`, `text`, `width` |
| `component - large divider`     | `large_divider` | `color` |

Field names in that table are the **old** ones; `preheader` becomes `heading` and `color` becomes `variant`, per the sections below.

`flipboard/techdigest.html` and `traction/index.html` are the other reference points — the block types they'd decompose into may differ from the list above.

## Settled: field representation

The authoring tool keeps images, links and constrained values as `fieldType: text` for v1 — no image, colour, link or select widgets. One exception was carved out: **`boolean` was added to the fieldType set** (see the authoring tool spec), because `icon_image_visible` is a real boolean and every text-based encoding of it would make the schema misdescribe its own data.

Consequences to design around rather than discover later:

- **Schemas should still declare `enum` and `format: uri`** even though the widget is a plain text box. The authoring tool's validator checks both, so constrained values and URLs are at least flagged when wrong — validation is the only guard rail here. This matters: the sample data contains `"bg_color": "##446740"`, a double-hash typo that shipped.
- **Authors hand-type CloudFront URLs.** Unpleasant but not blocking; the images are hosted externally already, and a serverless tool has nowhere to upload to regardless.
- **`icon_image_visible` needs a precedence rule.** The sample has `icon_image_visible: true` sitting next to `icon_image: ""` — the flag says show it, with nothing to show. Define it as: the icon renders **iff `icon_image` is non-empty *and* `icon_image_visible` is true.** Emptiness alone is not enough to hide an icon, and the flag alone cannot conjure one.
- **`discount header` has no visibility flag** despite carrying the same `icon_image` / `icon_link` pair. Either it gains one for consistency — permitted at zero cost by the additive-only rule, provided it is optional and defaults to `true` — or the inconsistency is deliberate and should be written down as such.

## Settled: `variant` replaces colour names

`button.color` and `large divider.color` both become **`variant`**, drawn from the shared `primary` / `secondary` scale the authoring tool spec defines. Colour names leave the document entirely; the theme resolves `(blockType, variant)` to an appearance.

The reasoning: the sample campaign uses two differently-coloured buttons (`calm-blue` and `blue`) in one email, so authors *do* differentiate and some selector has to stay in the document. But the existing vocabulary is already incoherent — `large divider` is also `blue`, and nothing says whether `blue` and `calm-blue` are the same token or two different ones.

Settled details:

- `button.variant` — `primary` / `secondary`, optional, defaults to `primary`.
- `large_divider.variant` — the same scale, same default. This reverses the earlier finding that the divider would be a zero-field block; it now has exactly one field.
- The names need no brand sign-off, because they name emphasis rather than colour. What the brand owner owns is the theme's mapping.

Worth noting how thin the evidence for a *divider* variant is: `flipboard/techdigest.html` contains ten dividers, all byte-identical (`1px solid #d8d8d8`), and `weekly.json` has exactly one. Buttons, by contrast, vary within a single campaign. In practice dividers may only ever use `primary` — which costs nothing, since the field is optional and the enum is shared rather than invented per block.

## Applying the layout principle

The authoring tool spec keeps a presentation field only where the value *is* the content. Provisional verdicts:

| Field | Verdict |
|---|---|
| `height` (spacer) | **Schema** — the block's entire meaning |
| `body`, `heading` (was `preheader`), `coupon_code`, `cta_text`, `expires_text`, `text`, `feature_type` | **Schema** — content |
| `variant` (was `color`, on button and divider) | **Schema** — a semantic selector, not styling |
| `icon_image_visible` | **Schema** — an authoring decision, now a `boolean` field |
| `bg_image`, `icon_image`, `avatar_image`, `*_link` | **Schema** — content |
| `padding`, `width`, `bg_position`, `bg_color` | **Theme** — styling |

Both questions this originally raised are now resolved above: `large divider` is not a zero-field block after all (it keeps a `variant`), and `button.color` becomes `button.variant`. No block in the library now has an empty form, so the authoring UI does not strictly need to handle that case — still worth building defensively, since the additive-only rule leaves a field-free block possible in future.

## Settled: naming

- **`blockType` values are snake_case identifiers** derived mechanically from the old snippet names, dropping the redundant `component` prefix — every block is a component. See the table above.
- **`preheader` becomes `heading` on every block that has one.** There is exactly one preheader in the system: the campaign-level metadata field, outside the blocks entirely. The name is reserved for it, and no block schema may define its own. What the old app called a block `preheader` is that block's heading text — and in both cases it is the *only* heading text the block has, so `heading` names it accurately rather than implying a headline it sits above.

## Settled: `body` stays `body`

`body` keeps its name and takes `fieldType: markdown`. Markdown is the notation an author fills the field in with, not a different kind of field — the same way `text` and `paragraph` are both just strings. The render layer converts it to HTML.

Raw HTML in a markdown field is **escaped, not passed through**. Standard markdown converters allow HTML through, which would leave the authoring tool's ban on raw HTML editing stated but unenforced.

That has one migration consequence: the legacy `body` in `weekly.json` is raw HTML (`"<p>THIS IS THE BEST I CAN DO</p>\n<p>wow it is great</p>"`). Under escaping it would render as visible literal angle brackets, so legacy values need converting to markdown as a one-off before any old campaign can round-trip through the new tools.

## Next step

**There are no open questions left.** Every decision this file was waiting on — the `boolean` gap, `button.color`, the `variant` vocabulary, `blockType` naming, `body`, and the `preheader` collision — is settled above.

What remains is the work itself:

1. Confirm the block set. The five in the table above are the obvious candidates, being the ones that actually shipped, but nothing has formally committed to them.
2. Write the schemas out, applying the decisions above.
3. `git mv` this file to `../specs/` once it describes work someone could start from without further clarification.
