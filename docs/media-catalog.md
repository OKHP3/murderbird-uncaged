# MurderBird media catalog

This collection supports the interactive exhibit without treating every draft
as approved publication material. Historical notes retain the status and paths
they had when written; this catalog provides current navigation.

| Material | Entry point | Current evidence |
|---|---|---|
| Origin story | [Story snapshot](../content/story/README.md) | Exact English source and published-page snapshots; public editorial route remains on overkillhill.com. |
| Character and visual direction | [Unified direction](murderbird-unified-direction.md), [art direction](../assets/murderbird/v2/ART-DIRECTION.md) | Fictional character canon and historical design direction. |
| Accepted website stills | [Website release register](../provenance/website-support/tests/fixtures/murderbird-still-release-register.json) | The website's existing accepted subset, preserved as evidence. Acceptance does not extend to all image variants. |
| Image masters and variants | [V2 library](../assets/murderbird/v2/README.md), `assets/img/`, `context/threads/` | Masters, derivatives, original sigil lineage, candidates, and rejected studies retain their original status. |
| Skillz Forge related artwork | [Related source copy](../assets/related/skillz/README.md) | Public Forge consumer derivatives, with unknown underlying generation lineage; retained separately and not approved as new exhibit inputs. |
| Video source collection | `assets/murderbird/production/video/`, [historical migration notes](../assets/docs/murderbird-video-migration-2026-09-08.md) | Legacy clips and pilots include held or rejected motion; preserve duplicate source copies. |
| Website motion clip | `assets/video/murderbird-first-choice-635f0e15.mp4` | Existing public website delivery copy. No new artistic approval is inferred. |
| Accepted sung theme v3 | [Audio brief](audio-brief.md), [release provenance](../provenance/iron-verdict-v3-release.json) | Owner accepted the synthesized sung theme and authorized publication; full-song MP3 and lossless loop are explicit app inputs. Editable sessions and stems remain local. |
| Historical Iron Verdict music | [Audio production README](../assets/murderbird/production/audio/iron-verdict/README.md) | Instrumental demo, GarageBand session and preview, MIDI, stems, arrangement, and source scripts. |
| Lyrics and vocal composition | [Performance sheet v2](../assets/murderbird/production/audio/iron-verdict/vocal-score-v2/performance-sheet.md) | Complete lyrics and notated melody with PDF, MusicXML, MIDI, pitch guide, and rehearsal mix. These are not a recorded singer's performance. |
| Earlier lyric and private sessions | `.local/archives/` in the owner's Mac clone | Preserved local archives include the earlier lyric and production sessions. Private library/profile context stays local. |
| Local 3D assembly study | [Production handoff](production-handoff.md), `assets/models/uncaged-study/` | New editable Blender source and grouped GLB; revised proportions await owner review. [Local verification](acceptance-report.md) is separate from artistic acceptance or release. |
| 3D staging | [Scale-stage notes](../assets/murderbird/v2/production/README.md) | Blender scale proxy, not a finished character model or rig. |
| Interactive app | `src/` | Procedural Three.js study, illustrated fallback, optional synthesized soundscape, and visitor-controlled accepted theme song. Imported visual production archives remain separate from the viewer. |

## Working from the collection

Use the original files as sources. Make deliberate, documented delivery copies
for the app and retain the source relationship. Do not move the production
archive into `public/`, autoplay music or video, substitute a rehearsal guide
for finished vocals, or treat mismatched stills as a coherent 3D turntable.

Imported scripts and notes can retain old absolute paths and tool assumptions.
They are preserved evidence. Review and adapt an active production copy before
running it; the import does not prove that an old workstation environment runs
unchanged on Replit or another computer.

Frozen imported dependency pins preserve reproducibility. The website audio
Dependabot entry was retired when its source tree moved. Establish an active
production working copy and its update checks before changing these pins; do
not let an automatic update overwrite the recorded source snapshot.

## Heavy-machine/predator mass study — September 27

The separate `assets/models/uncaged-mass-study/` Blender source and GLB respond to the owner's later strength/speed clarification. They are editable local studies, not accepted finished art. See [direction](mechanical-predator-direction.md), [current review](mass-study-review.md), and [derivative provenance](../provenance/uncaged-mass-study-2026-09-27.json). The original `uncaged-study/` files remain intact.
