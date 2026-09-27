import { html } from "../html.js";
import { row } from "../themes/shell.js";

// The theme keys the label and accent colour off feature_type.
export default function contentFeatureHeader(d, s) {
  const accent = s.accents?.[d.feature_type] ?? s.accent;
  const label = s.labels?.[d.feature_type] ?? d.feature_type;
  return row(html`
            <div style="font-family:${s.bodyFont};font-size:12px;line-height:16px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;color:${accent};">${label}</div>
            <h1 style="margin:8px 0 0 0;font-family:${s.headingFont};font-size:${s.headingSize}px;line-height:${Math.round(s.headingSize * 1.15)}px;font-weight:normal;color:${s.color};">${d.heading}</h1>
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:16px;"><tr><td width="48" height="4" bgcolor="${accent}" style="width:48px;height:4px;background-color:${accent};font-size:0;line-height:0;">&nbsp;</td></tr></table>`,
    { top: 32, bottom: 28, bg: s.bg });
}
