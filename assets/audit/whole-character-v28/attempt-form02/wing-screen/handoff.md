# Exact V28 Form02 wing-neighbor screen

This bounded diagnostic evaluates the exact Form02 combined native and compares pair identities with exact Form01. No geometry or runtime source was edited; the native and frozen wing source hashes were checked before and after.

Three native rest-relative wing poses were sampled with the composed torso/head/neck/legs at neutral rest. Every builder-era eligible evaluated mesh was included regardless of saved display hiding; tests require different rigid owners and at least one mantle/shield owner. This covers adjacent body/head/neck/legs wherever bounds overlap.

| Pose | Strict owner-pair contacts | Involving changed wing geometry |
|---|---:|---:|
| folded | 52 | 16 |
| guard | 54 | 18 |
| short-shove | 57 | 22 |

## Form01 comparison

folded: 47 → 52 strict pairs; 5 new identities and 0 removed identities.

- New: `Proposed later left bearing strap v4` versus `V28 left canopy oblique course 1 plate 4`
- New: `V28 left canopy oblique course 5 plate 1` versus `V28 left short shield leading fold`
- New: `V28 left short nested shield 1 plate 2` versus `left profiled mantle backing v4 left-mantle`
- New: `V28 right canopy oblique course 5 plate 1` versus `V28 right short shield leading fold`
- New: `V28 right short nested shield 1 plate 2` versus `right profiled mantle backing v4 right-mantle`

guard: 51 → 54 strict pairs; 4 new identities and 1 removed identities.

- New: `Proposed later left bearing strap v4` versus `V28 left canopy oblique course 1 plate 5`
- New: `V28 left canopy anterior folded return` versus `V28 left short nested shield 1 plate 1`
- New: `V28 right canopy oblique course 4 plate 1` versus `V28 right short nested shield 1 plate 1`
- New: `V28 right canopy oblique course 4 plate 7` versus `V28 right short nested shield 2 plate 5`
- Removed: `V28 right canopy oblique course 5 plate 1` versus `V28 right short nested shield 1 plate 1`

short-shove: 54 → 57 strict pairs; 3 new identities and 0 removed identities.

- New: `Proposed later left bearing strap v4` versus `V28 left canopy oblique course 1 plate 5`
- New: `V28 left canopy anterior folded return` versus `V28 left short nested shield 1 plate 1`
- New: `V28 right short nested shield 2 plate 3` versus `right profiled mantle backing v4 right-mantle`


## Actual identities

### folded

| Part A | Part B | Triangle witnesses |
|---|---|---:|
| left coaxial elbow journal | left swept upper wing load member | 56 |
| left profiled mantle backing v4 left-mantle | left profiled mantle backing v4 left-wing-shield | 5 |
| left profiled mantle backing v4 left-mantle | Proposed later left bearing strap v4 | 72 |
| left profiled mantle backing v4 left-mantle | V28 left short nested shield 1 plate 1 | 144 |
| left profiled mantle backing v4 left-mantle | V28 left short nested shield 1 plate 2 | 74 |
| left profiled mantle backing v4 left-mantle | V28 left short shield leading fold | 69 |
| left shouldered shoulder journal | V23 shoulder load link 1 | 49 |
| left shouldered shoulder journal | V24 fixed shoulder receiving journal 1 | 50 |
| left shouldered shoulder journal | V24 shoulder lower load fork 1 | 40 |
| left stepped elbow race -0.015 | left swept upper wing load member | 51 |
| left stepped elbow race 0.011 | left swept upper wing load member | 30 |
| left stepped shoulder race -0.033 | V23 shoulder load link 1 | 78 |
| left stepped shoulder race -0.033 | V24 fixed shoulder receiving journal 1 | 276 |
| left stepped shoulder race -0.033 | V24 shoulder lower load fork 1 | 42 |
| left stepped shoulder race -0.044 | V23 shoulder load link 1 | 82 |
| left stepped shoulder race -0.044 | V24 fixed shoulder receiving journal 1 | 140 |
| left stepped shoulder race -0.044 | V24 shoulder lower load fork 1 | 33 |
| left swept upper wing load member | V23 shoulder load link 1 | 32 |
| left swept upper wing load member | V24 fixed shoulder receiving journal 1 | 10 |
| left swept upper wing load member | V24 shoulder lower load fork 1 | 30 |
| left swept upper wing load member | V28 left nested shield receiving fork 1 | 48 |
| left swept upper wing load member | V28 left nested shield receiving fork 2 | 30 |
| Proposed later left bearing strap v4 | V28 left canopy oblique course 1 plate 4 | 8 |
| right coaxial elbow journal | right swept upper wing load member | 56 |
| right profiled mantle backing v4 right-mantle | right profiled mantle backing v4 right-wing-shield | 5 |
| right profiled mantle backing v4 right-mantle | V28 right short nested shield 1 plate 1 | 145 |
| right profiled mantle backing v4 right-mantle | V28 right short nested shield 1 plate 2 | 76 |
| right profiled mantle backing v4 right-mantle | V28 right short shield leading fold | 69 |
| right shouldered shoulder journal | V23 shoulder load link -1 | 51 |
| right shouldered shoulder journal | V24 fixed shoulder receiving journal -1 | 48 |
| right shouldered shoulder journal | V24 shoulder lower load fork -1 | 40 |
| right stepped elbow race -0.015 | right swept upper wing load member | 30 |
| right stepped elbow race 0.011 | right swept upper wing load member | 51 |
| right stepped shoulder race 0.033 | V23 shoulder load link -1 | 67 |
| right stepped shoulder race 0.033 | V24 fixed shoulder receiving journal -1 | 154 |
| right stepped shoulder race 0.033 | V24 shoulder lower load fork -1 | 46 |
| right stepped shoulder race 0.044 | V23 shoulder load link -1 | 65 |
| right stepped shoulder race 0.044 | V24 rising thoracic receiving cheek -1 | 59 |
| right stepped shoulder race 0.044 | V24 shoulder lower load fork -1 | 14 |
| right swept upper wing load member | V23 shoulder load link -1 | 31 |
| right swept upper wing load member | V24 fixed shoulder receiving journal -1 | 10 |
| right swept upper wing load member | V24 shoulder lower load fork -1 | 28 |
| right swept upper wing load member | V28 right nested shield receiving fork 1 | 45 |
| right swept upper wing load member | V28 right nested shield receiving fork 2 | 32 |
| V21 refined left shoulder journal bonnet | V23 shoulder load link 1 | 38 |
| V21 refined right shoulder journal bonnet | V23 shoulder load link -1 | 38 |
| V23 shoulder load link -1 | V24 mantle captive shoulder shaft -1 | 71 |
| V23 shoulder load link 1 | V24 mantle captive shoulder shaft 1 | 71 |
| V24 mantle captive shoulder shaft -1 | V24 shoulder lower load fork -1 | 46 |
| V24 mantle captive shoulder shaft 1 | V24 shoulder lower load fork 1 | 46 |
| V28 left canopy oblique course 5 plate 1 | V28 left short shield leading fold | 56 |
| V28 right canopy oblique course 5 plate 1 | V28 right short shield leading fold | 58 |

### guard

| Part A | Part B | Triangle witnesses |
|---|---|---:|
| left coaxial elbow journal | left swept upper wing load member | 56 |
| left profiled mantle backing v4 left-mantle | left profiled mantle backing v4 left-wing-shield | 123 |
| left profiled mantle backing v4 left-mantle | Proposed later left bearing strap v4 | 68 |
| left profiled mantle backing v4 left-mantle | V28 left short nested shield 2 plate 5 | 28 |
| left shouldered shoulder journal | V23 shoulder load link 1 | 48 |
| left shouldered shoulder journal | V24 fixed shoulder receiving journal 1 | 50 |
| left shouldered shoulder journal | V24 shoulder lower load fork 1 | 44 |
| left stepped elbow race -0.015 | left swept upper wing load member | 49 |
| left stepped elbow race 0.011 | left swept upper wing load member | 30 |
| left stepped shoulder race -0.033 | V23 shoulder load link 1 | 76 |
| left stepped shoulder race -0.033 | V24 fixed shoulder receiving journal 1 | 280 |
| left stepped shoulder race -0.033 | V24 shoulder lower load fork 1 | 44 |
| left stepped shoulder race -0.044 | V23 shoulder load link 1 | 80 |
| left stepped shoulder race -0.044 | V24 fixed shoulder receiving journal 1 | 140 |
| left stepped shoulder race -0.044 | V24 shoulder lower load fork 1 | 31 |
| left swept upper wing load member | V23 shoulder load link 1 | 32 |
| left swept upper wing load member | V24 fixed shoulder receiving journal 1 | 6 |
| left swept upper wing load member | V24 shoulder lower load fork 1 | 28 |
| left swept upper wing load member | V28 left nested shield receiving fork 1 | 48 |
| left swept upper wing load member | V28 left nested shield receiving fork 2 | 42 |
| Proposed later left bearing strap v4 | V28 left canopy oblique course 1 plate 5 | 22 |
| right coaxial elbow journal | right swept upper wing load member | 58 |
| right profiled mantle backing v4 right-mantle | right profiled mantle backing v4 right-wing-shield | 98 |
| right profiled mantle backing v4 right-mantle | V28 right short nested shield 2 plate 4 | 110 |
| right profiled mantle backing v4 right-mantle | V28 right short nested shield 2 plate 5 | 176 |
| right profiled mantle backing v4 right-wing-shield | V28 right canopy anterior folded return | 81 |
| right shouldered shoulder journal | V23 shoulder load link -1 | 47 |
| right shouldered shoulder journal | V24 fixed shoulder receiving journal -1 | 48 |
| right shouldered shoulder journal | V24 shoulder lower load fork -1 | 40 |
| right stepped elbow race -0.015 | right swept upper wing load member | 30 |
| right stepped elbow race 0.011 | right swept upper wing load member | 50 |
| right stepped shoulder race 0.033 | V23 shoulder load link -1 | 66 |
| right stepped shoulder race 0.033 | V24 fixed shoulder receiving journal -1 | 152 |
| right stepped shoulder race 0.033 | V24 shoulder lower load fork -1 | 46 |
| right stepped shoulder race 0.044 | V23 shoulder load link -1 | 64 |
| right stepped shoulder race 0.044 | V24 rising thoracic receiving cheek -1 | 69 |
| right stepped shoulder race 0.044 | V24 shoulder lower load fork -1 | 14 |
| right swept upper wing load member | V23 shoulder load link -1 | 35 |
| right swept upper wing load member | V24 fixed shoulder receiving journal -1 | 10 |
| right swept upper wing load member | V24 shoulder lower load fork -1 | 30 |
| right swept upper wing load member | V28 right nested shield receiving fork 1 | 50 |
| right swept upper wing load member | V28 right nested shield receiving fork 2 | 46 |
| V21 refined left shoulder journal bonnet | V23 shoulder load link 1 | 46 |
| V21 refined right shoulder journal bonnet | V23 shoulder load link -1 | 24 |
| V23 shoulder load link -1 | V24 mantle captive shoulder shaft -1 | 71 |
| V23 shoulder load link 1 | V24 mantle captive shoulder shaft 1 | 71 |
| V24 mantle captive shoulder shaft -1 | V24 shoulder lower load fork -1 | 46 |
| V24 mantle captive shoulder shaft 1 | V24 shoulder lower load fork 1 | 44 |
| V28 left canopy anterior folded return | V28 left short nested shield 1 plate 1 | 5 |
| V28 left canopy anterior folded return | V28 left short shield leading fold | 143 |
| V28 left canopy oblique course 5 plate 1 | V28 left short nested shield 1 plate 1 | 160 |
| V28 right canopy anterior folded return | V28 right short nested shield 1 plate 1 | 88 |
| V28 right canopy oblique course 4 plate 1 | V28 right short nested shield 1 plate 1 | 8 |
| V28 right canopy oblique course 4 plate 7 | V28 right short nested shield 2 plate 5 | 38 |

### short-shove

| Part A | Part B | Triangle witnesses |
|---|---|---:|
| left coaxial elbow journal | left swept upper wing load member | 56 |
| left profiled mantle backing v4 left-mantle | left profiled mantle backing v4 left-wing-shield | 123 |
| left profiled mantle backing v4 left-mantle | Proposed later left bearing strap v4 | 70 |
| left profiled mantle backing v4 left-mantle | V28 left short nested shield 2 plate 5 | 28 |
| left shouldered shoulder journal | V23 shoulder load link 1 | 48 |
| left shouldered shoulder journal | V24 fixed shoulder receiving journal 1 | 50 |
| left shouldered shoulder journal | V24 shoulder lower load fork 1 | 42 |
| left stepped elbow race -0.015 | left swept upper wing load member | 49 |
| left stepped elbow race 0.011 | left swept upper wing load member | 30 |
| left stepped shoulder race -0.033 | V23 shoulder load link 1 | 76 |
| left stepped shoulder race -0.033 | V24 fixed shoulder receiving journal 1 | 280 |
| left stepped shoulder race -0.033 | V24 shoulder lower load fork 1 | 44 |
| left stepped shoulder race -0.044 | V23 shoulder load link 1 | 78 |
| left stepped shoulder race -0.044 | V24 fixed shoulder receiving journal 1 | 140 |
| left stepped shoulder race -0.044 | V24 shoulder lower load fork 1 | 31 |
| left swept upper wing load member | V23 shoulder load link 1 | 32 |
| left swept upper wing load member | V24 fixed shoulder receiving journal 1 | 6 |
| left swept upper wing load member | V24 shoulder lower load fork 1 | 28 |
| left swept upper wing load member | V28 left nested shield receiving fork 1 | 48 |
| left swept upper wing load member | V28 left nested shield receiving fork 2 | 42 |
| Proposed later left bearing strap v4 | V28 left canopy oblique course 1 plate 5 | 28 |
| right coaxial elbow journal | right swept upper wing load member | 60 |
| right profiled mantle backing v4 right-mantle | right profiled mantle backing v4 right-wing-shield | 120 |
| right profiled mantle backing v4 right-mantle | V28 right short nested shield 2 plate 3 | 20 |
| right profiled mantle backing v4 right-mantle | V28 right short nested shield 2 plate 4 | 172 |
| right profiled mantle backing v4 right-mantle | V28 right short nested shield 2 plate 5 | 166 |
| right profiled mantle backing v4 right-wing-shield | V28 right canopy anterior folded return | 39 |
| right profiled mantle backing v4 right-wing-shield | V28 right canopy oblique course 3 plate 8 | 94 |
| right profiled mantle backing v4 right-wing-shield | V28 right canopy oblique course 4 plate 7 | 98 |
| right shouldered shoulder journal | V23 shoulder load link -1 | 48 |
| right shouldered shoulder journal | V24 fixed shoulder receiving journal -1 | 50 |
| right shouldered shoulder journal | V24 shoulder lower load fork -1 | 40 |
| right stepped elbow race -0.015 | right swept upper wing load member | 30 |
| right stepped elbow race 0.011 | right swept upper wing load member | 50 |
| right stepped shoulder race 0.033 | V23 shoulder load link -1 | 62 |
| right stepped shoulder race 0.033 | V24 fixed shoulder receiving journal -1 | 152 |
| right stepped shoulder race 0.033 | V24 shoulder lower load fork -1 | 44 |
| right stepped shoulder race 0.044 | V23 shoulder load link -1 | 56 |
| right stepped shoulder race 0.044 | V24 rising thoracic receiving cheek -1 | 73 |
| right stepped shoulder race 0.044 | V24 shoulder lower load fork -1 | 16 |
| right swept upper wing load member | V23 shoulder load link -1 | 35 |
| right swept upper wing load member | V24 fixed shoulder receiving journal -1 | 10 |
| right swept upper wing load member | V24 shoulder lower load fork -1 | 30 |
| right swept upper wing load member | V28 right nested shield receiving fork 1 | 40 |
| right swept upper wing load member | V28 right nested shield receiving fork 2 | 46 |
| V21 refined left shoulder journal bonnet | V23 shoulder load link 1 | 46 |
| V23 shoulder load link -1 | V24 mantle captive shoulder shaft -1 | 69 |
| V23 shoulder load link 1 | V24 mantle captive shoulder shaft 1 | 71 |
| V24 mantle captive shoulder shaft -1 | V24 shoulder lower load fork -1 | 46 |
| V24 mantle captive shoulder shaft 1 | V24 shoulder lower load fork 1 | 44 |
| V28 left canopy anterior folded return | V28 left short nested shield 1 plate 1 | 5 |
| V28 left canopy anterior folded return | V28 left short shield leading fold | 143 |
| V28 left canopy oblique course 5 plate 1 | V28 left short nested shield 1 plate 1 | 160 |
| V28 right canopy oblique course 3 plate 8 | V28 right short nested shield 2 plate 4 | 54 |
| V28 right canopy oblique course 3 plate 8 | V28 right short nested shield 2 plate 5 | 148 |
| V28 right canopy oblique course 4 plate 7 | V28 right short nested shield 2 plate 4 | 82 |
| V28 right canopy oblique course 4 plate 7 | V28 right short nested shield 2 plate 5 | 180 |

## Limits

These are strict triangle surface crossing witnesses, not collision-clearance or full-motion acceptance. Retained machinery and repaired hardware contacts remain in the report. No physical simulation, continuous sweep, complete attachment verification or likeness acceptance is claimed. No wholly contained-overlap guarantee; same-owner overlaps excluded. Exact coordinates and owner groups are in `receipt.json`.

Native SHA256: `838a86b16766ddd4491c9f1cbe6a7aa0039c2b9e8514a04eb710d1e9b2f9bd9d`

Wing source SHA256: `12ca01952c5b3d2a8551bf46c5e3d3b3ad26fa442b6a9ae3f505e1f564ea6da1`
