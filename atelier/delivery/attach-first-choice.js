// Bind a loaded GLTFLoader result inside a Three.js host. A host can use its
// own render loop, play policy, accessibility settings, lighting and camera.
import { AnimationMixer, LoopOnce } from 'three';

export function attachFirstChoice(gltf) {
  const clip = gltf.animations.find(animation => animation.name === 'First Choice');
  if (!clip) throw new Error('Missing First Choice animation');
  const pivots = new Map();
  gltf.scene.traverse(object => {
    const region = object.userData.fc_region;
    if (region) pivots.set(region, object);
  });
  for (const name of ['ground', 'stand', 'saddle', 'torso', 'neck', 'head']) {
    if (!pivots.has(name)) throw new Error('Missing rigid pivot: ' + name);
  }
  const mixer = new AnimationMixer(gltf.scene);
  const action = mixer.clipAction(clip);
  action.setLoop(LoopOnce, 1);
  action.clampWhenFinished = true;
  action.play();
  action.paused = true;
  function seek(seconds) {
    if (!Number.isFinite(seconds)) throw new RangeError('Animation time must be finite');
    action.time = Math.max(0, Math.min(clip.duration, seconds));
    mixer.update(0);
    gltf.scene.updateMatrixWorld(true);
  }
  seek(0);
  return {
    root: gltf.scene, pivots, duration: clip.duration, seek,
    dispose() {
      action.stop();
      mixer.uncacheRoot(gltf.scene);
    }
  };
}
