"""Write-once removable nasal/crown cap ownership study; no geometry edits."""
from pathlib import Path
import hashlib, itertools, json, runpy, shutil
import bpy
from mathutils import Matrix

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
BASE_SHA='cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
OUT=ROOT/'assets/models/uncaged-cranial-nasal-cover-ownership-study-v1'
AUDIT=ROOT/'assets/audit/cranial-nasal-cover-ownership-study-v1'
HELPER=ROOT/'scripts/build-uncaged-alignment-v7.py'
DIAGNOSTIC=ROOT/'scripts/diagnose-native-regional-clearance.py'
KERNEL=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
RENDER_HELPER=ROOT/'scripts/study-orbital-saddle-v8.py'
CHANGED=['Overlapping nasal hood','Nasal hood fixing','Nasal hood fixing.001','Cere root transition -1','Cere root transition 1']
REGION={'head','upper-bill','jaw','builder-optics','cranial-cover'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def mat_error(a,b):return max(abs(a[r][c]-b[r][c]) for r in range(4) for c in range(4))

def scan(native,label):
    bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    objects={o.name:o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in REGION}
    # Same union scope before and after: at least one original cover member or changed nasal member.
    movers={n for n,o in objects.items() if o.parent.name=='cranial-cover'}|set(CHANGED)
    pairs=[(a,b) for a,b in itertools.combinations(sorted(objects),2) if a in movers or b in movers]
    cover=bpy.data.objects['cranial-cover'];rest=cover.matrix_local.copy()
    rest_world={n:o.matrix_world.copy() for n,o in objects.items()}
    rows={};counts=[];static_cache={}
    for step in range(41):
        f=step/40;cover.matrix_local=rest.copy();cover.location.z=rest.translation.z+.08*f;bpy.context.view_layer.update()
        dg=bpy.context.evaluated_depsgraph_get();surfaces={n:D['surface'](o,dg) for n,o in objects.items()}
        current={'fraction':f,'sameOwnerStrictPairs':0,'differentOwnerStrictPairs':0}
        for a,b in pairs:
            oa,ob=objects[a].parent.name,objects[b].parent.name
            rigid_together=oa==ob or (oa!='cranial-cover' and ob!='cranial-cover')
            key=(a,b)
            if rigid_together and key in static_cache:
                candidate,confirmed=static_cache[key]
            else:
                sa,sb=surfaces[a],surfaces[b];candidate=confirmed=0
                if sa and sb and D['bounds_overlap'](sa,sb):
                    overlaps=sa['tree'].overlap(sb['tree']);candidate=len(overlaps)
                    if candidate:
                        proof=K['proper_crossing_receipt'](sa,sb,overlaps,rest_world[a]@objects[a].matrix_world.inverted(),rest_world[b]@objects[b].matrix_world.inverted())
                        confirmed=proof['confirmedSubjectTriangleCount']+proof['confirmedTargetTriangleCount']
                if rigid_together:static_cache[key]=(candidate,confirmed)
            if not confirmed:continue
            r=rows.setdefault(key,{'meshA':a,'meshB':b,'ownerA':oa,'ownerB':ob,'sameOwner':oa==ob,'fractions':[],'maxConfirmedTriangles':0})
            r['fractions'].append(f);r['maxConfirmedTriangles']=max(r['maxConfirmedTriangles'],confirmed)
            current['sameOwnerStrictPairs' if oa==ob else 'differentOwnerStrictPairs']+=1
        counts.append(current)
    result={'native':art(native),'sampleCount':41,'meshCount':len(objects),'pairScopeCount':len(pairs),'counts':counts,'strictPairs':list(rows.values()),'staticPairCache':'Rigid same-owner or two stationary-owner pairs are tested at rest and reused; relative geometry is invariant.'}
    write(AUDIT/f'{label}-opening-screen.json',result);return result

def render(native,label):
    bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;R['configure_render'](scene)
    camera=R['camera'](scene,'Temporary ownership review camera',(-6,-3,2.4),(0,-.29,1.78),.88)
    cover=bpy.data.objects['cranial-cover'];rest=cover.location.copy();images=[]
    for f in (0,.125,1):
        cover.location=rest.copy();cover.location.z+=.08*f;bpy.context.view_layer.update()
        p=AUDIT/f'{label}-opening-{round(f*1000):04d}.png';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True);images.append({'fraction':f,**art(p)})
    return images

def main():
    assert sha(BASE)==BASE_SHA
    assert sha(HELPER)=='39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
    assert not OUT.exists() and not AUDIT.exists(),'Existing version must be preserved'
    bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    before=H['scene_snapshot']();materials={m.name:H['material_signature'](m) for m in bpy.data.materials}
    worlds={o.name:o.matrix_world.copy() for o in bpy.data.objects}
    for name in CHANGED:
        obj=bpy.data.objects[name];assert obj.parent.name=='upper-bill',name
        obj.parent=bpy.data.objects['cranial-cover'];obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_world=worlds[name]
    bpy.context.view_layer.update();after=H['scene_snapshot']()
    assert before['empties']==after['empties'] and before['curves']==after['curves']
    assert set(before['meshes'])==set(after['meshes'])
    for name,b in before['meshes'].items():
        a=after['meshes'][name]
        assert a['mesh']==b['mesh'],name
        if name not in CHANGED:assert a==b,name
    maximum=max(mat_error(o.matrix_world,worlds[o.name]) for o in bpy.data.objects);assert maximum<2e-7
    assert materials=={m.name:H['material_signature'](m) for m in bpy.data.materials}
    OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);native=OUT/'murderbird-cranial-nasal-cover-ownership-study-v1.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert H['scene_snapshot']()==after
    shutil.copy2(__file__,AUDIT/'executed-generator.py')
    receipt={'status':'unreviewed removable nasal/crown cap reconstruction; no app selection','source':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'helpers':[art(p) for p in (HELPER,DIAGNOSTIC,KERNEL,RENDER_HELPER)],'changedOwnership':[{'name':n,'from':'upper-bill','to':'cranial-cover'} for n in CHANGED],'preservation':{'all699MeshGeometriesExact':True,'other694MeshRecordsExact':True,'all51PivotsAnd462GuidesExact':True,'materialsExact':True,'maximumClosedWorldMatrixDelta':maximum,'saveReloadExact':True},'construction':'The nasal roof, paired root transitions and their two roof fixings join the removable brow/crown cap. Fixed upper bill blades, optic mounts, lenses and mandible stay on their existing owners. This proposed maintenance split is not recovered canon.','limits':['Changing ownership does not make existing solid intersections into mechanically proven joints. Same-owner penetrations remain recorded and require a credible fixed assembly.','Guide/support and fastening details are not built.','The 41 native prescribed states do not establish runtime, full containment or continuous swept clearance.','No geometry, finish, export, application, story or publication changes.']}
    write(AUDIT/'receipt.json',receipt)
    a=scan(BASE,'before');b=scan(native,'after')
    amap={(x['meshA'],x['meshB']):x for x in a['strictPairs']};bmap={(x['meshA'],x['meshB']):x for x in b['strictPairs']}
    receipt['comparison']={'sameUnionPairScope':a['pairScopeCount']==b['pairScopeCount'],'newIdentities':[bmap[k] for k in sorted(set(bmap)-set(amap))],'resolvedIdentities':[amap[k] for k in sorted(set(amap)-set(bmap))],'inheritedCount':len(set(amap)&set(bmap)),'ownershipCategoryChanges':[{'pair':list(k),'beforeSameOwner':amap[k]['sameOwner'],'afterSameOwner':bmap[k]['sameOwner']} for k in sorted(set(amap)&set(bmap)) if amap[k]['sameOwner']!=bmap[k]['sameOwner']],'maximumDifferentOwnerStrictPairsBefore':max(x['differentOwnerStrictPairs'] for x in a['counts']),'maximumDifferentOwnerStrictPairsAfter':max(x['differentOwnerStrictPairs'] for x in b['counts'])}
    receipt['screens']=[art(AUDIT/f'{n}-opening-screen.json') for n in ('before','after')]
    write(AUDIT/'receipt.json',receipt)
    receipt['renders']=render(BASE,'before')+render(native,'after');write(AUDIT/'receipt.json',receipt)
    assert sha(BASE)==BASE_SHA;print(json.dumps({'native':art(native),'newStrictPairs':len(receipt['comparison']['newIdentities']),'resolvedStrictPairs':len(receipt['comparison']['resolvedIdentities']),'maxDifferentOwnerBefore':receipt['comparison']['maximumDifferentOwnerStrictPairsBefore'],'maxDifferentOwnerAfter':receipt['comparison']['maximumDifferentOwnerStrictPairsAfter']}))

H=runpy.run_path(str(HELPER),run_name='ownership_snapshot_helpers')
D=runpy.run_path(str(DIAGNOSTIC),run_name='ownership_surface_helpers')
K=runpy.run_path(str(KERNEL),run_name='ownership_strict_kernel')
R=runpy.run_path(str(RENDER_HELPER),run_name='ownership_render_helpers')
if __name__=='__main__':main()
