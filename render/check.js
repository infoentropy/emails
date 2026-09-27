#!/usr/bin/env node
// node render/check.js campaign.json [--theme NAME]
// Prints check()'s issues as JSON ([] means good). Exits 1 if any are errors, 2 if the file can't be read.
import { readFileSync } from "node:fs";
import { loadSchemas } from "./registry.js";
import { check } from "./render.js";

const args = process.argv.slice(2);
const opt = name => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : undefined; };
const theme = opt("--theme");
const [file] = args;
if (!file) { console.error("usage: node render/check.js campaign.json [--theme NAME]"); process.exit(2); }

let doc;
try { doc = JSON.parse(readFileSync(file, "utf8")); }
catch (e) { console.error(`Can't read ${file}: ${e.message}`); process.exit(2); }

const schemas = await loadSchemas(url => JSON.parse(readFileSync(url, "utf8")));
const issues = check(doc, { schemas, theme });
console.log(JSON.stringify(issues, null, 2));
process.exit(issues.some(i => i.severity === "error") ? 1 : 0);
