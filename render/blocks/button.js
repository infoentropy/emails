import { html, safeUrl } from "../html.js";
import { row } from "../themes/shell.js";

// A table-cell "bulletproof" button, so the colour shows even with images blocked.
export default function button(d, s) {
  const link = safeUrl(d.link);
  const label = html`<span style="font-family:${s.font};font-size:16px;line-height:20px;font-weight:bold;color:${s.color};">${d.text}</span>`;
  const inner = link
    ? html`<a href="${link}" style="display:inline-block;padding:14px 28px;text-decoration:none;color:${s.color};">${label}</a>`
    : html`<span style="display:inline-block;padding:14px 28px;">${label}</span>`;
  return row(html`
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="${s.align}" style="margin:0 ${s.align === "center" ? "auto" : "0"};border-collapse:separate;">
              <tr>
                <td align="center" bgcolor="${s.bg}" style="background-color:${s.bg};border:2px solid ${s.border};border-radius:${s.radius}px;">${inner}</td>
              </tr>
            </table>`, { top: 8, bottom: 28 });
}
