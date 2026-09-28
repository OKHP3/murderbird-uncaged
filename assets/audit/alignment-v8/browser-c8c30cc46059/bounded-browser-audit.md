# Bounded browser evidence audit — V8

Status: **completed machine-evidence audit; no visual acceptance claim.** The browser recorded the exact V8 GLB `c8c30cc46059cdd117baf9dce4ceb6ca47040f402618dda419b21acc9d984385` with HTTP 200 (4,636,416 bytes), and the local file hash matches. Motion sequence flags are `complete=true` and `sequenceComplete=true`.

## Motion and coverage

The recording script says it used normal browser `performance.now()` and UI waits with no accelerated stepping. It captured **868 telemetry samples** over 86.654 s; the sampling interval median was 0.100 s (range 0.049–0.106). Samples by era were Maker 313, Mechanic 315, and Advanced/builder 240. It recorded 52 UI/action events and 0 hidden samples at the sample instants.

Coverage represented in telemetry:

- **Maker:** jaw, neck, wing, leg, and tail levers reached sampled endpoints 0 and 1, returned to 0, and jaw/neck were also combined then released.
- **Mechanic:** one mechanism routine was engaged and stopped after its cycle. Sampled stages include load, dwell, release, settle, and disengaged.
- **Advanced/builder:** jump and shield-thrust stages were sampled; claw scrape samples cover approach, lift, contact, scrape, release, and recovery, with `contact=true` in five scrape samples. Visitor reach was followed by actual bill contact, strike recovery, then retreat.
- **Inspection:** all three eras were opened, separated to 100%, and reassembled in the motion sequence. The 15 settled static captures cover closed, open at 0/50/100% separation, and reassembled for each era. The 3 fallback captures identify a selected fixed preview for each era.

**Coverage gap:** there is no deliberate cage-test control event or full cage-test cycle. The only cage telemetry is the initial sample at 0.008 s, at phase 0.930 of an `edge-probe`, with near-zero extension and no contact. The motion script does not dwell at 50% inspection separation; that state is represented only by static captures.

## Timing and errors

The canvas capture requested 30 fps at 856×648. ffprobe found h264 MP4 duration 86.589 s, 2599000/86589 average fps, and 2599 frames. The VP9 WebM has the same 2599 frames but no reported container duration. JSON recorder elapsed time is 86.818 s, about 0.229 s longer than the MP4 duration. Do not treat these clocks as identical.

Sampled app telemetry reports a rolling frame-time P50 of 10.0 ms and P95 median of 11.7 ms, with a median reported P50 FPS of 100. These are app-reported values observed at roughly 100 ms intervals, not an external profiler or sustained benchmark.

No sequence error is recorded and the GLB request returned HTTP 200. The four input manifests do not include browser console, uncaught-exception, or resource-error logs, so the evidence cannot establish a clean console. `hiddenSamples=0` applies only at sampled instants.

## Evidence and limits

Machine data and hashes are recorded in [bounded-browser-audit.json](bounded-browser-audit.json). The audit hashes all four source JSON files, the local GLB, recording script, MP4/WebM, 15 static PNGs, 3 fallback screenshots, and the 3 referenced fallback preview assets. This review did not watch the video or inspect screenshot appearance; it makes no visual acceptance, deployment, or exhaustive trajectory claim.
