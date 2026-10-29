/** Inject into the local production page before reload through the browser QA API.
 * Observations only: no thresholds, simulated app state, audio, or acceptance.
 */
(() => {
  const run = window.__asusRun = {
    schema: 'asus-browser-run/v1', startedAt: new Date().toISOString(),
    representativeWorkload: 'Foreground V37 cold load, Advanced encounter, inspection, Maker and Mechanic transitions over two minutes after 3D readiness.',
    frames: [], heap: [], events: [], hiddenFrames: 0, done: false,
    viewportCssPixels: { width: innerWidth, height: innerHeight }, devicePixelRatio,
    networkConditions: 'Cache disabled; 25 Mbps downstream/upstream and 50 ms emulated latency; loopback server.',
    probeInjectedAtMs: performance.now(),
    inputFeedbackDefinition: 'Elapsed from click capture to a changed essential DOM feedback state and the following animation frame; conservative rendered-feedback observation, not human usability acceptance.',
  };
  document.addEventListener('click', event => {
    if (run.done) return;
    const button = event.target.closest('button');
    if (!button || !button.closest('#controls, [aria-label="Choose construction era"], .inspection-controls')) return;
    const record = { atMs: performance.now(), id: button.id || button.dataset.era,
      text: button.textContent?.trim().slice(0, 80) };
    const feedback = () => JSON.stringify({ status: document.querySelector('#encounter-status')?.textContent,
      pressed: button.getAttribute('aria-pressed'), disabled: button.disabled });
    const before = feedback();
    run.events.push(record);
    function observe(time) {
      if (feedback() !== before) {
        requestAnimationFrame(painted => { record.feedbackMs = painted - record.atMs; });
      } else if (time - record.atMs < 2000) requestAnimationFrame(observe);
      else record.feedbackMissing = true;
    }
    requestAnimationFrame(observe);
  }, { capture: true });
  let statusObserved = false, sceneObserved = false;
  function awaitScene(now) {
    const loading = document.querySelector('#loading');
    if (!statusObserved && loading && !loading.hidden && loading.getBoundingClientRect().height > 0) {
      statusObserved = true;
      requestAnimationFrame(painted => { run.usefulLoadingStatusMs = painted; });
    }
    const canvas = document.querySelector('#scene canvas');
    if (!loading?.hidden || !canvas) { requestAnimationFrame(awaitScene); return; }
    if (sceneObserved) return;
    sceneObserved = true;
    // Observe readiness after the app has had a frame to draw the loaded model.
    requestAnimationFrame(start);
    function start(now) {
    const gl = canvas.getContext('webgl2'), ext = gl.getExtension('WEBGL_debug_renderer_info');
    run.renderer = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
    run.interactiveSceneMs = now;
    run.viewportCssPixels = { width: innerWidth, height: innerHeight };
    run.sceneViewportCssPixels = { width: canvas.clientWidth, height: canvas.clientHeight };
    run.drawingBuffer = { width: canvas.width, height: canvas.height };
    let previous = now;
    function tick(time) {
      run.frames.push(time - previous); previous = time;
      run.hiddenFrames += Number(document.hidden);
      if (run.frames.length % 60 === 0 && performance.memory) run.heap.push(performance.memory.usedJSHeapSize);
      if (time - now < 120000) { requestAnimationFrame(tick); return; }
      run.observedDurationSeconds = (time - now) / 1000;
      run.finishedAt = new Date().toISOString(); run.done = true;
      const sorted = [...run.frames].sort((a, b) => a - b);
      run.frameSummary = {
        count: sorted.length, medianFrameMs: sorted[Math.floor((sorted.length - 1) * .5)],
        p95FrameMs: sorted[Math.floor((sorted.length - 1) * .95)], maxFrameMs: sorted.at(-1),
        stuttersOver50Ms: sorted.filter(value => value > 50).length,
        stuttersOver100Ms: sorted.filter(value => value > 100).length,
      };
      run.observedHeapPeakBytes = Math.max(0, ...run.heap);
      run.essentialInputResponse = {
        observedInputs: run.events.length,
        completedInputs: run.events.filter(event => Number.isFinite(event.feedbackMs)).length,
        missingFeedback: run.events.filter(event => !Number.isFinite(event.feedbackMs)).length,
        maxFeedbackMs: run.events.length && run.events.every(event => Number.isFinite(event.feedbackMs))
          ? Math.max(...run.events.map(event => event.feedbackMs)) : null,
      };
      run.resources = performance.getEntriesByType('resource').map(entry => ({
        url: entry.name, transferSize: entry.transferSize, encodedBodySize: entry.encodedBodySize,
        decodedBodySize: entry.decodedBodySize, duration: entry.duration,
      }));
    }
    requestAnimationFrame(tick);
    }
  }
  requestAnimationFrame(awaitScene);
})();
