import * as THREE from 'three';

const LEAF_SIZE = 12;
const DISTANCE_EPSILON_SQ = 1e-18;
const SEGMENT_EPSILON = 1e-12;
const scratchTriangle = new THREE.Triangle();
const closestPoint = new THREE.Vector3();
const segmentScratch = Array.from({ length: 10 }, () => new THREE.Vector3());

function boundsForTriangles(triangles, start, end) {
  const min = new THREE.Vector3(Infinity, Infinity, Infinity);
  const max = new THREE.Vector3(-Infinity, -Infinity, -Infinity);
  for (let i = start; i < end; i += 1) {
    const triangle = triangles[i];
    min.min(triangle.min);
    max.max(triangle.max);
  }
  return { min, max };
}

function buildTree(triangles, start = 0, end = triangles.length) {
  const bounds = boundsForTriangles(triangles, start, end);
  if (end - start <= LEAF_SIZE) return { ...bounds, start, end, triangles };

  const size = bounds.max.clone().sub(bounds.min);
  const axis = size.x >= size.y && size.x >= size.z ? 'x' : size.y >= size.z ? 'y' : 'z';
  const middle = (start + end) >> 1;
  triangles.slice(start, end).sort((a, b) => a.center[axis] - b.center[axis])
    .forEach((triangle, index) => { triangles[start + index] = triangle; });
  return {
    ...bounds,
    left: buildTree(triangles, start, middle),
    right: buildTree(triangles, middle, end),
  };
}

function visibleThroughAncestors(object, root) {
  for (let current = object; current && current !== root.parent; current = current.parent) {
    if (!current.visible) return false;
  }
  return true;
}

/** Build a world-space triangle surface from visible meshes under a group. */
export function buildTriangleSurface(root, { exclude = null, includeMesh = null, includeTriangle = null } = {}) {
  root.updateWorldMatrix(true, true);
  const triangles = [];
  const articulatedMeshes = new Map();
  let triangleIndex = 0;
  function visit(object) {
    if (object === exclude || !visibleThroughAncestors(object, root)) return;
    if (object.isMesh && object.geometry?.attributes?.position
        && (!includeMesh || includeMesh(object))) {
      const position = object.geometry.attributes.position;
      const index = object.geometry.index;
      const count = index ? index.count : position.count;
      for (let offset = 0; offset + 2 < count; offset += 3) {
        const localPoints = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
        const points = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
        for (let corner = 0; corner < 3; corner += 1) {
          localPoints[corner].fromBufferAttribute(position, index ? index.getX(offset + corner) : offset + corner);
          points[corner].copy(localPoints[corner]).applyMatrix4(object.matrixWorld);
        }
        const [a, b, c] = points;
        if (includeTriangle && !includeTriangle({ a, b, c, mesh: object, index: triangleIndex })) continue;
        const min = new THREE.Vector3().copy(a).min(b).min(c);
        const max = new THREE.Vector3().copy(a).max(b).max(c);
        const identity = triangleIndex++;
        triangles.push({
          a, b, c, min, max,
          center: new THREE.Vector3().add(a).add(b).add(c).multiplyScalar(1 / 3),
          mesh: object.name || object.uuid,
          meshUuid: object.uuid,
          index: identity,
        });
        let mesh = articulatedMeshes.get(object.uuid);
        if (!mesh) {
          const chain = [];
          for (let node = object; node; node = node.parent) {
            chain.push({
              uuid: node.uuid,
              position: node.position.clone(),
              quaternion: node.quaternion.clone(),
              scale: node.scale.clone(),
            });
          }
          chain.reverse();
          mesh = { uuid: object.uuid, name: object.name || object.uuid, chain, triangles: [] };
          articulatedMeshes.set(object.uuid, mesh);
        }
        mesh.triangles.push({ index: identity, vertices: localPoints });
      }
    }
    for (const child of object.children) visit(child);
  }
  visit(root);
  if (!triangles.length) throw new Error(`${root.name || 'surface'} has no visible mesh triangles`);
  return {
    name: root.name || 'surface',
    triangles,
    tree: buildTree(triangles),
    articulated: { meshes: [...articulatedMeshes.values()] },
  };
}

function boxDistanceSq(aMin, aMax, bMin, bMax) {
  let distance = 0;
  for (const axis of ['x', 'y', 'z']) {
    const gap = aMax[axis] < bMin[axis] ? bMin[axis] - aMax[axis]
      : bMax[axis] < aMin[axis] ? aMin[axis] - bMax[axis] : 0;
    distance += gap * gap;
  }
  return distance;
}

function segmentTriangleIntersects(start, end, triangle) {
  const [edge1, edge2, direction, p, tVector, q] = segmentScratch;
  edge1.subVectors(triangle.b, triangle.a);
  edge2.subVectors(triangle.c, triangle.a);
  direction.subVectors(end, start);
  p.crossVectors(direction, edge2);
  const determinant = edge1.dot(p);
  if (Math.abs(determinant) < SEGMENT_EPSILON) return false;
  const inverse = 1 / determinant;
  tVector.subVectors(start, triangle.a);
  const u = tVector.dot(p) * inverse;
  if (u < -SEGMENT_EPSILON || u > 1 + SEGMENT_EPSILON) return false;
  q.crossVectors(tVector, edge1);
  const v = direction.dot(q) * inverse;
  if (v < -SEGMENT_EPSILON || u + v > 1 + SEGMENT_EPSILON) return false;
  const t = edge2.dot(q) * inverse;
  return t >= -SEGMENT_EPSILON && t <= 1 + SEGMENT_EPSILON;
}

function segmentDistanceSq(p1, q1, p2, q2) {
  const d1 = segmentScratch[6], d2 = segmentScratch[7], r = segmentScratch[8];
  d1.subVectors(q1, p1);
  d2.subVectors(q2, p2);
  r.subVectors(p1, p2);
  const a = d1.dot(d1), e = d2.dot(d2), f = d2.dot(r);
  let s, t;
  if (a <= SEGMENT_EPSILON && e <= SEGMENT_EPSILON) return p1.distanceToSquared(p2);
  if (a <= SEGMENT_EPSILON) {
    s = 0;
    t = THREE.MathUtils.clamp(f / e, 0, 1);
  } else {
    const c = d1.dot(r);
    if (e <= SEGMENT_EPSILON) {
      t = 0;
      s = THREE.MathUtils.clamp(-c / a, 0, 1);
    } else {
      const b = d1.dot(d2);
      const denominator = a * e - b * b;
      s = denominator > SEGMENT_EPSILON ? THREE.MathUtils.clamp((b * f - c * e) / denominator, 0, 1) : 0;
      t = (b * s + f) / e;
      if (t < 0) { t = 0; s = THREE.MathUtils.clamp(-c / a, 0, 1); }
      else if (t > 1) { t = 1; s = THREE.MathUtils.clamp((b - c) / a, 0, 1); }
    }
  }
  const closest1 = segmentScratch[9].copy(p1).addScaledVector(d1, s);
  const closest2 = segmentScratch[5].copy(p2).addScaledVector(d2, t);
  return closest1.distanceToSquared(closest2);
}

function triangleDistanceSq(first, second) {
  scratchTriangle.set(first.a, first.b, first.c);
  const firstPoints = [first.a, first.b, first.c];
  const secondPoints = [second.a, second.b, second.c];
  const firstEdges = [[first.a, first.b], [first.b, first.c], [first.c, first.a]];
  const secondEdges = [[second.a, second.b], [second.b, second.c], [second.c, second.a]];

  for (const [start, end] of firstEdges) if (segmentTriangleIntersects(start, end, second)) return 0;
  for (const [start, end] of secondEdges) if (segmentTriangleIntersects(start, end, first)) return 0;

  let minimum = Infinity;
  for (const point of firstPoints) {
    scratchTriangle.set(second.a, second.b, second.c).closestPointToPoint(point, closestPoint);
    minimum = Math.min(minimum, point.distanceToSquared(closestPoint));
  }
  for (const point of secondPoints) {
    scratchTriangle.set(first.a, first.b, first.c).closestPointToPoint(point, closestPoint);
    minimum = Math.min(minimum, point.distanceToSquared(closestPoint));
  }
  for (const [a, b] of firstEdges) for (const [c, d] of secondEdges) {
    minimum = Math.min(minimum, segmentDistanceSq(a, b, c, d));
  }
  return minimum;
}

function orderedTriangles(surface) {
  return [...surface.triangles].sort((a, b) => a.index - b.index);
}

function hasStableArticulatedHierarchy(first, second) {
  if (!first.articulated || !second.articulated
      || first.articulated.meshes.length !== second.articulated.meshes.length) return false;
  return first.articulated.meshes.every((mesh, index) => {
    const other = second.articulated.meshes[index];
    return mesh.uuid === other.uuid
      && mesh.chain.length === other.chain.length
      && mesh.chain.every((node, chainIndex) => node.uuid === other.chain[chainIndex].uuid);
  });
}

function interpolateTransformChain(first, second, amount) {
  if (first.length !== second.length) throw new Error('Cannot interpolate articulated surface: hierarchy changed between poses');
  return first.map((start, index) => {
    const end = second[index];
    if (start.uuid !== end.uuid) throw new Error('Cannot interpolate articulated surface: hierarchy identity changed between poses');
    return {
      uuid: start.uuid,
      position: start.position.clone().lerp(end.position, amount),
      quaternion: start.quaternion.clone().slerp(end.quaternion, amount),
      scale: start.scale.clone().lerp(end.scale, amount),
    };
  });
}

function articulatedWorldMatrix(chain) {
  const world = new THREE.Matrix4();
  const local = new THREE.Matrix4();
  for (const transform of chain) {
    local.compose(transform.position, transform.quaternion, transform.scale);
    world.multiply(local);
  }
  return world;
}

function interpolateArticulatedSurface(first, second, amount) {
  const firstMeshes = first.articulated.meshes;
  const secondMeshes = second.articulated.meshes;
  if (firstMeshes.length !== secondMeshes.length) {
    throw new Error(`Cannot sweep ${first.name}: mesh topology changed between poses`);
  }
  const triangles = [];
  const meshes = firstMeshes.map((startMesh, meshIndex) => {
    const endMesh = secondMeshes[meshIndex];
    if (startMesh.uuid !== endMesh.uuid || startMesh.triangles.length !== endMesh.triangles.length) {
      throw new Error(`Cannot sweep ${first.name}: mesh identity changed between poses`);
    }
    const chain = interpolateTransformChain(startMesh.chain, endMesh.chain, amount);
    const matrixWorld = articulatedWorldMatrix(chain);
    const meshTriangles = startMesh.triangles.map((startTriangle, triangleIndex) => {
      const endTriangle = endMesh.triangles[triangleIndex];
      if (startTriangle.index !== endTriangle.index) {
        throw new Error(`Cannot sweep ${first.name}: triangle identity changed between poses`);
      }
      const vertices = startTriangle.vertices.map((vertex, corner) => {
        if (!vertex.equals(endTriangle.vertices[corner])) {
          throw new Error(`Cannot sweep ${first.name}: source geometry changed between poses`);
        }
        return vertex.clone();
      });
      const [a, b, c] = vertices.map(vertex => vertex.applyMatrix4(matrixWorld));
      const min = new THREE.Vector3().copy(a).min(b).min(c);
      const max = new THREE.Vector3().copy(a).max(b).max(c);
      triangles.push({
        a, b, c, min, max,
        center: new THREE.Vector3().add(a).add(b).add(c).multiplyScalar(1 / 3),
        mesh: startMesh.name,
        meshUuid: startMesh.uuid,
        index: startTriangle.index,
      });
      return { index: startTriangle.index, vertices: startTriangle.vertices };
    });
    return { uuid: startMesh.uuid, name: startMesh.name, chain, triangles: meshTriangles };
  });
  return {
    name: first.name,
    triangles,
    tree: buildTree(triangles),
    articulated: { meshes },
  };
}

function interpolateSurface(first, second, amount) {
  if (first.name !== second.name || first.triangles.length !== second.triangles.length) {
    throw new Error(`Cannot sweep ${first.name} to ${second.name}: triangle topology changed between poses`);
  }
  if (hasStableArticulatedHierarchy(first, second)) {
    return interpolateArticulatedSurface(first, second, amount);
  }
  const firstTriangles = orderedTriangles(first);
  const secondTriangles = orderedTriangles(second);
  const triangles = firstTriangles.map((start, index) => {
    const end = secondTriangles[index];
    if (start.index !== end.index || start.mesh !== end.mesh) {
      throw new Error(`Cannot sweep ${first.name}: triangle identity changed between poses`);
    }
    const a = start.a.clone().lerp(end.a, amount);
    const b = start.b.clone().lerp(end.b, amount);
    const c = start.c.clone().lerp(end.c, amount);
    return {
      a, b, c,
      min: new THREE.Vector3().copy(a).min(b).min(c),
      max: new THREE.Vector3().copy(a).max(b).max(c),
      center: new THREE.Vector3().add(a).add(b).add(c).multiplyScalar(1 / 3),
      mesh: start.mesh,
      index: start.index,
    };
  });
  return { name: first.name, triangles, tree: buildTree(triangles) };
}

function maximumArticulatedTravel(first, second) {
  if (first.articulated.meshes.length !== second.articulated.meshes.length) {
    throw new Error(`Cannot bound ${first.name} movement: mesh topology changed between poses`);
  }
  let maximum = 0;
  for (let meshIndex = 0; meshIndex < first.articulated.meshes.length; meshIndex += 1) {
    const startMesh = first.articulated.meshes[meshIndex];
    const endMesh = second.articulated.meshes[meshIndex];
    if (startMesh.uuid !== endMesh.uuid || startMesh.triangles.length !== endMesh.triangles.length) {
      throw new Error(`Cannot bound ${first.name} movement: mesh identity changed between poses`);
    }
    const chainStart = startMesh.chain;
    const chainEnd = endMesh.chain;
    if (chainStart.length !== chainEnd.length) {
      throw new Error(`Cannot bound ${first.name} movement: hierarchy changed between poses`);
    }
    let geometryRadius = 0;
    for (let triangleIndex = 0; triangleIndex < startMesh.triangles.length; triangleIndex += 1) {
      const startTriangle = startMesh.triangles[triangleIndex];
      const endTriangle = endMesh.triangles[triangleIndex];
      if (startTriangle.index !== endTriangle.index) {
        throw new Error(`Cannot bound ${first.name} movement: triangle identity changed between poses`);
      }
      for (let corner = 0; corner < 3; corner += 1) {
        if (!startTriangle.vertices[corner].equals(endTriangle.vertices[corner])) {
          throw new Error(`Cannot bound ${first.name} movement: source geometry changed between poses`);
        }
        geometryRadius = Math.max(geometryRadius, startTriangle.vertices[corner].length());
      }
    }

    const parentScale = new Array(chainStart.length);
    let scaleBefore = 1;
    for (let index = 0; index < chainStart.length; index += 1) {
      parentScale[index] = scaleBefore;
      const a = chainStart[index], b = chainEnd[index];
      if (a.uuid !== b.uuid) throw new Error(`Cannot bound ${first.name} movement: hierarchy identity changed between poses`);
      const maximumScale = Math.max(
        Math.abs(a.scale.x), Math.abs(a.scale.y), Math.abs(a.scale.z),
        Math.abs(b.scale.x), Math.abs(b.scale.y), Math.abs(b.scale.z),
      );
      scaleBefore *= maximumScale;
    }
    let radius = geometryRadius;
    let travel = 0;
    for (let index = chainStart.length - 1; index >= 0; index -= 1) {
      const a = chainStart[index], b = chainEnd[index];
      const maximumScale = Math.max(
        Math.abs(a.scale.x), Math.abs(a.scale.y), Math.abs(a.scale.z),
        Math.abs(b.scale.x), Math.abs(b.scale.y), Math.abs(b.scale.z),
      );
      const scaleChange = Math.max(
        Math.abs(a.scale.x - b.scale.x),
        Math.abs(a.scale.y - b.scale.y),
        Math.abs(a.scale.z - b.scale.z),
      );
      travel += parentScale[index] * (
        a.position.distanceTo(b.position)
        + a.quaternion.angleTo(b.quaternion) * maximumScale * radius
        + scaleChange * radius
      );
      radius = maximumScale * radius + Math.max(a.position.length(), b.position.length());
    }
    maximum = Math.max(maximum, travel);
  }
  return maximum;
}

function maximumVertexTravel(first, second) {
  if (hasStableArticulatedHierarchy(first, second)) return maximumArticulatedTravel(first, second);
  const firstTriangles = orderedTriangles(first);
  const secondTriangles = orderedTriangles(second);
  if (firstTriangles.length !== secondTriangles.length) {
    throw new Error(`Cannot bound ${first.name} movement: triangle topology changed between poses`);
  }
  let maximum = 0;
  for (let index = 0; index < firstTriangles.length; index += 1) {
    const a = firstTriangles[index], b = secondTriangles[index];
    if (a.index !== b.index || a.mesh !== b.mesh) {
      throw new Error(`Cannot bound ${first.name} movement: triangle identity changed between poses`);
    }
    maximum = Math.max(
      maximum,
      a.a.distanceTo(b.a), a.b.distanceTo(b.b), a.c.distanceTo(b.c),
    );
  }
  return maximum;
}

function searchNearest(triangle, node, best) {
  if (boxDistanceSq(triangle.min, triangle.max, node.min, node.max) >= best.distanceSq) return;
  if (node.start !== undefined) {
    for (let i = node.start; i < node.end; i += 1) {
      const candidate = node.triangles[i];
      if (boxDistanceSq(triangle.min, triangle.max, candidate.min, candidate.max) >= best.distanceSq) continue;
      const distanceSq = triangleDistanceSq(triangle, candidate);
      if (distanceSq < best.distanceSq) {
        best.distanceSq = distanceSq;
        best.first = triangle;
        best.second = candidate;
        if (distanceSq <= DISTANCE_EPSILON_SQ) return;
      }
    }
    return;
  }
  const leftDistance = boxDistanceSq(triangle.min, triangle.max, node.left.min, node.left.max);
  const rightDistance = boxDistanceSq(triangle.min, triangle.max, node.right.min, node.right.max);
  if (leftDistance <= rightDistance) {
    searchNearest(triangle, node.left, best);
    if (best.distanceSq > DISTANCE_EPSILON_SQ) searchNearest(triangle, node.right, best);
  } else {
    searchNearest(triangle, node.right, best);
    if (best.distanceSq > DISTANCE_EPSILON_SQ) searchNearest(triangle, node.left, best);
  }
}

/** Exact closest surface distance, accelerated by a triangle AABB hierarchy. */
export function measureSurfaceClearance(first, second) {
  const [smaller, larger] = first.triangles.length <= second.triangles.length ? [first, second] : [second, first];
  const best = { distanceSq: Infinity, first: null, second: null };
  // buildTree partitions the array in place; leaves reference the complete array.
  larger.tree.triangles = larger.triangles;
  for (const triangle of smaller.triangles) {
    searchNearest(triangle, larger.tree, best);
    if (best.distanceSq <= DISTANCE_EPSILON_SQ) break;
  }
  return {
    firstSurface: first.name,
    secondSurface: second.name,
    minimumSeparationMeters: Math.sqrt(best.distanceSq),
    surfaceIntersection: best.distanceSq <= DISTANCE_EPSILON_SQ,
    closestTriangles: best.first && best.second ? [
      { mesh: best.first.mesh, triangle: best.first.index },
      { mesh: best.second.mesh, triangle: best.second.index },
    ] : null,
  };
}

/**
 * Conservatively check an individual triangle pair between two
 * poses. The per-interval vertex travel bound lets distant surfaces be
 * certified without dense temporal sampling; only intervals that could cross
 * the requested clearance are bisected.
 */
function measureSweptTriangleClearance(
  firstStart,
  firstEnd,
  secondStart,
  secondEnd,
  {
    minimumSeparationMeters = 0,
    startTimeSeconds = 0,
    endTimeSeconds = 1,
    startMeasurement = null,
    endMeasurement = null,
    maximumDepth = 16,
  } = {},
) {
  if (!Number.isFinite(minimumSeparationMeters) || minimumSeparationMeters < 0) {
    throw new Error('minimumSeparationMeters must be finite and non-negative');
  }
  if (!Number.isFinite(startTimeSeconds) || !Number.isFinite(endTimeSeconds) || endTimeSeconds < startTimeSeconds) {
    throw new Error('Sweep times must be finite and ordered');
  }
  const firstTravel = maximumVertexTravel(firstStart, firstEnd);
  const secondTravel = maximumVertexTravel(secondStart, secondEnd);
  let minimum = { distance: Infinity, time: null, measurement: null };
  const violations = [];
  const uncertainties = [];
  const violates = value => value.surfaceIntersection
    || value.minimumSeparationMeters + 1e-9 < minimumSeparationMeters;
  let evaluations = 0;

  function observe(measurement, time) {
    evaluations += 1;
    if (measurement.minimumSeparationMeters < minimum.distance) {
      minimum = { distance: measurement.minimumSeparationMeters, time, measurement };
    }
    return measurement;
  }

  function recordViolation(measurement, timeIntervalSeconds, detectedAtSeconds, intervalEvidence = "observed-contact") {
    violations.push({
      timeIntervalSeconds,
      detectedAtSeconds,
      intervalEvidence,
      surfaces: `${measurement.firstSurface} / ${measurement.secondSurface}`,
      minimumSeparationMeters: measurement.minimumSeparationMeters,
      closestTriangles: measurement.closestTriangles,
    });
  }

  const startResult = observe(
    startMeasurement || measureSurfaceClearance(firstStart, secondStart),
    startTimeSeconds,
  );
  const endResult = observe(
    endMeasurement || measureSurfaceClearance(firstEnd, secondEnd),
    endTimeSeconds,
  );
  if (violates(startResult)) {
    recordViolation(startResult, [startTimeSeconds, startTimeSeconds], startTimeSeconds);
  }
  if (violates(endResult)) {
    recordViolation(endResult, [endTimeSeconds, endTimeSeconds], endTimeSeconds);
  }

  function search(firstA, firstB, secondA, secondB, firstMovement, secondMovement, from, to, atFrom, atTo, depth) {
    const movementBound = firstMovement + secondMovement;
    const lowerBound = Math.max(atFrom.minimumSeparationMeters, atTo.minimumSeparationMeters) - movementBound;
    if (lowerBound > Math.sqrt(DISTANCE_EPSILON_SQ)
        && lowerBound + 1e-9 >= minimumSeparationMeters) return;
    if (violates(atFrom)) {
      recordViolation(atFrom, [from, from], from);
    }
    if (violates(atTo)) {
      recordViolation(atTo, [to, to], to);
    }

    const middle = (from + to) / 2;
    const firstMiddle = interpolateSurface(firstA, firstB, .5);
    const secondMiddle = interpolateSurface(secondA, secondB, .5);
    const atMiddle = observe(measureSurfaceClearance(firstMiddle, secondMiddle), middle);
    const middleViolates = violates(atMiddle);

    // Only a bound for this exact triangle pair can certify a full contact span.
    const upperBound = Math.min(atFrom.minimumSeparationMeters, atTo.minimumSeparationMeters) + movementBound;
    if (upperBound + 1e-9 < minimumSeparationMeters
        || upperBound <= Math.sqrt(DISTANCE_EPSILON_SQ)) {
      recordViolation(atMiddle, [from, to], middle, "bounded-contact-span");
      return;
    }

    if (depth >= maximumDepth) {
      if (middleViolates) {
        recordViolation(atMiddle, [from, to], middle, "sampled-contact-bracket");
      }
      uncertainties.push({
          timeIntervalSeconds: [from, to],
          surfaces: `${atFrom.firstSurface} / ${atFrom.secondSurface}`,
          minimumObservedSeparationMeters: Math.min(
            atFrom.minimumSeparationMeters,
            atMiddle.minimumSeparationMeters,
            atTo.minimumSeparationMeters,
          ),
          conservativeLowerBoundMeters: Math.max(0,
            Math.max(atFrom.minimumSeparationMeters, atTo.minimumSeparationMeters) - movementBound),
          closestTriangles: [atFrom, atMiddle, atTo]
            .reduce((best, measurement) => measurement.minimumSeparationMeters < best.minimumSeparationMeters
              ? measurement : best).closestTriangles,
        });
      return;
    }

    search(firstA, firstMiddle, secondA, secondMiddle, maximumVertexTravel(firstA, firstMiddle), maximumVertexTravel(secondA, secondMiddle),
      from, middle, atFrom, atMiddle, depth + 1);
    search(firstMiddle, firstB, secondMiddle, secondB, maximumVertexTravel(firstMiddle, firstB), maximumVertexTravel(secondMiddle, secondB),
      middle, to, atMiddle, atTo, depth + 1);
  }

  search(firstStart, firstEnd, secondStart, secondEnd,
    firstTravel, secondTravel, startTimeSeconds, endTimeSeconds, startResult, endResult, 0);

  const trianglePairKey = issue => JSON.stringify(issue.closestTriangles);
  violations.sort((a, b) => a.timeIntervalSeconds[0] - b.timeIntervalSeconds[0]
    || a.timeIntervalSeconds[1] - b.timeIntervalSeconds[1]);
  const mergedViolations = [];
  const intervalMergeTolerance = 0;
  for (const issue of violations) {
    const previous = mergedViolations.at(-1);
    if (previous && previous.surfaces === issue.surfaces
        && trianglePairKey(previous) === trianglePairKey(issue)
        && issue.timeIntervalSeconds[0] <= previous.timeIntervalSeconds[1] + intervalMergeTolerance) {
      previous.timeIntervalSeconds[1] = Math.max(previous.timeIntervalSeconds[1], issue.timeIntervalSeconds[1]);
      if (previous.intervalEvidence === 'sampled-contact-bracket'
          || issue.intervalEvidence === 'sampled-contact-bracket') {
        previous.intervalEvidence = 'sampled-contact-bracket';
      } else if (previous.timeIntervalSeconds[1] > previous.timeIntervalSeconds[0]) {
        previous.intervalEvidence = 'bounded-contact-span';
      }
      if (issue.minimumSeparationMeters < previous.minimumSeparationMeters) {
        previous.minimumSeparationMeters = issue.minimumSeparationMeters;
        previous.detectedAtSeconds = issue.detectedAtSeconds;
      }
    } else {
      mergedViolations.push({ ...issue, timeIntervalSeconds: [...issue.timeIntervalSeconds] });
    }
  }
  const violation = mergedViolations[0] ?? null;
  return {
    firstSurface: firstStart.name,
    secondSurface: secondStart.name,
    minimumSeparationMeters: minimum.distance,
    minimumAtSeconds: minimum.time,
    closestTriangles: minimum.measurement?.closestTriangles ?? null,
    evaluations,
    status: mergedViolations.length ? 'violation' : uncertainties.length ? 'uncertain' : 'clear',
    violation,
    violations: mergedViolations,
    uncertain: uncertainties[0] ?? null,
    uncertainties,
  };
}

/** Return every qualifying triangle pair at one pose; nearest-only API is unchanged. */
export function measureSurfaceContacts(first, second, { minimumSeparationMeters = 0 } = {}) {
  if (!Number.isFinite(minimumSeparationMeters) || minimumSeparationMeters < 0) {
    throw new Error('minimumSeparationMeters must be finite and non-negative');
  }
  const contacts = [];
  const limitSq = Math.max(minimumSeparationMeters ** 2, DISTANCE_EPSILON_SQ);
  function visit(triangle, node) {
    if (boxDistanceSq(triangle.min, triangle.max, node.min, node.max) > limitSq) return;
    if (node.start === undefined) { visit(triangle, node.left); visit(triangle, node.right); return; }
    for (let i = node.start; i < node.end; i += 1) {
      const candidate = node.triangles[i];
      if (boxDistanceSq(triangle.min, triangle.max, candidate.min, candidate.max) > limitSq) continue;
      const distanceSq = triangleDistanceSq(triangle, candidate);
      const distance = Math.sqrt(distanceSq);
      if (distanceSq <= DISTANCE_EPSILON_SQ || distance + 1e-9 < minimumSeparationMeters) {
        contacts.push({ firstSurface: first.name, secondSurface: second.name,
          minimumSeparationMeters: distance, surfaceIntersection: distanceSq <= DISTANCE_EPSILON_SQ,
          closestTriangles: [{ mesh: triangle.mesh, triangle: triangle.index },
            { mesh: candidate.mesh, triangle: candidate.index }] });
      }
    }
  }
  for (const triangle of first.triangles) visit(triangle, second.tree);
  return contacts.sort((a,b) => a.closestTriangles[0].triangle - b.closestTriangles[0].triangle
    || a.closestTriangles[1].triangle - b.closestTriangles[1].triangle);
}

function singleTriangleSurface(surface, triangle) {
  const mesh = surface.articulated?.meshes.find(value => value.uuid === triangle.meshUuid);
  return { name: surface.name, triangles: [triangle], tree: buildTree([triangle]),
    ...(mesh ? { articulated: { meshes: [{ ...mesh,
      triangles: mesh.triangles.filter(value => value.index === triangle.index) }] } } : {}) };
}

/** Sweep each pair independently so persistent contact cannot hide another pair. */
export function measureSweptSurfaceClearance(firstStart, firstEnd, secondStart, secondEnd, options = {}) {
  const { minimumSeparationMeters = 0, startTimeSeconds = 0, endTimeSeconds = 1, maximumDepth = 16 } = options;
  if (!Number.isInteger(maximumDepth) || maximumDepth < 0 || maximumDepth > 20) {
    throw new Error('maximumDepth must be an integer between 0 and 20');
  }
  if (!Number.isFinite(minimumSeparationMeters) || minimumSeparationMeters < 0
      || !Number.isFinite(startTimeSeconds) || !Number.isFinite(endTimeSeconds)
      || endTimeSeconds < startTimeSeconds) throw new Error('Invalid sweep threshold or times');
  for (const [start,end] of [[firstStart,firstEnd],[secondStart,secondEnd]]) {
    if (!start.triangles.length || start.name !== end.name || start.triangles.length !== end.triangles.length) {
      throw new Error('Cannot sweep: surface topology changed or is empty');
    }
    const sharedMesh = start.articulated?.meshes.some(mesh => end.articulated?.meshes.some(other => other.uuid === mesh.uuid));
    if (sharedMesh && !hasStableArticulatedHierarchy(start,end)) throw new Error('Cannot sweep: articulated hierarchy changed');
    // Validate identities and immutable source geometry before any bound may return clear.
    interpolateSurface(start,end,0);
  }
  const firstEnds = new Map(firstEnd.triangles.map(triangle => [triangle.index,triangle]));
  const secondEnds = new Map(secondEnd.triangles.map(triangle => [triangle.index,triangle]));
  let minimum = null, evaluations = 0;
  const violations = [], uncertainties = [];
  for (const a of orderedTriangles(firstStart)) for (const b of orderedTriangles(secondStart)) {
    const result = measureSweptTriangleClearance(
      singleTriangleSurface(firstStart,a), singleTriangleSurface(firstEnd,firstEnds.get(a.index)),
      singleTriangleSurface(secondStart,b), singleTriangleSurface(secondEnd,secondEnds.get(b.index)),
      // A surface-wide cached nearest pair cannot describe this individual pair.
      { minimumSeparationMeters, startTimeSeconds, endTimeSeconds, maximumDepth });
    evaluations += result.evaluations;
    if (!minimum || result.minimumSeparationMeters < minimum.minimumSeparationMeters) minimum = result;
    violations.push(...result.violations); uncertainties.push(...result.uncertainties);
  }
  violations.sort((a,b) => a.timeIntervalSeconds[0]-b.timeIntervalSeconds[0]
    || a.closestTriangles[0].triangle-b.closestTriangles[0].triangle
    || a.closestTriangles[1].triangle-b.closestTriangles[1].triangle);
  return { firstSurface:firstStart.name, secondSurface:secondStart.name,
    minimumSeparationMeters:minimum.minimumSeparationMeters, minimumAtSeconds:minimum.minimumAtSeconds,
    closestTriangles:minimum.closestTriangles, evaluations,
    status:violations.length ? 'violation' : uncertainties.length ? 'uncertain' : 'clear',
    violation:violations[0] ?? null, violations, uncertain:uncertainties[0] ?? null, uncertainties };
}
