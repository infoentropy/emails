// Every block type the tools know. Each has a schema at ../blocks/<type>.json.
// Order is the order the editor's palette lists them in.
export const blockTypes = [
  "article",
  "button",
  "content_feature_header",
  "divider",
  "image_with_text",
];

// Resolved against this file, so it works under /emails/ on Pages, on a local server, and from Node.
export const schemaUrl = type => new URL(`../blocks/${type}.json`, import.meta.url);
