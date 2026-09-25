# Block segmentation

Show or hide a block depending on who receives the email, e.g. "show this block only in the US". This generalises the block-level `hidden` flag proposed in `claude-authoring-plugin.md`: `hidden` is an unconditional off switch, and segmentation makes visibility depend on the recipient.

## Shape

Keep `hidden` as it is: the author's manual off switch, which always wins. Add a separate optional block-level `ruleset`, next to `id`, `blockType` and `hidden` and outside `data`, for the same reason as `hidden`: it's about when the block is shown, not what the block contains. Every block type gets it without a schema change. With no `ruleset`, the block goes to everyone.

**`ruleset` is a plain-language note, not a grammar.** The author writes the conditions the way they'd say them, and an AI turns them into the sending platform's conditional code later:

```json
{
  "id": "b4",
  "blockType": "button",
  "ruleset": "users in US, CA, GB. subscription paying user",
  "data": { … }
}
```

A note can hold several conditions ("in US, CA or GB" *and* "is a paying subscriber"). The name is deliberately general: it isn't limited to geography or to one kind of audience.

**The document and the tools know nothing about personalization attributes.** Country, subscription status and every other attribute exist only in the sending environment. Their names, where they live and how their values are coded (`lead.subscription_status = 'paying'`? `user.plan == "paid"`? a list membership?) depend on that user's platform and setup, and can't be assumed generically. So nothing in this repo lists or validates attributes. Working that out is the translation step's job.

The note alone doesn't say exactly what will happen. Its meaning only becomes fixed once it's translated, so the translation step below is where review has to happen.

## Switch groups: one of several blocks

Separate rulesets can overlap. With one block for "users in US" and another for "paying users", a paying US user gets both. And there's no clean way to say "everyone else": a fallback block's ruleset would have to restate the negation of all the others, and it goes wrong as soon as a case is added. A **switch group** handles both problems.

Blocks stay a flat list. One more optional block-level field, `switch`, names a group:

```json
"blocks": [
  { "id": "b3", "blockType": "button", "switch": "cta", "ruleset": "users in US",
    "data": { "text": "Shop US deals" } },
  { "id": "b4", "blockType": "button", "switch": "cta", "ruleset": "users in GB",
    "data": { "text": "Shop UK deals" } },
  { "id": "b5", "blockType": "button", "switch": "cta",
    "data": { "text": "Shop now" } }
]
```

- Blocks sharing a `switch` value form one group. Cases are checked **in document order and the first match wins**, so at most one block in the group is shown.
- The block in the group with **no `ruleset` is the default**. There's at most one default. A group with none shows nothing when no case matches.
- The group renders as a single if / else-if / else chain in the flavor's syntax, which Iterable supports natively:

  ```handlebars
  {{#if condition1}}
    …b3…
  {{else if condition2}}
    …b4…
  {{else}}
    …b5…
  {{/if}}
  ```

  A group with no default omits the `{{else}}` branch.
- There's no `switch(variable)`. Each case keeps its own free-text ruleset for the AI to translate, so cases don't have to test the same attribute ("users in US" and "paying users" can be cases in one group). The group only adds ordering and the fallback.
- `hidden` on a case drops just that case from the chain. If the default is hidden, the group has no default.
- Blocks in a group don't have to share a `blockType`: a US `image_with_text` can fall back to a generic `article`.

Rules the tools enforce:

- **Group members must be adjacent**, since the whole chain renders in one place. A split group is a validation error in the authoring tool and a hard error in the render layer.
- **Authoring tool:** shows a group as one bracketed unit with its cases in order and the default last, so reordering can't split it. Case order matters and should be visible.
- The `switch` value is only a label that ties blocks together. It needs to be unique within the document, and nothing more.

The flat shape was chosen over a nested container block (`{"blockType": "switch", "cases": [{"ruleset": …, "blocks": [...]}]}`). That shape states the structure more directly, but every tool so far assumes a flat block list, and nesting would ripple through the editor, validation and rendering.

A related but separate case is when only the copy varies between cases (the button text above) and not the block. A per-field switch inside `data` might be simpler for authors there. Not designed yet.

## Evaluation: one file, conditionals in the ESP's language

**Decided:** the render layer produces **one HTML file** in which each block with a `ruleset` is wrapped in the sending platform's own conditional syntax. The platform then decides per recipient at send time. Blocks without a `ruleset` are emitted bare.

Which syntax to produce is an **output flavor**, a render-layer configuration option (see `../specs/render-layer-tool.md`, **Output flavors**). **Iterable** (Iterable's Handlebars dialect) is the first flavor; SendGrid, whose Handlebars dialect differs, is expected to follow as its own flavor. The document itself never names a platform: the same ruleset is translated for whichever flavor is selected.

## Translation: ruleset → conditional

An AI reads each ruleset, splits it into its conditions, and works out what each one means **in this user's environment**. For example, "users in US, CA, GB" might map to a country field and "subscription paying user" to something like `lead.subscription_status = 'paying'`. It then writes the combined condition in the flavor's syntax. Its inputs are:

- the ruleset text,
- the output flavor, plus a reference for that flavor's conditional syntax and helpers (confirm Iterable's exact helper set against Iterable's docs),
- **environment context**: whatever describes the user's actual attributes: field names, paths and value coding. This is supplied per environment (a config file, a sample user profile, the platform's schema, or the user answering questions) and never baked into these tools. The AI must never invent a field: if it can't find where "paying subscriber" lives, it asks.

The review step shows how the AI read the note as well as the code. For example: "US **or** CA **or** GB, **and** subscription status is paying → `…`". Implicit logic like the full stop between the two conditions above is exactly where a misreading would hide.

Keep the AI out of the render script itself:

1. **Translate step (AI):** produces a translations file, one entry per distinct ruleset per environment and flavor: ruleset text → condition. In the plugin, this is Claude inside Skill C.
2. **Review:** the user sees each ruleset, the AI's reading of it and the generated condition, and approves or corrects it. This takes the place of the preview-as-segment switch, which can't work in the editor any more because the editor has no way to evaluate free text.
3. **Render step (script):** stays deterministic. It takes the document plus the approved translations and wraps blocks accordingly. A ruleset with no approved translation is a **hard error**, never an unwrapped block, since sending a US-only block to everyone isn't a safe fallback.

Translations are **cached** by (ruleset text, environment, flavor). Re-rendering after a copy fix then reuses the approved conditions instead of re-asking the AI and possibly getting a different answer. Editing a ruleset's text invalidates only that entry.

A condition the AI can't map to a real attribute ("our best customers", "people who liked the last email") must come back as a question to the user, not as a guess.

**Escaping is part of each flavor.** Once the output is a Handlebars template, any `{{` in authored copy would be read as a tag at send time. Each flavor must escape its own syntax in rendered content, the same way markdown rendering already escapes raw HTML. This doesn't apply to the generated conditions themselves, which are meant to be live.

## Tool touchpoints

- **Authoring tool:** a per-block free-text "ruleset" field, with blocks that have one visibly badged, plus switch groups as described above. No validation of ruleset text beyond "is it text".
- **Render layer:** consumes approved translations as described above. Its Python script never calls an AI.
- **Plugin:** Skill A copies notes like "US only" or "paying subscribers only" from the copy doc straight into `ruleset`; since rulesets are free text, no interpretation is needed at this stage. Skill C runs the translate-and-review step before rendering.

## Open questions

- Where does the translations file live: next to the document, or inside it? Inside keeps it with the email but puts platform-specific code into a document that's meant to be platform-neutral.
- What form does the environment context take: a hand-written notes file per environment, a sample user profile, or pulled from the platform (e.g. Iterable's API)? Whatever it is, it belongs to the user's environment, not to this repo.
- Outside the plugin, who runs the translate step? For example, a small script that calls the Claude API, run before the render script.
- An email where every block is excluded for some segment can't be detected at render time. Should the review step flag rulesets that together leave some audience with nothing?
