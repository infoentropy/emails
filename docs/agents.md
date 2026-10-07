# Guide for agents

The procedures agents follow live in this repo's Claude plugin, as skills. Each one is self-contained: you don't need the specs or `blocks.md`.

| Skill | For |
|---|---|
| [`email-document`](../skills/email-document/SKILL.md) | Drafting and editing email documents: the format, the blocks, ids, `hidden`/`ruleset`/`switch`, `check`, the editor, previews. |
| [`settle-audiences`](../skills/settle-audiences/SKILL.md) | Settling free-text rulesets into approved facets, with the person. |
| [`send-to-iterable`](../skills/send-to-iterable/SKILL.md) | Building the HTML for sending and converting audience markers into Iterable Handlebars. |
| [`campaign-setup`](../skills/campaign-setup/SKILL.md) | Creating a private campaign repo from the starter template. |

With the plugin installed (`/plugin marketplace add infoentropy/emails`, then `/plugin install emails@infoentropy`), Claude loads these when they apply. Without it, read the skill file directly, and read `${CLAUDE_PLUGIN_ROOT}` in its commands as the root of this repo.
