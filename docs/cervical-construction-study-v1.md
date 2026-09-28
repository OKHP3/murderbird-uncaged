# Two-stage cervical construction study

Status: isolated structural correction in progress. The application still selects Alignment V8 (`c8c30cc46059…`). No cervical study is artistically approved or selected for release.

The selected common-body illustration supports a substantial curved neck flowing into the breast. The July image remains head-only authority. A serial mechanical joint, its location, ownership boundaries, pitch allocation and hidden load members are reconstructed details, not dimensions recovered from either perspective illustration. There is no biological tissue or physical-force simulation.

## Construction contract under test

The native intermediate pivot `cervical-upper` is parented to `neck`, at native rest world `(0, −0.235, 1.452)` metres, local `(0, −0.135, 0.192)`. Native coordinates are X anatomical left, −Y forward, Z up. Browser coordinates are `(X, Z, −Y)`. The head is reparented to the intermediate joint with its rest world transform preserved. This changes the native rig from 51 to 52 pivots.

Total commanded pitch is allocated 35% to the lower neck and 65% to the intermediate local-X hinge. Yaw and roll remain at the lower attachment. These are authored kinematic choices. Both structural lengths stay fixed; the contact solver tests the actual exported bill triangles and counter-rotates the head. It recomputes approach distance using both joints. It does not translate the neck, intermediate pivot or skull to obtain contact.

| Region | Rigid attachment and allowed motion | Exterior/clearance responsibility | Era source of motion |
| --- | --- | --- | --- |
| Lower cervical frame | `neck`; lower pitch plus yaw; retained body attachment | Fixed curved load rails support an intermediate transverse journal. No long rigid plate bridges the joint. | Maker external control; Mechanic stationary neck; Advanced existing lower actuator pair. |
| Upper cervical frame | `cervical-upper`; local-X pitch only | Separate curved rails and journal hardware; clear lower frame and mandible at combined controls. | Additional Maker control routing and Advanced upper actuator remain to be built. Mechanic requires a readable passive restraint. |
| Upper guards | Upper joint; no metal stretching | Courses 1–3 must overlap a nested lower guard through the full pitch range, with clean thickness and returns. | Passive surfaces, inherited across eras. |
| Lower joint guard | Lower neck | Course 4 must cover the hinge without scraping the upper courses or breast during pitch and yaw. | Passive surface, inherited. |
| Neck-to-breast transition | Attempt07: lower neck and extra breast yoke. Attempts08/09: courses5/6 on breast cover. Attempts10–12: courses5/6 on body | Neither moving-cover nor body ownership has produced an accepted transition. Body-owned plates need brackets and an access seam; cover-owned plates need clearance through opening. | Passive surfaces; all alternatives remain proposals. |
| Head and bill | Head on upper joint; jaw retains its own existing hinge | Keep looking, lowered and strike clearances. Head counter-rotation uses total commanded cervical pitch. | Existing era eligibility and optic controls remain in force. |

Rigid frame and guards do not need skeletal skinning. Flexible control lines, conduit and sliding actuator members need their own deliberate endpoint/routing treatment. An added empty transform alone is not evidence of a complete drive mechanism.

## Preserved iterations and findings

Attempts01–03 explored a wider curved envelope on the original single-joint rig. They exposed an incompatibility between a full-neck base bend and a convincing covered breast transition. Attempts04/05 failed before saving and retain explicit failure records. Attempt06 introduced the second joint, but its first re-derived pose report omitted the external scene/root transform; zero-pitch displacement was therefore misreported. Attempt07 corrects that report and preserves the earlier evidence.

Attempt07 native is `751d8149032941774c6ba31824c76f6fa840bb0d767e433bae8000535f3a2b98`; its diagnostic GLB is `5736ca592c5ebfa7da78315b136b53ad6a48050ede66f6d60b9ccf860afa8ecf`. Its neutral transition is fuller than V8, but broad lower throat bands still read as a cuff. Its upper/lower guards intersect in sampled poses. It is held.

Attempt08 native is `1703786958ca2fc188ffeb4b0c43f79f0b8327556427723738ad47e333e5f558`; diagnostic GLB is `cff0d74b12f6f92960f6182e623f7bd6931adf64d35aa0d76ceb1d053dcccfa5`. Primary review rejected its visible pointed flaps, jagged rim strips, hollow side window and detached-looking lower pieces. Removing interfering faces did not produce credible construction.

Attempts09–12 tried closed sector interfaces and whole side guards. They remain held: the resulting bowl-like bands, projecting strips and hollow transitions lose the intended curved neck. Attempt12 native is `d5fb38f474b708d4e0c305efdb12b0df4e601c6ef1a023aa0947038b8560fbc5`. The primary agent reviewed its profile and agrees with the worker's hold. No attempt13 was started. The [consolidation report](../assets/audit/cervical-construction-study-v1/construction-consolidation-v1.md) and [index](../assets/audit/cervical-construction-study-v1/study-index.json) preserve exact versions, strict penetrating triangle evidence, editable neighborhoods and the limits of replaying attempt07 poses on later variants.

Attempt07 independently matches its diagnostic export across all106 groups,52 pivots and261,828 triangles. Its contact interference spans substantial parts of courses3/4 and the backing, so shortening a lip is insufficient. Later annular journal seats are useful proposed construction, but attempt07's overlapping solid rail/race endpoints are not certified bearing interfaces.

Four proposed actuator placements were evaluated without adding hardware. V2 cleared plates but lost leverage at a dead-centre position and was rejected. V4 retains a consistent40–60mm moment arm and clearance in sampled operating poses, but the opening breast panel crosses its proposed actuator at75% open. Its brackets, end fittings, continuous sweep and interaction with procedural controls remain unverified. A deliberate access-path design is required before adopting that placement.

## Runtime evidence

[`runtime-support-receipt.json`](../assets/audit/cervical-runtime-study-v1/runtime-support-receipt.json) binds the optional runtime support and both model identities. The original seven affected checks passed on V8. The same seven passed on the attempt07 diagnostic, including stricter checks of total cervical pitch, intermediate fixed attachment and local-X hinge axis. These checks cover kinematic behavior and existing limited geometry assertions; they do not certify the new neck guards.

A fresh [21-pose packet](../assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json) records the actual attempt07 runtime. It includes all five Maker controls, simultaneous Maker neck and jaw, Advanced attention/strike/contact/recovery/jump/thrust, a Mechanic stepped turn, and inspection openings of 0/25/50/75/100% plus separation of 50/100%. Each pose records the actual exported transforms and source hashes. This supersedes using old51-pivot matrices as proof for the changed rig. Sampled contact uses total pitch of 0.578242 rad, allocated lower 0.202385 / upper 0.375857, with zero translation error at the three cervical attachments.

The local V8 build with optional serial-joint support passes `npm ci`, `npm run build`, and the publication-boundary checker. It contains 134 intended paths and 16 exact active-model/folio/fallback matches. The diagnostic GLB, native files and audit trees are excluded. The running V8 WebGL scene was inspected after the change; each of its three fixed fallback images decoded at 1100×1100. Browser receipts and captures are preserved in `assets/audit/cervical-runtime-study-v1/v8-build/`. Existing large Three.js chunk and unapproved fsevents install-script notices remain recorded. No remote CI or deployment was performed.

## Remaining work

Finish clean plate overlap and backing geometry, re-check combined controls and intermediate breast opening, then supply era-correct drive/constraint hardware. Re-export the final chosen native, verify native/export correspondence, recapture actual runtime poses, inspect WebGL and fallback output, and present matched whole-body and close-up views. The owner’s neutral whole-candidate artistic gate remains ahead of dependent surface finishing. V10 repair chronology and V12 historical footage scope remain separate unresolved owner decisions in the reference packet.
