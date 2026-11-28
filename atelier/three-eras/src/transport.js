import {TextureSource} from 'three'
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js'
export const modelDigest='2f9ff345f3a06732367d5c1dd2d2703b924bc3061b25d7a040bf24b9b597ba54'
export async function fetchModel(url){
 const response=await fetch(url)
 if(!response.ok)throw Error('Could not load model')
 const raw=new Uint8Array(await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer())
 const n=new DataView(raw.buffer).getUint32(0,true)
 const header=JSON.parse(new TextDecoder().decode(raw.subarray(4,4+n)))
 if(header.sha256!==modelDigest || header.bytes!==46141044)throw Error('Unexpected model version')
 const bytes=new Uint8Array(header.bytes);let from=n+4,to=0
 await MeshoptDecoder.ready
 for(const [size,stored,method,stride] of header.ranges){
   const input=raw.subarray(from,from+stored),output=bytes.subarray(to,to+size)
   if(method==='raw')output.set(input)
   else if(method==='v')MeshoptDecoder.decodeVertexBuffer(output,size/stride,stride,input)
   else if(method==='i')MeshoptDecoder.decodeIndexSequence(output,size/stride,stride,input)
   else throw Error('Unsupported model encoding')
   from+=stored;to+=size
 }
 const hash=new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))
 if(from!==raw.length||to!==header.bytes||Array.from(hash,b=>b.toString(16).padStart(2,'0')).join('')!==modelDigest)throw Error('Model failed integrity verification')
 return bytes.buffer
}

export const fullDigest='20632ff6116f93827bc814d53301749dec1ef035165749db2d819bb89edcd41c'
function layout(bytes){
 const size=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength).getUint32(12,true)
 return {doc:JSON.parse(new TextDecoder().decode(bytes.subarray(20,20+size))), start:28+size}
}
function sha(bytes){return crypto.subtle.digest('SHA-256',bytes).then(h=>Array.from(new Uint8Array(h),b=>b.toString(16).padStart(2,'0')).join(''))}
// The second transfer contains only the full-resolution textures and the original GLB header.
// Vertex buffers, winding, animation and all non-image payloads are identical at first draw.
export async function applyDetail(url,first,gltf,renderer) {
 const r=await fetch(url);if(!r.ok)throw Error('Full surface maps unavailable')
 const details=new Uint8Array(await new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer())
 const full=layout(details),lowBytes=new Uint8Array(first),low=layout(lowBytes)
 const exact=new Uint8Array(55884688);exact.set(details.subarray(0,full.start));let offset=full.start
 const ids=new Set(full.doc.images.map(i=>i.bufferView)),images=new Map()
 for(const [i,view] of full.doc.bufferViews.entries()){
  let payload
  if(ids.has(i)){payload=details.subarray(offset,offset+view.byteLength);images.set(i,payload);offset+=view.byteLength}
  else{const v=low.doc.bufferViews[i];if(v.byteLength!==view.byteLength)throw Error('Incompatible geometry');payload=lowBytes.subarray(low.start+v.byteOffset,low.start+v.byteOffset+v.byteLength)}
  exact.set(payload,full.start+view.byteOffset)
 }
 if(offset!==details.length||await sha(exact)!==fullDigest)throw Error('Full material integrity check failed')
 const decoded=await Promise.all(full.doc.images.map(async i=>{
    const blob=new Blob([images.get(i.bufferView)],{type:i.mimeType})
    if(typeof createImageBitmap==='function')return createImageBitmap(blob,{colorSpaceConversion:'none',premultiplyAlpha:'none'})
    const img=new Image(),url=URL.createObjectURL(blob);try{img.src=url;await img.decode();return img}finally{URL.revokeObjectURL(url)}
 }))
 const textures=await Promise.all(full.doc.textures.map((_,i)=>gltf.parser.getDependency('texture',i)))
 // A WebGL2 texture's allocated dimensions are immutable. Prepare full-sized GPU
 // sources separately so that a rejected upload leaves the preview usable.
 const sources=decoded.map(image=>new TextureSource(image))
 const replacements=new Map(textures.map((texture,i)=>[texture.source,sources[full.doc.textures[i].source]]))
 const original=new Map()
 for(const texture of new Set([...textures,...gltf.parser.associations.keys()])){
   if(texture.isTexture && replacements.has(texture.source))original.set(texture,texture.source)
 }
 const gl=renderer.getContext(),probes=[],changed=[]
 let committed=false
 try{
   for(const [texture,preview] of original){
     const fullTexture=texture.clone()
     fullTexture.source=replacements.get(preview)
     fullTexture.needsUpdate=true
     probes.push(fullTexture)
     renderer.initTexture(fullTexture)
     if(gl.getError()!==gl.NO_ERROR || gl.isContextLost())throw Error('Full surface GPU allocation failed')
   }
   // Keep the material's existing Texture object, including its UV set, color
   // space and sampler. Its old allocation is released before changing sources.
   for(const [texture,preview] of original){
     texture.dispose()
     texture.source=replacements.get(preview)
     changed.push(texture)
     texture.needsUpdate=true
     renderer.initTexture(texture)
   }
   if(gl.getError()!==gl.NO_ERROR || gl.isContextLost())throw Error('Full surfaces unavailable')
   committed=true
 }catch(error){
   for(const texture of changed){
     texture.dispose()
     texture.source=original.get(texture)
     texture.needsUpdate=true
   }
   throw error
 }finally{
   for(const probe of probes)probe.dispose()
   if(!committed)for(const image of decoded)image.close?.()
 }
 return fullDigest
}
