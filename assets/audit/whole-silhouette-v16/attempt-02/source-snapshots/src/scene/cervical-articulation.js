// Rigid serial neck joints. The optional upper joint is an isolated structural
// proposal; models without it retain their single-pivot motion.
export function createCervicalArticulation(model, nodes, rest) {
  const upper = model.getObjectByName('cervical-upper');
  if (upper && (upper.parent !== nodes.neck || nodes.head.parent !== upper)) {
    throw new Error('Two-stage cervical hierarchy is incomplete.');
  }
  const upperRest = upper ? {
    position: upper.position.clone(), rotation: upper.rotation.clone(),
  } : null;
  const lowerFraction = upper ? .35 : 1;
  return {
    upper,
    restoreAttachments() {
      nodes.neck.position.copy(rest.neck.position);
      nodes.head.position.copy(rest.head.position);
      if (upper) {
        upper.position.copy(upperRest.position);
        upper.rotation.copy(upperRest.rotation);
      }
    },
    setPitch(pitch, yaw = nodes.neck.rotation.y, roll = nodes.neck.rotation.z) {
      nodes.neck.rotation.set(pitch * lowerFraction, yaw, roll);
      if (upper) upper.rotation.set(pitch * (1 - lowerFraction), 0, 0);
    },
    get pitch() { return nodes.neck.rotation.x + (upper?.rotation.x ?? 0); },
    metrics() {
      return {
        jointCount: upper ? 2 : 1,
        lowerPitchFraction: lowerFraction,
        upperTranslationError: upper ? upper.position.distanceTo(upperRest.position) : 0,
        upperPitch: upper?.rotation.x ?? 0,
        totalPitch: this.pitch,
      };
    },
  };
}
