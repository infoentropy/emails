#!/usr/bin/env node
// node render/email.js campaign.json [--theme NAME] > email.html
// Writes the email's HTML for sending, with audiences as <!--audience …--> markers (see docs/agents.md).
// If the document has errors, prints check()'s issues as JSON to stderr and exits 1.
import { readFileSync } from "node:fs";
import { loadSchemas } from "./registry.js";
import { renderHtml } from "./render.js";

const args = process.argv.slice(2);
const opt = name => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : undefined; };
const theme = opt("--theme");
const [file] = args;
if (!file) { console.error("usage: node render/email.js campaign.json [--theme NAME] > email.html"); process.exit(2); }

let doc;
try { doc = JSON.parse(readFileSync(file, "utf8")); }
catch (e) { console.error(`Can't read ${file}: ${e.message}`); process.exit(2); }

const schemas = await loadSchemas(url => JSON.parse(readFileSync(url, "utf8")));
try {
  process.stdout.write(renderHtml(doc, { schemas, theme }));
} catch (e) {
  if (!e.issues) throw e;
  console.error(JSON.stringify(e.issues, null, 2));
  process.exit(1);
}
