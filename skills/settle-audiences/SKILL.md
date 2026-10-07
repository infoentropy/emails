---
name: settle-audiences
description: Settle an email document's free-text audience rulesets ("US folks who haven't paid") into approved, reusable facets from iterable/facets.json, with the person confirming each one. Use when check reports ruleset_unsettled, before sending an email with audiences, or when adding or changing a facet.
---

# Settling rulesets into facets (with the person)

Before an email with audiences is sent, every free-text ruleset is settled into facets from `iterable/facets.json` in the campaign repo. This is a conversation: you propose, the person decides.

`${CLAUDE_PLUGIN_ROOT}` below is this plugin's root directory; if it isn't filled in, it's two directories up from this skill's base directory. Run commands from the campaign repo's root. For the document format itself, see the `email-document` skill.

Find what needs settling:

```sh
node "${CLAUDE_PLUGIN_ROOT}/render/check.js" campaigns/<file>.json
```

For each ruleset it reports as `ruleset_unsettled`:

1. **Decompose** it by category (`region`, `subscription`, `behavior`, …). "US/Canada/UK folks who haven't paid yet" is region + subscription.
2. **Match** each part to an existing facet **by meaning**, using its `description` and `examples`, and ask: "region → `region.us-ca-gb` (country is US, CA or UK)?"
3. **Propose a new facet** only when none fits. Give it an id (`category.name`, lower case, hyphens), a `description`, the `fields` it uses and a `condition` (below). Use only fields described in `iterable/fields.md`, and ask about anything ambiguous ("does 'haven't paid' include lapsed users?"). Point out any existing facet that's close before adding one.
4. When the person confirms: rewrite the block's `ruleset` to the settled form (facet ids joined with ` + `, at most one per category, in `facets.json`'s category order), add new facets with `"approved": "<today>"`, and add the original wording to the matched facet's `examples`.

Re-read the document before writing it (the person may have it open in the editor), and run `check` again afterwards.

## A facet's condition

One Iterable block-helper test, plus an optional negation:

```json
{ "test": "ifEq subscriptionStatus \"paying\"", "negate": true }
```

The `send-to-iterable` skill turns these into Handlebars.

## Rules

- **Never settle, add or approve a facet without the person.** A facet without `approved` can't be used.
- **Changing an approved facet** affects every campaign that uses it. List them first (search `campaigns/` for the facet id), and get approval for the change.
- **When `fields.md` changes**, re-check the facets whose `fields` include the changed field.
- An **or** across categories ("US, or paying anywhere") isn't one ruleset: suggest a switch group or two blocks.
