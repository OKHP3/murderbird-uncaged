---
name: Exterior source/output alignment
description: How to distinguish a regional geometry edit from older differences between committed source and frozen model assets.
---

Before a regional geometry regeneration, compare the frozen deliverable with a clean rebuild from the pre-edit source. A narrowly scoped source diff does not guarantee that the resulting model differs only in that region when the frozen artifact is already stale.

**Why:** A full rebuild can materialize geometry already present in source but absent from the frozen model, making prior drift look like a change introduced by the current task.

**How to apply:** Compare both the frozen candidate and a clean pre-change-source rebuild against the new output. Record off-region differences, get an explicit scope decision when they affect the visible candidate, and keep that distinction clear in review and release notes.