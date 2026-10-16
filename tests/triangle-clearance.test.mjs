import assert from 'node:assert/strict';
import test from 'node:test';
import * as THREE from 'three';
import { buildTriangleSurface, measureSurfaceClearance, measureSurfaceContacts, measureSweptSurfaceClearance } from '../scripts/triangle-clearance.mjs';

function triangleSurface(name, triangles) {
  const root = new THREE.Group();
  root.name = name;
  for (const { name: meshName, x, z } of triangles) {
    const geometry = new THREE.BufferGeometry().setAttribute(
      'position',
      new THREE.Float32BufferAttribute([
        x, 0, z,
        x + .2, 0, z,
        x, .2, z,
      ], 3),
    );
    const mesh = new THREE.Mesh(geometry);
    mesh.name = meshName;
    root.add(mesh);
  }
  return buildTriangleSurface(root);
}

test('swept clearance reports every separate collision window with its surfaces and triangles', () => {
  const movingAt = (laneAZ, laneBZ) => triangleSurface('moving', [
    { name: 'moving-lane-a', x: 0, z: laneAZ },
    { name: 'moving-lane-b', x: 2, z: laneBZ },
  ]);
  const obstacle = triangleSurface('obstacles', [
    { name: 'obstacle-lane-a', x: 0, z: 0 },
    { name: 'obstacle-lane-b', x: 2, z: 0 },
  ]);

  const result = measureSweptSurfaceClearance(
    movingAt(-.5, .8),
    movingAt(.5, -.2),
    obstacle,
    obstacle,
    { minimumSeparationMeters: .002 },
  );

  assert.equal(result.status, 'violation');
  assert.equal(result.violations.length, 2);
  assert.equal(result.violation, result.violations[0], 'legacy first-violation access remains available');
  assert.deepEqual(result.violations.map(issue => issue.closestTriangles), [
    [
      { mesh: 'moving-lane-a', triangle: 0 },
      { mesh: 'obstacle-lane-a', triangle: 0 },
    ],
    [
      { mesh: 'moving-lane-b', triangle: 1 },
      { mesh: 'obstacle-lane-b', triangle: 1 },
    ],
  ]);
  assert.ok(result.violations[0].timeIntervalSeconds[0] <= .5
    && result.violations[0].timeIntervalSeconds[1] >= .5);
  assert.ok(result.violations[1].timeIntervalSeconds[0] <= .8
    && result.violations[1].timeIntervalSeconds[1] >= .8);
  assert.ok(result.violations[0].timeIntervalSeconds[1] < result.violations[1].timeIntervalSeconds[0]);
  assert.ok(result.violations.every(issue => issue.surfaces === 'moving / obstacles'
    && Number.isFinite(issue.minimumSeparationMeters)
    && issue.minimumSeparationMeters < .002));
});

function surface(name,zs){const root=new THREE.Group();root.name=name;zs.forEach((z,i)=>{const x=i*2;const m=new THREE.Mesh(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute([x,0,z,x+.2,0,z,x,.2,z],3)));m.name=name+'-'+i;root.add(m);});return buildTriangleSurface(root);}
function sweep(a,b,threshold=.002){const obstacle=surface('obstacle',a.map(()=>0));return measureSweptSurfaceClearance(surface('moving',a),surface('moving',b),obstacle,obstacle,{minimumSeparationMeters:threshold});}

test('both simultaneous contact pairs are reported',()=>{const r=sweep([-.5,-.5],[.5,.5]);assert.equal(new Set(r.violations.map(v=>JSON.stringify(v.closestTriangles))).size,2);});
test('middle contact is retained when endpoints and midpoint involve different pairs',()=>{const r=sweep([0,-.01,-.02],[.02,.01,0]);assert.ok(r.violations.some(v=>v.closestTriangles.some(t=>t.mesh==='moving-1')),'missing middle lane contact');});
test('zero-clearance request cannot label an actual crossing clear',()=>{const r=sweep([-.5],[.5],0);assert.notEqual(r.status,'clear');});

test('contact enumeration visits split BVH leaves and preserves caller pair order',()=>{
 const a=surface('a',Array(16).fill(0)), b=surface('b',Array(16).fill(.001));
 for(const [first,second] of [[a,b],[b,a]]){
  const contacts=measureSurfaceContacts(first,second,{minimumSeparationMeters:.002});
  assert.equal(contacts.length,16);
  assert.equal(new Set(contacts.map(v=>JSON.stringify(v.closestTriangles))).size,16);
  assert.ok(contacts.every(v=>v.closestTriangles[0].mesh.startsWith(first.name+'-') && v.closestTriangles[1].mesh.startsWith(second.name+'-')));
 }
 assert.ok(Math.abs(measureSurfaceClearance(a,b).minimumSeparationMeters-.001)<1e-7);
});
test('persistent contact cannot conceal a second transient contact',()=>{
 const r=sweep([0,-.5],[0,.5]);
 assert.equal(new Set(r.violations.map(v=>v.closestTriangles[0].mesh)).size,2);
 assert.ok(r.violations.some(v=>v.closestTriangles[0].mesh==='moving-0' && v.timeIntervalSeconds[0]===0 && v.timeIntervalSeconds[1]===1));
});
test('separated windows do not acquire a broad interval over a known clear gap',()=>{
 const r=sweep([0,-.01,-.02],[.02,.01,0]);
 assert.ok(!r.violations.some(v=>v.timeIntervalSeconds[0]<=.25 && v.timeIntervalSeconds[1]>=.25));
});
test('depth-limited unproven intervals remain uncertain, including each pair',()=>{
 const obstacle=surface('obstacle',[0,0]);
 const r=measureSweptSurfaceClearance(surface('moving',[-.07,-.07]),surface('moving',[.13,.13]),obstacle,obstacle,{minimumSeparationMeters:.002,maximumDepth:0});
 assert.equal(r.status,'uncertain'); assert.equal(r.uncertainties.length,2);
 assert.equal(r.uncertain,r.uncertainties[0]); assert.equal(r.violations.length,0);
});
test('sweep validates depth, threshold and time inputs',()=>{
 const a=surface('a',[0]),b=surface('b',[1]);
 for(const maximumDepth of [-1,.5,21,NaN]) assert.throws(()=>measureSweptSurfaceClearance(a,a,b,b,{maximumDepth}));
 for(const minimumSeparationMeters of [-1,NaN,Infinity]) assert.throws(()=>measureSweptSurfaceClearance(a,a,b,b,{minimumSeparationMeters}));
 assert.throws(()=>measureSweptSurfaceClearance(a,a,b,b,{startTimeSeconds:2,endTimeSeconds:1}));
});
test('shared articulated mesh cannot silently fall back after a hierarchy change',()=>{
 const root=new THREE.Group();root.name='moving';const m=new THREE.Mesh(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,1,0,0,0,1,0],3)));root.add(m);
 const start=buildTriangleSurface(root);const parent=new THREE.Group();root.add(parent);parent.add(m);const end=buildTriangleSurface(root);const obstacle=surface('obstacle',[2]);
 assert.throws(()=>measureSweptSurfaceClearance(start,end,obstacle,obstacle),/hierarchy changed/);
});
test('mutated source geometry is rejected before a distant interval can be certified',()=>{
 const root=new THREE.Group();root.name='moving';const m=new THREE.Mesh(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,1,0,0,0,1,0],3)));root.add(m);
 const start=buildTriangleSurface(root);m.geometry.attributes.position.setX(0,.2);const end=buildTriangleSurface(root);const obstacle=surface('obstacle',[20]);
 assert.throws(()=>measureSweptSurfaceClearance(start,end,obstacle,obstacle),/source geometry changed/);
});

const MIN_TOE_CLEARANCE_METERS=.002;
function verifyTriangleClearanceKernel() {
  const makeTriangle = (name, points) => {
    const mesh = new THREE.Mesh(new THREE.BufferGeometry().setAttribute(
      'position', new THREE.Float32BufferAttribute(points.flat(), 3),
    ));
    mesh.name = name;
    const root = new THREE.Group();
    root.name = name;
    root.add(mesh);
    return root;
  };
  const plane = makeTriangle('plane', [[0, 0, 0], [1, 0, 0], [0, 1, 0]]);
  const near = makeTriangle('near-parallel', [[0, 0, .01], [1, 0, .01], [0, 1, .01]]);
  const crossing = makeTriangle('crossing', [[.25, .25, -.5], [.25, .25, .5], [.75, .25, 0]]);
  const distance = measureSurfaceClearance(buildTriangleSurface(plane), buildTriangleSurface(near));
  const intersection = measureSurfaceClearance(buildTriangleSurface(plane), buildTriangleSurface(crossing));
  // Keep the mesh identity stable and put the crossing off the midpoint so
  // the test proves adaptive subdivision, not just a single midpoint sample.
  const below = makeTriangle('swept-moving', [[.2, .2, -.07], [.7, .2, -.07], [.2, .7, -.07]]);
  const above = makeTriangle('swept-moving', [[.2, .2, .13], [.7, .2, .13], [.2, .7, .13]]);
  const sweptThrough = measureSweptSurfaceClearance(
    buildTriangleSurface(below), buildTriangleSurface(above),
    buildTriangleSurface(plane), buildTriangleSurface(plane),
    { minimumSeparationMeters: MIN_TOE_CLEARANCE_METERS, startTimeSeconds: 4, endTimeSeconds: 5 },
  );
  const arcScene = new THREE.Group();
  const pivot = new THREE.Group();
  pivot.name = 'articulated-arc-pivot';
  const movingMesh = new THREE.Mesh(new THREE.BufferGeometry().setAttribute(
    'position', new THREE.Float32BufferAttribute([
      .99, -.01, 0,
      1.01, -.01, 0,
      1, .01, 0,
    ], 3),
  ));
  movingMesh.name = 'articulated-arc-triangle';
  pivot.add(movingMesh);
  const obstacle = makeTriangle('arc-obstacle', [
    [.998, -.006, .001],
    [1.002, -.006, .001],
    [1, .006, .001],
  ]);
  arcScene.add(pivot, obstacle);
  pivot.rotation.z = -.35;
  const arcStart = buildTriangleSurface(pivot);
  pivot.rotation.z = .35;
  const arcEnd = buildTriangleSurface(pivot);
  const obstacleSurface = buildTriangleSurface(obstacle);
  const firstArcTriangle = arcStart.triangles[0];
  const lastArcTriangle = arcEnd.triangles[0];
  const chordRoot = makeTriangle('arc-endpoint-chord', [
    firstArcTriangle.a.clone().lerp(lastArcTriangle.a, .5).toArray(),
    firstArcTriangle.b.clone().lerp(lastArcTriangle.b, .5).toArray(),
    firstArcTriangle.c.clone().lerp(lastArcTriangle.c, .5).toArray(),
  ]);
  const chordClearance = measureSurfaceClearance(buildTriangleSurface(chordRoot), obstacleSurface);
  const articulatedArc = measureSweptSurfaceClearance(
    arcStart, arcEnd, obstacleSurface, obstacleSurface,
    { minimumSeparationMeters: MIN_TOE_CLEARANCE_METERS },
  );
  const laneTriangle = (name, x, z) => makeTriangle(name, [
    [x, 0, z], [x + .2, 0, z], [x, .2, z],
  ]);
  const movingAt = (laneAZ, laneBZ) => {
    const surface = new THREE.Group();
    surface.name = 'double-window-moving';
    surface.add(laneTriangle('moving-lane-a', 0, laneAZ));
    surface.add(laneTriangle('moving-lane-b', 2, laneBZ));
    return buildTriangleSurface(surface);
  };
  const doubleWindowObstacleRoot = new THREE.Group();
  doubleWindowObstacleRoot.name = 'double-window-obstacle';
  doubleWindowObstacleRoot.add(laneTriangle('obstacle-lane-a', 0, 0));
  doubleWindowObstacleRoot.add(laneTriangle('obstacle-lane-b', 2, 0));
  const doubleWindowObstacle = buildTriangleSurface(doubleWindowObstacleRoot);
  const doubleWindow = measureSweptSurfaceClearance(
    movingAt(-.5, .8), movingAt(.5, -.2),
    doubleWindowObstacle, doubleWindowObstacle,
    { minimumSeparationMeters: MIN_TOE_CLEARANCE_METERS },
  );
  assert.ok(Math.abs(distance.minimumSeparationMeters - .01) < 1e-6,
    `parallel-triangle separation was ${distance.minimumSeparationMeters}m`);
  assert.equal(distance.surfaceIntersection, false);
  assert.equal(intersection.surfaceIntersection, true, 'crossing triangle surfaces were not detected');
  assert.equal(sweptThrough.status, 'violation', 'triangle surfaces crossing between endpoints were not detected');
  assert.ok(sweptThrough.violation.timeIntervalSeconds[0] <= 4.35
    && sweptThrough.violation.timeIntervalSeconds[1] >= 4.35,
  'adaptive sweep did not bracket the off-midpoint collision time');
  assert.ok(chordClearance.minimumSeparationMeters > MIN_TOE_CLEARANCE_METERS,
    `straight endpoint chord unexpectedly approached the obstacle: ${chordClearance.minimumSeparationMeters}m`);
  assert.equal(articulatedArc.status, 'violation',
    'the rotating articulated path collided with the obstacle but was not detected');
  assert.ok(articulatedArc.violation.minimumSeparationMeters < MIN_TOE_CLEARANCE_METERS,
    'the articulated-path regression did not cross the configured clearance threshold');
  assert.equal(doubleWindow.violations.length, 2,
    `expected two separate between-pose collision intervals, received ${JSON.stringify(doubleWindow.violations)}`);
  assert.notDeepEqual(
    doubleWindow.violations[0].closestTriangles,
    doubleWindow.violations[1].closestTriangles,
    'the separate collision windows did not retain their distinct triangle identities',
  );
  assert.ok(doubleWindow.violations[0].timeIntervalSeconds[1] < doubleWindow.violations[1].timeIntervalSeconds[0],
    'separate collision windows were incorrectly merged');
  return {
    parallelTriangleSeparationMeters: distance.minimumSeparationMeters,
    crossingTriangleIntersectionDetected: intersection.surfaceIntersection,
    betweenPoseIntersectionDetected: sweptThrough.status === 'violation',
    betweenPoseIntervalSeconds: sweptThrough.violation.timeIntervalSeconds,
    betweenPoseMinimumSeparationMeters: sweptThrough.violation.minimumSeparationMeters,
    curvedPathChordClearanceMeters: chordClearance.minimumSeparationMeters,
    curvedPathCollisionDetected: articulatedArc.status === 'violation',
    curvedPathMinimumSeparationMeters: articulatedArc.violation.minimumSeparationMeters,
    allBetweenPoseWindowsReported: doubleWindow.violations.length,
    betweenPoseWindows: doubleWindow.violations,
    minimumRequiredSeparationMeters: MIN_TOE_CLEARANCE_METERS,
  };
}


test('retained static, off-midpoint, articulated-arc and separate-window kernel cases',()=>{verifyTriangleClearanceKernel();});
