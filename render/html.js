// Markup helpers shared by block templates and theme shells.

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export const escapeHtml = s => String(s).replace(/[&<>"']/g, c => ESC[c]);

class Raw {
  constructor(s) { this.s = s; }
  toString() { return this.s; }
}

// Marks a string as already-safe markup, so `html` inserts it unescaped.
export const raw = s => new Raw(String(s));

function part(v) {
  if (v instanceof Raw) return v.s;
  if (Array.isArray(v)) return v.map(part).join("");
  if (v === null || v === undefined || v === false) return "";
  return escapeHtml(v);
}

// Tagged template: every interpolated value is HTML-escaped unless wrapped in raw().
// Arrays are joined, and null / undefined / false render as nothing.
export function html(strings, ...values) {
  let out = strings[0];
  values.forEach((v, i) => { out += part(v) + strings[i + 1]; });
  return raw(out);
}

// Only http(s) URLs are ever written into href/src. Anything else (javascript:, typos) becomes "".
export const safeUrl = v => (typeof v === "string" && /^https?:\/\/\S+$/i.test(v.trim()) ? v.trim() : "");

// Scales an image to fit maxWidth, keeping its aspect ratio. Unknown dimensions give height null.
export function fit(width, height, maxWidth) {
  const w = Number(width), h = Number(height);
  if (!(w > 0)) return { width: maxWidth, height: null };
  const outW = Math.min(Math.round(w), maxWidth);
  return { width: outW, height: h > 0 ? Math.round((h * outW) / w) : null };
}

// Many clients block images on first open, so alt text needs a readable font and colour.
export const altText = (font, color) => `font-family:${font};font-size:14px;line-height:18px;color:${color};`;

// Stand-in for markdown until it's supported: escaped text, blank lines split paragraphs,
// single newlines become <br>.
export function paragraphs(text, pStyle) {
  return String(text ?? "")
    .split(/\n\s*\n/)
    .map(p => p.trim())
    .filter(Boolean)
    .map(p => html`<p style="${pStyle}">${p.split("\n").map((line, i) => [i ? raw("<br>") : "", line])}</p>`);
}
