# Campaign repo template

A starting point for the **private** repo that holds your campaigns: the email documents, your Iterable fields, and the approved audience facets. The tool (editor, render layer, Claude skills) stays in the public repo, [`infoentropy/emails`](https://github.com/infoentropy/emails), and reaches Claude as the `emails` plugin. Keep content out of that repo: it's public and published on GitHub Pages.

A live copy of this folder is published as the public example repo [`infoentropy/email-campaigns`](https://github.com/infoentropy/email-campaigns) (sample data only, no Iterable keys). Keep the two in step: when this folder changes, copy the change there.

## Set up

**Easiest:** in Claude Code, install the plugin and ask Claude to set up a campaign repo (the `campaign-setup` skill copies this folder for you):

```
/plugin marketplace add infoentropy/emails
/plugin install emails@infoentropy
```

**By hand:** copy the example and push it to a new private repo:

```sh
git clone https://github.com/infoentropy/email-campaigns my-campaigns
cd my-campaigns && rm -rf .git && git init -b main
gh repo create my-campaigns --private --source=. --push
```

(Don't fork the example: a fork of a public repo is public.) `.claude/settings.json` enables the plugin for anyone who opens the repo in Claude Code, so the tool repo doesn't need cloning. Then:

1. **Rewrite `iterable/fields.md`** for your Iterable project: the user fields that exist, and how their values are coded. The example rows are made up. Everything about audiences depends on this file being right.
2. **Empty or trim `iterable/facets.json`.** The example facets use the example fields. Facets get added as you settle audiences with Claude.
3. Delete `campaigns/2026-10-sleep-stories.json` once you've tried it, or keep it as a reference.

Never commit an Iterable API key. Keep it in your environment (e.g. `ITERABLE_API_KEY`).

## Try the example

Ask Claude to check `campaigns/2026-10-sleep-stories.json` and build its HTML. To run the commands yourself, clone [`infoentropy/emails`](https://github.com/infoentropy/emails) anywhere (Node is the only requirement) and, from this repo:

```sh
node <path-to-emails>/render/check.js campaigns/2026-10-sleep-stories.json          # [] = no problems
node <path-to-emails>/render/email.js campaigns/2026-10-sleep-stories.json > out/sleep-stories.html
```

In Chrome or Edge, open the editor at <https://infoentropy.github.io/emails/authoring/> and use **Open file** on `campaigns/2026-10-sleep-stories.json`. The editor stays attached to the file: your edits save to it, and edits Claude makes to it show up within a couple of seconds. Use **Preview as** to see what each audience gets.

## Making an email

1. **Draft.** Ask Claude to turn the copy into a document in `campaigns/`, or build it in the editor. Audiences start as free text in each block's `ruleset` ("US/Canada/UK folks who haven't paid").
2. **Review and tweak** in the editor: the live preview, the themes, and Preview as.
3. **Settle audiences with Claude.** It matches each free-text ruleset to facets in `iterable/facets.json` by meaning, asks you to confirm, and proposes new facets (from `fields.md`) only when none fit. Nothing is settled or approved without you.
4. **Build for Iterable.** Claude runs `email.js`, which gives plain HTML with `<!--audience …-->` markers, and converts the markers into Iterable Handlebars from the approved facets. The result goes in `out/<campaign>.iterable.html`.
5. **Send to Iterable and proof.** Paste the file into Iterable's template editor and send proofs to test users. Pushing through Iterable's API is planned but not set up yet.

The procedures Claude follows are the plugin's skills, in [`skills/`](https://github.com/infoentropy/emails/tree/master/skills) in the tool repo: `email-document`, `settle-audiences` and `send-to-iterable`.
