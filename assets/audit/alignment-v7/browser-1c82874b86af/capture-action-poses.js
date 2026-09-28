(async()=>{
 const results=[],start=performance.now();window.__v7Poses={complete:false,results};
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 async function ready(selector){const start=performance.now();while(!document.querySelector(selector)||document.querySelector(selector).disabled){if(performance.now()-start>30000)throw Error('ready timeout '+selector);await sleep(50)}}
 async function capture(label,predicate){return new Promise((resolve,reject)=>{const begin=performance.now();function tick(){const m=__uncaged.metrics();if(predicate(m)){const canvas=document.querySelector('#scene canvas');results.push({label,seconds:(performance.now()-start)/1000,snapshot:__uncaged.getSnapshot(),metrics:m,png:canvas.toDataURL('image/png')});resolve()}else if(performance.now()-begin>30000)reject(Error('pose timeout '+label));else requestAnimationFrame(tick)}requestAnimationFrame(tick)})}
 async function run(){
  __uncaged.reviewCamera('threeQuarterLeft');__uncaged.reviewLighting('neutral');
  await ready('#power-jump');document.querySelector('#power-jump').click();
  await capture('jump-airborne',m=>m.motion.powerMove?.kind==='jump'&&m.motion.powerMove.height>.22);
  await ready('#shield-thrust');document.querySelector('#shield-thrust').click();
  await capture('shield-thrust-extended',m=>m.motion.powerMove?.kind==='thrust'&&m.motion.powerMove.phase>.45&&m.motion.powerMove.phase<.7);
  await ready('#claw-scrape');__uncaged.reviewCamera('feet');document.querySelector('#claw-scrape').click();
  await capture('claw-contact-exact',m=>m.motion.clawAction?.contact===true);
  await ready('#reach');__uncaged.reviewCamera('threeQuarter');document.querySelector('#reach').click();
  await capture('bill-contact-exact',m=>m.motion.contact===true);document.querySelector('#retreat').click();
 }
 run().catch(e=>window.__v7Poses.error=String(e)).finally(()=>window.__v7Poses.complete=true);
 return {started:true,method:'Same requestAnimationFrame callback reads metrics and rendered canvas; no video seek matching; normal clock; scripted controls'};
})()
