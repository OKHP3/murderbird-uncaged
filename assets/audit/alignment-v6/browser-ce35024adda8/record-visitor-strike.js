(async()=>{
  await new Promise((resolve,reject)=>{const start=performance.now();function check(){if(window.__uncaged?.metrics()?.kind==='webgl')resolve();else if(performance.now()-start>15000)reject(Error('WebGL startup timeout'));else requestAnimationFrame(check)}check()});
  const canvas=document.querySelector('#scene canvas'), start=performance.now(), chunks=[], samples=[], events=[];
  const mime=['video/webm;codecs=vp9','video/webm;codecs=vp8','video/webm'].find(MediaRecorder.isTypeSupported);
  const recorder=new MediaRecorder(canvas.captureStream(30),{mimeType:mime,videoBitsPerSecond:2500000});
  const result={run:'visitor-strike-confirmed-contact',declaredSha256:'ce35024adda89681a0f37e7018e2563a74af67cd06558a887222df87b78a87fe',modelUrl:__uncaged.metrics().modelUrl,clock:'Normal browser requestAnimationFrame and performance.now; UI controls with condition waits; no accelerated step',initialSnapshot:__uncaged.getSnapshot(),initialMetrics:__uncaged.metrics(),mime,requestedFps:30,canvas:{width:canvas.width,height:canvas.height},complete:false,sequenceComplete:false,samples,events};
  window.__v6Demo={result,recorder};
  function sample(){const m=__uncaged.metrics(),s=__uncaged.getSnapshot();samples.push({seconds:(performance.now()-start)/1000,hidden:document.hidden,snapshot:s,era:m.era,open:m.open,separation:m.separation,motion:m.motion,wingAngles:m.wingAngles,performance:m.performance});}
  sample();const timer=setInterval(sample,100);
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
  recorder.onstop=async()=>{clearInterval(timer);sample();const blob=new Blob(chunks,{type:mime}),bytes=new Uint8Array(await blob.arrayBuffer());let value='';for(let i=0;i<bytes.length;i+=32768)value+=String.fromCharCode(...bytes.subarray(i,i+32768));window.__v6Demo.base64=btoa(value);result.bytes=bytes.length;result.durationSeconds=(performance.now()-start)/1000;result.hiddenSamples=samples.filter(s=>s.hidden).length;result.complete=true;};
  const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
  const log=(name,detail={})=>events.push({seconds:(performance.now()-start)/1000,name,...detail});
  async function waitFor(test,label,timeout=18000){const t=performance.now();while(!test()){if(performance.now()-t>timeout)throw Error('Timed out: '+label);await sleep(50)}}
  async function click(selector,label){await waitFor(()=>{const e=document.querySelector(selector);return e&&!e.disabled},label);document.querySelector(selector).click();log(label);}
  async function era(name){await click('[data-era="'+name+'"]','select '+name);await waitFor(()=>__uncaged.getSnapshot().era===name&&!__uncaged.getSnapshot().pendingEra&&__uncaged.metrics().motion.settled,'settled '+name);await sleep(300);}
  async function lever(id,value){const selector='#lever-'+id;await waitFor(()=>!document.querySelector(selector).disabled,'lever '+id);const e=document.querySelector(selector);e.value=String(value);e.dispatchEvent(new Event('input',{bubbles:true}));log('Maker '+id,{value});}
  function camera(name){__uncaged.reviewCamera(name);log('camera '+name);}
  async function sequence(){
    camera('threeQuarter');__uncaged.reviewLighting('exhibit');
    await click('#reach','visitor reach request');
    await waitFor(()=>__uncaged.metrics().motion.contact,'actual bill contact',25000);
    log('actual bill contact',{motion:__uncaged.metrics().motion});
    await waitFor(()=>__uncaged.getSnapshot().state==='recover','strike recovery',5000);
    log('entered strike recovery',{state:__uncaged.getSnapshot().state});
    await click('#retreat','visitor retreat after contact');await sleep(5000);
    result.sequenceComplete=true;log('sequence complete');
  }
  recorder.start(1000);const watchdog=setTimeout(()=>{log('watchdog timeout');if(recorder.state==='recording')recorder.stop()},40000);
  sequence().catch(e=>{result.error=String(e);log('sequence failed',{error:String(e)})}).finally(()=>{clearTimeout(watchdog);if(recorder.state==='recording')recorder.stop()});
  return {started:true,run:result.run,initialTime:result.initialMetrics.motion.time,mime};
})()
