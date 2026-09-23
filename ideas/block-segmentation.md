# Block segmentation

Show or hide a block depending on who receives the email, e.g. "show this block only in the US". This generalises the block-level `hidden` flag proposed in `claude-authoring-plugin.md`: `hidden` is an unconditional off switch, and segmentation makes visibility depend on the recipient.

## Shape

Keep `hidden` as it is: the author's manual off switch, which always wins. Add a separate optional block-level rule, next to `id`, `blockType` and `hidden` and outside `data`, for the same reason as `hidden`: it's about who sees the block, not what the block contains. Every block type gets it without a schema change. With no rule, the block goes to everyone.

The rule is **data, not code**: a small fixed vocabulary the authoring tool can show as a form and the render layer can translate. Nobody writes expressions. For example:

```json
{
  "id": "b4",
  "blockType": "button",
  "audience": { "country": { "in": ["US"] } },
  "data": { … }
}
```

Start with the one dimension that's actually needed, country, with `in` and `not_in`. Add dimensions (region, language, subscriber tier…) only as they come up. Widening the vocabulary is additive, so this is the same kind of safe change as widening an `enum` under the schema-evolution rules.

## Evaluation: one file, conditionals in the ESP's language

**Decided:** the render layer produces **one HTML file** in which each block with an `audience` rule is wrapped in the sending platform's own conditional syntax. The platform then decides per recipient at send time. Blocks without a rule are emitted bare.

Which syntax to produce is an **output flavor**, a render-layer configuration option (see `../specs/render-layer-tool.md`, **Output flavors**). **Handlebars** is the first flavor; SendGrid, Marketo and others are added later as further flavors. The document itself never names a platform: the same `audience` rule renders as whatever the selected flavor produces.

Roughly, for `{"country": {"in": ["US", "CA"]}}`:

| Flavor | Shape |
|---|---|
| Handlebars | `{{#if (includes recipient.country "US" "CA")}}…{{/if}}`. Plain Handlebars has no built-in comparison helpers, so the sending side must register them. The flavor config names the helpers to use. |
| SendGrid | Handlebars-based, with its own built-in helpers (`{{#equals}}`, `{{#or}}`…), so it's a separate flavor from plain Handlebars. |
| Marketo | Velocity via email script tokens, not inline tags. It'll need the most design work of the three. |

Each flavor also needs a **field mapping**: the document says `country`, and the flavor config maps it to the recipient field the platform actually has (`recipient.country`, `Country`, `lead.countryCode`…).

**Escaping is part of each flavor.** Once the output is a Handlebars template, any `{{` in authored copy would be read as a tag at send time. Each flavor must escape its own syntax in rendered content, the same way markdown rendering already escapes raw HTML.

## Tool touchpoints

- **Authoring tool:** a per-block "audience" control, with blocks that have a rule visibly badged. A **preview-as-segment** switch ("view as: US / non-US / everyone") is probably what makes this usable, because otherwise an author can't see what any given recipient actually gets.
- **Render layer:** wraps ruled blocks in the selected flavor's conditionals, per the section above. An unknown dimension or operator should be a hard error, since guessing wrong about who sees a block isn't a safe fallback.
- **Plugin, Skill A:** copy docs often carry notes like "US only" or "EU version:". Skill A could turn those into rules instead of leaving the author to add them in the editor.

## Open questions

- Are country codes ISO 3166-1 alpha-2, and does the platform use the same codes?
- Does anything beyond geo come up soon enough to design for now?
- An email where every block is excluded for some segment can't be detected at render time any more, since the render layer doesn't know the segments. Should the render layer warn when every block has a rule, or is that the platform's problem?
- The editor's preview-as-segment switch evaluates rules itself, in JavaScript. It has to match what each flavor's conditionals do at send time.
