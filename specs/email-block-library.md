# Email block library

The set of block types available to the authoring tool. `serverless-email-authoring-tool.md` defines the document format and the tool; this file defines the blocks, and the schemas themselves live in `../blocks/`, one JSON Schema document per type.

## The blocks

| `blockType` | Fields, in `weight` order |
|---|---|
| `content_feature_header` | `heading`, `feature_type` |
| `image_with_text` | `heading`, `body`, `image`, `image_alt`, `image_width`, `image_height` |
| `article` | `headline`, `link`, `image`, `image_alt`, `image_width`, `image_height`, `variant` |
| `button` | `text`, `link`, `variant` |
| `divider` | `variant` |

Every field is content. Presentation — colour, background, spacing, size, arrangement — belongs to the theme, per the content-only rule in the authoring tool spec. Image dimensions are the sole exception, because email clients need explicit `width` and `height` to reserve space while images are blocked.

### `article`

One block per article. Prominence is the shared `variant`: `primary` is the lead feature, `secondary` a regular item, so a newspaper-style run is one `primary` followed by several `secondary`. There is no separate `feature_article` type, because emphasis is what `variant` is for.

`variant` defaults to `secondary` here, unlike other blocks — a digest has one lead and many regulars.

Two properties of the minimal field set, both deliberate:

- **Source and read time are not carried**, though `flipboard/techdigest.html` shows both on all fourteen of its articles. Neither can come from the theme, since they are per-article facts. Adding them back is a permitted change (a new optional field with a default), so this is recoverable.
- **Every article must have an image** — all four image fields are `required`, so a text-only article is impossible. Relaxable later: *removing* a field from `required` is permitted, *adding* one is not.

### `content_feature_header`

A heading and a category. It carries no imagery of its own: the theme is expected to key visuals off `feature_type`, which makes that field load-bearing.

`feature_type` is enumerated as `meditate` / `sleep`. Both values are drawn from evidence in `content/weekly.json` and nowhere else, and the list was deliberately not padded with plausible-looking product areas — *widening* an enum is permitted, so a missing value is a one-line change, while *narrowing* is forbidden, so a speculative value is stuck for the life of the block type. Add values as real campaigns need them.

## Field conventions

- **`blockType` values are snake_case identifiers**, and carry no presentation words — a block is named for what it is, not how it looks or how large it is.
- **`preheader` is reserved.** There is exactly one preheader: the campaign-level metadata field, outside the blocks. No block schema may define one. A block's own heading text is `heading`.
- **`body` takes `fieldType: markdown`.** Markdown is the notation the field is filled in with, not a different kind of field. The render layer converts it, and escapes raw HTML rather than passing it through — otherwise the tool's ban on raw HTML editing would be stated but unenforced.
- **Declare `enum` and `format: uri` even though the widget is a plain text box.** v1 has no constraining widgets, so the validator is the only guard rail on URLs and constrained values. The sample data contains `"bg_color": "##446740"`, a double-hash typo that shipped.
- **An empty optional field means "not filled in."** The validator skips `format` and `enum` checks on it, and the render layer omits whatever it would have produced.
- **Authors hand-type image URLs.** The images are hosted externally and a serverless tool has nowhere to upload to.

## Migrating the sample campaign

`content/weekly.json` is a real campaign from the old Django app. Its snippets map as:

| Snippet name (old) | `blockType` |
|---|---|
| `component - content feature header` | `content_feature_header` |
| `component - button` | `button` |
| `component - large divider` | `divider` |
| `component - discount header` | *(no equivalent)* |
| `component - spacer` | *(no equivalent)* |

Field renames: `preheader` → `heading`, `color` → `variant`.

What migration loses:

- **Two instances have nowhere to go** — the discount header and the spacer, whose block types do not exist.
- **`bg_image` held real CloudFront URLs** and now comes from the theme. That is a capability change, not a relocation: a theme styles a block *type*, so every instance shares one background where each could previously differ. If per-campaign backgrounds matter, the answer is a theme per campaign.
- **Legacy `body` values are raw HTML** (`"<p>THIS IS THE BEST I CAN DO</p>..."`). Since markdown fields escape HTML, these need converting to markdown as a one-off before an old campaign can round-trip.

Everything else dropped was either styling (`bg_color`, `bg_position`, `padding`, `width`) or empty in the source (`icon_image`, `icon_link`).

## Limitations

- **No arrays.** The schema layer is flat scalars, so a block cannot hold a list, and a fourteen-article digest is fourteen blocks. This is the limitation most likely to matter, given the newspaper-style content the library is aimed at. A repeating-list block would need arrays of objects in the schema, the form renderer and the validator.
- **Conditional requirements are not expressible.** `dependentRequired` would say an image's alt text and dimensions matter only when the image is filled, but the validator subset is `required` / `type` / `enum` / `format`. It does not bite today, since the image fields are required outright — it will the moment one becomes optional.
- **`paragraph`, `date` and `float` are declared but unused.** `text`, `markdown` and `integer` are exercised.

## Status

All five schemas exist in `../blocks/` and validate against the conventions above. Nothing reads them yet, so this stays in `specs/` rather than `../completed/`; it moves once the render layer can consume them, which is also when the theme work may reshape the set again.
