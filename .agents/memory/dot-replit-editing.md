---
name: Safe .replit edits
description: Replit workspace guardrails for changing the root .replit TOML file.
---

Do not edit `.replit` with ordinary patch or direct file-write tools. If a
requested change genuinely requires updating it, stage the complete TOML at an
absolute workspace path and pass that file to `verifyAndReplaceDotReplit`.
Prefer the dedicated workflow, package, or service tools for those settings
instead of changing `.replit` directly.

**Why:** The workspace rejects direct `.replit` edits and requires schema
validation before replacing the project configuration.

**How to apply:** Confirm the full current TOML and the exact requested
configuration change first. Avoid touching `.replit` when an automatic
environment adjustment is unrelated to the user's task.