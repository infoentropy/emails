import { html, safeUrl, fit, altText } from "../html.js";
import { row, CONTENT } from "../themes/shell.js";

const THUMB = 120;

// primary: the lead story, full-width image over a large headline.
// secondary: a regular item, headline beside a thumbnail.
export default function article(d, s) {
  const link = safeUrl(d.link), src = safeUrl(d.image);
  const linked = (inner, color) =>
    link ? html`<a href="${link}" style="color:${color};text-decoration:none;">${inner}</a>` : inner;
  const img = (w, cls) => {
    if (!src) return "";
    const f = fit(d.image_width, d.image_height, w);
    return linked(html`<img src="${src}" alt="${d.image_alt}" width="${f.width}"${f.height ? html` height="${f.height}"` : ""} class="${cls}" style="display:block;width:${f.width}px;max-width:100%;height:auto;border:0;${altText(s.bodyFont, s.muted)}${s.imageRadius ? `border-radius:${s.imageRadius}px;` : ""}" />`, s.headline);
  };
  const headline = html`<div style="font-family:${s.headingFont};font-size:${s.headlineSize}px;line-height:${Math.round(s.headlineSize * 1.25)}px;font-weight:bold;color:${s.headline};">${linked(d.headline, s.headline)}</div>`;

  if (d.variant === "primary") {
    return row(html`
            ${img(CONTENT, "fluid")}
            <div style="height:16px;line-height:16px;font-size:0;">&nbsp;</div>
            ${headline}`, { top: 8, bottom: 28 });
  }
  return row(html`
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td valign="top" style="padding-right:16px;">${headline}</td>
                ${src ? html`<td width="${THUMB}" valign="top" style="width:${THUMB}px;">${img(THUMB, "")}</td>` : ""}
              </tr>
            </table>`, { top: 4, bottom: 20 });
}
