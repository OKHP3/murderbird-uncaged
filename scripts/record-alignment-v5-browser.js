// Inject through the supported browser developer interface on the local DEV exhibit.
// Records the actual WebGL canvas at normal application speed, without audio.
// No __uncaged.step() calls are used during this recording.
(() => {
  if (window.__v5LiveReview) throw new Error('A recording already exists; preserve it before restarting.');
  const canvas = document.querySelector('#viewer canvas');
  if (!canvas || __uncaged.metrics().kind === 'illustrated') throw new Error('Live canvas required.');
  const stream = canvas.captureStream(30);
  const mimeType = 'video/webm;codecs=vp9';
  if (!MediaRecorder.isTypeSupported(mimeType)) throw new Error('VP9 recorder unavailable.');
  const recorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 3000000 });
  const chunks = [];
  const record = window.__v5LiveReview = {
    startedAt: new Date().toISOString(), start: performance.now(), events: [], samples: [],
    method: 'Actual WebGL canvas captureStream at requested 30fps; normal application clock; no audio; 250ms telemetry. UI outside canvas is not recorded.',
    viewport: { width: innerWidth, height: innerHeight, dpr: devicePixelRatio },
    canvas: { width: canvas.width, height: canvas.height },
    complete: false,
  };
  const elapsed = () => (performance.now() - record.start) / 1000;
  function act(name, fn) {
    const event = { name, seconds: elapsed() };
    try { event.result = fn(); } catch (e) { event.error = String(e); }
    record.events.push(event);
  }
  function click(id) {
    const node = document.getElementById(id);
    if (!node || node.disabled) throw new Error(`${id} unavailable`);
    node.click();
    return 'UI action dispatched; observed state in samples determines completion';
  }
  const at = (seconds, name, fn) => setTimeout(() => act(name, fn), seconds * 1000);
  const reset = () => ['jaw','neck','wing','leg','tail'].forEach(id => __uncaged.articulate(id, 0));
  recorder.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
  recorder.onstop = async () => {
    clearInterval(sampler);
    stream.getTracks().forEach(t => t.stop());
    const blob = new Blob(chunks, {type: mimeType});
    const reader = new FileReader();
    reader.onload = () => { record.dataUrl = reader.result; record.bytes = blob.size; record.complete = true; };
    reader.readAsDataURL(blob);
    record.durationSeconds = elapsed();
  };
  const sampler = setInterval(() => {
    const m = __uncaged.metrics();
    record.samples.push({ seconds: elapsed(), hidden: document.hidden, snapshot: __uncaged.getSnapshot(), motion: m.motion, open: m.open, separation: m.separation, performance: m.performance });
  }, 250);
  recorder.start(1000);
  act('select Maker', () => __uncaged.era('maker'));
  at(2, 'neutral three-quarter camera', () => { __uncaged.reviewLighting('neutral'); __uncaged.reviewCamera('threeQuarter'); });
  for (const [index,id] of ['jaw','neck','wing','leg','tail'].entries()) {
    at(3 + index*4, `Maker ${id}`, () => __uncaged.articulate(id, 1));
    at(6 + index*4, `release ${id}`, reset);
  }
  at(23,'select Mechanic',() => __uncaged.era('mechanic'));
  at(26,'Mechanic camera',() => __uncaged.reviewCamera('threeQuarter'));
  at(27,'Mechanic start',() => click('run-mechanism'));
  at(41,'Mechanic stop after cycle',() => click('stop-mechanism'));
  at(47,'select Advanced',() => __uncaged.era('builder'));
  at(50,'Advanced camera',() => __uncaged.reviewCamera('threeQuarter'));
  at(51,'Advanced jump',() => click('power-jump'));
  at(59,'Advanced shield thrust',() => click('shield-thrust'));
  at(65,'Advanced claw scrape',() => click('claw-scrape'));
  at(78,'Advanced reach',() => click('reach'));
  at(88,'Advanced retreat',() => click('retreat'));
  at(96,'Advanced inspect',() => click('section-toggle'));
  at(102,'Advanced separate',() => { const n=document.getElementById('separation'); if(n.disabled)throw new Error('separation unavailable');n.value='100';n.dispatchEvent(new Event('input',{bubbles:true})); });
  at(108,'Advanced reassemble',() => click('reassemble'));
  at(115,'stop capture',() => recorder.stop());
  return { started: record.startedAt, requestedDurationSeconds: 115, canvas: record.canvas };
})();
