import { emailShell } from "../shell.js";

const t = {
  page: "#eef3ea", surface: "#ffffff", text: "#1f2a24", muted: "#5f6f66",
  accent: "#3f7d4e", accentSoft: "#e3efe4", warm: "#d9822b", line: "#d5e0d6", link: "#3f7d4e",
  heading: "Georgia, 'Times New Roman', serif",
  body: "Helvetica, Arial, sans-serif",
};

export default {
  label: "Spring",
  imageSide: "left",
  dateFormat: { month: "long", day: "numeric", year: "numeric" },
  styles: {
    content_feature_header: {
      primary: {
        bg: t.accentSoft, color: t.text, accent: t.accent, headingFont: t.heading, bodyFont: t.body, headingSize: 34,
        labels: { sleep: "Sleep", meditate: "Meditate" },
        accents: { sleep: "#4f6db8", meditate: t.accent },
      },
    },
    article: {
      primary: { headingFont: t.heading, bodyFont: t.body, headlineSize: 26, headline: t.text, muted: t.muted, imageRadius: 6 },
      secondary: { headingFont: t.heading, bodyFont: t.body, headlineSize: 18, headline: t.text, muted: t.muted, imageRadius: 4 },
    },
    button: {
      primary: { bg: t.accent, border: t.accent, color: "#ffffff", font: t.body, radius: 24, align: "center" },
      secondary: { bg: t.surface, border: t.accent, color: t.accent, font: t.body, radius: 24, align: "center" },
    },
    divider: {
      primary: { color: t.accent, thickness: 3, width: "100%" },
      secondary: { color: t.line, thickness: 1, width: "100%" },
    },
    image_with_text: {
      primary: { headingFont: t.heading, bodyFont: t.body, heading: t.text, body: t.muted, imageRadius: 6 },
    },
  },
  shell: ({ subject, preheader, body }) => emailShell({ subject, preheader, body, t }),
};
