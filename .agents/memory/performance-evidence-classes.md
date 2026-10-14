---
name: Performance evidence classes
description: Device performance receipt policy for separating verified hardware results from cloud/software and historical telemetry.
---

Performance receipts should explicitly classify each evidence category and state whether it is eligible for hardware-performance claims. Cloud/software-renderer evidence and historical non-target telemetry are always hardware-ineligible; an ASUS measurement requires verified physical access and observed browser, exact version, and selected WebGL renderer on that device.

Do not promote proposed budgets into benchmark verdicts: MEASURED requires actual numeric observations and a traceable evidence reference; PASS/FAIL additionally requires explicitly approved thresholds, approval evidence dated before the run, and comparison evidence. Keep deployment authorization and owner likeness acceptance as independent statuses.

**Why:** Similar-looking timing data can come from different devices, software renderers, or older builds; without explicit classification it can be mistaken for evidence about the current target.

**How to apply:** When adding or changing browser-performance receipts, keep each evidence source in its own category and enforce measurement evidence, pre-run threshold approval, provenance, and release/likeness separation in automated validation.
