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
  // Optional outer receivers straddle the root and skull ball joints. Each is
  // a rigid sibling of its driven joint; only its orientation is interpolated.
  const receivers = [
    ['cervical-root-cover', nodes.neck, nodes.body],
    ['cervical-skull-cover', nodes.head, upper],
  ].flatMap(([name, joint, parent]) => {
    const node = model.getObjectByName(name);
    if (!node) return [];
    if (!parent || node.parent !== parent || joint.parent !== parent
        || node.position.distanceTo(joint.position) > 1e-6) {
      throw new Error(`${name} must share its driven joint's parent and centre.`);
    }
    return [{ node, joint, position: node.position.clone(),
      orientation: node.quaternion.clone(), inverseJointRest: joint.quaternion.clone().invert(),
      half: node.quaternion.clone(), delta: node.quaternion.clone() }];
  });
  function updateCovers() {
    for (const receiver of receivers) {
      // Work in the shared parent's coordinates, including simultaneous yaw
      // and pitch. Averaging Euler components would not bisect that rotation.
      receiver.delta.copy(receiver.joint.quaternion).multiply(receiver.inverseJointRest);
      receiver.half.identity().slerp(receiver.delta, .5);
      receiver.node.quaternion.copy(receiver.half).multiply(receiver.orientation);
    }
    return receivers.length > 0;
  }
  const lowerFraction = upper ? .35 : 1;
  return {
    upper,
    updateCovers,
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
      for (const receiver of receivers) {
        receiver.node.position.copy(receiver.position);
        receiver.node.quaternion.copy(receiver.orientation);
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
      updateCovers();
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
        outerReceivers: receivers.map(({ node, joint, position }) => ({
          name: node.name,
          translationError: node.position.distanceTo(position),
          jointCentreError: node.position.distanceTo(joint.position),
          quaternion: node.quaternion.toArray(),
        })),
        totalPitch: this.pitch,
      };
    },
  };
}
