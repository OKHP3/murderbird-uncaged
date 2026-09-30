import { LinearSRGBColorSpace, NormalBlending } from 'three';

const eras = new Set(['maker', 'mechanic', 'builder']);
const record = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const unit = value => typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1;
const vector = (value, length) => Array.isArray(value) && value.length === length && value.every(unit);

function profileIssue(profile) {
  if (!record(profile)) return 'profile must be an object';
  if (!vector(profile.baseColorFactor, 4) || profile.baseColorFactor[3] !== 1) return 'baseColorFactor must be four linear factors in [0, 1], with opaque alpha 1';
  if (!unit(profile.metallicFactor)) return 'metallicFactor must be in [0, 1]';
  if (!unit(profile.roughnessFactor)) return 'roughnessFactor must be in [0, 1]';
  if (profile.emissiveFactor !== undefined && !vector(profile.emissiveFactor, 3)) return 'emissiveFactor must be three linear factors in [0, 1]';
  return null;
}

/** Apply explicit glTF material extras in place. Missing eras remain ineligible;
 * visibility and shared references belong to the existing assembly controller.
 * Untagged released models are a no-op. Invalid tagged materials stay untouched.
 */
export function applyEraFinishes(model, era) {
  if (!eras.has(era)) throw new RangeError(`Unknown finish era: ${era}`);
  if (typeof model?.traverse !== 'function') throw new TypeError('Era finishes require a traversable model');
  const seen = new Set();
  const report = { era, taggedMaterials: 0, appliedMaterials: 0, ineligibleMaterials: 0, invalidMaterials: 0, issues: [] };
  model.traverse(object => {
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      if (!material || seen.has(material)) continue;
      seen.add(material);
      if (!Object.hasOwn(material.userData ?? {}, 'eraFinishes')) continue;
      report.taggedMaterials++;
      const profiles = material.userData.eraFinishes;
      let issue = record(profiles) ? null : 'eraFinishes must be an object';
      if (!issue) {
        for (const [key, value] of Object.entries(profiles)) {
          issue = !eras.has(key) ? `unknown profile era ${key}` : profileIssue(value);
          if (issue) { issue = `${key}: ${issue}`; break; }
        }
      }
      if (!issue && (!material.isMeshStandardMaterial || !material.color?.setRGB || !material.emissive?.setRGB)) issue = 'tagged material must support standard metallic-roughness PBR';
      if (issue) {
        report.invalidMaterials++;
        report.issues.push({ material: material.name || material.uuid || '(unnamed)', issue });
        continue;
      }
      if (!Object.hasOwn(profiles, era)) { report.ineligibleMaterials++; continue; }
      const profile = profiles[era];
      material.color.setRGB(...profile.baseColorFactor.slice(0, 3), LinearSRGBColorSpace);
      material.metalness = profile.metallicFactor;
      material.roughness = profile.roughnessFactor;
      material.emissive.setRGB(...(profile.emissiveFactor ?? [0, 0, 0]), LinearSRGBColorSpace);
      material.emissiveIntensity = 1;
      material.opacity = 1;
      material.transparent = false;
      material.alphaTest = 0;
      material.alphaHash = false;
      material.depthWrite = true;
      material.blending = NormalBlending;
      material.needsUpdate = true;
      report.appliedMaterials++;
    }
  });
  return report;
}
