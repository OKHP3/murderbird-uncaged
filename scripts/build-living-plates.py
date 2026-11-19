#!/usr/bin/env python3
"""Build the Living Plates layers for public/plates/ from the pinned reference images.

Each plate is one reference image lifted into two layers:
  <name>-front.webp   the reference pixels; alpha is 0 only on the far side of occlusion edges
  <name>-back.webp    the same image with foreground rims replaced by mirrored background texture
  <name>-depth.png    16-bit disparity packed in R (high) and G (low); left half front, right half back

Depth comes from Depth Anything V2 Small (Apache-2.0, ONNX build `onnx-community/depth-anything-v2-small`).
No model geometry is used and no reference image is altered: at rest the page shows the reference art.

This is an offline authoring tool. It is not part of `npm run build`, CI or the publication verifiers.
Requires: python3, numpy, pillow, opencv-python-headless, scipy, onnxruntime, huggingface_hub.
Run from the repository root with the reference images hydrated from Git LFS:

    python3 scripts/build-living-plates.py

The committed outputs were produced on 2026-11-14; see records/living-plates-2026-11-14.json.
"""
import json, numpy as np, cv2
from PIL import Image

L="assets/img/library/"
OUT="public/plates/img/"
SC={"canon":L+"murderbird-unified-master-candidate-03-2026-09-06.png",
    "maker":L+"murderbird-unified-maker-clean-candidate-2026-09-06.png",
    "mechanic":L+"murderbird-unified-mechanic-candidate-2026-09-06.png",
    "builder":L+"murderbird-unified-heart-candidate-2026-09-06.png"}
GW=512; MAXW=1600; RFRAC=0.09; TE=0.06; SLACK=0.05   # grid width, colour width cap, hidden-band radius, edge jump, flood slack
DEPTH_LONG=1036                                      # long side fed to the depth model (multiple of 14)

def depth_session():
    import onnxruntime as ort
    from huggingface_hub import hf_hub_download
    p=hf_hub_download("onnx-community/depth-anything-v2-small","onnx/model.onnx")
    so=ort.SessionOptions(); so.enable_cpu_mem_arena=False
    return ort.InferenceSession(p,so,providers=["CPUExecutionProvider"])

def disparity(path, s):
    im=Image.open(path).convert("RGB"); W,H=im.size
    sc=DEPTH_LONG/max(W,H); w=max(14,round(W*sc/14)*14); h=max(14,round(H*sc/14)*14)
    x=np.asarray(im.resize((w,h),Image.BICUBIC),dtype=np.float32)/255.
    x=((x-[0.485,0.456,0.406])/[0.229,0.224,0.225]).transpose(2,0,1)[None].astype(np.float32)
    return np.squeeze(s.run(None,{s.get_inputs()[0].name:x})[0]).astype(np.float32)

session=depth_session()
def ell(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
meta={}
for name,src in SC.items():
    im=Image.open(src).convert("RGB"); W0,H0=im.size
    Wc=min(W0,MAXW); Hc=round(H0*Wc/W0); im=im.resize((Wc,Hc),Image.LANCZOS) if Wc!=W0 else im
    img=np.asarray(im).astype(np.float32)
    d=disparity(src, session); d=(d-d.min())/(d.max()-d.min())
    D=cv2.resize(d,(Wc,Hc),interpolation=cv2.INTER_CUBIC).clip(0,1)
    cell=Wc/GW; GH=round(GW*Hc/Wc)
    # ---- occlusion edges: true disparity jumps inside a 5px window, widened to a zone
    E=(cv2.dilate(D,ell(2))-cv2.erode(D,ell(2)))>TE
    r2=int(round(2.5*cell)); rb=int(round(5*cell)); dil=cv2.dilate(D,ell(rb)); ero=cv2.erode(D,ell(rb))
    Z=cv2.dilate(E.astype(np.uint8),ell(r2))>0; mid=(dil+ero)/2
    farside=Z&(D<mid)
    alpha=np.ones_like(D); alpha[farside]=0.0
    alpha=cv2.GaussianBlur(alpha,(0,0),0.7)
    # ---- background layer: under each foreground rim, continue the far side inward
    R=int(round(RFRAC*Wc)); k3=np.ones((3,3),np.uint8)
    near=Z&(~farside)
    carried=np.where(near,D,-1.0).astype(np.float32); M=near.copy()
    for it in range(R):
        c=cv2.dilate(carried,k3)
        cand=(~M)&(c>=0)&(D>=c-SLACK)&(~farside)
        if not cand.any(): break
        carried[cand]=c[cand]; M|=cand
    Dfar=np.where(farside,ero,D)                      # far-side rim snapped to the background plateau
    # nearest far-side rim pixel for every band pixel; texture is mirrored across that rim point
    from scipy import ndimage as ndi
    rimdirty=farside&(cv2.dilate(near.astype(np.uint8),ell(5))>0)      # far-side pixels still tinted by the foreground edge
    seeds=farside&(~rimdirty)
    dist,(sy,sx)=ndi.distance_transform_edt(~seeds,return_indices=True)
    yy,xx=np.mgrid[0:Hc,0:Wc]
    ry=2*sy-yy; rx=2*sx-xx
    bgok=(~M)&(~near)&(~rimdirty)
    inb=(ry>=0)&(ry<Hc)&(rx>=0)&(rx<Wc)
    ryc=ry.clip(0,Hc-1); rxc=rx.clip(0,Wc-1)
    okref=inb&bgok[ryc,rxc]
    fy=np.where(okref,ryc,sy); fx=np.where(okref,rxc,sx)
    filled=(M|rimdirty)&(dist<=R+8)
    C=img.copy(); C[filled]=img[fy[filled],fx[filled]]
    Cs=cv2.GaussianBlur(C,(0,0),2.2)
    back=img.copy(); back[filled]=Cs[filled]
    Lraw=Dfar.copy(); Lraw[filled]=Dfar[sy[filled],sx[filled]]
    wk=(filled|seeds).astype(np.float32); sig=max(3.0,R/6)
    Ls=cv2.GaussianBlur(Lraw*wk,(0,0),sig)/(cv2.GaussianBlur(wk,(0,0),sig)+1e-6)
    Dbg=Dfar.copy(); Dbg[filled]=np.minimum(Ls,D)[filled]
    left=int((M&~filled).sum())
    # ---- grid-res depth: front (foreground rim lifted over the far side), back
    Dg=cv2.resize(D,(GW,GH),interpolation=cv2.INTER_AREA)
    far_g=cv2.resize(farside.astype(np.float32),(GW,GH),interpolation=cv2.INTER_AREA)>0.5
    near_g=(cv2.resize(near.astype(np.float32),(GW,GH),interpolation=cv2.INTER_AREA)>0.5)&(~far_g)
    Df=Dg.copy(); plateau=cv2.dilate(Dg,ell(2)); Df[near_g]=plateau[near_g]     # near rim snapped to the foreground plateau
    lift=cv2.dilate(Df,np.ones((3,3),np.uint8)); Df[far_g]=lift[far_g]           # one invisible cell carries the rim outward
    Dbg_g=cv2.resize(Dbg,(GW,GH),interpolation=cv2.INTER_AREA)
    def pack(a):
        v=(a.clip(0,1)*65535).round().astype(np.uint16); o=np.zeros(a.shape+(3,),np.uint8); o[...,0]=v>>8; o[...,1]=v&255; return o
    dp=np.concatenate([pack(Df),pack(Dbg_g)],1)
    out=OUT
    Image.fromarray(dp).save(out+f"{name}-depth.png",optimize=True)
    rgba=np.dstack([img,alpha*255]).clip(0,255).astype(np.uint8)
    Image.fromarray(rgba,"RGBA").save(out+f"{name}-front.webp",quality=88,method=6,exact=True)
    Image.fromarray(back.clip(0,255).astype(np.uint8)).save(out+f"{name}-back.webp",quality=82,method=6)
    meta[name]={"w":Wc,"h":Hc,"gw":GW,"gh":GH}
    print(name,(Wc,Hc),"grid",(GW,GH),"cell %.2f R %d band %.1f%% unfilled %d zone %.1f%% edge %.1f%%"%(cell,R,100*M.mean(),left,100*Z.mean(),100*E.mean()))
print(json.dumps(meta))
