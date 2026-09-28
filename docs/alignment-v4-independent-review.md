# Alignment v4 — independent visual review

**Assessment: revision required.** The frozen candidate improves plate overlap, surface continuity, and the optic/cheek connection over v3. It still falls short of the selected references in head construction and the visual hierarchy of the body, mantle, and feet. This is a bounded static-image critique, not owner acceptance, a full likeness approval, or a motion/contact certificate.

## Candidate and evidence

- Reviewed GLB: [`murderbird-alignment-v4.glb`](../assets/models/uncaged-alignment-v4/murderbird-alignment-v4.glb), SHA-256 `bcfb03ef96c6b64f3bf18caca7851d7b3bd5808d196c55e334ecda1e1ca04299`.
- Its [alignment inventory](../assets/models/uncaged-alignment-v4/alignment-inventory.json) identifies the proposal as neutral geometry awaiting owner review. The [27-image authoring manifest](../assets/audit/alignment-v4/authoring-views.json) binds every view to this GLB; the image files were present and the model hash was independently recomputed during this review.
- The visual comparison opened the v4 three-quarter, front, rear, side, head, breast, mantle and feet views, plus the Maker, Mechanic and Builder reference-perspective views. It compared them with the exact v3 GLB and matching v3 authoring views (SHA-256 `c4dc308f77399410368b82443a1b21b9113cfedb258aa055906b4f13c92dda21`) and the sources recorded in the [reference packet](../assets/models/uncaged-neutral-v2/reference-packet.json).
- Scope follows the packet: the documented owner-selected July illustration controls **head identity only**. Candidate 03 is the lead-selected common full-body illustration, but does not establish dimensions or final-art approval. The Maker-clean, Mechanic, and Sentinel illustrations provide story-era context; they do not establish hidden topology or measured dimensions.
- Views use neutral studio lighting without textures. They support visual review of authored shapes, not material finish, exact source measurements, or production acceptance.

## Observed progress

The breast now has visibly curved, overlapping shields and a tapered central course where v3 had broad smooth gutters between flatter patches. The repaired mantle is continuous through its quad lofts and no longer shows the former open pod bands or the conspicuous crossing slivers. The optic surround now sits within a cheek plate, and the large rectangular opening seen in v3 is substantially reduced. These are concrete construction improvements; the newest views do not establish final likeness.

The common outline remains a compact, grounded mechanical bird. The three-quarter and side views retain a deep breast, folded mantle, and short rear contour. Maker, Mechanic, and Builder perspective previews keep the same neutral geometry proposal; their distinct surface histories and mechanisms are outside what these neutral stills can validate. The Builder still shows a warm optic while the Maker view keeps a dark optic, consistent with the limited era cues visible in the selected illustrations.

## Remaining priorities

1. **Head identity:** The deep hooked bill and circular eye remain legible, and the optic no longer reads as a detached ring. The eye is now dominated by a broad, smooth cheek/optic shield with a plain inset; the July source has a more mechanically nested circular housing and more articulated cheek members around its open cheek/mandible silhouette. The crown in the close-up still reads as broad, smooth cap pieces and straps more than as swept, compact overlapping laminae. Refine the optic surround, cheek negative space, and crown course together rather than enlarging or decorating the eye alone.
2. **Body and mantle hierarchy:** V4 improves the overlap and curvature over v3, but the breast still resolves into readily counted, similarly sized pointed courses. The mantle’s clean continuous surface is a regression from its richer source hierarchy in one respect: broad, rounded fields dominate, with a small number of regularly spaced tiers. Candidate 03 and the selected story-era illustrations show a clearer transition from clustered shoulder coverts into longer, directional plates. Preserve the improved continuity while varying plate scale, sweep, and course boundaries so the armor does not read as uniform rows across breast and wing.
3. **Leg and foot mass:** The legs remain visually dominated by large drum joints, narrow exposed links, and long smooth ankle sheaths. The feet have visible separate digits and hooked tips, but the toe roots read as bulbous curled knuckles compared with the selected full-body illustration’s substantial, more articulated digit armor. Refine the transitions from ankle guard to toe joints and the mass of the toe shells. These stills do not establish planted support, grip, or load capacity.

## Neck participation and limits

I authored [`alignment-v4-neck.py`](../scripts/alignment-v4-neck.py), so the cervical armor is **not independently reviewed** here. In the fixed side and three-quarter views, the neck’s repeated plates improve visible coverage, but the rear/side strut remains conspicuous and the connection from head through throat to breast reads as separate stepped bands. Treat those as self-review observations, not an independent neck finding; a separate reviewer should assess that region against the preserved v3 envelope and source scope.

The comparisons are static and qualitative. No numerical likeness score is reported. This review did not inspect WebGL rendering, browser behavior, animation, full motion clearance, physical support, final materials, or human acceptance. The next visual pass should use views bound to any later geometry identity and include the revised head, breast, and mantle details before likeness is reconsidered.
