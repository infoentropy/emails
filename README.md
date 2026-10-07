# emails

A block-based email authoring tool. Emails are JSON documents made of content blocks. The tool previews them live in switchable themes, shows each audience's version, and produces email-safe HTML for your sending platform (Iterable first). People and Claude work on the same documents.

- **The editor:** <https://infoentropy.github.io/emails/authoring/> (use Chrome or Edge to stay attached to a file on disk)
- **The Claude plugin:** this repo is also a Claude plugin marketplace. In Claude Code:
  ```
  /plugin marketplace add infoentropy/emails
  /plugin install emails@infoentropy
  ```
  Its skills: `email-document` (draft and edit), `settle-audiences`, `send-to-iterable`, and `campaign-setup`.
- **Your campaigns** live in a separate **private** repo, never in this one: this repo is public and published on GitHub Pages. Ask Claude to set one up (`campaign-setup`), or start from [`skills/campaign-setup/template/`](skills/campaign-setup/template/); its README walks through setup and a first email. A public, cloneable copy is at [`infoentropy/email-campaigns`](https://github.com/infoentropy/email-campaigns).

## How an email gets made

1. **Draft:** Claude turns the copy into a document, or you build one in the editor.
2. **Review and tweak** in the editor: the live preview, theme switching, and "preview as" for each audience.
3. **Settle audiences:** Claude turns free-text audience notes ("US folks who haven't paid") into approved, reusable facets (`region.us-ca-gb + subscription.not-paying`), with you confirming each one.
4. **Build:** `render/email.js` writes plain HTML with neutral `<!--audience …-->` markers. Claude converts the markers into Iterable Handlebars from the approved facets.
5. **Send:** paste into Iterable and proof. Pushing through Iterable's API is planned.

## What's here

| Path | What it is |
|---|---|
| `.claude-plugin/` | The plugin manifest (`plugin.json`) and the marketplace that lists it (`marketplace.json`). |
| `skills/` | The plugin's skills: the procedures Claude follows. `campaign-setup/template/` is the starter for your private campaign repo: example email, `fields.md`, `facets.json`, and a `CLAUDE.md` and `.claude/settings.json` that enable the plugin there. |
| `authoring/` | The editor: one dependency-free page. |
| `blocks/` | Block schemas: which content fields each block type has. |
| `render/` | The render layer (browser and Node): `check`, the preview, the HTML for sending, block templates and themes. Commands: `check.js`, `preview.js`, `email.js`. |
| `docs/agents.md` | An index of the skills, for agents working without the plugin. |
| `docs/blocks.md` | The developer guide: document format, block library, render layer, adding block types. |
| `specs/`, `completed/`, `ideas/`, `feedback/` | How things were decided (see `CLAUDE.md`, **Project management**). |
| `flipboard/`, `traction/`, `content/` | Older hand-written templates and sample data. |

## Running locally

The editor must be served, not opened as a file:

```sh
python3 -m http.server     # in this repo's root
# then open http://localhost:8000/authoring/
```

Check a document or build its HTML with Node (no install needed):

```sh
node render/check.js path/to/campaign.json            # issues as JSON; [] = good
node render/email.js path/to/campaign.json > out.html  # HTML for sending, audiences as markers
```

There's no build step, package manager or test suite. `render/package.json` only marks `render/` as ES modules for Node.
