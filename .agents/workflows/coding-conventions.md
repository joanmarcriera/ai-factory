---
description: Project Coding Conventions and Guidelines
---

# OVERALL GOAL
We are building a Tampermonkey overlay for Google Maps for lead generation.

# JAVASCRIPT CONVENTIONS
- Write clean, modern ES6+ Javascript.
- When querying for URLs, be robust (e.g., check for `window.location.hostname` and `pathname` instead of hardcoding full exact URL strings).
- Prefer descriptive variable names.
- ALWAYS fulfill the EXACT instructions in the task description. If a task says to write a specific string or comment, do it exactly as asked to ensure validation passes.

# HTML/CSS CONVENTIONS
- Use basic, minimal HTML tags.
- For CSS, utilize basic class names. If "glassmorphism" is requested, use `backdrop-filter: blur(10px)` and semi-transparent backgrounds.
