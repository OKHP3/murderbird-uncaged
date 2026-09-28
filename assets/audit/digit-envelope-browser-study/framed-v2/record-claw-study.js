(async () => {
  const output = window.__digitBrowserStudy = { complete: false, samples: [], frames: [], events: [] };
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  let cleanup = () => {};
  try {
    // Accelerated setup is separate from the subsequent normal-clock capture.
    __uncaged.era('maker'); __uncaged.step(3);
    __uncaged.era('builder'); __uncaged.step(2);
    __uncaged.reviewCamera('feet'); __uncaged.reviewLighting('neutral');
    document.querySelector('[data-view="out"]').click(); document.querySelector('[data-view="out"]').click();
    await sleep(200);
    const canvas = document.querySelector('#scene canvas');
    if (!canvas || __uncaged.metrics()?.kind !== 'webgl') throw Error('WebGL unavailable');
    const chunks = [], stream = canvas.captureStream(30);
    const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
    const recorder = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 4000000 });
    cleanup = () => { if (recorder.state !== 'inactive') recorder.stop(); stream.getTracks().forEach(track => track.stop()); };
    const stopped = new Promise(resolve => {
      recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: mime });
        output.video = await new Promise(done => { const reader = new FileReader(); reader.onload = () => done(reader.result); reader.readAsDataURL(blob); });
        output.videoBytes = blob.size; stream.getTracks().forEach(track => track.stop()); resolve();
      };
    });
    output.setup = { accelerated: true, purpose: 'Era reset only; capture below uses ordinary animation clock', metrics: __uncaged.metrics() };
    const start = performance.now();
    recorder.start(200);
    output.events.push({ seconds: 0, event: 'recording-start' });
    let running = true, contact = false, recovery = false, lastSample = -1000;
    const frame = () => {
      const now = performance.now(), metrics = __uncaged.metrics();
      const seconds = (now - start) / 1000;
      if (now - lastSample > 80) {
        output.samples.push({ seconds, hidden: document.hidden, state: metrics.state,
          claw: metrics.motion.clawAction, feet: metrics.motion.feet.map(foot => ({ side: foot.side, groundMin: foot.groundMin, digits: foot.digits })) });
        lastSample = now;
      }
      const action = metrics.motion.clawAction;
      if (action?.contact && !contact) {
        contact = true; output.frames.push({ name: 'claw-contact', seconds, metrics, png: canvas.toDataURL('image/png') });
      }
      if (contact && action?.stage === 'recovery' && !recovery) {
        recovery = true; output.frames.push({ name: 'claw-recovery', seconds, metrics, png: canvas.toDataURL('image/png') });
      }
      if (running && !output.complete) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
    await sleep(600);
    const waitStart = performance.now();
    while (document.querySelector('#claw-scrape').disabled) {
      if (performance.now() - waitStart > 8000) throw Error('Claw control never became ready');
      await sleep(50);
    }
    document.querySelector('#claw-scrape').click();
    output.events.push({ seconds: (performance.now() - start) / 1000, event: 'claw-scrape-control-click' });
    await sleep(6000);
    running = false; recorder.stop(); await stopped;
    output.durationSeconds = (performance.now() - start) / 1000;
    output.final = __uncaged.metrics();
    if (!contact) throw Error('No contact frame observed');
  } catch (error) { output.error = String(error); cleanup(); }
  output.complete = true;
  return { complete: output.complete, error: output.error, frames: output.frames.map(frame => frame.name), samples: output.samples.length };
})()
