import * as THREE from 'three'
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'
import concreteUrl from './stage-assets/concrete.jpg?url'
import enamelUrl from './stage-assets/enamel.jpg?url'
import plasterUrl from './stage-assets/plaster.jpg?url'
import oakUrl from './stage-assets/oak.jpg?url'
import phosphorUrl from './stage-assets/phosphor.png?url'
import contactUrl from './stage-assets/standing-contact.png?url'
import ironUrl from './maps/stand-albedo.jpg?url'
import floorNormalUrl from './maps/floor-normal.jpg?url'

const TAU = Math.PI * 2
const identity = new THREE.Matrix4()

function frame(x, y, z, heading = 0) {
  return new THREE.Matrix4().makeRotationY(heading).setPosition(x, y, z)
}

// Closed radial loft of rounded rectangular profiles. The tube, bezel and case
// share a centerline but have different depth and curvature, as in a real CRT.
function roundedLoop(width, height, radius, z, steps = 6) {
  const points = []
  for (let i = 0; i < 4; i++) {
    const cx = (i === 0 || i === 3 ? 1 : -1) * (width / 2 - radius)
    const cy = (i < 2 ? 1 : -1) * (height / 2 - radius)
    for (let j = 0; j <= steps; j++) {
      const angle = Math.PI * .5 * (i + j / steps)
      points.push([cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius, z])
    }
  }
  return points
}

function ringLoft(profiles, backCap = false) {
  const positions = [], uvs = [], indices = []
  const rings = profiles.map(([w, h, r, z]) => roundedLoop(w, h, r, z))
  const count = rings[0].length
  for (let k = 0; k < rings.length; k++) {
    for (let j = 0; j < count; j++) {
      positions.push(...rings[k][j])
      uvs.push(j / count, k / (rings.length - 1))
      if (k > 0) {
        const a = (k - 1) * count + j, b = (k - 1) * count + (j + 1) % count
        indices.push(a, b, b + count, a, b + count, a + count)
      }
    }
  }
  if (backCap) {
    for (let j = 1; j < count - 1; j++) indices.push(0, j + 1, j)
  }
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2))
  geometry.setIndex(indices)
  geometry.computeVertexNormals()
  return geometry
}

function curvedGlass() {
  const positions = [], uvs = [], indices = []
  const w = .322, h = .228, radius = .025, nx = 32, ny = 22
  for (let j = 0; j <= ny; j++) {
    const v = j / ny, y = (v - .5) * h
    const dy = Math.max(0, Math.abs(y) - h / 2 + radius)
    const half = w / 2 - radius + Math.sqrt(Math.max(0, radius * radius - dy * dy))
    for (let i = 0; i <= nx; i++) {
      const u = i / nx, x = (u * 2 - 1) * half
      const lift = .008 * (1 - (x / (w / 2)) ** 2) * (1 - (y / (h / 2)) ** 2)
      positions.push(x, y, lift); uvs.push(x / w + .5, v)
      if (i < nx && j < ny) {
        const a = j * (nx + 1) + i
        indices.push(a, a + 1, a + nx + 2, a, a + nx + 2, a + nx + 1)
      }
    }
  }
  const g = new THREE.BufferGeometry()
  g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2))
  g.setIndex(indices); g.computeVertexNormals(); return g
}

function workshopEnvironment(renderer) {
  // Large, soft off-camera cards give the worked metal legible reflections.
  // The dark gaps between them keep recessed parts readable on an orbit.
  const width = 256, height = 128, data = new Float32Array(width * height * 4)
  const cards = [
    [[-1.8, 1.65, .7], [.89,.81,.68], 4.2, .18, .40],
    [[1.3, 1.30, -.65], [.85,.67,.45], 3.1, .14, .37],
    [[-.35, .75, 1.8], [.49,.69,.90], 1.9, .36, .42],
    [[.35, 2.1, .35], [.70,.69,.66], 1.45, .52, .20],
  ].map(([xyz,color,gain,a,b]) => {
    const normal = new THREE.Vector3(...xyz).normalize()
    const right = new THREE.Vector3(0,1,0).cross(normal).normalize()
    const up = normal.clone().cross(right).normalize()
    return {normal, right, up, color, gain, a, b}
  })
  const dir = new THREE.Vector3()
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const phi = (x + .5) / width * TAU - Math.PI
    const lat = ((y + .5) / height - .5) * Math.PI
    dir.set(Math.cos(lat)*Math.cos(phi), Math.sin(lat), Math.cos(lat)*Math.sin(phi))
    const floor = .018 + .075 * Math.max(0, dir.y)
    const c = [floor*1.07, floor, floor*.89]
    for (const card of cards) {
      const d = dir.dot(card.normal)
      if (d <= .3) continue
      const h = Math.abs(dir.dot(card.right)) / (d*card.a)
      const v = Math.abs(dir.dot(card.up)) / (d*card.b)
      const gain = card.gain * Math.exp(-.88 * (h**4 + v**4))
      for (let i=0; i<3; i++) c[i] += card.color[i]*gain
    }
    data.set([c[0],c[1],c[2],1], 4*(y*width+x))
  }
  const texture = new THREE.DataTexture(data, width, height, THREE.RGBAFormat, THREE.FloatType)
  texture.mapping = THREE.EquirectangularReflectionMapping
  texture.colorSpace = THREE.LinearSRGBColorSpace
  texture.needsUpdate = true
  const pmrem = new THREE.PMREMGenerator(renderer)
  const env = pmrem.fromEquirectangular(texture)
  texture.dispose(); pmrem.dispose()
  return env
}

export function makeStage(renderer, scene) {
  const architecture = new THREE.Group()
  architecture.name = 'First Choice workshop'
  scene.add(architecture)
  const ownedMaterials = [], textures = [], prototypeGeometry = new Set()
  const tex = (url, repeatX = 1, repeatY = 1, color = true) => {
    const t = new THREE.TextureLoader().load(url)
    if (repeatX !== 1 || repeatY !== 1) t.wrapS = t.wrapT = THREE.RepeatWrapping
    t.repeat.set(repeatX, repeatY)
    t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy())
    if (color) t.colorSpace = THREE.SRGBColorSpace
    textures.push(t); return t
  }
  const make = (color, roughness, metalness=0, map=null, more={}) => {
    const m = new THREE.MeshStandardMaterial({color,roughness,metalness,map,...more})
    ownedMaterials.push(m); return m
  }
  const concrete = tex(concreteUrl, 8, 8)
  const normal = tex(floorNormalUrl, 13, 13, false)
  const oak = tex(oakUrl)
  const plaster = tex(plasterUrl, 2.8, 1)
  const iron = tex(ironUrl)
  const enamel = tex(enamelUrl)
  const screen = tex(phosphorUrl)
  const materials = {
    wall: make(0xafaca0, .98, 0, plaster),
    wood: make(0x999995, .80, .01, oak),
    worn: make(0xbbb7ad, .58, .34, enamel),
    paint: make(0xa5a496, .75, .27, enamel),
    black: make(0x222421,.66,.40),
    iron: make(0x5f5a4d,.54,.73,iron),
    brass: make(0x827253,.48,.72),
    bezel: make(0x242522,.71,.12),
    case: make(0xbbbaab,.76,.24,enamel),
    key: make(0x3e403b,.75,.08),
    edges: make(0x776b59,.61,.34),
    leather: make(0x4b4033,.8,.03),
    paper: make(0xa09478,.91),
    filament: make(0xf3deb0,.57,0,null,{emissive:0xffcb7d,emissiveIntensity:1.6}),
    lampInside: make(0xc4b69b,.67,.14),
    glass: make(0xa8b9ad,.38,.10,screen,{emissive:new THREE.Color(0xadbfae),emissiveMap:screen,emissiveIntensity:1.55}),
  }
  const ground = make(0xc0bcb5, .86, .055, concrete, {normalMap:normal,normalScale:new THREE.Vector2(.16,.16)})
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(34,34),ground)
  floor.rotation.x = -Math.PI/2; floor.position.y = -.001
  floor.receiveShadow = true; scene.add(floor)

  // The alpha mask is a softened height projection of the actual fixed model groups.
  const contactMap = tex(contactUrl)
  const contactMaterial = new THREE.MeshBasicMaterial({map:contactMap,transparent:true,depthWrite:false,opacity:.96,
                                                        polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1})
  const contact = new THREE.Mesh(new THREE.PlaneGeometry(2.30,2.30),contactMaterial)
  contact.name = 'Foot and stand contact'; contact.rotation.x = -Math.PI/2
  contact.position.set(0,-.0004,.39); contact.renderOrder = 1
  scene.add(contact)
  const env = workshopEnvironment(renderer)
  scene.environment = env.texture

  const batches = new Map()
  function stagingGroup(name) {
    const g = new THREE.Group(); g.name = name; architecture.add(g)
    batches.set(g,new Map()); return g
  }
  const benchGroup = stagingGroup('Terminal bench')
  const room = stagingGroup('Workshop walls')
  const backGroup = stagingGroup('Repair bay')
  const frontWallGroup = stagingGroup('Opposite wall')
  const cube = new THREE.BoxGeometry(1,1,1)
  const cylinder = new THREE.CylinderGeometry(1,1,1,16)
  function part(group, geometry, material, at, scale=[1,1,1], rotation=[0,0,0], parent=identity) {
    prototypeGeometry.add(geometry)
    const matrix = new THREE.Matrix4().compose(new THREE.Vector3(...at),
      new THREE.Quaternion().setFromEuler(new THREE.Euler(...rotation)),new THREE.Vector3(...scale)).premultiply(parent)
    const g = geometry.index ? geometry.toNonIndexed() : geometry.clone()
    g.applyMatrix4(matrix)
    const bucket = batches.get(group)
    if (!bucket.has(material)) bucket.set(material,[])
    bucket.get(material).push(g)
  }
  function box(g,m,at,sz,parent,rotation) { part(g,cube,m,at,sz,rotation,parent) }
  function softBox(g,m,at,sz,bevel,parent,rotation) {
    part(g,new RoundedBoxGeometry(...sz,1,bevel),m,at,undefined,rotation,parent)
  }
  function pin(g,m,at,radius,depth,parent,rotation) {
    part(g,cylinder,m,at,[radius,depth,radius],rotation,parent)
  }
  function tube(g,m,points,r,parent) {
    const curve = new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)))
    part(g,new THREE.TubeGeometry(curve,Math.max(8,points.length*4),r,7,false),m,[0,0,0],undefined,undefined,parent)
  }
  const m = materials
  function benchContact(g, matrix, width, depth) {
    const size=128, fullW=width+.55, fullD=depth+.62
    const rgba=new Uint8Array(size*size*4)
    const footXs=[-.38*width-.065,.415*width]
    for(let j=0;j<size;j++) for(let i=0;i<size;i++) {
      const x=(i/(size-1)-.5)*fullW, z=(j/(size-1)-.5)*fullD
      const edge=Math.hypot(Math.max(0,Math.abs(x)-width*.42),
                            Math.max(0,Math.abs(z)-depth*.29))
      let opacity=.19*Math.exp(-((edge/.16)**2))
      const cupboard=Math.hypot(Math.max(0,Math.abs(x+.38*width-.095)-.14),
                                Math.max(0,Math.abs(z)-depth*.27))
      opacity+=.33*Math.exp(-((cupboard/.105)**2))
      for(const fx of footXs) for(const fz of [-1,1]) {
        const d=Math.hypot(x-fx,z-fz*(depth*.5-.065))
        opacity+=.59*Math.exp(-((d/.043)**2))
      }
      rgba.set([18,15,12,Math.round(255*Math.min(.90,opacity))],4*(j*size+i))
    }
    const t=new THREE.DataTexture(rgba,size,size)
    t.flipY=true; t.magFilter=t.minFilter=THREE.LinearFilter
    t.colorSpace=THREE.SRGBColorSpace;t.needsUpdate=true;textures.push(t)
    const mat=new THREE.MeshBasicMaterial({map:t,transparent:true,depthWrite:false})
    ownedMaterials.push(mat)
    const contactPlane=new THREE.Mesh(new THREE.PlaneGeometry(fullW,fullD),mat)
    contactPlane.matrixAutoUpdate=false
    contactPlane.matrix.copy(matrix).multiply(new THREE.Matrix4().makeTranslation(0,-.00025,0))
      .multiply(new THREE.Matrix4().makeRotationX(-Math.PI/2))
    contactPlane.renderOrder=1
    g.add(contactPlane)
  }
  function table(g, matrix, width, depth, height) {
    const under = height-.065, left = -.38*width, right = .415*width
    box(g,m.black,[0,under-.045,0],[width-.035,.085,depth-.035],matrix)
    box(g,m.wood,[0,height-.031,0],[width,.058,depth],matrix)
    box(g,m.worn,[0,under+.002,depth*.5],[width,.027,.012],matrix)
    for (const x of [left-.065,right]) for (const z of [-1,1]) {
      const zz = z*(depth*.5-.065)
      box(g,m.paint,[x,under*.5,zz],[.047,under,.052],matrix)
      box(g,m.black,[x,.023,zz],[.079,.044,.084],matrix)
    }
    for(let i=0;i<9;i++) {
      const x=width*(i/8-.5)*.95
      pin(g,m.iron,[x,under,depth/2+.006],.0048,.006,matrix,[Math.PI/2,0,0])
    }
    // Folded sheet drawer bank, with a deep toe-kick and rolled pull handles.
    softBox(g,m.paint,[left+.095,under*.56,-.008],[.46,under*.84,depth-.11],.009,matrix)
    for (let k=0;k<3;k++) {
      const y=.25+k*.143, z=depth*.5-.046
      softBox(g,m.worn,[left+.095,y,z],[.433,.123,.018],.003,matrix)
      box(g,m.brass,[left+.246,y+.028,z+.010],[.040,.017,.003],matrix)
      box(g,m.black,[left+.246,y+.028,z+.012],[.029,.009,.001],matrix)
      tube(g,m.edges,[[left+.029,y+.016,z+.008],[left+.03,y+.005,z+.026],
                       [left+.16,y+.005,z+.026],[left+.162,y+.016,z+.008]],.006,matrix)
    }
    const shelfStart=left+.095+.218, shelfEnd=right+.021
    const shelfMid=(shelfStart+shelfEnd)/2
    for (const z of [-1,1]) {
      box(g,m.black,[shelfMid,.141,z*(depth*.5-.077)],[shelfEnd-shelfStart,.042,.040],matrix)
    }
    box(g,m.worn,[shelfMid,.161,-.002],[shelfEnd-shelfStart,.018,depth-.15],matrix)
    benchContact(g,matrix,width,depth)
    tube(g,m.paint,[[left+.22,.183,-depth*.39],[right-.01,under-.06,-depth*.39]],.014,matrix)
  }

  const bench = frame(.20,0,-1.78,-1.16)
  table(benchGroup,bench,1.63,.72,.776)
  const terminal = bench.clone().multiply(frame(-.286,.789,-.055,.11))
  softBox(benchGroup,m.black,[0,.021,-.018],[.335,.043,.268],.012,terminal)
  const terminalCenter = [0,.195,-.008]
  part(benchGroup,ringLoft([[.285,.221,.024,-.189],[.320,.261,.023,-.154],
                            [.417,.324,.017,.078],[.421,.327,.016,.122],[.416,.322,.016,.133]],true),
       m.case,terminalCenter,undefined,undefined,terminal)
  part(benchGroup,ringLoft([[.414,.319,.017,.132],[.406,.314,.015,.138],
                            [.357,.262,.021,.138],[.337,.247,.025,.130],[.322,.229,.026,.124]]),
       m.bezel,terminalCenter,undefined,undefined,terminal)
  part(benchGroup,curvedGlass(),m.glass,[0,.195,.117],undefined,undefined,terminal)
  for (const x of [-.188,.188]) for(const y of [.064,.326]) {
    pin(benchGroup,m.iron,[x,y,.131],.0055,.0034,terminal,[Math.PI/2,0,0])
  }
  pin(benchGroup,m.black,[.163,.054,.131],.009,.008,terminal,[Math.PI/2,0,0])
  for (let i=0;i<9;i++) box(benchGroup,m.black,[-.209,.148+i*.012,.035],[.002,.003,.070],terminal)
  const keyboard = bench.clone().multiply(frame(.094,.784,.222,-.12))
  softBox(benchGroup,m.case,[0,.014,0],[.493,.030,.156],.007,keyboard,[-.06,0,0])
  for(let row=0;row<5;row++) {
    for(let col=0;col<16;col++) {
      if (row===4 && col>3 && col<11) continue
      const space = row===4 && col===3
      box(benchGroup,m.key,[-.200+col*.026+(space?.095:0),.034-row*.0011,(row-2)*.025],
          [space?.207:.022,.009,.020],keyboard,[-.055,0,0])
    }
  }
  tube(benchGroup,m.black,[[-.06,.808,.07],[-.02,.816,-.06],[-.1,.797,-.22],[-.26,.802,-.25]],.0032,bench)
  tube(benchGroup,m.black,[[-.34,.847,-.18],[-.49,.829,-.31],[-.56,.71,-.372],
                           [-.53,.30,-.387],[-.40,.132,-.27]],.005,bench)
  softBox(benchGroup,m.leather,[.50,.792,-.085],[.19,.018,.236],.003,bench,[0,-.17,0])
  box(benchGroup,m.paper,[.51,.796,-.083],[.171,.009,.216],bench,[0,-.17,0])

  // Single-sided walls stay open to the orbit when the visitor moves outside them.
  const wall = new THREE.PlaneGeometry(15.6,4.65)
  part(room,wall,m.wall,[5.08,2.305,-.3],undefined,[0,-Math.PI/2,0])
  part(room,wall,m.wall,[.1,2.305,-7.1])
  part(frontWallGroup,wall,m.wall,[-6.55,2.305,.2],undefined,[0,Math.PI/2,0])
  part(frontWallGroup,wall,m.wall,[.1,2.305,7.6],undefined,[0,Math.PI,0])
  const rear = frame(4.57,0,1.72,-Math.PI/2)
  table(backGroup,rear,2.35,.60,.854)
  // Localized peg rail and three hanging wrenches sit inside the repair bay.
  box(backGroup,m.wood,[0,1.36,-.254],[1.88,.054,.036],rear)
  for (let i=0;i<5;i++) {
    const x=-.43+i*.159, h=.14+(i%3)*.038
    pin(backGroup,m.iron,[x,1.375,-.216],.008,.055,rear,[Math.PI/2,0,0])
    softBox(backGroup,m.iron,[x,1.29-h*.4,-.196],[.019,h,.011],.003,rear,[0,0,(i-2)*.04])
    const ring=new THREE.TorusGeometry(.017,.0042,6,14)
    part(backGroup,ring,m.worn,[x,1.283-h*.90,-.196],undefined,undefined,rear)
  }
  // A short coil hangs on its own stud, outside the bird's viewing corridor.
  pin(backGroup,m.iron,[.76,1.59,-.237],.010,.075,rear,[Math.PI/2,0,0])
  const coil=[]
  for(let i=0;i<=54;i++) {
    const a=i/54*TAU*3.25
    coil.push([.76+.087*Math.cos(a),1.471+.105*Math.sin(a),-.211+.016*i/54])
  }
  coil.push([.718,1.315,-.190],[.714,1.273,-.193])
  tube(backGroup,m.black,coil,.0085,rear)
  // Small bench vise beside a dark storage can and a folded shop rag.
  softBox(backGroup,m.black,[.70,.892,.095],[.19,.065,.14],.012,rear)
  softBox(backGroup,m.paint,[.69,.958,.085],[.18,.103,.105],.014,rear)
  for (const x of [.645,.728]) box(backGroup,m.iron,[x,1.018,.087],[.028,.035,.116],rear)
  tube(backGroup,m.worn,[[.78,.961,.075],[.87,.961,.075],[.87,.915,.075]],.006,rear)
  pin(backGroup,m.iron,[-.71,.916,-.11],.052,.118,rear)
  pin(backGroup,m.black,[-.71,.980,-.11],.056,.012,rear)
  // The warm enamel pendant establishes one practical light behind the work.
  const lamp = frame(3.97,0,1.55)
  tube(backGroup,m.black,[[0,4.0,0],[.003,3.1,.001],[.012,2.05,-.002]],.0065,lamp)
  pin(backGroup,m.brass,[.012,2.047,0],.026,.061,lamp)
  const shadeProfile = [[.020,.072],[.046,.053],[.055,.021],[.123,-.053],[.132,-.059],[.133,-.067],[.121,-.071]]
  part(backGroup,new THREE.LatheGeometry(shadeProfile.slice().reverse().map(([x,y])=>new THREE.Vector2(x,y)),36),
       m.black,[.012,1.985,0],undefined,undefined,lamp)
  part(backGroup,new THREE.LatheGeometry([[.022,.050],[.050,.014],[.123,-.065]].map(([x,y])=>new THREE.Vector2(x,y)),36),
       m.lampInside,[.012,1.985,0],undefined,undefined,lamp)
  pin(backGroup,m.filament,[.012,1.927,0],.057,.008,lamp)
  // Keep the central horizon behind the skull clear. Far side columns and
  // conduit catch the practical in interrupted, low-contrast lengths.
  for (const z of [-5.15,3.21,5.62]) {
    box(backGroup,m.black,[5.004,2.05,z],[.055,4.10,.085])
    box(backGroup,m.iron,[4.967,2.05,z],[.026,4.10,.103])
  }
  tube(backGroup,m.iron,[[4.96,.35,-3.4],[4.94,1.12,-3.4],[4.90,1.22,-3.38],
                         [4.90,1.23,-3.23],[4.94,1.30,-3.18],[4.94,3.91,-3.18]],.015)

  for (const [group, byMaterial] of batches) {
    for (const [material,pieces] of byMaterial) {
      const geometry=mergeGeometries(pieces)
      const mesh=new THREE.Mesh(geometry,material)
      mesh.castShadow = group === benchGroup
      mesh.receiveShadow = true
      group.add(mesh)
      pieces.forEach(g=>g.dispose())
    }
  }
  prototypeGeometry.forEach(g=>g.dispose())

  renderer.shadowMap.enabled=true
  renderer.shadowMap.type=THREE.PCFShadowMap
  renderer.toneMapping=THREE.ACESFilmicToneMapping
  const sky=new THREE.HemisphereLight(0xcdd8e4,0x64513b,.35)
  scene.add(sky)
  function spot(color,intensity,at,aim,angle,penumbra,distance,shadow=false) {
    const light=new THREE.SpotLight(color,intensity,distance,angle,penumbra,2)
    light.position.set(...at);light.target.position.set(...aim);light.castShadow=shadow
    if(shadow) {
      light.shadow.mapSize.set(1024,1024)
      light.shadow.radius=5.0; light.shadow.intensity=.58
      light.shadow.camera.near=.1; light.shadow.camera.far=distance
      light.shadow.normalBias=.0012;light.shadow.bias=-.00012
    }
    scene.add(light,light.target);return light
  }
  const key = spot(0xffe5c7,76,[-2.05,3.47,.84],[0,.73,.10],.70,.73,10,true)
  const rim = spot(0xffe2bc,47,[2.8,2.95,-1.7],[0,1.12,.04],.56,.72,8)
  const fill = spot(0xafceee,22,[-.30,2.14,3.48],[0,.91,0],.77,.88,8)
  const practical=spot(0xffc48a,7.2,[3.982,1.913,1.55],[4.67,.78,1.63],1.03,.79,4.0)
  const spill=new THREE.PointLight(0xffc89b,2.6,3.2,2)
  spill.position.set(4.47,1.39,1.65);scene.add(spill)
  const studioKey=new THREE.DirectionalLight(0xfff2dd,2.0)
  studioKey.position.set(-2,3,2);scene.add(studioKey)
  let workshop=true
  const previousBeforeRender=scene.onBeforeRender
  scene.onBeforeRender=function(...args) {
    previousBeforeRender?.apply(this,args)
    if(!workshop)return
    const camera=args[2]
    if(!camera)return
    const p=camera.position
    backGroup.visible=p.x<4.87
    frontWallGroup.visible=p.x> -6.45 && p.z<7.45
    const radius=Math.hypot(p.x,p.z)
    const ux=p.x/Math.max(radius,.001), uz=p.z/Math.max(radius,.001)
    const benchDepth=.20*ux-1.78*uz
    const lateral=Math.abs(.20*uz+1.78*ux)
    const silhouetteMargin=.32 + .82*Math.abs(.399*uz-.917*ux) + .36*Math.abs(.917*uz+.399*ux)
    benchGroup.visible=!(p.y<2.1 && benchDepth>.5 && benchDepth<radius+.35 && lateral<silhouetteMargin)
  }
  function setLighting(mode='workshop') {
    workshop=mode==='workshop'
    architecture.visible=workshop
    scene.background=new THREE.Color(workshop?0x171614:0x4e4d49)
    scene.fog=new THREE.Fog(workshop?0x1e1b17:0x62605b,workshop?3.75:7,workshop?15:20)
    scene.environmentIntensity=workshop?.88:1.6
    scene.environmentRotation.set(0,workshop?-.14:-.2,0)
    renderer.toneMappingExposure=workshop?1.04:1.21
    key.color.set(workshop?0xffe5c7:0xfff5e5)
    key.intensity=workshop?76:54
    rim.intensity=workshop?47:22
    fill.intensity=workshop?22:28
    sky.intensity=workshop?.32:.92
    practical.visible=spill.visible=workshop
    studioKey.visible=!workshop
    ground.map=workshop?concrete:null;ground.normalMap=workshop?normal:null
    ground.color.set(workshop?0xc0bcb5:0x75736c);ground.needsUpdate=true
  }
  setLighting()
  return {setLighting,dispose(){
    scene.onBeforeRender=previousBeforeRender
    scene.remove(architecture,floor,contact,sky,spill,studioKey)
    for(const light of [key,rim,fill,practical])scene.remove(light,light.target)
    architecture.traverse(obj=>obj.geometry?.dispose())
    floor.geometry.dispose();contact.geometry.dispose();contactMaterial.dispose()
    ownedMaterials.forEach(m=>m.dispose());textures.forEach(t=>t.dispose())
    key.shadow.dispose();env.dispose();scene.environment=null
  }}
}
