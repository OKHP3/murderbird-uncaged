import './theme-player.css';

// The full song uses its listening copy; the loop is lossless and repeats exact
// decoded samples. Private working masters remain an opt-in local override.
const localPreview = import.meta.env.DEV && __LOCAL_THEME_PREVIEW__;
const tracks = localPreview ? {
  full: '/__theme-preview/full.wav',
  loop: '/__theme-preview/loop.wav',
} : {
  full: `${import.meta.env.BASE_URL}audio/iron-verdict-v3/full-song.mp3`,
  loop: `${import.meta.env.BASE_URL}audio/iron-verdict-v3/seamless-loop.flac`,
};

export function mountThemePlayer(container, sound, { onStart = () => {} } = {}) {
  const panel = document.createElement('section');
  panel.className = 'theme-player';
  panel.setAttribute('aria-labelledby', 'theme-title');
  panel.innerHTML = `
    <div class="theme-heading"><div><p class="theme-eyebrow">${localPreview ? 'LOCAL LISTENING PREVIEW' : 'THE SOUND OF MURDERBIRD'}</p><h3 id="theme-title">Iron Verdict</h3></div><span class="theme-badge">MURDERBIRD THEME</span></div>
    <p class="theme-description">Choose the full song or repeating exhibit mix. Playback begins when you press Play. <a href="${import.meta.env.BASE_URL}audio/iron-verdict-v3/lyrics.txt">Read the lyrics</a>.</p>
    <div class="theme-controls">
      <button id="theme-play" type="button" aria-pressed="false">Play</button>
      <button id="theme-restart" type="button">Restart</button>
      <label class="theme-mode">Version<select id="theme-version"><option value="full">Full song</option><option value="loop">Seamless loop</option></select></label>
    </div>
    <div class="theme-level"><button id="theme-mute" type="button" aria-pressed="false">Mute</button><label for="theme-volume">Volume</label><input id="theme-volume" type="range" min="0" max="100" value="60" /><output id="theme-volume-value" for="theme-volume">60%</output></div>
    <div class="theme-progress"><span id="theme-status" role="status">Ready when you are.</span><span id="theme-time" aria-label="Playback time">0:00 / —</span></div>`;
  container.append(panel);

  const play = panel.querySelector('#theme-play');
  const restart = panel.querySelector('#theme-restart');
  const mode = panel.querySelector('#theme-version');
  const mute = panel.querySelector('#theme-mute');
  const volume = panel.querySelector('#theme-volume');
  const volumeValue = panel.querySelector('#theme-volume-value');
  const status = panel.querySelector('#theme-status');
  const time = panel.querySelector('#theme-time');
  const buffers = new Map();
  let context, gain, source, loading, requestId = 0, offset = 0, startTime = 0, muted = false;

  const label = () => mode.value === 'loop' ? 'Seamless loop' : 'Full song';
  const formatTime = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
  function position() {
    const duration = buffers.get(mode.value)?.duration || 0;
    const elapsed = source ? offset + context.currentTime - startTime : offset;
    return duration ? (mode.value === 'loop' ? elapsed % duration : Math.min(elapsed, duration)) : 0;
  }
  function updateTime() {
    const duration = buffers.get(mode.value)?.duration;
    time.textContent = `${formatTime(position())} / ${duration ? formatTime(duration) : '—'}`;
  }
  function updateControls() {
    play.textContent = loading ? 'Cancel' : source ? 'Pause' : 'Play';
    play.setAttribute('aria-pressed', String(Boolean(source)));
    restart.disabled = Boolean(loading);
    panel.setAttribute('aria-busy', String(Boolean(loading)));
  }
  function updateGain() {
    if (gain) gain.gain.setTargetAtTime(muted ? 0 : Number(volume.value) / 100, context.currentTime, .015);
    mute.textContent = muted ? 'Unmute' : 'Mute';
    mute.setAttribute('aria-pressed', String(muted));
    volumeValue.textContent = `${volume.value}%`;
  }
  function stop(keepPosition = true) {
    offset = keepPosition ? position() : 0;
    if (source) {
      source.onended = null;
      source.stop();
      source.disconnect();
      source = undefined;
    }
    loading?.abort();
    loading = undefined;
    requestId++;
    sound.setThemePlaying(false);
    updateControls();
    updateTime();
  }
  async function start(fromBeginning = false) {
    if (fromBeginning) stop(false);
    onStart();
    const selectedMode = mode.value;
    const currentRequest = ++requestId;
    try {
      context = sound.getContext();
      // Resume synchronously from the click gesture, before fetching or decoding.
      await context.resume();
      if (currentRequest !== requestId) return;
      if (!gain) {
        gain = context.createGain();
        gain.gain.value = muted ? 0 : Number(volume.value) / 100;
        gain.connect(context.destination);
      }
      let buffer = buffers.get(selectedMode);
      if (!buffer) {
        loading = new AbortController();
        status.textContent = `Loading ${label().toLowerCase()}…`;
        updateControls();
        const response = await fetch(tracks[selectedMode], { signal: loading.signal, cache: localPreview ? 'no-store' : 'default' });
        if (!response.ok) throw new Error('The selected song could not be loaded.');
        buffer = await context.decodeAudioData(await response.arrayBuffer());
        if (currentRequest !== requestId) return;
        buffers.set(selectedMode, buffer);
      }
      if (currentRequest !== requestId) return;
      loading = undefined;
      if (offset >= buffer.duration) offset = 0;
      source = context.createBufferSource();
      source.buffer = buffer;
      source.loop = selectedMode === 'loop';
      source.connect(gain);
      source.onended = () => {
        offset = buffer.duration;
        source.disconnect();
        source = undefined;
        sound.setThemePlaying(false);
        status.textContent = 'Full song finished. Play to listen again.';
        updateControls();
        updateTime();
      };
      startTime = context.currentTime;
      source.start(0, offset);
      sound.setThemePlaying(true);
      status.textContent = `${label()} loaded · ${selectedMode === 'loop' ? 'repeating' : 'playing'}.`;
      updateControls();
      updateTime();
    } catch (error) {
      if (currentRequest !== requestId) return;
      stop();
      status.textContent = error.name === 'AbortError' ? 'Loading canceled.' : `${error.message} Press Play to retry.`;
    }
  }
  play.addEventListener('click', () => {
    if (source || loading) {
      const wasLoading = Boolean(loading);
      stop();
      status.textContent = wasLoading ? 'Loading canceled. Press Play to retry.' : `${label()} paused.`;
    } else start();
  });
  restart.addEventListener('click', () => start(true));
  mode.addEventListener('change', () => {
    stop(false);
    status.textContent = `${label()} selected. Press Play to listen.`;
  });
  mute.addEventListener('click', () => { muted = !muted; updateGain(); });
  volume.addEventListener('input', updateGain);
  const timer = window.setInterval(updateTime, 250);
  window.addEventListener('pagehide', () => { stop(); window.clearInterval(timer); }, { once: true });

  return {
    pause() {
      if (!source && !loading) return false;
      const wasLoading = Boolean(loading);
      stop();
      status.textContent = wasLoading ? 'Loading canceled. Press Play to retry.' : `${label()} paused.`;
      return true;
    },
  };
}
