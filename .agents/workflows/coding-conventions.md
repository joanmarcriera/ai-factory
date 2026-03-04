---
description: Project Coding Conventions and Guidelines
---

# OVERALL GOAL
We are building a Tampermonkey overlay for Google Maps for lead generation.

# JAVASCRIPT CONVENTIONS
- Write clean, modern ES6+ Javascript.
- When querying for URLs, be robust (e.g., check for `window.location.hostname` and `pathname` instead of hardcoding full exact URL strings).
- ALWAYS fulfill the EXACT instructions in the task description. If a task says to write a specific string or comment, do it exactly as asked to ensure validation passes.
- **NO PLACEHOLDERS**: Never use comments like `// Rest of the code remains the same` or truncate files. You must always write the complete file contents and all functions. If you omit code, the script will throw ReferenceErrors and crash.
- **Tampermonkey Scripts**: Any script intended for Tampermonkey MUST include a valid `==UserScript==` metadata block at the very top of the file, including `@name`, `@namespace`, `@version`, `@description`, `@match`, and `@grant`.
- **Self-Contained UI**: Tampermonkey scripts consist of an isolated Javascript file. Do not assume `index.html` or `styles.css` exist in the browser context. All UI overlays MUST be dynamically injected via `document.createElement`, `innerHTML`, and `<style>` tag appending. 
- **Lead Qualification**: When evaluating DOM elements for business information, strongly favor identifying missing attributes (e.g. `phone: null` or `claimed: false`). This missing information is precisely what defines a high-value lead for monetization.

# HTML/CSS CONVENTIONS
- Use basic, minimal HTML tags.
- For CSS, utilize basic class names. If "glassmorphism" is requested, use `backdrop-filter: blur(10px)` and semi-transparent backgrounds.
