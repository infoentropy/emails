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

## The big question: where is the rule evaluated?

The render layer is a static script that has no idea who the recipient is. There are two options:

1. **Render one HTML file per segment.** The render layer takes a segment (e.g. `country=US`) and drops the blocks whose rule doesn't match. This is simple and ESP-agnostic, and each output is plain HTML. However, the number of outputs grows with the number of segments, and the ESP has to be set up to send each file to the right list.
2. **Emit conditionals in the ESP's personalisation language** (Liquid, AMPscript, Handlebars, merge tags…). One HTML file is produced, and the ESP decides per recipient at send time. This scales, but it ties the render layer to a specific ESP (or needs one adapter per ESP), and the ESP's field names (`country` vs `Country` vs `geo.country_code`) have to be mapped in config.

Which ESP(s) will actually send these emails decides this. Option 1 works everywhere and could come first, with option 2 added as an adapter once the ESP is known.

## Tool touchpoints

- **Authoring tool:** a per-block "audience" control, with blocks that have a rule visibly badged. A **preview-as-segment** switch ("view as: US / non-US / everyone") is probably what makes this usable, because otherwise an author can't see what any given recipient actually gets.
- **Render layer:** option 1 and/or 2 above. An unknown dimension or operator should be a hard error, since guessing wrong about who sees a block isn't a safe fallback.
- **Plugin, Skill A:** copy docs often carry notes like "US only" or "EU version:". Skill A could turn those into rules instead of leaving the author to add them in the editor.

## Open questions

- Which ESP, and does it support conditional content? This decides option 1 vs 2.
- Are country codes ISO 3166-1 alpha-2, and does the ESP use the same codes?
- Does anything beyond geo come up soon enough to design for now?
- Is an email where every block is excluded for some segment an error, a warning, or allowed?
