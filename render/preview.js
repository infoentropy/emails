#!/usr/bin/env node
// node render/preview.js campaign.json [--theme NAME] [--as FACET_OR_RULESET]... > preview.html
// Writes the same HTML as the editor's preview pane, for someone who matches every --as:
// a facet id (region.us-ca-gb), a whole settled ruleset, or an unsettled ruleset's text.
import { readFileSync } from "node:fs";
import { loadSchemas } from "./registry.js";
import { renderPreview } from "./render.js";

const args = process.argv.slice(2), as = [];
let theme, file;
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--theme") theme = args[++i];
  else if (args[i] === "--as") as.push(args[++i]);
  else file = args[i];
}
if (!file) { console.error('usage: node render/preview.js campaign.json [--theme NAME] [--as FACET_OR_RULESET]...'); process.exit(2); }

let doc;
try { doc = JSON.parse(readFileSync(file, "utf8")); }
catch (e) { console.error(`Can't read ${file}: ${e.message}`); process.exit(2); }

const schemas = await loadSchemas(url => JSON.parse(readFileSync(url, "utf8")));
process.stdout.write(renderPreview(doc, { schemas, theme, as }));
