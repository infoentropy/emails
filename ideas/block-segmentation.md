# Block segmentation

Show or hide a block depending on who receives the email, e.g. "show this block only in the US". This generalises the block-level `hidden` flag proposed in `claude-authoring-plugin.md`: `hidden` is an unconditional off switch, and segmentation makes visibility depend on the recipient.

## Shape

Keep `hidden` as it is: the author's manual off switch, which always wins. Add a separate optional block-level `audience`, next to `id`, `blockType` and `hidden` and outside `data`, for the same reason as `hidden`: it's about who sees the block, not what the block contains. Every block type gets it without a schema change. With no `audience`, the block goes to everyone.

**`audience` is a plain-language annotation, not a grammar.** The author writes who the block is for, and an AI turns that into the sending platform's conditional code later:

```json
{
  "id": "b4",
  "blockType": "button",
  "audience": "US only",
  "data": { … }
}
```

No rule vocabulary needs defining or growing: "US and Canada", "everyone except the EU" or "Spanish-speaking subscribers" all work without a format change. The cost is that the annotation alone doesn't say exactly what will happen. That meaning only becomes fixed once it's translated, so the translation step below is where review has to happen.

## Evaluation: one file, conditionals in the ESP's language

**Decided:** the render layer produces **one HTML file** in which each block with an `audience` is wrapped in the sending platform's own conditional syntax. The platform then decides per recipient at send time. Blocks without an `audience` are emitted bare.

Which syntax to produce is an **output flavor**, a render-layer configuration option (see `../specs/render-layer-tool.md`, **Output flavors**). **Iterable** (Iterable's Handlebars dialect) is the first flavor; SendGrid, whose Handlebars dialect differs, is expected to follow as its own flavor. The document itself never names a platform: the same annotation is translated for whichever flavor is selected.

## Translation: annotation → conditional

An AI reads each annotation and writes the flavor's condition, e.g. "US and Canada" might become `{{#if (or (eq country "US") (eq country "CA"))}}` for Iterable. (Confirm the exact helper set against Iterable's docs.) Its inputs are:

- the annotation text,
- the output flavor, plus a reference for that flavor's conditional syntax and helpers,
- the **recipient fields the platform actually has** (for Iterable, the user profile fields, e.g. `country` or `address.country`), and how their values are coded (ISO country codes or not). This replaces a hand-written field mapping, but the AI still needs the real field list. It must never invent a field.

Keep the AI out of the render script itself:

1. **Translate step (AI):** produces a translations file, one entry per distinct annotation per flavor: `"US only"` → condition. In the plugin, this is Claude inside Skill C.
2. **Review:** the user sees each annotation next to its generated condition and approves or corrects it. This takes the place of the preview-as-segment switch, which can't work in the editor any more because the editor has no way to evaluate free text.
3. **Render step (script):** stays deterministic. It takes the document plus the approved translations and wraps blocks accordingly. An annotation with no translation is a **hard error**, never an unwrapped block, since sending a US-only block to everyone isn't a safe fallback.

Translations are **cached** by (annotation text, flavor). Re-rendering after a copy fix then reuses the approved conditions instead of re-asking the AI and possibly getting a different answer. Editing an annotation's text invalidates only that entry.

An annotation the AI can't map to a real field ("our best customers", "people who liked the last email") must come back as a question to the user, not as a guess.

**Escaping is part of each flavor.** Once the output is a Handlebars template, any `{{` in authored copy would be read as a tag at send time. Each flavor must escape its own syntax in rendered content, the same way markdown rendering already escapes raw HTML. This doesn't apply to the generated conditions themselves, which are meant to be live.

## Tool touchpoints

- **Authoring tool:** a per-block free-text "audience" field, with annotated blocks visibly badged. No validation beyond "is it text".
- **Render layer:** consumes approved translations as described above. Its Python script never calls an AI.
- **Plugin:** Skill A copies notes like "US only" or "EU version:" from the copy doc straight into `audience`; since annotations are free text, no interpretation is needed at this stage. Skill C runs the translate-and-review step before rendering.

## Open questions

- Where does the translations file live: next to the document, or inside it? Inside keeps it with the email but puts platform-specific code into a document that's meant to be platform-neutral.
- Where does the list of recipient fields come from: a hand-maintained file per flavor, or pulled from the platform (e.g. Iterable's API)?
- Outside the plugin, who runs the translate step? For example, a small script that calls the Claude API, run before the render script.
- An email where every block is excluded for some segment can't be detected at render time. Should the review step flag annotations that together leave some audience with nothing?
