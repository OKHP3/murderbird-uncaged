// Gesture-armed mechanical foley. Source time is also the playback clock.
const cues = {
  advanced: [[1.5, 168, .22, -.5], [1.875, 80, .48, -.15], [2.958, 114, .22, .16], [6.375, 370, .13, .42]],
  mechanic: [[.15, 186, .18, -.55], [.92, 260, .09, -.2], [1.86, 168, .13, .1], [2.78, 330, .11, .34], [3.73, 192, .12, -.2], [4.72, 125, .27, -.4]],
  approach: [[.35, 200, .1, .25], [1.3, 141, .18, -.2], [2.35, 310, .13, .5], [3.45, 97, .25, -.1]],
  patrol: Array.from({length:8},(_,i)=>[i+.81,i%2?78:97,.20,i%2?.45:-.45]),
  maker: [[0, 113, .15, -.6]],
}
export function createFoley() {
  let ctx, master, enabled = false, activity = 0
  const active = new Set()
  function silence() {
    for (const source of active) { try {source.stop()} catch {} }
    active.clear()
  }
  function mute() {
    enabled=false; silence()
    if (master) master.gain.value = 0
  }
  async function enable() {
    ctx ||= new (window.AudioContext || window.webkitAudioContext)()
    if (!master) { master = ctx.createGain(); master.connect(ctx.destination) }
    await ctx.resume()
    master.gain.value = .39
    enabled = true
  }
  function strike(freq, duration, side, era) {
    if (!enabled || !ctx || ctx.state !== 'running') return
    const t = ctx.currentTime
    const stereo = ctx.createStereoPanner()
    stereo.pan.value = Math.max(-1,Math.min(1,side))
    stereo.connect(master)
    let remaining = 3
    for (let i=0;i<3;i++) {
      const src = ctx.createOscillator(), env = ctx.createGain()
      src.type = i===2 && era==='mechanic' ? 'triangle':'sine'
      src.frequency.setValueAtTime(freq*[1,2.71,5.19][i],t)
      src.frequency.exponentialRampToValueAtTime(freq*[.68,2.23,4.71][i],t+duration)
      env.gain.setValueAtTime(.0001,t);env.gain.exponentialRampToValueAtTime(.19/(i+1),t+.009)
      env.gain.exponentialRampToValueAtTime(.0001,t+duration)
      src.connect(env).connect(stereo);active.add(src)
      src.onended=()=>{active.delete(src);src.disconnect();env.disconnect();if(!--remaining)stereo.disconnect()}
      src.start(t);src.stop(t+duration+.01)
    }
    activity++
  }
  return {enable,mute,silence,get enabled(){return enabled},get time(){return enabled ? ctx.currentTime:null},get count(){return activity},
    advance(mode,from,to,pan=1) {for (const [at,f,d,s] of cues[mode]||[]) if(at>from && at<=to)strike(f,d,s*pan,mode)},
    contact(lane){strike(212,.17,lane==='left'?-.65:lane==='right'?.65:0,'advanced')},
    hand(value,pan=1) {strike(95+value*160,.11,-.6*pan,'maker')}
  }
}
