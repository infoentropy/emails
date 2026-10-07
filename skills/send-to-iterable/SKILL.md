---
name: send-to-iterable
description: Build the sendable HTML for an email document and convert its audience markers into Iterable Handlebars from the approved facets, producing out/<campaign>.iterable.html. Use when the person wants the email's HTML, wants to send or proof it in Iterable, or asks for the Iterable template.
---

# Building the email for Iterable

`${CLAUDE_PLUGIN_ROOT}` below is this plugin's root directory; if it isn't filled in, it's two directories up from this skill's base directory. Run commands from the campaign repo's root.

## 1. Build the HTML

```sh
node "${CLAUDE_PLUGIN_ROOT}/render/email.js" campaigns/<file>.json > out/<campaign>.html
```

This writes the email's HTML with every hidden block left out and each audience wrapped in `<!--audience …-->` markers. It never contains a sending platform's syntax. Like `check`, it stops on errors; fix them with the `email-document` skill.

If the email has no audiences, there are no markers, and `out/<campaign>.html` is ready to paste.

## 2. Convert markers for Iterable

`email.js` output has neutral markers; Iterable needs Handlebars. Convert them yourself, from `iterable/facets.json`. This is the only place Iterable syntax is written.

A facet's `condition` is one Iterable block-helper test, plus an optional negation:

```json
{ "test": "ifEq subscriptionStatus \"paying\"", "negate": true }
```

**Stop** if any marker's ruleset isn't settled, or names a facet that's missing from `facets.json` or not approved: settle it first with the `settle-audiences` skill. Otherwise, for each chain `<!--audience if="A"--> X <!--audience elseif="B"--> Y <!--audience else--> Z <!--audience end-->`:

- **One facet**, content *yes*, otherwise *no*: `{{#<test>}}yes{{else}}no{{/<helper>}}`, where `<helper>` is the test's first word. Leave out `{{else}}` when *no* is empty. With `"negate": true`, swap *yes* and *no*.
- **Several facets** (`f1 + f2`): nest them. `f1` wraps `f2`, which wraps the content, and every level gets the same *no*.
- **A chain:** convert `if A` with *yes* = `X` and *no* = the rest of the chain converted the same way (`elseif B` with *yes* = `Y`, *no* = `Z`). A chain without `else` ends with an empty *no*. So the fallback is repeated once per test, which is fine for small groups.

Worked example, from the example campaign in the `campaign-setup` skill's template: the switch group converts to

```handlebars
{{#ifMatchesRegexStr country "^(US|CA|GB)$"}}
  {{#ifEq subscriptionStatus "paying"}}
    {{#ifEq subscriptionStatus "paying"}}…Open tonight's story…{{else}}…Explore Sleep Stories…{{/ifEq}}
  {{else}}
    …Start your free trial…
  {{/ifEq}}
{{else}}
  {{#ifEq subscriptionStatus "paying"}}…Open tonight's story…{{else}}…Explore Sleep Stories…{{/ifEq}}
{{/ifMatchesRegexStr}}
```

Region fails → the rest of the chain. Region holds but the person pays (`not-paying` is negated) → the rest of the chain. Otherwise → the trial.

Then:
- Save it as `out/<campaign>.iterable.html`. Check that no `<!--audience` is left, and that every `{{#…}}` has its `{{/…}}`.
- Don't touch anything else: content is already escaped (`{` is `&#123;`), so the only `{{` in the file are yours.

## 3. Hand it over

- Pushing to Iterable through its API isn't set up yet. Hand the person the `out/…iterable.html` file to paste into Iterable's template editor, and say which facets it uses.
- The first proof send of a new condition confirms Iterable evaluates it as intended; that condition form is still unconfirmed against a real send.
- `out/` is git-ignored; never commit it. Never commit secrets: an Iterable API key, if one is used, comes from the environment (e.g. `ITERABLE_API_KEY`).
