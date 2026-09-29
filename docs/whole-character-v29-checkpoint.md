# V29 — bounded hinge and wing fit correction

Local review: http://127.0.0.1:5183/assets/audit/whole-character-v29/index.html

**HOLD for likeness.** This checkpoint fixes two mechanical interfaces on V28 Form02. It does not resolve the owner's Squidward comparison, finish the three exteriors, or promote a new model into the main exhibit. The head, neck, breast shell and stance still need substantial visual work. The earlier whole-form owner direction question remains unanswered.

## Exact editable candidate

- Base: V28 Form02, native SHA `838a86b16766ddd4491c9f1cbe6a7aa0039c2b9e8514a04eb710d1e9b2f9bd9d`.
- [Fit01 native](../assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.blend): 2,842,520 bytes; SHA `04040543c39e98dd3d20da3d51a5ba40fd87151315ef074d328276eed97c63e7`.
- [Fit01 browser GLB](../assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.glb): 9,124,756 bytes; SHA `d6e5d4b92480fbff94805f06bc3bf6190e553c51f7bb7704290e394534053f6a`.
- Builders: `scripts/build-whole-character-v29.py`, `scripts/export-whole-character-v29.py`. Composition uses only `whole-character-v29-breast-hinge.py` and `whole-character-v29-wing-interface.py`. Frozen executed sources are beside the output.
- `whole-character-v29-neck-root-receiver.py` is a **rejected experiment**. Do not include it in Fit01 regeneration or promote its native trials.

The candidate has 564 rigid meshes, 54 empty nodes, 436,006 exported triangles and eight retained materials. All 54 rest nodes, the two bill contact anchors and 94 foot/toe meshes remain exact. Save/reopen, finite coordinates and material definitions pass. Historical source media, V28 assets, runtime motion code and public model selection are unchanged.

## Regional construction and inheritance

| Region | Before → after | Attachment and clearance | Era eligibility and reference scope |
|---|---|---|---|
| Breast hinge | Solid fixed forks and moving channels started at the shaft axis → paired fixed clevis cheeks, moving annular seats and returns attached outside the bearing rim | Existing breast pivot and captive shaft retained. Fixed arms seat on the actual thoracic rib web; breast returns follow the opening panel. All surfaces are rigid. Panel shell and its opening remain independent. | Six existing passive supports rebuilt; two passive seats added. All three source states. Hidden arrangement is a reconstruction, not a recovered historical mechanism. Owner whole-bird controls the unchanged exterior envelope. |
| Compact wings | Coplanar short shield and mantle backing → shield packet recessed 45 mm in the authored transverse space; receiving forks terminate at actual journal/liner surfaces | Canopy and all named pivots retained. A finite window in the right shield liner and two plates receives the upper load member through its sampled travel. Left restricted travel remains unchanged. No sheet bridges owners. | 28 rigid passive meshes changed; no powered hardware or sensing added. Owner flightless tucked-guard/short-shove direction controls the assembly. The 45 mm offset is an editable modeling choice, not an image measurement. |
| Neck, head, torso, pelvis, legs and feet | V28 form retained | Existing limitations and regional contract remain in the V28 checkpoint | No change to era eligibility. The July reference continues to control head only; its excluded body is not restored. |

All earlier era-specific part metadata is preserved. Source visibility is **not** a complete three-era reconstruction; the full procedural controls, transmission and advanced machinery are not loaded into this isolated viewer.

## Evidence of improvement and remaining failure

The [exact-composition hinge screen](../assets/audit/whole-character-v29/attempt-fit01/hinge-screen/comparison.json) removes all six hinge crossing identities at five opening angles. Total breast-neighbor counts change from **13/6/6/6/6 to 7/0/0/0/0**. The seven closed-state neck/root/receiving-cover identities remain failures outside that repair.

The [exact-composition wing screen](../assets/audit/whole-character-v29/attempt-fit01/wing-screen/receipt.json) changes folded/guard/shove counts from **52/54/57 to 38/38/37**. No edited-interface pairs or new neighbor pair identities occur in these three samples. The remaining retained-part witnesses are recorded and unresolved; inheritance is not an exemption.

The [neck screen](../assets/audit/whole-character-v29/attempt-fit01/neck-screen/screen.json) remains **5/17/5/9/6/4/4** across rest, Maker, attention, contact, thrust and both yaw extremes. These are discrete finite surface-crossing diagnostics, not continuous collision testing, penetration depths or physical simulation. Same-owner and fully contained overlap require other methods.

Root neck02 cut a sampled receiving aperture and reduced root interference, but independent visual review rejected the resulting detached-looking throat. Neck03 restored coverage using rigid inner returns but increased crossing counts to **10/23/14/18/10/10/11**. Both are preserved and excluded. Neck01 failed before a native was produced because duplicate convex-hull delete operands were supplied; its exact executed inputs and failure record remain.

The [independent decision](../assets/audit/whole-character-v29/independent-decision.md) retains the two bounded fit repairs and keeps overall artistic acceptance on hold. A lower collision count does not outweigh a worse silhouette.

## Review views and actual runtime

Matched neutral [front](../assets/audit/whole-character-v29/attempt-fit01/after-front.png), [side](../assets/audit/whole-character-v29/attempt-fit01/after-side.png), [three-quarter](../assets/audit/whole-character-v29/attempt-fit01/after-reference-angle.png), [rear](../assets/audit/whole-character-v29/attempt-fit01/after-rear.png) and [neck](../assets/audit/whole-character-v29/attempt-fit01/after-neck.png) use the V28 cameras. Regional packets preserve actual paired before/after views and both worker trials.

The actual browser [closed view](../assets/audit/whole-character-v29/attempt-fit01/browser/whole-neutral.png), [inspection view](../assets/audit/whole-character-v29/attempt-fit01/browser/inspection-open-separated.png) and [14.70-second recording](../assets/audit/whole-character-v29/attempt-fit01/browser/jaw-strike-jump-thrust.webm) show the exported derivative. Six motion samples—stepped turn, attention, strike, angled approach, jump and thrust—execute. All 619 scene objects restore exactly after motion and inspection. Source visibility counts are Maker 528, Mechanic 529 and Advanced 564. This does not establish complete era hardware, support physics or finished movement clearance.

Actual GLTFLoader validation compares all 618 native node world matrices with the GLB; finite vertex attributes, fixed cervical origins, rigid bases, pitch sum and pose restoration pass. Browser inspection opens/separates/reassembles and switches source-era visibility. Context-loss fallback loads the current still and disables 16 controls; reload restores WebGL and enabled controls. No unexpected browser warnings were captured before the intentional context loss.

Timing: visible Codex in-app browser on Apple M4 Max / ANGLE Metal, 1056×690 drawing buffer, DPR 1, closed neutral Advanced rest, 180 frames: median **10.0 ms**, P95 **10.9 ms**, 565 draw calls. This is one local condition, not a device-matrix benchmark.

## Build and publication boundary

`npm ci`, `npm run build` and both publication-boundary tests passed. All 133 declared output files match their bytes/hashes; 134 files include the release manifest. Production output still selects V9 and excludes V28/V29 studies, native files, private archives and provenance/source trees. Existing large-bundle and fsevents script-policy warnings remain. The build records parent revision `8d3d595` with a modified local tree; exact V29 identity is established above by content hashes. No push, remote CI or deployment was performed.

## Outstanding decisions and next implementation

The face remains generic, the breast has large plain bands, the shoulder transition is weak, and the tall stance lacks the target's grounded mass. Neck articulation coverage is unresolved. The current process has delivered real fit repairs but has not yet delivered the requested likeness; another fit-only checkpoint cannot close the owner's rejection.

The next visible improvement must address the whole-character head/breast/stance relationship with matched silhouette evidence. Keep the owner's early direction gate separate from automated checks. Do not begin final exterior treatment or publish this candidate as an accepted correction. F01–F04 stay OPEN, F05 PARTIAL, F06 GATED; F07–F09 retain bounded evidence only and F10 remains local verification.
