# V29 coarse02 interface fit screen on V28 Form02

This bounded diagnostic evaluates the exact V29 coarse02 combined native and compares pair identities with exact V28 Form02. No geometry or runtime source was edited; the native and frozen wing source hashes were checked before and after.

Three native rest-relative wing poses were sampled with the composed torso/head/neck/legs at neutral rest. Every builder-era eligible evaluated mesh was included regardless of saved display hiding; tests require different rigid owners and at least one mantle/shield owner. This covers adjacent body/head/neck/legs wherever bounds overlap.

| Pose | Strict owner-pair contacts | Involving changed V29 interface geometry |
|---|---:|---:|
| folded | 38 | 0 |
| guard | 38 | 0 |
| short-shove | 37 | 0 |

## V28 Form02 comparison

folded: 52 → 38 strict pairs; 0 new identities and 14 removed identities.

- Removed: `V28 left canopy oblique course 5 plate 1` versus `V28 left short shield leading fold`
- Removed: `V28 left nested shield receiving fork 1` versus `left swept upper wing load member`
- Removed: `V28 left nested shield receiving fork 2` versus `left swept upper wing load member`
- Removed: `V28 left short nested shield 1 plate 1` versus `left profiled mantle backing v4 left-mantle`
- Removed: `V28 left short nested shield 1 plate 2` versus `left profiled mantle backing v4 left-mantle`
- Removed: `V28 left short shield leading fold` versus `left profiled mantle backing v4 left-mantle`
- Removed: `V28 right canopy oblique course 5 plate 1` versus `V28 right short shield leading fold`
- Removed: `V28 right nested shield receiving fork 1` versus `right swept upper wing load member`
- Removed: `V28 right nested shield receiving fork 2` versus `right swept upper wing load member`
- Removed: `V28 right short nested shield 1 plate 1` versus `right profiled mantle backing v4 right-mantle`
- Removed: `V28 right short nested shield 1 plate 2` versus `right profiled mantle backing v4 right-mantle`
- Removed: `V28 right short shield leading fold` versus `right profiled mantle backing v4 right-mantle`
- Removed: `left profiled mantle backing v4 left-mantle` versus `left profiled mantle backing v4 left-wing-shield`
- Removed: `right profiled mantle backing v4 right-mantle` versus `right profiled mantle backing v4 right-wing-shield`

guard: 54 → 38 strict pairs; 0 new identities and 16 removed identities.

- Removed: `V28 left canopy anterior folded return` versus `V28 left short nested shield 1 plate 1`
- Removed: `V28 left canopy anterior folded return` versus `V28 left short shield leading fold`
- Removed: `V28 left canopy oblique course 5 plate 1` versus `V28 left short nested shield 1 plate 1`
- Removed: `V28 left nested shield receiving fork 1` versus `left swept upper wing load member`
- Removed: `V28 left nested shield receiving fork 2` versus `left swept upper wing load member`
- Removed: `V28 left short nested shield 2 plate 5` versus `left profiled mantle backing v4 left-mantle`
- Removed: `V28 right canopy anterior folded return` versus `V28 right short nested shield 1 plate 1`
- Removed: `V28 right canopy anterior folded return` versus `right profiled mantle backing v4 right-wing-shield`
- Removed: `V28 right canopy oblique course 4 plate 1` versus `V28 right short nested shield 1 plate 1`
- Removed: `V28 right canopy oblique course 4 plate 7` versus `V28 right short nested shield 2 plate 5`
- Removed: `V28 right nested shield receiving fork 1` versus `right swept upper wing load member`
- Removed: `V28 right nested shield receiving fork 2` versus `right swept upper wing load member`
- Removed: `V28 right short nested shield 2 plate 4` versus `right profiled mantle backing v4 right-mantle`
- Removed: `V28 right short nested shield 2 plate 5` versus `right profiled mantle backing v4 right-mantle`
- Removed: `left profiled mantle backing v4 left-mantle` versus `left profiled mantle backing v4 left-wing-shield`
- Removed: `right profiled mantle backing v4 right-mantle` versus `right profiled mantle backing v4 right-wing-shield`

short-shove: 57 → 37 strict pairs; 0 new identities and 20 removed identities.

- Removed: `V28 left canopy anterior folded return` versus `V28 left short nested shield 1 plate 1`
- Removed: `V28 left canopy anterior folded return` versus `V28 left short shield leading fold`
- Removed: `V28 left canopy oblique course 5 plate 1` versus `V28 left short nested shield 1 plate 1`
- Removed: `V28 left nested shield receiving fork 1` versus `left swept upper wing load member`
- Removed: `V28 left nested shield receiving fork 2` versus `left swept upper wing load member`
- Removed: `V28 left short nested shield 2 plate 5` versus `left profiled mantle backing v4 left-mantle`
- Removed: `V28 right canopy anterior folded return` versus `right profiled mantle backing v4 right-wing-shield`
- Removed: `V28 right canopy oblique course 3 plate 8` versus `V28 right short nested shield 2 plate 4`
- Removed: `V28 right canopy oblique course 3 plate 8` versus `V28 right short nested shield 2 plate 5`
- Removed: `V28 right canopy oblique course 3 plate 8` versus `right profiled mantle backing v4 right-wing-shield`
- Removed: `V28 right canopy oblique course 4 plate 7` versus `V28 right short nested shield 2 plate 4`
- Removed: `V28 right canopy oblique course 4 plate 7` versus `V28 right short nested shield 2 plate 5`
- Removed: `V28 right canopy oblique course 4 plate 7` versus `right profiled mantle backing v4 right-wing-shield`
- Removed: `V28 right nested shield receiving fork 1` versus `right swept upper wing load member`
- Removed: `V28 right nested shield receiving fork 2` versus `right swept upper wing load member`
- Removed: `V28 right short nested shield 2 plate 3` versus `right profiled mantle backing v4 right-mantle`
- Removed: `V28 right short nested shield 2 plate 4` versus `right profiled mantle backing v4 right-mantle`
- Removed: `V28 right short nested shield 2 plate 5` versus `right profiled mantle backing v4 right-mantle`
- Removed: `left profiled mantle backing v4 left-mantle` versus `left profiled mantle backing v4 left-wing-shield`
- Removed: `right profiled mantle backing v4 right-mantle` versus `right profiled mantle backing v4 right-wing-shield`


## Actual identities

### folded

| Part A | Part B | Triangle witnesses |
|---|---|---:|
| left coaxial elbow journal | left swept upper wing load member | 56 |
| left profiled mantle backing v4 left-mantle | Proposed later left bearing strap v4 | 72 |
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
| Proposed later left bearing strap v4 | V28 left canopy oblique course 1 plate 4 | 8 |
| right coaxial elbow journal | right swept upper wing load member | 56 |
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
| V21 refined left shoulder journal bonnet | V23 shoulder load link 1 | 38 |
| V21 refined right shoulder journal bonnet | V23 shoulder load link -1 | 38 |
| V23 shoulder load link -1 | V24 mantle captive shoulder shaft -1 | 71 |
| V23 shoulder load link 1 | V24 mantle captive shoulder shaft 1 | 71 |
| V24 mantle captive shoulder shaft -1 | V24 shoulder lower load fork -1 | 46 |
| V24 mantle captive shoulder shaft 1 | V24 shoulder lower load fork 1 | 46 |

### guard

| Part A | Part B | Triangle witnesses |
|---|---|---:|
| left coaxial elbow journal | left swept upper wing load member | 56 |
| left profiled mantle backing v4 left-mantle | Proposed later left bearing strap v4 | 68 |
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
| Proposed later left bearing strap v4 | V28 left canopy oblique course 1 plate 5 | 22 |
| right coaxial elbow journal | right swept upper wing load member | 58 |
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
| V21 refined left shoulder journal bonnet | V23 shoulder load link 1 | 46 |
| V21 refined right shoulder journal bonnet | V23 shoulder load link -1 | 24 |
| V23 shoulder load link -1 | V24 mantle captive shoulder shaft -1 | 71 |
| V23 shoulder load link 1 | V24 mantle captive shoulder shaft 1 | 71 |
| V24 mantle captive shoulder shaft -1 | V24 shoulder lower load fork -1 | 46 |
| V24 mantle captive shoulder shaft 1 | V24 shoulder lower load fork 1 | 44 |

### short-shove

| Part A | Part B | Triangle witnesses |
|---|---|---:|
| left coaxial elbow journal | left swept upper wing load member | 56 |
| left profiled mantle backing v4 left-mantle | Proposed later left bearing strap v4 | 70 |
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
| Proposed later left bearing strap v4 | V28 left canopy oblique course 1 plate 5 | 28 |
| right coaxial elbow journal | right swept upper wing load member | 60 |
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
| V21 refined left shoulder journal bonnet | V23 shoulder load link 1 | 46 |
| V23 shoulder load link -1 | V24 mantle captive shoulder shaft -1 | 69 |
| V23 shoulder load link 1 | V24 mantle captive shoulder shaft 1 | 71 |
| V24 mantle captive shoulder shaft -1 | V24 shoulder lower load fork -1 | 46 |
| V24 mantle captive shoulder shaft 1 | V24 shoulder lower load fork 1 | 44 |

## Limits

These are strict triangle surface crossing witnesses, not collision-clearance or full-motion acceptance. Retained machinery and repaired hardware contacts remain in the report. No physical simulation, continuous sweep, complete attachment verification or likeness acceptance is claimed. No wholly contained-overlap guarantee; same-owner overlaps excluded. Exact coordinates and owner groups are in `receipt.json`.

Native SHA256: `2eacf9639f0590aafbf16ba1eeac8fb81bf71f17de2d3c05b5b9c142049b567c`

Wing source SHA256: `139d7e6fba09474e9ca2d56c7029a64b24a62bce0c96e212e8d85c11c9f3ef6a`
