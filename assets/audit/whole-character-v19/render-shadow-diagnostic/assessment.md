# Native illustration shadow diagnosis

Confirmed for the exact V18 Advanced-contact sample in the accompanying receipt: the thin floor-directed lines disappear when only Workbench `show_shadows` is disabled. The pose matrices, visible meshes, hidden historical curves, camera, floor and cavity settings are identical. No mesh was hidden or edited between these two views. The native remains byte-identical.

This isolates these observed lines to cast-shadow rendering in this sample. It does not prove the model has no geometric defects, explain every prior image, or turn a native pose illustration into browser evidence. The specific numerical cause inside Workbench is not established.

The pose illustration tool now accepts an explicit `--no-shadows` flag and records its state in the render receipt. Existing outputs and its default remain unchanged. Shadow-free illustrations make the construction easier to inspect but do not visually establish ground support; contact and browser evidence remain separate requirements.
