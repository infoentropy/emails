// Everything the tools know about. Adding a block type, theme or flavor means adding it here.
import article from "./blocks/article.js";
import button from "./blocks/button.js";
import content_feature_header from "./blocks/content_feature_header.js";
import divider from "./blocks/divider.js";
import image_with_text from "./blocks/image_with_text.js";
import spring from "./themes/spring/theme.js";
import sleep from "./themes/sleep/theme.js";

// Block type → template. Each also has a schema at ../blocks/<type>.json. Order is palette order.
export const templates = { article, button, content_feature_header, divider, image_with_text };
export const blockTypes = Object.keys(templates);

// Theme name → theme. Order is the theme picker's order.
export const themes = { spring, sleep };
export const defaultTheme = "spring";

// Resolved against this file, so it works under /emails/ on Pages, on a local server, and from Node.
export const schemaUrl = type => new URL(`../blocks/${type}.json`, import.meta.url);

// readJson(url) → parsed JSON. The browser passes a fetch, Node a file read.
export async function loadSchemas(readJson) {
  const loaded = await Promise.all(blockTypes.map(type => readJson(schemaUrl(type))));
  return Object.fromEntries(blockTypes.map((type, i) => [type, loaded[i]]));
}
