import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { makeStage } from '../finish/stage.js'

const element = id => document.getElementById(id)
const canvas = element('viewer-canvas')
const stageElement = element('stage')
const message = element('stage-message')
const statusText = element('stage-status')
const playButton = element('play')
const scrubber = element('timeline')
const lightButtons = Array.from(document.querySelectorAll('[data-light]'))
const viewButtons = Array.from(document.querySelectorAll('[data-view]'))
const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)')
const embeddedAssetURL = window.firstChoiceEmbeddedAssetURL
if (embeddedAssetURL) THREE.DefaultLoadingManager.setURLModifier(embeddedAssetURL)
const fileUrl = name => embeddedAssetURL ? embeddedAssetURL(name) : new URL(name, document.baseURI).href

const views = {
  portrait: { target: [0, .99, .07], azimuth: -65, elevation: 7, distance: 4.35, minWidth: 1.7 },
  profile:  { target: [0, .99, .09], azimuth: -89, elevation: 3, distance: 4.33, minWidth: 1.7 },
  detail:   { target: [-.07, 1.68, .27], azimuth: -72, elevation: 7, distance: 1.65, minWidth: .84 },
  support:  { target: [-.1, .808, .438], azimuth: -59, elevation: 12, distance: 2.44, minWidth: 1.03 },
}

const scene = new THREE.Scene()
const camera = new THREE.PerspectiveCamera(30, 1, .025, 75)
const eyeOffset = new THREE.Vector3()
const state = {
  status: 'loading', lighting: 'workshop', view: 'portrait',
  duration: 0, currentTime: 0, playing: false, clipName: '',
  drawnFrames: 0, error: null,
}
let renderer, controls, set, mixer, action, frame
let lastPlaybackTime = 0
let activeLoad = true
let documentVisible = !document.hidden

function formatTime(time) {
  const tenths = Math.floor(Math.max(time, 0) * 10 + .0001)
  const seconds = Math.floor(tenths / 10)
  return Math.floor(seconds / 60) + ':' + String(seconds % 60).padStart(2, '0') + '.' + tenths % 10
}

function updateTransport() {
  const label = state.playing ? 'Pause' : 'Play'
  playButton.classList.toggle('is-playing', state.playing)
  if (element('play-label').textContent !== label) element('play-label').textContent = label
  scrubber.value = String(state.currentTime)
  const progress = state.duration ? state.currentTime / state.duration : 0
  scrubber.style.setProperty('--progress', (progress * 100) + '%')
  scrubber.setAttribute('aria-valuetext', state.currentTime.toFixed(1) + ' seconds')
  const time = formatTime(state.currentTime)
  if (element('elapsed').textContent !== time) element('elapsed').textContent = time
}

function setPlaying(playing) {
  state.playing = Boolean(playing && action && state.status === 'ready')
  lastPlaybackTime = performance.now()
  updateTransport()
  requestDraw()
}

function samplePose() {
  if (!action) return
  action.time = state.currentTime
  mixer.update(0)
}

function seek(seconds) {
  if (!action || !Number.isFinite(seconds) || state.status !== 'ready') return false
  setPlaying(false)
  state.currentTime = THREE.MathUtils.clamp(seconds, 0, state.duration)
  samplePose()
  updateTransport()
  requestDraw()
  return true
}

function togglePlayback() {
  if (!action) return
  if (state.currentTime >= state.duration) seek(0)
  setPlaying(!state.playing)
}

function draw(now) {
  frame = undefined
  if (state.status !== 'ready' || !documentVisible) return
  if (state.playing) {
    state.currentTime = Math.min(state.duration, state.currentTime + (now - lastPlaybackTime) / 1000)
    lastPlaybackTime = now
    if (state.currentTime >= state.duration) state.playing = false
    samplePose()
    updateTransport()
  }
  renderer.render(scene, camera)
  state.drawnFrames += 1
  if (state.playing) requestDraw()
}

function requestDraw() {
  if (frame === undefined && documentVisible && state.status === 'ready') {
    frame = requestAnimationFrame(draw)
  }
}

function orbitTo(azimuth, elevation, distance) {
  if (!controls || !Number.isFinite(azimuth) || !Number.isFinite(elevation)) return false
  const radius = THREE.MathUtils.clamp(
    Number.isFinite(distance) ? distance : camera.position.distanceTo(controls.target),
    controls.minDistance, controls.maxDistance,
  )
  const az = THREE.MathUtils.degToRad(azimuth)
  const el = THREE.MathUtils.degToRad(THREE.MathUtils.clamp(elevation, -3, 77))
  eyeOffset.set(Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el))
  camera.position.copy(controls.target).addScaledVector(eyeOffset, radius)
  controls.update()
  requestDraw()
  return true
}

function setView(name) {
  const view = views[name]
  if (!view || !controls) return false
  controls.target.fromArray(view.target)
  const halfAngle = THREE.MathUtils.degToRad(camera.fov * .5)
  const widthFitDistance = view.minWidth / (2 * Math.tan(halfAngle) * camera.aspect)
  orbitTo(view.azimuth, view.elevation, Math.max(view.distance, widthFitDistance))
  state.view = name
  viewButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === name)))
  return true
}

function clearViewSelection() {
  state.view = 'custom'
  for (const button of viewButtons) button.setAttribute('aria-pressed', 'false')
}

function setLighting(mode) {
  if (!set || !['workshop', 'neutral'].includes(mode)) return false
  set.setLighting(mode)
  state.lighting = mode
  lightButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.light === mode)))
  requestDraw()
  return true
}

function resize() {
  if (!renderer) return
  const {width, height} = stageElement.getBoundingClientRect()
  if (width <= 0 || height <= 0) return
  renderer.setSize(Math.round(width), Math.round(height), false)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  if (state.view in views) setView(state.view)
  requestDraw()
}

function cameraSnapshot() {
  if (!controls) return null
  return {
    position: camera.position.toArray(),
    target: controls.target.toArray(),
    azimuth: THREE.MathUtils.radToDeg(controls.getAzimuthalAngle()),
    elevation: 90 - THREE.MathUtils.radToDeg(controls.getPolarAngle()),
    distance: camera.position.distanceTo(controls.target),
  }
}

function getState() {
  return {
    ...state, camera: cameraSnapshot(),
    reducedMotion: motionPreference.matches,
    triangles: renderer?.info.render.triangles ?? 0,
    drawCalls: renderer?.info.render.calls ?? 0,
  }
}

Object.defineProperty(window, 'firstChoiceReview', {
  value: Object.freeze({
    getState, seek, setView, setLighting,
    orbitTo(azimuth, elevation, distance) {
      if (!orbitTo(azimuth, elevation, distance)) return false
      clearViewSelection()
      return true
    },
  }),
})

function showFallback(reason, text) {
  activeLoad = false
  state.status = 'fallback'
  state.error = reason
  setPlaying(false)
  stageElement.classList.remove('ready')
  canvas.hidden = true
  message.hidden = false
  statusText.textContent = text
  element('load-progress').hidden = true
  element('retry').hidden = false
  for (const control of [...viewButtons, ...lightButtons, playButton, scrubber, element('replay'), element('reset-camera')]) {
    control.disabled = true
  }
  const poster = element('poster')
  poster.onload = () => { poster.hidden = false; message.classList.add('has-still') }
  poster.onerror = () => { poster.hidden = true; message.classList.remove('has-still') }
  poster.src = fileUrl('first-choice-still.jpg')
}

function initializeModel(gltf) {
  if (!activeLoad) return
  scene.add(gltf.scene)
  gltf.scene.traverse(object => {
    if (!object.isMesh) return
    object.castShadow = true
    object.receiveShadow = true
  })
  const clips = gltf.animations.filter(clip => clip.duration > 0 && clip.tracks.length)
  const clip = clips.find(clip => /first[\s_.-]*choice/i.test(clip.name))
    ?? clips.sort((a, b) => b.duration - a.duration)[0]
  if (clip) {
    mixer = new THREE.AnimationMixer(gltf.scene)
    action = mixer.clipAction(clip)
    action.setLoop(THREE.LoopOnce, 1)
    action.clampWhenFinished = true
    action.play()
    action.paused = true
    state.duration = clip.duration
    state.clipName = clip.name
    samplePose()
    scrubber.max = String(clip.duration)
    element('duration').textContent = formatTime(clip.duration)
  }
  // Warm the stationary scene before starting the clock. GPU uploads on the
  // first frame can otherwise consume the seated-fastener beat on mobile.
  renderer.render(scene, camera)
  state.drawnFrames += 1
  if (!activeLoad) return
  activeLoad = false
  state.status = 'ready'
  for (const control of [...viewButtons, ...lightButtons, element('reset-camera')]) control.disabled = false
  for (const control of [playButton, scrubber, element('replay')]) control.disabled = !clip
  stageElement.classList.add('ready')
  statusText.textContent = clip ? 'Model ready' : 'Model ready. Motion unavailable.'
  message.hidden = true
  if (!clip) {
    element('timing').hidden = true
    element('motion-note').hidden = false
  }
  setPlaying(Boolean(clip) && !motionPreference.matches && documentVisible)
  requestDraw()
}

function loadModel() {
  const progress = element('load-progress')
  new GLTFLoader().load(fileUrl('first-choice.glb'), initializeModel, event => {
    if (!event.lengthComputable || !activeLoad) return
    progress.max = event.total
    progress.value = event.loaded
    if (event.loaded >= event.total) statusText.textContent = 'Preparing the model…'
  }, () => {
    if (activeLoad) showFallback('model-load', 'The 3D model could not be opened.')
  })
}

function initialize() {
  try {
    renderer = new THREE.WebGLRenderer({canvas, antialias: true, powerPreference: 'high-performance'})
  } catch {
    showFallback('webgl-unavailable', 'This browser could not open the interactive 3D view.')
    return
  }
  try {
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFShadowMap
    controls = new OrbitControls(camera, canvas)
    controls.enableDamping = false
    controls.enablePan = false
    controls.rotateSpeed = .75
    controls.zoomSpeed = .82
    controls.minDistance = .45
    controls.maxDistance = 10
    controls.minPolarAngle = THREE.MathUtils.degToRad(13)
    controls.maxPolarAngle = THREE.MathUtils.degToRad(93)
    controls.addEventListener('change', requestDraw)
    controls.addEventListener('start', clearViewSelection)
    set = makeStage(renderer, scene)
    setLighting('workshop')
    resize()
    new ResizeObserver(resize).observe(stageElement)
    THREE.DefaultLoadingManager.onLoad = requestDraw
    loadModel()
  } catch {
    showFallback('scene-initialization', 'The interactive scene could not be initialized.')
  }
}

playButton.addEventListener('click', togglePlayback)
element('replay').addEventListener('click', () => { if (seek(0)) setPlaying(true) })
scrubber.addEventListener('input', () => seek(Number(scrubber.value)))
element('reset-camera').addEventListener('click', () => setView('portrait'))
viewButtons.forEach(button => button.addEventListener('click', () => setView(button.dataset.view)))
lightButtons.forEach(button => button.addEventListener('click', () => setLighting(button.dataset.light)))
element('retry').addEventListener('click', () => location.reload())
element('help').addEventListener('click', () => element('guide').showModal())
canvas.addEventListener('webglcontextlost', event => {
  event.preventDefault()
  showFallback('webgl-context-lost', 'The 3D view was interrupted.')
})

canvas.addEventListener('keydown', event => {
  if (state.status !== 'ready' || event.ctrlKey || event.metaKey || event.altKey) return
  const {azimuth, elevation, distance} = cameraSnapshot()
  const step = event.shiftKey ? 15 : 5
  switch (event.key) {
    case 'ArrowLeft': orbitTo(azimuth - step, elevation, distance); break
    case 'ArrowRight': orbitTo(azimuth + step, elevation, distance); break
    case 'ArrowUp': orbitTo(azimuth, elevation + step, distance); break
    case 'ArrowDown': orbitTo(azimuth, elevation - step, distance); break
    case '+': case '=': orbitTo(azimuth, elevation, distance / 1.12); break
    case '-': case '_': orbitTo(azimuth, elevation, distance * 1.12); break
    case 'Home': setView('portrait'); event.preventDefault(); return
    case ' ': if (!event.repeat) togglePlayback(); event.preventDefault(); return
    default: return
  }
  clearViewSelection()
  event.preventDefault()
})

document.addEventListener('visibilitychange', () => {
  documentVisible = !document.hidden
  lastPlaybackTime = performance.now()
  if (documentVisible) requestDraw()
})
motionPreference.addEventListener('change', () => {
  if (motionPreference.matches) setPlaying(false)
})
if (matchMedia('(pointer: coarse)').matches) {
  element('orbit-help').textContent = 'Drag to orbit · Pinch to zoom'
}

initialize()
