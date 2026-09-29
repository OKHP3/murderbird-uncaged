(async () => {
  const app = window.__uncaged, canvas = document.querySelector('#scene canvas');
  if (!canvas || app.metrics().kind !== 'webgl') throw Error('Actual WebGL required');
  const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
  const until = async (predicate, max = 7000) => {
    const start = performance.now();
    while (!predicate()) { if (performance.now() - start > max) throw Error('UI state did not settle'); await frame(); }
  };
  const dwell = async ms => { const begin = performance.now(); while (performance.now() - begin < ms) await frame(); };
  if (app.getSnapshot().paused) document.getElementById('pause').click();
  if (document.getElementById('reduced-motion').checked) document.getElementById('reduced-motion').click();
  const era = async value => {
    app.era(value);
    await until(() => app.metrics().era === value && !app.getSnapshot().pendingEra);
    app.reviewCamera('threeQuarter'); app.reviewLighting('neutral'); await frame();
  };
  await era('maker');
  const stream = canvas.captureStream(30);
  const recorder = new MediaRecorder(stream, {mimeType:'video/webm;codecs=vp9',videoBitsPerSecond:3000000});
  const chunks = [], segments = []; recorder.ondataavailable = event => {if(event.data.size) chunks.push(event.data);};
  const start = performance.now();
  const segment = async (label, action) => {
    const began = performance.now(); await action();
    segments.push({label, startSeconds:(began-start)/1000, endSeconds:(performance.now()-start)/1000,
      era:app.metrics().era, state:app.getSnapshot().state, motion:app.metrics().motion});
  };
  let failure = null;
  recorder.start();
  try {
    for (const id of ['leg','wing','tail','neck','jaw']) await segment('Maker external '+id, async () => {
      app.articulate(id,1); await dwell(1000); app.articulate(id,0); await dwell(1000);
    });
    await era('mechanic');
    await segment('Mechanic stepped drive', async () => {
      document.getElementById('run-mechanism').click(); await dwell(12000);
      document.getElementById('stop-mechanism').click();
    });
    await era('builder');
    for (const [id,label] of [['power-jump','Advanced jump'],['shield-thrust','Advanced shield thrust']]) {
      await until(() => !document.getElementById(id).disabled);
      await segment(label,async()=>{document.getElementById(id).click();await dwell(3300);});
    }
    await until(()=>!document.getElementById('reach').disabled);
    await segment('Advanced strike and recovery',async()=>{document.getElementById('reach').click();await dwell(11500);});
  } catch (error) { failure=error.message; }
  const stopped = new Promise(resolve=>recorder.onstop=resolve); recorder.stop(); await stopped;
  stream.getTracks().forEach(track=>track.stop());
  const blob = new Blob(chunks,{type:recorder.mimeType});
  const data = await new Promise(resolve=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.readAsDataURL(blob);});
  return {data,metadata:{modelUrl:app.metrics().modelUrl,kind:'actual full-exhibit canvas capture',mime:recorder.mimeType,
    requestedCaptureFPS:30,canvas:[canvas.width,canvas.height],seconds:(performance.now()-start)/1000,segments,failure,
    limits:'Real UI actions and runtime mechanisms. Sample demonstration, not physical simulation, continuous clearance, artistic acceptance or finished materials.'}};
})()
