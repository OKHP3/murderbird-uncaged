// Read-only world-space bounds of actual GLB parts. Not a likeness score.
import fs from 'node:fs';
import crypto from 'node:crypto';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { Box3, Vector3 } from 'three';
const path=process.argv[2], bytes=fs.readFileSync(path);
const {scene}=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
scene.updateMatrixWorld(true);
const crown=new Box3();let count=0, optic=null;
scene.traverse(o=>{
 const name=o.name.replaceAll('_',' ');
 if(o.isMesh&&name.startsWith('V38 swept crown course ')){crown.union(new Box3().setFromObject(o));count++;}
 if(o.isMesh&&name==='V33 recessed optic retaining lip 1')optic=new Box3().setFromObject(o);
});
if(count!==58||!optic)throw new Error('Expected actual crown58 and optic lip');
const center=optic.getCenter(new Vector3()),radius=optic.getSize(new Vector3()).y/2;
console.log(JSON.stringify({path,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),coordinates:'GLB world Y=height,Z=forward (native negativeY)',crownMeshCount:count,crownBounds:[crown.min.toArray(),crown.max.toArray()],opticCenter:center.toArray(),outerCupRadius:radius,topAboveEyeInCupRadii:(crown.max.y-center.y)/radius,rearBeyondEyeInCupRadii:(center.z-crown.min.z)/radius,limit:'Actual rendered-part bounds, not metrology from reference art or a similarity score'},null,2));
