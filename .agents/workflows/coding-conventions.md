---
description: Project Coding Conventions and Guidelines
---

# OVERALL GOAL
We are building a Tampermonkey overlay for Google Maps for lead generation.

# JAVASCRIPT CONVENTIONS
- Write clean, modern ES6+ Javascript.
- When querying for URLs, be robust (e.g., check for `window.location.hostname` and `pathname` instead of hardcoding full exact URL strings).
- ALWAYS fulfill the EXACT instructions in the task description. If a task says to write a specific string or comment, do it exactly as asked to ensure validation passes.
- **NO PLACEHOLDERS & NO REGRESSIONS**: Never use comments like `// Rest of code...` or truncate files. You must always maintain the complete file contents. When adding a new feature, DO NOT overwrite or revert previous features (such as extraction logic or existing functions) to an older state.
- **NO DUPLICATE FUNCTIONS**: Never create two functions with the same name in the same file. Always consolidate logic into a single function definition.
- **Indentation**: Use 2 spaces for indentation in all JavaScript files. This is the standard community convention. Do not use hard tabs.
- **Tampermonkey Scripts**: Any script intended for Tampermonkey MUST include a valid `==UserScript==` metadata block at the very top of the file, including `@name`, `@namespace`, `@version`, `@description`, `@match`, and `@grant`. It MUST also include `@updateURL` and `@downloadURL` pointing to the raw source file in the repository to enable auto-updating.
- **Auto-Versioning**: Every time you modify a Tampermonkey script in a new task, you MUST increment the `@version` number in the metadata block (e.g., from `1.0` to `1.1`).
- **Self-Contained UI**: Tampermonkey scripts consist of an isolated Javascript file. Do not assume `index.html` or `styles.css` exist in the browser context. All UI overlays MUST be dynamically injected via `document.createElement`, `innerHTML`, and `<style>` tag appending. They MUST always include `z-index: 999999 !important;` to prevent being buried under Google Maps UI.
- **Lead Qualification**: When evaluating DOM elements for business information, strongly favor identifying missing attributes (e.g. `phone: null` or `claimed: false`). This missing information is precisely what defines a high-value lead for monetization.
- **Idempotent DOM Modifications**: Because scripts often rely on `setInterval` or `MutationObserver`, any manipulation of the page DOM (like appending a new button or a highlight label) **MUST** check if the modification has already been applied. Usually, this means adding a class like `.ai-injected` to the parent and skipping elements that already have it.
- **Robust Scraping Tactics**: Google Maps obfuscates classes and `aria-label` text is highly localized and unreliable. Extract data by structural heuristics (e.g., getting the element's innerText, or looking for specific tag hierarchies like `a[href^="http"]` for websites, or regexing for phone numbers in the full text payload).

# HTML/CSS CONVENTIONS
- Use basic, minimal HTML tags.
- For CSS, utilize basic class names. If "glassmorphism" is requested, use `backdrop-filter: blur(10px)` and semi-transparent backgrounds.
