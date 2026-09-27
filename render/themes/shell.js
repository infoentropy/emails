import { html, raw } from "../html.js";

// Width of the email body, and of the content inside its side padding. Block templates size images to CONTENT.
export const WIDTH = 600;
export const GUTTER = 24;
export const CONTENT = WIDTH - 2 * GUTTER;

// The email-safe outer document that themes build on: XHTML transitional doctype, client resets,
// Outlook (mso) settings, a hidden preheader and a centred fixed-width table. Blocks are <tr> rows.
export function emailShell({ subject, preheader, body, t }) {
  return html`<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="x-apple-disable-message-reformatting" />
<title>${subject}</title>
<!--[if gte mso 9]><xml><o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml><![endif]-->
<style type="text/css">
  body, #bodyTable { height:100% !important; width:100% !important; margin:0; padding:0; }
  body, table, td, p, a, li { -ms-text-size-adjust:100%; -webkit-text-size-adjust:100%; }
  .ReadMsgBody, .ExternalClass { width:100%; }
  .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div { line-height:100%; }
  table, td { border-collapse:collapse; mso-table-lspace:0pt; mso-table-rspace:0pt; }
  img { -ms-interpolation-mode:bicubic; border:0; outline:none; text-decoration:none; }
  a img { border:0; }
  p { margin:0 0 12px 0; }
  a { color:${t.link}; }
  @media only screen and (max-width:620px) {
    .container { width:100% !important; }
    .gutter { padding-left:16px !important; padding-right:16px !important; }
    .fluid { width:100% !important; max-width:100% !important; height:auto !important; }
    .stack { display:block !important; width:100% !important; padding-left:0 !important; padding-right:0 !important; }
    .stack-gap { padding-top:16px !important; }
  }
</style>
<!--[if gte mso 9]><style type="text/css">body, table, td, p, a, h1, h2, h3 { font-family:Arial, sans-serif !important; }</style><![endif]-->
</head>
<body id="bodyTable" bgcolor="${t.page}" style="margin:0;padding:0;background-color:${t.page};">
<span class="preheader" style="display:none !important;visibility:hidden;opacity:0;color:transparent;height:0;width:0;max-height:0;max-width:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;">${preheader}</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${t.page}" style="background-color:${t.page};">
  <tr>
    <td align="center" style="padding:24px 0;">
      <table role="presentation" class="container" width="${WIDTH}" cellpadding="0" cellspacing="0" border="0" bgcolor="${t.surface}" style="width:${WIDTH}px;background-color:${t.surface};">
${raw(body)}
      </table>
    </td>
  </tr>
</table>
</body>
</html>
`;
}

// One block row: side gutters plus vertical spacing.
export const row = (inner, { top = 0, bottom = 24, bg = "" } = {}) => html`
        <tr>
          <td class="gutter" ${bg ? raw(`bgcolor="${bg}" `) : ""}style="padding:${top}px ${GUTTER}px ${bottom}px ${GUTTER}px;${bg ? `background-color:${bg};` : ""}">${inner}</td>
        </tr>`;
