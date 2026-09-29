import * as THREE from 'three';

// The exported knee journals run along local X. The hip may orient the whole
// linkage, but the shin has one hinge degree of freedom, never a ball joint.
const TRANSVERSE = new THREE.Vector3(1, 0, 0);
const FORWARD = new THREE.Vector3(0, 0, 1);

export function solveTransverseLeg(upper, lower, target) {
  const upperLength = upper.length(), lowerLength = lower.length();
  if (upperLength < 1e-6 || lowerLength < 1e-6) throw new Error('Rigid leg links must have positive length.');
  const cosine = upper.y * lower.y + upper.z * lower.z;
  const sine = upper.z * lower.y - upper.y * lower.z;
  const radial = Math.hypot(cosine, sine);
  if (radial < 1e-9) throw new Error('Rigid leg links must span the transverse hinge plane.');
  const fixed = upper.x * lower.x;
  const squares = upperLength ** 2 + lowerLength ** 2;
  const minimumReach = Math.sqrt(Math.max(0, squares + 2 * (fixed - radial)));
  const maximumReach = Math.sqrt(Math.max(0, squares + 2 * (fixed + radial)));
  const distance = THREE.MathUtils.clamp(target.length(), minimumReach + 1e-6, maximumReach - 1e-6);
  const direction = target.lengthSq() > 1e-12 ? target.clone().normalize() : new THREE.Vector3(0, -1, 0);
  const hingeAngle = Math.atan2(sine, cosine) + Math.acos(THREE.MathUtils.clamp(((distance ** 2 - squares) / 2 - fixed) / radial, -1, 1));
  const kneeQuaternion = new THREE.Quaternion().setFromAxisAngle(TRANSVERSE, hingeAngle);
  const hingedLower = lower.clone().applyQuaternion(kneeQuaternion);

  // Aim the knee forward while retaining the exact exported offsets. Mapping
  // both link vectors also fixes hip twist; shortest-arc rotations alone let
  // the knee drift sideways around the visible journal.
  const along = (upperLength ** 2 - lowerLength ** 2 + distance ** 2) / (2 * distance);
  const height = Math.sqrt(Math.max(0, upperLength ** 2 - along ** 2));
  const bend = FORWARD.clone().addScaledVector(direction, -direction.z);
  if (bend.lengthSq() < 1e-10) bend.set(0, 1, 0).addScaledVector(direction, -direction.y);
  bend.normalize();
  const desiredUpper = direction.clone().multiplyScalar(along).addScaledVector(bend, height);
  const desiredLower = direction.clone().multiplyScalar(distance).sub(desiredUpper);
  const basis = (first, second) => {
    const x = first.clone().normalize();
    const z = first.clone().cross(second).normalize();
    const y = z.clone().cross(x);
    return new THREE.Matrix4().makeBasis(x, y, z);
  };
  const rotation = basis(desiredUpper, desiredLower).multiply(basis(upper, hingedLower).transpose());
  const hipQuaternion = new THREE.Quaternion().setFromRotationMatrix(rotation).normalize();
  return { hipQuaternion, kneeQuaternion, hingeAngle, minimumReach, maximumReach, clamped: Math.abs(target.length() - distance) > 1e-7 };
}
