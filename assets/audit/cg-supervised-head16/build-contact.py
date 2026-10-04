"""Display-only contact assembly; no new 3D renders or edited source binaries."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import hashlib, json, datetime

OUT=Path(__file__).resolve().parent
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
whole='assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'
july='context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png'
advanced='assets/img/library/murderbird-unified-heart-candidate-2026-09-06.png'
before=BASE/'assets/audit/cg-supervised-head15/attempt02'
rows=[
    [('Locked Sept22 full-character canon',BASE/whole,None),
     ('Frozen head15 actual before',before/'after-pbr-source-full-bird.png',None),
     ('Trial16 actual: slot0 only',OUT/'trial16-pbr-source-full-bird.png',None)],
    [('July source: head-only display crop',BASE/july,(475,30,1024,490)),
     ('Frozen head15 actual grazing',before/'after-pbr-head-grazing.png',None),
     ('Trial16 actual matched grazing',OUT/'trial16-pbr-head-grazing.png',None)]
]
records=[]
for row, name, height in zip(rows,['source-before15-trial16-whole-contact.jpg','source-before15-trial16-head-contact.jpg'],[427,640]):
    board=Image.new('RGB',(1920,height+40),(20,20,20));d=ImageDraw.Draw(board)
    for i,(label,path,crop) in enumerate(row):
        im=Image.open(path).convert('RGB')
        if crop:im=im.crop(crop)
        im=ImageOps.contain(im,(640,height),Image.Resampling.LANCZOS)
        board.paste(im,(i*640+(640-im.width)//2,40+(height-im.height)//2));d.text((i*640+10,12),label,fill='white')
        records.append({'contact':name,'label':label,'input_path':str(path),'input_sha256':sha(path),'display_crop_pixels':crop,'transform':'aspect-preserving resize, letterbox and labels only'})
    board.save(OUT/name,quality=94)
provenance={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status':'FAILED_TRIAL_RETAINED_NOT_PROMOTED','inputs':records,
    'pinned_sources_inspected':[{'path':str(BASE/p),'sha256':sha(BASE/p),'scope':scope} for p,scope in [(whole,'full-character canon'),(july,'head identity only; body excluded'),(advanced,'Advanced finish')]],
    'rights':'Creative material all rights reserved under NOTICE.md; no publication or owner artistic acceptance.',
    'source_camera_status':'Estimated comparison; source camera and source material physics unknown.',
    'before_candidate_match':'Frozen head15 exact camera matrices, scales, shifts, resolutions, Cycles8 denoising and native light/world/exposure retained.',
    'not_a_reference_substitution':True,'additional_3d_renders':0,
    'source_owner_acceptance':False,'integration':'No gain supported; do not promote. Root alone adjudicates after separate head15 retention/full09 QC.'}
(OUT/'comparison-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
(OUT/'triage15-input.json').write_bytes(Path('/tmp/cg-source-appearance-triage15.json').read_bytes())
print('HEAD16_CONTACTS_COMPLETE')
