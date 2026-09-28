"""Preserve the verified bill derivative as a versioned whole-bird review candidate."""
from pathlib import Path
import argparse, copy, hashlib, html, json, os, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'assets/models/uncaged-alignment-v9'
AUDIT=ROOT/'assets/audit/alignment-v9'
NATIVE=ROOT/'assets/models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.blend'
GLB=ROOT/'assets/models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.glb'
EXPECTED=('4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe','f5c0f5ad99ace316ed84426d2a1148a093706612c9602d78b93023d46d989e6e')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def init():
    assert not MODEL.exists(),'Preserve previous version'
    assert (sha(NATIVE),sha(GLB))==EXPECTED
    comparison=json.loads((AUDIT/'v8-native-comparison.json').read_text())
    assert comparison['unchangedMeshCount']==690 and comparison['pivotsExact']==51 and comparison['guidesExact']==462
    old_path=ROOT/'assets/models/uncaged-alignment-v8/alignment-inventory.json';old=json.loads(old_path.read_text())
    MODEL.mkdir(parents=True)
    newnative=MODEL/'murderbird-alignment-v9.blend';newglb=MODEL/'murderbird-alignment-v9.glb'
    shutil.copy2(NATIVE,newnative);shutil.copy2(GLB,newglb)
    assert (sha(newnative),sha(newglb))==EXPECTED
    inherited=['parts','pivots','controlCurves','sourceReferences','conventions','jointContract','billContact','billContactSpace','controls']
    inv={k:copy.deepcopy(old[k]) for k in inherited}
    changed={x['name'] for x in comparison['changedMeshes']}
    for part in inv['parts']:
        if part['name'] in changed:part['geometryStatus']='V9 formed bill/shorter mandible or reseated root-fixing reconstruction; owner acceptance pending'
    inv.update({'status':'local neutral structural candidate; likeness revision required; no publication',
      'startingRevision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'scope':'V8 with five bill/mandible mesh changes and four bill-root fixing transforms. Other690meshes,51pivots,462guides and materials retain the V8 state. Unfinished orbital/neck/limb studies are excluded.',
      'base':art(ROOT/'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend'),
      'verifiedDerivativeSources':[art(NATIVE),art(GLB)],
      'generatedFiles':[art(newnative),art(newglb)],
      'nativeComparison':art(AUDIT/'v8-native-comparison.json'),
      'independentExportEvidence':art(ROOT/'assets/audit/uncaged-bill-root-fixing-study-v1/independent-native-export-v1/geometry-parity.json'),
      'reviewedBillEvidence':art(ROOT/'assets/audit/uncaged-bill-root-fixing-study-v1/supervisor-runtime-review-v2.json'),
      'previousCandidate':{'inventory':art(old_path),'runtime':next(x for x in old['generatedFiles'] if x['path'].endswith('.glb'))},
      'limits':['Byte-identical adoption of independently checked source/export; no new export operation.',
        'Regional technical checks do not establish whole-bird artistic acceptance.',
        'Rear bill-root fixings remain concealed behind the fixed optic mounting wall; no claim that all four heads are externally visible.',
        'Three-era materials and repairs remain provisional; source art and historical assets are preserved.']})
    write(MODEL/'alignment-inventory.json',inv);shutil.copy2(__file__,AUDIT/'executed-review-builder.py')
    print('V9 copied byte-identically; native/export:',*EXPECTED)

def finish():
    ip=MODEL/'alignment-inventory.json';inv=json.loads(ip.read_text());rp=AUDIT/'neutral-views/authoring-views.json';renders=json.loads(rp.read_text())
    assert not (AUDIT/'index.html').exists()
    old=json.loads((ROOT/'assets/audit/alignment-v8/neutral-views/authoring-views.json').read_text())
    assert renders['native']['sha256']==EXPECTED[0] and renders['runtimeDerivative']['sha256']==EXPECTED[1]
    current={(x['era'],x['view']):x for x in renders['views']};before={(x['era'],x['view']):x for x in old['views']}
    for row in renders['views']+old['views']:assert sha(ROOT/row['path'])==row['sha256']
    previews=[]
    for era in ('maker','mechanic','builder'):
        src=ROOT/current[(era,'left-three-quarter')]['path'];dst=MODEL/f'{era}-preview.png';assert not dst.exists();shutil.copy2(src,dst)
        previews.append({**art(dst),'from':str(src.relative_to(ROOT)),'status':'fixed native neutral render; excludes procedural runtime mechanisms'})
    inv['fallbackPreviews']=previews;inv['generatedFiles'] += [{k:r[k] for k in ('path','sha256','bytes')} for r in previews]
    inv['authoringViewReceipt']=art(rp);inv['reviewBuilder']=art(AUDIT/'executed-review-builder.py');write(ip,inv)
    refs={x['id']:x for x in inv['sourceReferences']['sources']};verified={}
    def url(p):return html.escape(os.path.relpath(ROOT/p,AUDIT),quote=True)
    def fig(row,label):
        p=ROOT/row['path'];assert sha(p)==row['sha256'];verified[row['path']]=art(p)
        u=url(row['path']);return f'<figure><a href="{u}"><img loading="lazy" src="{u}" alt="{html.escape(label)}"></a><figcaption>{html.escape(label)}</figcaption></figure>'
    sections=['<section><h2>Three inherited construction states</h2><p>The formed bill and shorter lower mandible are now in the whole bird. These neutral renders omit the browser’s procedural era mechanisms. Materials, neck, shoulders and limb likeness still need work.</p><div class="grid">'+''.join(fig(current[(e,'three-quarter')],label) for e,label in [('maker','I · Maker'),('mechanic','II · Mechanic'),('builder','III · Advanced')])+'</div></section>']
    sections+=['<section><h2>Controlling references</h2><p>Candidate03 controls the common body direction; Maker-clean and Mechanic guide their era state. Perspective illustrations do not supply exact dimensions.</p><div class="grid">'+''.join(fig(refs[k],label) for k,label in [('candidate-03','Common body direction'),('maker-clean','Newly fabricated Maker'),('mechanic','Inherited Mechanic body')])+'</div></section>']
    july=refs['july-head'];assert sha(ROOT/july['path'])==july['sha256'];verified[july['path']]=art(ROOT/july['path'])
    sections+=['<section><h2>Head-only authority</h2><p>The July selection controls the head. Its excluded body, perch and long hanging plates are not adopted.</p><div class="pair"><figure><svg viewBox="510 20 500 490" role="img" aria-label="July head-only crop"><image href="'+url(july['path'])+'" width="1024" height="1536"/></svg><figcaption>July · head-only scope</figcaption></figure>'+fig(current[('builder','head')],'V9 · head, neutral')+'</div></section>']
    matched=[]
    for era,label in [('maker','Maker'),('mechanic','Mechanic'),('builder','Advanced')]:
        for view in ('three-quarter','front','side-right','side-left','rear','head'):
            a,b=before[(era,view)],current[(era,view)]
            for k in ('camera','target','projection','orthoScale','resolution'):assert a[k]==b[k]
            matched.append([era,view]);sections.append(f'<section><h2>{label} · {view.replace("-"," ")}</h2><div class="pair">'+fig(a,'V8 · before')+fig(b,'V9 · formed bill and mandible')+'</div></section>')
    for era,label in [('maker','Maker'),('mechanic','Mechanic'),('builder','Advanced')]:
        sections.append(f'<section><h2>{label} · remaining regional views</h2><div class="grid">'+''.join(fig(r,r['view'].replace('-',' ')) for r in renders['views'] if r['era']==era and r['view'] not in ('three-quarter','front','side-right','side-left','rear','head'))+'</div></section>')
    sections.append('<section><h2>Review limits</h2><p>Likeness remains revision required. The neck contour, shoulder transition, sparse limbs and regional plate hierarchy are open findings. No new owner acceptance, physical simulation or deployment is claimed.</p><p><a href="../uncaged-bill-root-fixing-study-v1/index.html">Interactive bill comparison and jaw controls</a> · <a href="../alignment-v8/index.html">Preserved V8 motion and inspection evidence</a> · <a href="../../../docs/alignment-v9-review.md">V9 checks and remaining decisions</a></p></section>')
    css='body{margin:0;background:#151719;color:#e8e8e5;font:16px/1.5 system-ui,sans-serif}main{max-width:1240px;margin:auto;padding:28px}a{color:#d8b978}p{max-width:80ch}.grid,.pair{display:grid;gap:16px}.grid{grid-template-columns:repeat(3,minmax(0,1fr))}.pair{grid-template-columns:repeat(2,minmax(0,1fr))}figure{margin:0;background:#202427;min-width:0}img,svg{display:block;width:100%}figcaption{padding:12px}section{border-top:1px solid #444;margin-top:30px;padding-top:6px}code{overflow-wrap:anywhere}@media(max-width:650px){main{padding:16px}.grid,.pair{grid-template-columns:minmax(0,1fr)}}'
    header='<header><p>Local work in progress · artistic acceptance pending</p><h1>MurderBird · Alignment V9</h1><p>A bounded whole-bird update carrying the verified formed bill, shorter mandible and seated root fixings. The separate crown, neck and leg experiments are not included.</p><p>Runtime <code>'+EXPECTED[1]+'</code></p><p><a href="../../../">Local exhibit</a> · <a href="'+url(str((MODEL/'murderbird-alignment-v9.blend').relative_to(ROOT)))+'">Editable source</a> · <a href="'+url(str((MODEL/'murderbird-alignment-v9.glb').relative_to(ROOT)))+'">Runtime model</a></p></header>'
    page=AUDIT/'index.html';page.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MurderBird V9 local review</title><style>'+css+'</style></head><body><main>'+header+''.join(sections)+'</main></body></html>\n')
    write(AUDIT/'gallery-manifest.json',{'status':'local native comparison; actual browser review separate','html':art(page),'inventory':art(ip),'nativeSha256':EXPECTED[0],'runtimeSha256':EXPECTED[1],'matchedComparisons':matched,'newRenderCount':len(renders['views']),'verifiedFiles':list(verified.values())})
    print('Finished V9 gallery:',len(renders['views']),'new views,',len(matched),'matched comparisons')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['init','finish']);args=ap.parse_args();init() if args.stage=='init' else finish()
