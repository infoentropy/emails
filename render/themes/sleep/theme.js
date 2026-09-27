import { emailShell } from "../shell.js";

const t = {
  page: "#070b18", surface: "#111831", text: "#e8eaf6", muted: "#a6adcf",
  accent: "#9aa8ff", accentSoft: "#1b2447", warm: "#f2c46b", line: "#2a3360", link: "#b8c2ff",
  heading: "Georgia, 'Times New Roman', serif",
  body: "Helvetica, Arial, sans-serif",
};

export default {
  label: "Sleep",
  imageSide: "right",
  dateFormat: { weekday: "long", month: "long", day: "numeric" },
  styles: {
    content_feature_header: {
      primary: {
        bg: t.accentSoft, color: t.text, accent: t.warm, headingFont: t.heading, bodyFont: t.body, headingSize: 36,
        labels: { sleep: "Sleep", meditate: "Meditate" },
        accents: { sleep: t.warm, meditate: t.accent },
      },
    },
    article: {
      primary: { headingFont: t.heading, bodyFont: t.body, headlineSize: 26, headline: t.text, muted: t.muted, imageRadius: 10 },
      secondary: { headingFont: t.heading, bodyFont: t.body, headlineSize: 18, headline: t.text, muted: t.muted, imageRadius: 8 },
    },
    button: {
      primary: { bg: t.warm, border: t.warm, color: "#111831", font: t.body, radius: 8, align: "left" },
      secondary: { bg: t.surface, border: t.accent, color: t.accent, font: t.body, radius: 8, align: "left" },
    },
    divider: {
      primary: { color: t.warm, thickness: 2, width: "100%" },
      secondary: { color: t.line, thickness: 1, width: "60%" },
    },
    image_with_text: {
      primary: { headingFont: t.heading, bodyFont: t.body, heading: t.text, body: t.muted, imageRadius: 10 },
    },
  },
  shell: ({ subject, preheader, body }) => emailShell({ subject, preheader, body, t }),
};
