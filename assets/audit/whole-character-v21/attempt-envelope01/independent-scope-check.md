# Independent V21 saved-native scope check

The pinned source native still has SHA256 `eb15a9d87de56fb8a06004d9c69448c38089f0ecacd888e3e7fde921a353d42a`. The saved candidate at `assets/models/whole-character-v21/attempt-envelope01/murderbird-whole-character-v21.blend` matches its receipt SHA256 `81406a3b7b3243f9dc3cc4eeed65d9cf8b28e5c087f24f723028493e2ee997b0`.

Independent Blender inspection confirms 52 named EMPTY pivots with identical names and parent relationships. Only world rest pivots `neck`, `cervical-upper`, and `head` differ. Their candidate world positions are respectively `(0,-0.170000,1.300000)`, `(0,-0.240000,1.455000)`, and `(0,-0.280000,1.580000)`. Local compensation also updates child/anchor transforms; this does not change their world-space results.

The candidate has 614 evaluated finite meshes: 573 retained source meshes, 171 staged-out source meshes, and 41 added meshes. For every same-named retained mesh, the exact ordered world-space evaluated vertex-coordinate digest matches the source; no parent changes were found. This includes every retained mesh under the head/crown/jaw/bill/optic subtree (160), wings (193), and legs/feet (184). All 41 new meshes have a direct rigid parent, `region`, `surfaceRole`, `exteriorEras`, and `constructionClass` metadata; they are marked proposed passive and eligible in all three eras. Owner distribution: body 16, cervical-upper 9, neck 9, breastplate 6, head 1.

The body still carries V20 `mechanismLayoutV1` socket metadata, while its V21 `sharedEnvelopeV21` property explicitly calls those sockets stale under the new rests. This candidate is native-only: there is no sibling GLB and no V21 runtime route. The check did not assess collisions, surface joins, movement, load path strength, rendering, or artistic acceptance.

Machine-readable counts and input identities are in [`independent-scope-check.json`](independent-scope-check.json). The independent read-only Blender snapshot comparison used Blender 5.2.1 LTS and did not render or edit either native.
