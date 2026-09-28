// Supported browser developer injection: supplemental normal-speed claw clip.
// The first broad demonstration's fixed schedule hit disabled action controls.
// This capture waits for the real control to become available; no time stepping.
(() => {
  if (window.__v5ClawReview) throw new Error('Preserve the existing claw capture.');
  const canvas = document.querySelector('#viewer canvas');
  const stream = canvas.captureStream(30);
  const recorder = new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp9',videoBitsPerSecond:3000000});
  const chunks=[];
  const r=window.__v5ClawReview={start:performance.now(),startedAt:new Date().toISOString(),events:[],samples:[],complete:false,method:'Normal application clock, actual canvas, silent; waits for enabled claw control; no accelerated steps.'};
  const time=()=> (performance.now()-r.start)/1000;
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
  recorder.onstop=()=>{clearInterval(timer);stream.getTracks().forEach(t=>t.stop());const b=new Blob(chunks,{type:'video/webm'});const f=new FileReader();f.onload=()=>{r.dataUrl=f.result;r.bytes=b.size;r.complete=true;};f.readAsDataURL(b);r.durationSeconds=time();};
  __uncaged.reviewCamera('threeQuarter');
  let clicked=false;
  const timer=setInterval(()=>{
    const m=__uncaged.metrics(); const snapshot=__uncaged.getSnapshot();
    r.samples.push({seconds:time(),hidden:document.hidden,snapshot,motion:m.motion});
    if(!clicked&&!document.getElementById('claw-scrape').disabled){
      document.getElementById('claw-scrape').click();clicked=true;r.events.push({name:'claw dispatched',seconds:time()});
    }
  },100);
  recorder.start(1000);
  setTimeout(()=>{r.events.push({name:'stop',seconds:time(),clawDispatched:clicked});recorder.stop();},20000);
  return {startedAt:r.startedAt};
})();
