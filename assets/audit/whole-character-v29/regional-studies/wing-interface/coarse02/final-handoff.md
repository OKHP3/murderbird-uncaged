# V29 bounded wing interface handoff

Status: two preserved native construction proposals. Coarse01 retained canopy appearance but introduced three right shield/load-member crossing pairs in guard/shove. Coarse02 retains the complete canopy and eliminates all crossings involving the edited interface at the three sampled poses. Root visual acceptance and whole-character macroform review remain separate; this is not a full motion, physics or engineering pass.

## Actual implementation

`scripts/regions/whole-character-v29-wing-interface.py` supplies composable `apply()` on V28 Form02. It recesses the 24 short-shield plates/folds/liners 45 mm inboard in existing tucked space without Y/Z rescaling. Four receiving forks are rebuilt from evaluated inner elbow-journal lower seats to evaluated recessed liner points. Coarse02 cuts a real finite receiving window through only the right liner and first-course short-shield plates 3/4, using a conservative convex sweep of the actual retained upper load member at 19 relative shield angles over 0…0.72 rad, expanded 3 mm. The construction envelope is authored clearance allowance, not a validated continuous sweep.

Complete canopy coverage, exterior outline, canopy folds/backing, all actual journals/races/load members, left restriction and other geometry remain exact. Each part has one original rigid owner; no cross-hinge rigid bridge. Original materials and passive three-era eligibility remain.

## Checks that ran

28 evaluated edited solids are finite, closed-edge, positive-volume with zero loose vertices. All 54 named empty rests/properties, 534 outside mesh records and original material definitions are exact. Native saved/reopened exactly. Four receiver centerline seats terminate on evaluated actual journal and liner surfaces, including after the receiving window, within numerical mesh tolerance (maximum recorded rest-distance 7.5e-9 m; not a manufacturing tolerance). No complete attachment or bearing engineering approval claimed.

Actual matched folded whole front/side/three-quarter and bilateral folded/guard/short-shove closeups are preserved in each candidate directory. The complete canopy is visible; nothing was hidden from final geometry to obtain the fit result.

## Bounded strict cross-owner screen

Every builder-era eligible evaluated neighbor mesh included, even if saved display-hidden; body/head/neck/legs checked wherever bounds overlap. Actual native rest-relative wing angles with neutral body, three poses only.

| Pose | V28 Form02 | V29 coarse01 | V29 coarse02 | Coarse02 edited-interface pairs |
|---|---:|---:|---:|---:|
| folded | 52 | 38 | 38 | 0 |
| guard | 54 | 41 | 38 | 0 |
| short-shove | 57 | 40 | 37 | 0 |

No new pair identities versus exact V28 Form02 at these samples. No head/neck/leg/shin witnesses. Exact remaining identities, owner groups, triangle witness counts and coordinates are in `fit-screen.json`.

The remaining 38/38/37 witnesses are not exempted: bilateral elbow journals/races against retained swept upper load members, retained body receiving links/journals/forks/shafts against mantle machinery, and the later left bearing strap against unchanged mantle liner/upper canopy plates. Some may represent intended captive machinery, but engineering validity is unconfirmed. Same-owner overlaps are outside this screen; surface triangle crossing does not detect all contained overlap or prove continuous collision clearance.

## Exact provenance

- V28 Form02 base: `838a86b16766ddd4491c9f1cbe6a7aa0039c2b9e8514a04eb710d1e9b2f9bd9d`
- Coarse02 source: `139d7e6fba09474e9ca2d56c7029a64b24a62bce0c96e212e8d85c11c9f3ef6a`
- Coarse02 native: `2eacf9639f0590aafbf16ba1eeac8fb81bf71f17de2d3c05b5b9c142049b567c`

Coarse01 source/native/renders/receipts remain at `/tmp/v29-wing-interface/coarse01`; no geometry trial was overwritten. Both candidates are editable proposals. No runtime, body, head, foot or root-builder edits were made by this worker.
