# Final diagnostic: body and stance without head points

[Concrete overlay](body-only-overlay.png) · [Clay](body-only-clay.png) · [Neutral PBR](body-only-pbr.png) · [Receipt](receipt.json)

The three crown/optic/bill landmarks have zero fitting weight here. Ten shoulder, breast, knee, hock, ankle and plantar points retain their previous weights. All points, including the excluded head, still report residuals. Geometry, materials, stance anchors and source bytes remain unchanged; the complete bird remains in frame.

The sampled body-only optimum is **64° from side, 22° elevation**, orthographic scale **2.8762604**. Body weighted RMS is **50.99px**, versus **82.12px** at the original canonical camera. The complete landmark RMS increases to **88.77px**; excluded optic and bill residuals are **186.66px** and **161.90px**. The global compromise remains 35°/16°, with RMS72.22px.

| Separation | Source declaration px | Body-only projection px |
|---|---:|---:|
| Knees | 230 | 133.59 |
| Ankles | 217 | 174.39 |
| Plantar housing centers | 220 | 174.39 |

**Inference:** the body benefits from a more frontal view than the head. A relative head turn could reconcile some of that difference, but does not follow uniquely from these images. The present head shape, narrow symmetric joint spacing, partly occluded far joints and source stance asymmetry also explain mismatches. Even the body-only view leaves substantial knee spacing error; a head turn alone cannot solve it.

**Unknown:** the true physical camera, relative head yaw and source joint world positions. These are image hypotheses, not calibrated measurements or authorization to move approved anchors. Owner steering would be needed before a separately scoped source-matching pose study.

`camera(root_path, 'body-only')` returns this diagnostic camera; apply identically to retained/candidate models for comparison only. Coarse grid: yaw0–90° in10° steps, elevation0–20° in4° steps; refinement ±6° yaw/±4° elevation in2° steps. No new modeling attempt, native save, runtime change or publication occurred.
