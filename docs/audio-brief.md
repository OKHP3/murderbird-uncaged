# Audio brief

The owner's September 26 production direction controls the new theme: an original,
roughly 2½-minute guitar-led rock/metal entrance song with intelligible sung vocals,
a strong chorus, and a heavy, deliberate, weathered character. The earlier workshop
work-song direction below is historical design context, not a constraint on this song.

## Proposed exhibit states

These states are a design brief. The normal app uses an optional synthesized
soundscape. An explicitly enabled local listening preview can audition selected
new production masters; no new production audio is bundled or published. Playback
must begin with a visitor action.

| State | Content | Trigger |
|---|---|---|
| Attract / idle | Instrumental bed, low volume, subtle mechanical ticks | Visitor enables sound |
| Explore | Instrumental bed, ducked lower, SFX one-shots layered on top | Rotate / inspect / hotspot open |
| Climax | Full vocal theme song, unducked | Completing the three-era arc |

Needs Web Audio API (gain-node ducking, low-latency one-shots, crossfade into climax), not `<audio>` tags.

## Available production material

The September 26 migration includes the [Iron Verdict production tree](../assets/murderbird/production/audio/iron-verdict/README.md):
instrumental demo, GarageBand session and preview, MIDI, seven aligned stems,
arrangement, and reproducible source. The [v2 performance sheet](../assets/murderbird/production/audio/iron-verdict/vocal-score-v2/performance-sheet.md)
contains the full lyric and performance directions; the same folder holds
the notated melody, MusicXML, MIDI, pitch guide, and rehearsal mix.

These are source and audition materials. No recorded vocalist performance
or completed vocal audition is established. The earlier lyric draft remains
in the owner's private local session archive. Preserve the imported files;
create approved delivery copies and record their provenance when integrating
music into the exhibit. See the [media catalog](media-catalog.md).

## Local theme audition

Run `MURDERBIRD_THEME_PREVIEW=1 npm run dev -- --host 127.0.0.1` and open the
printed loopback URL. The listening panel provides play/pause, restart, volume,
mute, elapsed time, loading/error feedback, and a full-song/seamless-loop selector.
It fetches only after a playback action, decodes WAV with Web Audio, and uses a
looping `AudioBufferSourceNode` for sample-continuous repetition. The production
master itself must still have a verified musical loop boundary; the player does
not manufacture one. Track selection stops playback and waits for another Play.

The local middleware exposes exactly two selected delivery masters:

| Local route | Private local delivery master |
|---|---|
| `/__theme-preview/full.wav` | `.local/theme-production/masters/iron-verdict-full.wav` |
| `/__theme-preview/loop.wav` | `.local/theme-production/masters/iron-verdict-loop.wav` |

The server must bind to loopback. Requests from non-loopback connections, other
hosts, or cross-origin browser contexts are rejected. These masters are opt-in
local browser responses only; sessions, stems, provenance, archives, and other
private files have no preview route. Direct Vite file serving of `.local/` and
`provenance/` is denied. The selected master paths cannot be symbolic links.
Missing masters produce a recoverable message in the player.

The listening panel uses the existing soundscape's Web Audio context and an
independent song gain. While the song plays, the synthesized background pulse is
suppressed; the existing SOUND control still governs optional interaction effects.
Ordinary builds and `vite preview` omit the listening panel and preview middleware,
even if the environment flag is set. Run `npm ci` and `npm run build`, then inspect
all `dist/` files before any future release. Local playback, a successful build,
technical audio checks, and the owner's listening acceptance are separate evidence.
