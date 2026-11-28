import lyrics from '../assets/lyrics.txt?raw'

const loopBytes = 30880257
const loopHash = 'd9bc121c0c2f1a04ff8456b8aeea1ae6d48fdc1777119ef4823bebc458425a72'
const loopParts = [
  ['loop-a.bin', 16777216, '2ba794a303136aabf87f7718443acee358ea2b61e8431fcc6b12c29feff66bda'],
  ['loop-b.bin', 14103041, '7ddf62587fcb471bdba6ea1639e843b2263b508dad29d573b4213e2c2fddddca'],
]
const durations = {full: 147.75, loop: 145.384625}
const clock = time => Math.floor(time / 60) + ':' + String(Math.floor(time % 60)).padStart(2, '0')

async function sha256(bytes) {
  const digest = await crypto.subtle.digest('SHA-256', bytes)
  return Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2, '0')).join('')
}

async function fetchLoop(asset, signal) {
  const parts = await Promise.all(loopParts.map(async ([name, length, digest]) => {
    const response = await fetch(asset(name), {signal})
    if (!response.ok) throw new Error('The lossless loop could not be loaded.')
    const bytes = await response.arrayBuffer()
    if (bytes.byteLength !== length || await sha256(bytes) !== digest) {
      throw new Error('The lossless loop download was incomplete or damaged.')
    }
    return new Uint8Array(bytes)
  }))
  const joined = new Uint8Array(loopBytes)
  let offset = 0
  for (const part of parts) { joined.set(part, offset); offset += part.length }
  return joined.buffer
}

export function installMedia(asset, onMediaStart = () => {}) {
  const element = id => document.getElementById(id)
  const song = element('song'), pilot = element('pilot')
  const version = element('music-version'), play = element('music-play'), mute = element('music-mute')
  const volume = element('music-volume'), seek = element('music-seek'), status = element('music-status')
  const companion = element('loop-companion'), fileInput = element('loop-file')
  const localFile = location.protocol === 'file:' || typeof window.exhibitAsset === 'function'
  let context, gain, buffer, loopSource, startedAt, controller
  let state = 'idle', ticket = 0, fileRevision = 0, offset = 0, muted = false, loadedFile = null
  element('lyrics').textContent = lyrics

  function position() {
    if (version.value === 'full') return song.currentTime || 0
    return loopSource ? (offset + context.currentTime - startedAt) % buffer.duration : offset
  }
  function updateTime() {
    const pos = position(), total = durations[version.value]
    seek.max = String(total)
    seek.value = String(pos)
    seek.setAttribute('aria-valuetext', clock(pos) + ' of ' + clock(total))
    element('music-time').textContent = clock(pos) + ' / ' + clock(total)
  }
  function render() {
    play.textContent = state === 'loading' ? 'Cancel loading' : state === 'playing' ? 'Pause music' : 'Play music'
    const needsFile = localFile && version.value === 'loop' && !loadedFile
    play.disabled = needsFile
    element('music-restart').disabled = needsFile || state === 'loading'
    seek.disabled = state === 'loading' || (version.value === 'full' ? song.readyState < 1 : !buffer)
    companion.hidden = !(localFile && version.value === 'loop')
    updateTime()
  }
  function setLevel() {
    const level = Number(volume.value) / 100
    song.volume = level
    song.muted = muted
    if (gain) gain.gain.setValueAtTime(muted ? 0 : level, context.currentTime)
    mute.setAttribute('aria-pressed', String(muted))
    mute.textContent = muted ? 'Unmute music' : 'Mute music'
    element('music-level').textContent = volume.value + '%'
  }
  function stop(reset = false) {
    const last = position()
    ticket++
    controller?.abort()
    controller = null
    if (loopSource) {
      loopSource.stop()
      loopSource.disconnect()
      loopSource = null
    }
    song.pause()
    if (reset && song.readyState) song.currentTime = 0
    offset = reset ? 0 : last
    state = 'idle'
    render()
  }
  function pause() {
    if (state !== 'idle') {
      stop()
      status.textContent = 'Music paused.'
    }
    pilot.pause()
  }
  function startLoop(at) {
    offset = at % buffer.duration
    startedAt = context.currentTime
    loopSource = context.createBufferSource()
    loopSource.buffer = buffer
    loopSource.loop = true
    loopSource.loopStart = 0
    loopSource.loopEnd = buffer.duration
    loopSource.connect(gain)
    loopSource.start(0, offset)
  }
  async function start(restart = false) {
    if (restart) stop(true)
    const request = ++ticket
    pilot.pause()
    onMediaStart()
    state = 'loading'
    status.textContent = 'Loading the selected recording…'
    render()
    try {
      if (version.value === 'full') {
        if (!song.getAttribute('src')) song.src = asset('full-song.mp3')
        if (song.ended) song.currentTime = 0
        await song.play()
      } else {
        const Audio = window.AudioContext || window.webkitAudioContext
        if (!Audio) throw new Error('This browser cannot play the lossless loop.')
        context ||= new Audio({sampleRate: 48000})
        await context.resume()
        if (ticket !== request) return
        if (!gain) { gain = context.createGain(); gain.connect(context.destination); setLevel() }
        if (!buffer) {
          let bytes
          if (localFile) {
            if (!loadedFile) throw new Error('Open the companion FLAC first.')
            bytes = await loadedFile.arrayBuffer()
          } else {
            controller = new AbortController()
            bytes = await fetchLoop(asset, controller.signal)
          }
          if (ticket !== request) return
          if (bytes.byteLength !== loopBytes) throw new Error('The selected file has the wrong size.')
          const decoded = await context.decodeAudioData(bytes)
          if (ticket !== request) return
          buffer = decoded
        }
        startLoop(offset)
      }
      if (ticket !== request) return
      state = 'playing'
      controller = null
      status.textContent = version.value === 'loop' ? 'Lossless loop playing continuously.' : 'Full song playing.'
      render()
    } catch (error) {
      if (ticket !== request) return
      stop()
      status.textContent = error.message + ' Select Play music to try again.'
    }
  }
  version.addEventListener('change', () => {
    stop(true)
    status.textContent = version.value === 'loop' && localFile && !loadedFile ?
      'The lossless recording is available in the review kit.' : 'Recording selected. Choose Play music to begin.'
  })
  fileInput.addEventListener('change', async () => {
    stop(true)
    const revision = ++fileRevision, file = fileInput.files[0]
    loadedFile = null
    buffer = null
    render()
    if (!file) return
    try {
      if (file.size !== loopBytes) throw new Error('Choose the original seamless-loop.flac supplied with the review kit.')
      const bytes = await file.arrayBuffer()
      const hash = await sha256(bytes)
      if (hash !== loopHash) throw new Error('This file differs from the accepted loop. Choose the copy supplied with the review kit.')
      if (fileRevision !== revision) return
      loadedFile = file
      if (version.value === 'loop') status.textContent = 'Accepted loop verified. Choose Play music to begin.'
    } catch (error) {
      if (fileRevision === revision && version.value === 'loop') status.textContent = error.message
    }
    render()
  })
  play.addEventListener('click', () => {
    if (state === 'idle') start()
    else { stop(); status.textContent = 'Music paused.' }
  })
  element('music-restart').addEventListener('click', () => start(true))
  mute.addEventListener('click', () => { muted = !muted; setLevel() })
  volume.addEventListener('input', setLevel)
  seek.addEventListener('input', () => {
    const at = Number(seek.value)
    if (version.value === 'full') song.currentTime = at
    else if (loopSource) { loopSource.stop(); loopSource.disconnect(); startLoop(at) }
    else offset = at
    updateTime()
  })
  song.addEventListener('loadedmetadata', render)
  song.addEventListener('ended', () => {
    if (version.value === 'full') { state = 'idle'; status.textContent = 'Full song finished.'; render() }
  })
  song.addEventListener('error', () => {
    if (!song.getAttribute('src')) return
    if (version.value === 'full') stop()
    song.removeAttribute('src')
    song.load()
    if (version.value === 'full') status.textContent = 'The full song could not be loaded. Select Play music to try again.'
  })
  const pilotPanel = element('pilot-panel')
  pilotPanel.addEventListener('toggle', () => {
    if (!pilotPanel.open) { pilot.pause(); return }
    if (!pilot.getAttribute('src')) {
      pilot.poster = asset('murderbird-first-choice-poster.jpg')
      pilot.src = asset('murderbird-first-choice-635f0e15.mp4')
    }
  })
  pilot.addEventListener('play', () => {
    stop()
    onMediaStart()
    status.textContent = 'Music paused while the silent pilot plays.'
  })
  pilot.addEventListener('error', () => {
    element('pilot-status').textContent = 'The silent pilot could not be loaded. Close this panel and reopen it to retry.'
    pilot.removeAttribute('src')
  })
  window.setInterval(() => { if (state === 'playing' && element('music-panel').open) updateTime() }, 250)
  window.addEventListener('pagehide', pause)
  setLevel()
  render()
  return {pause}
}
