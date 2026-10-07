# CLAUDE.md

This is a **private campaign repo**: email documents and audience definitions for the email tool in [`infoentropy/emails`](https://github.com/infoentropy/emails). The tool comes as the `emails` Claude plugin, which `.claude/settings.json` enables for this repo. Its skills hold the procedures:

- `email-document`: drafting and editing documents in `campaigns/`, and `check`.
- `settle-audiences`: turning free-text rulesets into approved facets.
- `send-to-iterable`: building the HTML and converting audience markers for Iterable.

Use them rather than working from memory. If the plugin isn't available, ask the person to install it (`/plugin marketplace add infoentropy/emails`, then `/plugin install emails@infoentropy`).

## Layout

- `campaigns/*.json`: one email document each. The person may have one open in the editor (file sync), so re-read a file before each change and write it in one go.
- `iterable/fields.md`: the Iterable user fields. A person writes it. Write facet conditions only from what it says, and ask when it doesn't say.
- `iterable/facets.json`: the approved facet library. Change it only with the person's explicit approval, following the `settle-audiences` skill.
- `out/`: built HTML. It's git-ignored; never commit it.

## Rules

- Never commit secrets. An Iterable API key, if one is used, comes from the environment (e.g. `ITERABLE_API_KEY`).
- Never settle a ruleset, add a facet or approve one without the person.
- Iterable syntax is written only when converting markers into `out/<name>.iterable.html`, never into documents.
- Pushing to Iterable through its API isn't set up yet. Hand the person the `out/…iterable.html` file to paste into Iterable, and say which facets it uses.
