---
name: campaign-setup
description: Create a private campaign repo (campaigns/, iterable/fields.md, iterable/facets.json, out/) from this plugin's starter template, with an example email. Use when the person wants to start making emails and has no campaign repo yet, or asks how to set one up.
---

# Setting up a campaign repo

Email documents and audience definitions live in a **private** repo of the person's own. Never put real campaign content in the public tool repo (`infoentropy/emails`): it's published on GitHub Pages.

The starter files are in this skill's `template/` directory: `campaigns/` (one example email), `iterable/fields.md`, `iterable/facets.json`, `out/`, a `.gitignore`, a `CLAUDE.md`, a `.claude/settings.json` that enables this plugin, and a README.

## Steps

1. **Ask where** the repo should go (a new empty directory), and confirm before creating or overwriting anything.
2. **Copy the template**, hidden files included:

   ```sh
   cp -R "<this skill's base directory>/template/." <target>/
   ```

3. **Initialise git** there (`git init -b main`) if it isn't a repo yet. If the person wants it on GitHub, it must be **private** (`gh repo create <name> --private --source=. --push`). Don't push without asking.
4. **Check the example** works:

   ```sh
   node "${CLAUDE_PLUGIN_ROOT}/render/check.js" campaigns/2026-10-sleep-stories.json
   ```

   (`${CLAUDE_PLUGIN_ROOT}` is this plugin's root; if it isn't filled in, it's two directories up from this skill's base directory.) `[]` means good.
5. **Tell the person what's theirs to do:**
   - Rewrite `iterable/fields.md` for their Iterable project: the user fields that exist and how their values are coded. The example rows are made up, and everything about audiences depends on this file being right. Don't write it for them from guesses.
   - Empty or trim `iterable/facets.json`: the example facets use the example fields. Facets get added as audiences are settled.
   - Delete `campaigns/2026-10-sleep-stories.json` once they've tried it, or keep it as a reference.
   - Open the editor at <https://infoentropy.github.io/emails/authoring/> (Chrome or Edge) and use *Open file* on a campaign to see it.

Then drafting starts with the `email-document` skill.
