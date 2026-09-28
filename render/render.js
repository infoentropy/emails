// check() and renderPreview(): shared by the editor (browser) and agents (Node). No I/O, no AI.
// Callers load the schemas (registry.loadSchemas) and pass them in.
import { templates, themes, defaultTheme } from "./registry.js";
import { html, raw, escapeHtml } from "./html.js";

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

// A settled ruleset is facet ids ("category.name") joined with " + ", meaning and:
// "region.us-ca-gb + subscription.not-paying". Anything else non-empty is unsettled free text.
const FACET = /^[a-z0-9-]+\.[a-z0-9-]+$/;
export function parseRuleset(ruleset) {
  const text = typeof ruleset === "string" ? ruleset.trim() : "";
  if (!text) return { empty: true };
  const parts = text.split(/\s*\+\s*/);
  return parts.every(p => FACET.test(p)) ? { facets: parts } : { text };
}

// What the "preview as" picker offers: the facets in use, by category (in order of first use),
// and the unsettled rulesets. Hidden blocks are left out, since they never show.
export function audienceOptions(document) {
  const facets = new Map(), rulesets = [];
  for (const b of document.blocks || []) {
    if (!b || typeof b !== "object" || b.hidden === true) continue;
    const r = parseRuleset(b.ruleset);
    if (r.text && !rulesets.includes(r.text)) rulesets.push(r.text);
    for (const f of r.facets || []) {
      const [category, name] = f.split(".");
      if (!facets.has(category)) facets.set(category, []);
      if (!facets.get(category).includes(name)) facets.get(category).push(name);
    }
  }
  return { facets: Object.fromEntries(facets), rulesets };
}

// Plain HTML for the preview pane, for someone who matches `as`: facet ids, whole settled rulesets
// (their facets), or unsettled ruleset texts. A block matches when it has no ruleset, when all its
// facets are in `as`, or when its unsettled text is. A hidden block never shows.
export function renderPreview(document, { schemas, theme, as = [] } = {}) {
  const name = theme ?? themeName(document), th = themes[name];
  if (!th) {
    return String(html`<!DOCTYPE html><html><body style="font:15px/1.5 Arial, sans-serif;padding:24px;color:#a93226;">Unknown theme "${name}". Pick a theme to preview this email.</body></html>`);
  }
  const on = new Set();
  for (const a of as) { const r = parseRuleset(a); for (const k of r.facets || [r.text]) if (k) on.add(k); }
  const matches = b => {
    if (b.hidden === true) return false;
    const r = parseRuleset(b.ruleset);
    return r.empty || (r.facets ? r.facets.every(f => on.has(f)) : on.has(r.text));
  };
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

// A ruleset's own problems: still free text (normal while drafting, but it must be settled into facets
// before sending), or two facets from one category.
function rulesetIssues(b, add) {
  const r = parseRuleset(b.ruleset), at = { block: b.id, field: "ruleset" };
  if (r.text) add("warning", "ruleset_unsettled", "Not settled into facets yet. Claude settles rulesets with you before the email is sent.", at);
  const categories = (r.facets || []).map(f => f.split(".")[0]);
  if (new Set(categories).size < categories.length)
    add("error", "facet_category_repeated", "Two facets from one category in one ruleset; use at most one per category.", at);
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
    rulesetIssues(b, add);
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

// Templating languages (Handlebars and the like) read "{{" as a tag. An entity renders the same in any
// email, so authored text can never become one, whichever platform the HTML ends up in.
const noBraces = text => String(text).replaceAll("{", "&#123;");
const markerText = ruleset => escapeHtml(ruleset.trim()).replace(/-{2,}/g, m => "&#45;".repeat(m.length));

// The email's HTML for sending: every block that isn't hidden, with audiences as neutral markers that the
// platform's conditionals replace when the email is pushed (see docs/agents.md):
//   <!--audience if="region.us-ca-gb + subscription.not-paying"-->  …  <!--audience elseif="…"-->  …
//   <!--audience else-->  …  <!--audience end-->
// A block with a ruleset is an if…end; a switch group is one chain. Throws if check() finds errors.
export function renderHtml(document, { schemas, theme } = {}) {
  const issues = check(document, { schemas, theme });
  const errors = issues.filter(i => i.severity === "error");
  if (errors.length) {
    const e = new Error(`Can't build the email: ${errors.length} error${errors.length === 1 ? "" : "s"}. ` +
                        errors.map(i => (i.block ? i.block + ": " : "") + i.message).join(" "));
    e.issues = issues;
    throw e;
  }
  const name = theme ?? themeName(document), th = themes[name];
  const content = b => noBraces(renderBlock(b, schemas, th, name));
  const rows = [];
  for (const u of units(document.blocks.filter(b => b && typeof b === "object"))) {
    const cases = (u.block ? [u.block] : u.cases).filter(b => b.hidden !== true);
    let open = false;
    for (const b of cases) {
      const rule = ruleOf(b);
      if (!rule) {                                   // matches everyone: it's the else, and ends the chain
        rows.push(open ? `\n<!--audience else-->${content(b)}` : content(b));
        break;
      }
      rows.push(`\n<!--audience ${open ? "elseif" : "if"}="${markerText(rule)}"-->${content(b)}`);
      open = true;
    }
    if (open) rows.push("\n<!--audience end-->");
  }
  const text = v => raw(noBraces(escapeHtml(v ?? "")));
  return String(th.shell({ subject: text(document.subject), preheader: text(document.preheader), body: rows.join("") }));
}
