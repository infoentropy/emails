import { html } from "../html.js";
import { row } from "../themes/shell.js";

export default function divider(d, s) {
  return row(html`
            <table role="presentation" width="${s.width}" align="center" cellpadding="0" cellspacing="0" border="0" style="width:${s.width};margin:0 auto;">
              <tr><td height="${s.thickness}" bgcolor="${s.color}" style="height:${s.thickness}px;background-color:${s.color};font-size:0;line-height:0;">&nbsp;</td></tr>
            </table>`, { top: 8, bottom: 28 });
}
