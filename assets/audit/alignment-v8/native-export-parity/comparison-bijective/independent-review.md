# Independent review: bijective position comparison

The revised matcher addresses the prior cardinality-collapse concern. It first rejects unequal unique-point counts, builds candidates within the declared 10 µm tolerance, and uses augmenting-path reassignment to find a maximum one-to-one matching. The three added fixtures exercise unequal cardinality, equal-count collapse, and a case where greedy nearest matching would fail but reassignment finds the valid pairing. I found no correctness issue in that matching logic.

The current bound result is **pass** for the exact V8 native and GLB hashes recorded in `geometry-parity.json`: 102 position groups, 51/51 rigid pivots, and 235788 triangles. The fixture receipt reports all nine cases true. The independent source hash recorded in that result identifies the inspected comparator.

Remaining scope is stated accurately: position sets, triangle counts, semantic group tags, and listed pivots are compared; topology, winding, normals, UVs, shader behavior, and motion are not established. No rerun was performed for this review.
