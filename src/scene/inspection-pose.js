import * as THREE from 'three';

// Local-space offsets for the exported inspection assemblies. Keep these
// values shared by the runtime pose and the actual-GLB regression check.
export const INSPECTION_EXPLODED_OFFSETS = Object.freeze({
  breastplate: Object.freeze([-.70, -.12, .18]),
  'left-mantle': Object.freeze([.39, .09, 0]),
  'right-mantle': Object.freeze([-.39, .09, 0]),
  'left-wing-shield': Object.freeze([.11, -.04, .12]),
  'right-wing-shield': Object.freeze([-.11, -.04, .12]),
  'winding-drive': Object.freeze([-.45, -.10, .22]),
  'power-core': Object.freeze([.32, -.05, .28]),
  processing: Object.freeze([.28, .20, 0]),
  'cranial-cover': Object.freeze([0, .14, 0]),
});

const offsetVector = new THREE.Vector3();

/** Apply the exported exterior's inspection opening and exploded offsets. */
export function applyInspectionPose(nodes, rest, open, separation) {
  // A reconstructed cover may have a different mechanical hinge. Its axis is
  // stored on that rigid node in the exported model, in glTF local space.
  // Untagged historical models retain their original side-opening behavior.
  const declaredAxis = nodes.breastplate.userData?.inspectionAxis;
  const declaredAngle = nodes.breastplate.userData?.inspectionOpenRadians;
  const explicitHinge = ['x', 'y', 'z'].includes(declaredAxis)
    && Number.isFinite(declaredAngle) && Math.abs(declaredAngle) <= Math.PI / 2
    && Math.abs(declaredAngle) >= .2;
  const axis = explicitHinge ? declaredAxis : 'y';
  const angle = explicitHinge ? declaredAngle : -1.35;
  nodes.breastplate.rotation[axis] = open * angle;
  nodes['cranial-cover'].position.y = rest['cranial-cover'].position.y + open * .08;
  Object.entries(INSPECTION_EXPLODED_OFFSETS).forEach(([name, offset]) => {
    nodes[name].position.addScaledVector(offsetVector.set(...offset), separation);
  });
}
