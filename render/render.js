// check() and renderPreview(): shared by the editor (browser) and agents (Node). No I/O, no AI.
// Callers load the schemas (registry.loadSchemas) and pass them in.
import { templates, themes, defaultTheme } from "./registry.js";
import { html, raw } from "./html.js";

export { html, raw };

const DEFAULT_DATE_FORMAT = { month: "long", day: "numeric", year: "numeric" };

const sorted = s => Object.entries(s.properties || {}).sort((a, b) => (a[1].weight ?? 0) - (b[1].weight ?? 0));
const isEmpty = v => v === undefined || v === null || String(v).trim() === "";
const switchOf = b => (typeof b.switch === "string" && b.switch !== "" ? b.switch : "");
const ruleOf = b => (typeof b.ruleset === "string" ? b.ruleset.trim() : "");
const dataOf = b => (b.data && typeof b.data === "object" ? b.data : {});

export const themeName = doc => (typeof doc.theme === "string" && doc.theme !== "" ? doc.theme : defaultTheme);

// Adjacent blocks sharing a switch value form one group, checked top to bottom, first match wins.
function units(blocks) {
  const out = [];
  for (const b of blocks) {
    const name = switchOf(b), last = out.at(-1);
    if (name && last?.switch === name) last.cases.push(b);
    else out.push(name ? { switch: name, cases: [b] } : { block: b });
  }
  return out;
}

function formatDate(value, fmt) {
  const d = new Date(value + "T00:00:00Z");
  if (isNaN(d)) return value;
  return new Intl.DateTimeFormat("en-US", { ...(fmt || DEFAULT_DATE_FORMAT), timeZone: "UTC" }).format(d);
}

// Schema fields only, in weight order: empty → default, numeric strings → numbers, dates formatted.
function prepare(block, schema, theme) {
  const src = dataOf(block), d = {};
  for (const [k, f] of sorted(schema)) {
    let v = src[k];
    if (isEmpty(v) && "default" in f) v = f.default;
    if ((f.type === "integer" || f.type === "number") && !isEmpty(v) && !isNaN(Number(v))) v = Number(v);
    if (f.format === "date" && typeof v === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v)) v = formatDate(v, theme.dateFormat);
    d[k] = v;
  }
  return d;
}

// A variant the theme doesn't style renders as primary (and check() warns).
function styleFor(type, d, schema, theme) {
  const byVariant = theme.styles?.[type];
  const wanted = schema.properties?.variant ? d.variant || "primary" : "primary";
  if (byVariant?.[wanted]) return { style: byVariant[wanted], variant: wanted };
  if (byVariant?.primary) return { style: byVariant.primary, variant: "primary", unstyled: wanted };
  return { error: true };
}

function renderBlock(block, schemas, theme, name) {
  const schema = schemas[block.blockType], template = templates[block.blockType];
  if (!schema || !template) throw new Error(`Unknown block type "${block.blockType}".`);
  const d = prepare(block, schema, theme);
  const st = styleFor(block.blockType, d, schema, theme);
  if (st.error) throw new Error(`Theme "${name}" has no styles for ${block.blockType}.`);
  if (schema.properties?.variant) d.variant = st.variant;
  return template(d, st.style, theme);
}

const errorRow = (block, message) => html`
        <tr><td style="padding:8px 24px;"><div style="border:2px dashed #c0392b;border-radius:6px;padding:10px 12px;background:#fff5f4;color:#a93226;font:13px/1.4 Arial, sans-serif;">${block.id} (${block.blockType}): ${message}</div></td></tr>`;

// Plain HTML for the preview pane. `rulesets` are the ruleset texts to treat as true;
// a block with no ruleset always matches, and a hidden block never shows.
export function renderPreview(document, { schemas, theme, rulesets = [] } = {}) {
  const name = theme ?? themeName(document), th = themes[name];
  if (!th) {
    return String(html`<!DOCTYPE html><html><body style="font:15px/1.5 Arial, sans-serif;padding:24px;color:#a93226;">Unknown theme "${name}". Pick a theme to preview this email.</body></html>`);
  }
  const on = new Set(rulesets.map(r => String(r).trim()));
  const matches = b => b.hidden !== true && (!ruleOf(b) || on.has(ruleOf(b)));
  const shown = [];
  for (const u of units(document.blocks || [])) {
    const hit = u.block ? (matches(u.block) ? u.block : null) : u.cases.find(matches);
    if (hit) shown.push(hit);
  }
  const rows = shown.map(b => {
    try { return renderBlock(b, schemas, th, name); }
    catch (e) { return errorRow(b, e.message); }
  });
  return String(th.shell({ subject: document.subject ?? "", preheader: document.preheader ?? "", body: rows.join("") }));
}

function fieldIssues(b, schema, add) {
  const data = dataOf(b), req = new Set(schema.required || []);
  for (const [k, f] of sorted(schema)) {
    const v = data[k], at = { block: b.id, field: k };
    if (isEmpty(v)) {                                   // not filled in: only `required` applies
      if (req.has(k)) add("error", "required", `${f.title} is required.`, at);
      continue;
    }
    const str = String(v).trim();
    if (f.type === "integer" && !/^-?\d+$/.test(str)) add("error", "type", "Must be a whole number.", at);
    else if (f.type === "number" && isNaN(Number(str))) add("error", "type", "Must be a number.", at);
    if (f.enum && !f.enum.includes(v)) add("error", "enum", `Must be one of: ${f.enum.join(", ")}.`, at);
    if (f.format === "uri" && !/^https?:\/\/\S+$/i.test(str)) add("error", "format", "Must start with http:// or https://", at);
    if (f.format === "date" && !/^\d{4}-\d{2}-\d{2}$/.test(str)) add("error", "format", "Must be a date, as YYYY-MM-DD.", at);
  }
}

// Every problem with the document, as [{severity, block, field, code, message}]. Empty means good.
// Errors make the email wrong or unrenderable; warnings are worth a look. Hidden blocks aren't checked.
export function check(document, { schemas, theme } = {}) {
  const issues = [];
  const add = (severity, code, message, at = {}) =>
    issues.push({ severity, block: at.block ?? null, field: at.field ?? null, code, message, ...(at.switch ? { switch: at.switch } : {}) });

  if (!document || typeof document !== "object" || !Array.isArray(document.blocks)) {
    add("error", "not_a_document", "The document has no blocks array.");
    return issues;
  }
  const blocks = document.blocks.filter(b => b && typeof b === "object");

  const name = theme ?? themeName(document), th = themes[name];
  if (!th) add("error", "unknown_theme", `Unknown theme "${name}". Known themes: ${Object.keys(themes).join(", ")}.`, { field: "theme" });

  const ids = new Set();
  let maxId = 0;
  for (const b of blocks) {
    if (ids.has(b.id)) add("error", "duplicate_id", `Block id ${b.id} is used more than once.`, { block: b.id, field: "id" });
    ids.add(b.id);
    const m = /^b(\d+)$/.exec(String(b.id ?? ""));
    if (m) maxId = Math.max(maxId, +m[1]);
  }
  if (document.nextId !== undefined && !(Number.isInteger(document.nextId) && document.nextId > maxId))
    add("warning", "next_id", `nextId must be a whole number above every existing id (highest is b${maxId}), so ids are never reused.`, { field: "nextId" });

  for (const b of blocks) {
    if (b.hidden === true) continue;
    const schema = schemas[b.blockType];
    if (!schema || !templates[b.blockType]) {
      add("error", "unknown_block_type", `Unknown block type "${b.blockType}". Known types: ${Object.keys(templates).join(", ")}.`, { block: b.id, field: "blockType" });
      continue;
    }
    const before = issues.length;
    fieldIssues(b, schema, add);
    if (!th) continue;
    const st = styleFor(b.blockType, prepare(b, schema, th), schema, th);
    if (st.error) { add("error", "theme_missing_type", `Theme "${name}" has no styles for ${b.blockType}.`, { block: b.id }); continue; }
    if (st.unstyled) add("warning", "variant_unstyled", `Theme "${name}" has no style for ${b.blockType}/${st.unstyled}; rendering as primary.`, { block: b.id, field: "variant" });
    if (issues.length === before) {
      try { renderBlock(b, schemas, th, name); }
      catch (e) { add("error", "render_failed", `Couldn't render: ${e.message}`, { block: b.id }); }
    }
  }

  const seen = new Set(), reported = new Set();
  for (const u of units(blocks)) {
    if (!u.switch) continue;
    if (seen.has(u.switch) && !reported.has(u.switch)) {
      reported.add(u.switch);
      add("error", "switch_split", `Switch ${u.switch} is split up. Its cases must sit together.`, { block: u.cases[0].id, switch: u.switch });
    }
    seen.add(u.switch);
    for (const b of u.cases.slice(0, -1))
      if (b.hidden !== true && !ruleOf(b))
        add("warning", "ruleset_empty", "Empty ruleset: this case matches everyone, so the cases below it never show.", { block: b.id, field: "ruleset", switch: u.switch });
  }
  return issues;
}
