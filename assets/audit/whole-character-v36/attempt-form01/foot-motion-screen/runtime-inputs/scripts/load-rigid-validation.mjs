import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// Node motion checks consume the actual exported transforms and vertex buffers.
// Image decoding belongs to the separate hardware-WebGL appearance checks.
// Remove only texture bindings from an in-memory copy; never rewrite the GLB.
export async function loadRigidValidation(bytes) {
  const input=Buffer.from(bytes),length=input.readUInt32LE(12);
  const json=JSON.parse(input.subarray(20,20+length).toString('utf8'));
  delete json.images;delete json.textures;delete json.samplers;
  for(const mat of json.materials||[]){
    delete mat.normalTexture;delete mat.occlusionTexture;delete mat.emissiveTexture;
    if(mat.pbrMetallicRoughness){delete mat.pbrMetallicRoughness.baseColorTexture;delete mat.pbrMetallicRoughness.metallicRoughnessTexture;}
  }
  const raw=Buffer.from(JSON.stringify(json)),pad=Buffer.alloc((4-raw.length%4)%4,32);
  const body=Buffer.concat([raw,pad]),tail=input.subarray(20+length),header=Buffer.alloc(20);
  header.writeUInt32LE(0x46546c67,0);header.writeUInt32LE(2,4);header.writeUInt32LE(20+body.length+tail.length,8);header.writeUInt32LE(body.length,12);header.writeUInt32LE(0x4e4f534a,16);
  const sanitized=Buffer.concat([header,body,tail]);
  return new GLTFLoader().parseAsync(sanitized.buffer.slice(sanitized.byteOffset,sanitized.byteOffset+sanitized.byteLength),'');
}
