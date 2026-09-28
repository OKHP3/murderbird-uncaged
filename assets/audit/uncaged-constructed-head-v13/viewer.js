import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const mount=document.querySelector('#viewer'),status=document.querySelector('#status'),still=document.querySelector('#render-fallback');
const modelUrl=new URL('../../models/uncaged-constructed-head-v13/attempt-01/murderbird-constructed-head-v13.glb',import.meta.url).href;
let model,renderer,camera,controls;let fixed=false;
const positions={reference:[-6,2.75,3.5],front:[0,1.65,7],side:[-7.5,1.25,0],rear:[0,1.65,-7]};
function showCamera(name){camera.position.fromArray(positions[name]);controls.target.set(0,1.02,.08);camera.zoom=1;camera.updateProjectionMatrix();controls.update();document.querySelectorAll('[data-camera]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.camera===name)));}
function era(){const choice=document.querySelector('#era').value;model?.traverse(o=>{if(o.isMesh)o.visible=String(o.userData.exteriorEras||'maker,mechanic,builder').split(',').includes(choice);});}
function showFixed(value){if(!value&&!model)return;fixed=value;mount.hidden=value;still.hidden=!value;document.querySelector('#toggle-render').setAttribute('aria-pressed',String(value));document.querySelector('#toggle-render').textContent=value?'Show actual 3D':'Show fixed render';status.textContent=value?'Fixed native reference-angle render · not interactive motion.':'Actual WebGL model · neutral rest geometry · motion not yet reconciled.';document.querySelectorAll('[data-camera]').forEach(b=>b.disabled=value);document.querySelector('#era').disabled=value;}
document.querySelector('#toggle-render').addEventListener('click',()=>showFixed(!fixed));
document.querySelector('#toggle-render').disabled=true;document.querySelector('#era').disabled=true;document.querySelectorAll('[data-camera]').forEach(b=>b.disabled=true);
try{
 renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor(0x53575b);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;mount.appendChild(renderer.domElement);
 const scene=new THREE.Scene();scene.add(new THREE.HemisphereLight(0xffffff,0x626874,2.1));
 for(const [pos,intensity] of [[[-3,5,4],3.4],[[4,3,-2],1.6]]){const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.fromArray(pos);scene.add(light);}
 camera=new THREE.OrthographicCamera(-1.25,1.25,1.25,-1.25,.01,50);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minZoom=.6;controls.maxZoom=3;
 const resize=()=>{const w=mount.clientWidth||400,h=mount.clientHeight||530;camera.left=-1.25*w/h;camera.right=1.25*w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false);};new ResizeObserver(resize).observe(mount);resize();showCamera('reference');
 const gltf=await new GLTFLoader().loadAsync(modelUrl);model=gltf.scene;
 const clay=new THREE.MeshStandardMaterial({color:0xadb0b3,metalness:.05,roughness:.72});
 let meshes=0;model.traverse(o=>{if(o.isMesh){o.material=clay;meshes++;}});scene.add(model);era();
 const gl=renderer.getContext(),info=gl.getExtension('WEBGL_debug_renderer_info');
 window.__silhouetteReview={modelUrl,scope:'static exported rest geometry; no main exhibit mechanism or motion driver',meshCount:meshes,renderer:info?gl.getParameter(info.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),snapshot:()=>({era:document.querySelector('#era').value,fixedRender:fixed,visibleMeshes:[...function*(){const out=[];model.traverse(o=>{if(o.isMesh&&o.visible)out.push(o.name)});yield* out;}()].length,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,camera:camera.position.toArray(),target:controls.target.toArray()})};
 document.querySelector('#toggle-render').disabled=false;document.querySelector('#era').disabled=false;document.querySelectorAll('[data-camera]').forEach(b=>b.disabled=false);
 status.textContent='Actual WebGL model · neutral rest geometry · motion not yet reconciled.';
 document.querySelector('#era').addEventListener('change',era);document.querySelectorAll('[data-camera]').forEach(b=>b.addEventListener('click',()=>showCamera(b.dataset.camera)));
 renderer.setAnimationLoop(()=>{if(!fixed){controls.update();renderer.render(scene,camera);}});
}catch(error){showFixed(true);document.querySelector('#toggle-render').textContent='Fixed render only';status.textContent='Fixed native render shown. The 3D preview is unavailable; reload this page to retry.';console.error(error);}
