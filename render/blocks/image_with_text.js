import { html, safeUrl, fit, paragraphs, altText } from "../html.js";
import { row, CONTENT } from "../themes/shell.js";

const COL = (CONTENT - 24) / 2;

// Image and text side by side; the theme's imageSide picks the side. Columns stack on narrow screens.
export default function imageWithText(d, s, theme) {
  const src = safeUrl(d.image);
  const f = fit(d.image_width, d.image_height, COL);
  const image = src
    ? html`<img src="${src}" alt="${d.image_alt}" width="${f.width}"${f.height ? html` height="${f.height}"` : ""} class="fluid" style="display:block;width:${f.width}px;max-width:100%;height:auto;border:0;${altText(s.bodyFont, s.body)}${s.imageRadius ? `border-radius:${s.imageRadius}px;` : ""}" />`
    : "";
  const text = html`
                  <h2 style="margin:0 0 10px 0;font-family:${s.headingFont};font-size:22px;line-height:28px;font-weight:bold;color:${s.heading};">${d.heading}</h2>
                  ${paragraphs(d.body, `margin:0 0 12px 0;font-family:${s.bodyFont};font-size:15px;line-height:23px;color:${s.body};`)}`;
  const imgFirst = theme.imageSide !== "right";
  const cell = (inner, side) => html`
                <td class="stack${side === "second" ? " stack-gap" : ""}" width="${COL}" valign="top" style="width:${COL}px;${side === "first" ? "padding-right:12px;" : "padding-left:12px;"}">${inner}</td>`;
  return row(html`
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>${imgFirst ? [cell(image, "first"), cell(text, "second")] : [cell(text, "first"), cell(image, "second")]}
              </tr>
            </table>`, { top: 8, bottom: 28 });
}
