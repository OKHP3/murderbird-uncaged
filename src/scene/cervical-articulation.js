// Optional authored chain uses rest-relative local rotations. Legacy layouts
// retain their existing two-stage/single-stage controls and receivers.
function readChainLayout(body) {
  const raw = body.userData?.cervicalLayoutV2 ?? body.userData?.extras?.cervicalLayoutV2;
  if (raw === undefined) return null;
  let layout;
  try { layout = typeof raw === 'string' ? JSON.parse(raw) : raw; }
  catch { throw new Error('Invalid cervicalLayoutV2 JSON.'); }
  const expected = ['neck', 'cervical-mid-a', 'cervical-mid-b', 'cervical-upper'];
  if (!layout || layout.schema !== 1 || !Array.isArray(layout.pitchJoints)
      || layout.pitchJoints.length !== 4 || layout.pitchJoints.some((name, i) => name !== expected[i])
      || layout.rootYaw !== 'neck' || layout.headOwner !== 'head'
      || !Array.isArray(layout.weights) || layout.weights.length !== 4
      || layout.weights.some(weight => typeof weight !== 'number' || !Number.isFinite(weight) || weight <= 0 || weight > 1)
      || Math.abs(layout.weights.reduce((sum, weight) => sum + weight, 0) - 1) > 1e-9) {
    throw new Error('Invalid cervicalLayoutV2 joint names, weights or schema.');
  }
  return layout;
}

function poseHelpers(objects) {
  const unique = [...new Set(objects.filter(Boolean))];
  return {
    capturePose() {
      return unique.map(node => ({ node, position: node.position.clone(),
        quaternion: node.quaternion.clone(), order: node.rotation.order }));
    },
    restorePose(pose) {
      if (!Array.isArray(pose) || pose.length !== unique.length
          || pose.some((item, i) => item.node !== unique[i])) {
        throw new Error('Cervical pose snapshot belongs to a different articulation.');
      }
      for (const { node, position, quaternion, order } of pose) {
        node.position.copy(position); node.rotation.order = order; node.quaternion.copy(quaternion);
      }
    },
  };
}

function createChain(model, nodes, rest, layout) {
  const joints = layout.pitchJoints.map(name => model.getObjectByName(name));
  if (joints.some((joint, i) => !joint || joint.parent !== (i ? joints[i - 1] : nodes.body))
      || joints[0] !== nodes.neck || nodes.head.parent !== joints[3]) {
    throw new Error('Four-stage cervical hierarchy is incomplete.');
  }
  if (layout.skullReceiver !== undefined && layout.skullReceiver !== 'cervical-skull-cover') {
    throw new Error('Invalid cervicalLayoutV2 skullReceiver.');
  }
  const receiver = model.getObjectByName('cervical-skull-cover');
  if (['cervical-joint-cover', 'cervical-root-cover'].some(name => model.getObjectByName(name))
      || (receiver && !layout.skullReceiver)) {
    throw new Error('Four-stage cervical layout does not declare legacy cover owners.');
  }
  if (layout.skullReceiver && (!receiver || receiver.parent !== joints[3]
      || receiver.position.distanceTo(nodes.head.position) > 1e-6)) {
    throw new Error('Declared skull receiver must share the head parent and centre.');
  }
  const origins = joints.map(node => ({ position: node.position.clone(), quaternion: node.quaternion.clone(),
    inverse: node.quaternion.clone().invert() }));
  const headOrigin = nodes.head.position.clone();
  const headOrientation = nodes.head.quaternion.clone();
  const receiverRest = receiver ? { position: receiver.position.clone(), quaternion: receiver.quaternion.clone() } : null;
  const inverseHeadRest = headOrientation.clone().invert();
  const headDelta = headOrientation.clone(), half = headOrientation.clone();
  function updateCovers() {
    if (!receiver) return false;
    // Both owners share the skull bearing. Bisect the head's rest-relative
    // rotation in parent space; the receiver and its armor remain rigid.
    headDelta.copy(nodes.head.quaternion).multiply(inverseHeadRest);
    half.identity().slerp(headDelta, .5);
    receiver.quaternion.copy(half).multiply(receiverRest.quaternion);
    return true;
  }
  const euler = nodes.neck.rotation.clone(); const delta = nodes.neck.quaternion.clone();
  function relativeAngles(index) {
    delta.copy(origins[index].inverse).multiply(joints[index].quaternion);
    return euler.setFromQuaternion(delta, 'XYZ');
  }
  return {
    upper: joints[3], joints,
    ...poseHelpers([...joints, nodes.head, receiver]),
    updateCovers,
    restoreAttachments() {
      joints.forEach((joint, i) => {
        joint.position.copy(origins[i].position); joint.quaternion.copy(origins[i].quaternion);
      });
      nodes.head.position.copy(headOrigin);
      // Early Maker/claw branches do not assign the skull orientation. Start
      // each authored-chain action from its captured rest, then let normal
      // attention/contact logic apply the current frame counterrotation.
      nodes.head.quaternion.copy(headOrientation);
      if (receiver) {
        receiver.position.copy(receiverRest.position);
        receiver.quaternion.copy(receiverRest.quaternion);
      }
    },
    setPitch(pitch, yaw, roll) {
      if (yaw === undefined || roll === undefined) {
        const angles = relativeAngles(0);
        yaw ??= angles.y; roll ??= angles.z;
      }
      joints.forEach((joint, i) => {
        euler.set(pitch * layout.weights[i], i === 0 ? yaw : 0, i === 0 ? roll : 0, 'XYZ');
        delta.setFromEuler(euler);
        joint.quaternion.copy(origins[i].quaternion).multiply(delta);
      });
    },
    get pitch() { return joints.reduce((sum, _, i) => sum + relativeAngles(i).x, 0); },
    metrics() {
      return { jointCount: 4, lowerPitchFraction: layout.weights[0],
        upperTranslationError: joints[3].position.distanceTo(origins[3].position),
        upperPitch: relativeAngles(3).x, linkedCoverPitch: null,
        linkedCoverTranslationError: null, outerReceivers: receiver ? [{
          name: receiver.name, translationError: receiver.position.distanceTo(receiverRest.position),
          jointCentreError: receiver.position.distanceTo(nodes.head.position),
          quaternion: receiver.quaternion.toArray(),
        }] : [], totalPitch: this.pitch,
        pitchJoints: joints.map((joint, i) => ({ name: joint.name, weight: layout.weights[i],
          pitch: relativeAngles(i).x, translationError: joint.position.distanceTo(origins[i].position) })) };
    },
  };
}

// Rigid serial neck joints. The optional upper joint is an isolated structural
// proposal; models without it retain their single-pivot motion.
export function createCervicalArticulation(model, nodes, rest) {
  const layout = readChainLayout(nodes.body);
  if (layout) return createChain(model, nodes, rest, layout);
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
    joints: [nodes.neck, upper].filter(Boolean),
    ...poseHelpers([nodes.neck, upper, nodes.head, cover, ...receivers.map(receiver => receiver.node)]),
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
