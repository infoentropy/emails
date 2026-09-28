# Editing email documents: guide for agents

Everything an agent needs to draft or change an email document. You don't need the specs or `blocks.md`.

**The rule: work on the JSON, get feedback from `check`, leave visual judgement to the person.** Don't read rendered HTML (it's large and says little that `check` doesn't). A person watches the live preview in the editor.

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
    { "id": "b2", "blockType": "button", "switch": "s1", "ruleset": "users in US, CA, GB. not a paying subscriber",
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

## Looking at it yourself (rarely)

Only at milestones: after a first draft, or when trying a new theme. Never after routine edits.

```
node render/preview.js campaign.json [--theme sleep] [--as region.us-ca-gb --as subscription.not-paying] > /tmp/preview.html
```

Each `--as` is something the imagined recipient matches: a facet id, a whole settled ruleset, or an unsettled ruleset's exact text. Without `--as`, you see what someone matching no ruleset gets. Take one screenshot of the file with a headless browser, if your environment has one, rather than reading the HTML.
