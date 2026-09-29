# Editing email documents: guide for agents

Everything an agent needs to draft or change an email document. You don't need the specs or `blocks.md`.

**The rule: work on the JSON, get feedback from `check`, leave visual judgement to the person.** Don't read rendered HTML (it's large and says little that `check` doesn't). A person watches the live preview in the editor.

## Where things live

Email content lives in a **private campaign repo**, never in this public one. Its layout (a starter copy is in `campaign-repo-template/`):

```
campaigns/<date>-<slug>.json   one document per email
iterable/fields.md             the Iterable user fields (a person writes it)
iterable/facets.json           approved facets (you add to it only with the person's approval)
out/                           built HTML (git-ignored)
```

This repo (the tool) is cloned next to it, as `../emails`. The commands below are written from this repo's root; from the campaign repo, prefix them with `../emails/` (`node ../emails/render/check.js campaigns/….json`).

## The document

```json
{
  "version": 1,
  "name": "Sleep Stories — weekly",
  "subject": "Three new Sleep Stories for this week",
  "preheader": "Narrated by voices you'll actually drift off to",
  "theme": "sleep",
  "nextId": 4,
  "blocks": [
    { "id": "b1", "blockType": "content_feature_header", "data": { "heading": "New This Week", "feature_type": "sleep" } },
    { "id": "b2", "blockType": "button", "switch": "s1", "ruleset": "region.us-ca-gb + subscription.not-paying",
      "data": { "text": "Start your free trial", "link": "https://www.calm.com/trial" } },
    { "id": "b3", "blockType": "button", "switch": "s1", "data": { "text": "Open tonight's story", "link": "https://www.calm.com/sleep" } }
  ]
}
```

- `name` is internal. `subject` and `preheader` are what the inbox shows. There's one preheader, here, never in a block.
- `theme` is a theme name: `spring` (the default when missing) or `sleep`. It's the only thing to change to restyle the whole email.
- `blocks` is in send order.

## Blocks

Each block's fields are defined by its schema, `blocks/<blockType>.json`. Read only the schemas for the types you use. Required fields are listed in `required`, and `enum` lists allowed values.

| `blockType` | Fields (`*` required) |
|---|---|
| `content_feature_header` | `heading*`, `feature_type*` (`meditate` \| `sleep`) |
| `article` | `headline*`, `link*`, `image*`, `image_alt*`, `image_width*`, `image_height*`, `variant` (`primary` = the lead story, `secondary` = regular; default `secondary`) |
| `image_with_text` | `heading*`, `body` (plain text; blank line = new paragraph), `image*`, `image_alt*`, `image_width*`, `image_height*` |
| `button` | `text*`, `link*`, `variant` (`primary` \| `secondary`; default `primary`) |
| `divider` | `variant` (`primary` \| `secondary`; default `primary`) |

- **Content only.** Never add colours, sizes, spacing or layout to `data`; the theme decides all of that. Image width and height (pixels, whole numbers) are the one exception.
- Links and image URLs must start with `https://` (or `http://`).
- Don't invent block types or fields. If the copy needs something no block can hold, say so.

## Block ids

- Refer to blocks by id (`b7`). The editor shows ids, so the person sees the same ones.
- **New block:** its id is `"b" + nextId`, then increase `nextId` by one. Never reuse an id, even one that was deleted.

## Audiences: `hidden`, `ruleset`, `switch`

- `"hidden": true`: the block stays in the document but is never sent. Use it for a block the copy has nothing for yet.
- `"ruleset": "…"`: free text, in the copy's own words, saying who sees the block ("US only", "paying subscribers"). Copy it across as written; don't turn it into code. No `ruleset` means everyone.
  Once settled with the person, a ruleset becomes facet ids joined with ` + ` (`region.us-ca-gb + subscription.not-paying`). Don't settle one or invent facets on your own; `check` warns about unsettled rulesets (`ruleset_unsettled`), which is normal while drafting.
- **Switch group:** adjacent blocks with the same `"switch"` value (`s1`, `s2`, …). Each recipient sees the first case whose ruleset matches. A last case without a `ruleset` is the fallback for everyone else. Keep a group's blocks next to each other.

## Making a change

1. Edit only what was asked for. Change fields in place; don't rewrite or reorder the rest of the document. Keep its 2-space indentation.
2. Run the check:

   ```
   node render/check.js campaign.json
   ```

   It prints a JSON list and exits 1 if any issue is an `error`. `[]` means good. Each issue names the place to fix:

   ```json
   { "severity": "error", "block": "b7", "field": "image_alt", "code": "required", "message": "Image alt text is required." }
   ```

   Fix errors. Mention warnings to the person rather than working around them (`variant_unstyled` is the theme's gap, not the document's).
3. Hand back, saying which blocks changed, by id. If the person has the file open in the editor (Chrome or Edge), your change is already on their screen: the editor reloads the file within a couple of seconds. Otherwise they open it with *Open file*.

The person may also be editing the same file in the editor, which saves every change straight to it. So **read the file again before each change** rather than relying on an earlier read, and write it in one go. A half-written file is harmless: the editor waits until it parses.

Hidden blocks aren't checked, so an empty hidden block is fine.

## The HTML for sending

```
node render/email.js campaign.json > /tmp/email.html
```

This writes the email's HTML with every hidden block left out and each audience wrapped in `<!--audience …-->` markers. It never contains a sending platform's syntax; converting the markers is a separate step when pushing. Like `check`, it stops on errors.

## Settling rulesets (with the person)

Before an email with audiences is sent, every free-text ruleset is settled into facets from `iterable/facets.json`. This is a conversation: you propose, the person decides. For each ruleset `check` reports as `ruleset_unsettled`:

1. **Decompose** it by category (`region`, `subscription`, `behavior`, …). "US/Canada/UK folks who haven't paid yet" is region + subscription.
2. **Match** each part to an existing facet **by meaning**, using its `description` and `examples`, and ask: "region → `region.us-ca-gb` (country is US, CA or UK)?"
3. **Propose a new facet** only when none fits. Give it an id (`category.name`, lower case, hyphens), a `description`, the `fields` it uses and a `condition` (see **Converting markers** for the form). Use only fields described in `iterable/fields.md`, and ask about anything ambiguous ("does 'haven't paid' include lapsed users?"). Point out any existing facet that's close before adding one.
4. When the person confirms: rewrite the block's `ruleset` to the settled form (facet ids joined with ` + `, at most one per category, in `facets.json`'s category order), add new facets with `"approved": "<today>"`, and add the original wording to the matched facet's `examples`.

Also:
- **Never settle, add or approve a facet without the person.** A facet without `approved` can't be used.
- **Changing an approved facet** affects every campaign that uses it. List them first (search `campaigns/` for the facet id), and get approval for the change.
- **When `fields.md` changes**, re-check the facets whose `fields` include the changed field.
- An **or** across categories ("US, or paying anywhere") isn't one ruleset: suggest a switch group or two blocks.

## Converting markers for Iterable (when sending)

`email.js` output has neutral markers; Iterable needs Handlebars. Convert them yourself, from `iterable/facets.json`. This is the only place Iterable syntax is written.

A facet's `condition` is one Iterable block-helper test, plus an optional negation:

```json
{ "test": "ifEq subscriptionStatus \"paying\"", "negate": true }
```

**Stop** if any marker's ruleset isn't settled, or names a facet that's missing from `facets.json` or not approved. Otherwise, for each chain `<!--audience if="A"--> X <!--audience elseif="B"--> Y <!--audience else--> Z <!--audience end-->`:

- **One facet**, content *yes*, otherwise *no*: `{{#<test>}}yes{{else}}no{{/<helper>}}`, where `<helper>` is the test's first word. Leave out `{{else}}` when *no* is empty. With `"negate": true`, swap *yes* and *no*.
- **Several facets** (`f1 + f2`): nest them. `f1` wraps `f2`, which wraps the content, and every level gets the same *no*.
- **A chain:** convert `if A` with *yes* = `X` and *no* = the rest of the chain converted the same way (`elseif B` with *yes* = `Y`, *no* = `Z`). A chain without `else` ends with an empty *no*. So the fallback is repeated once per test, which is fine for small groups.

Worked example, from `campaign-repo-template/`: the switch group converts to

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
- Tell the person which facets it used. The first proof send of a new condition confirms Iterable evaluates it as intended; that condition form is still unconfirmed against a real send.

## Looking at it yourself (rarely)

Only at milestones: after a first draft, or when trying a new theme. Never after routine edits.

```
node render/preview.js campaign.json [--theme sleep] [--as region.us-ca-gb --as subscription.not-paying] > /tmp/preview.html
```

Each `--as` is something the imagined recipient matches: a facet id, a whole settled ruleset, or an unsettled ruleset's exact text. Without `--as`, you see what someone matching no ruleset gets. Take one screenshot of the file with a headless browser, if your environment has one, rather than reading the HTML.
