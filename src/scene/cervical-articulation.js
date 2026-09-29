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
  const cover = model.getObjectByName('cervical-joint-cover');
  if (cover && (!upper || cover.parent !== nodes.neck)) {
    throw new Error('Linked cervical cover requires the upper joint and lower-neck attachment.');
  }
  const coverRest = cover ? {
    position: cover.position.clone(), rotation: cover.rotation.clone(),
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
      if (cover) {
        cover.position.copy(coverRest.position);
        cover.rotation.copy(coverRest.rotation);
      }
    },
    setPitch(pitch, yaw = nodes.neck.rotation.y, roll = nodes.neck.rotation.z) {
      nodes.neck.rotation.set(pitch * lowerFraction, yaw, roll);
      if (upper) upper.rotation.set(pitch * (1 - lowerFraction), 0, 0);
      // A separate rigid receiver follows half of the upper hinge excursion.
      // Metal stays rigid; the opening is shared between two sliding sectors.
      if (cover) cover.rotation.set(
        coverRest.rotation.x + .5 * (upper.rotation.x - upperRest.rotation.x),
        coverRest.rotation.y, coverRest.rotation.z,
      );
    },
    get pitch() { return nodes.neck.rotation.x + (upper?.rotation.x ?? 0); },
    metrics() {
      return {
        jointCount: upper ? 2 : 1,
        lowerPitchFraction: lowerFraction,
        upperTranslationError: upper ? upper.position.distanceTo(upperRest.position) : 0,
        upperPitch: upper?.rotation.x ?? 0,
        linkedCoverPitch: cover?.rotation.x ?? null,
        linkedCoverTranslationError: cover ? cover.position.distanceTo(coverRest.position) : null,
        totalPitch: this.pitch,
      };
    },
  };
}
