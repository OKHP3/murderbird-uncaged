"""Bounded contour refinement on accepted detailed 1C; materials stay intact."""
import bpy
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    changed=[];cages=[];plates=[]
    def bounds(o):
        e=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
        pts=[e.matrix_world@Vector(p) for p in e.bound_box]
        return [[min(p[k] for p in pts) for k in range(3)],
                [max(p[k] for p in pts) for k in range(3)]]
    for o in list(scene.objects):
        if o.type!='MESH' or not o.get('cg1cRegion') in ('head','neck') or o.hide_render:continue
        name=o.name.lower();cage=any(s in name for s in ('continuous skull dark cavity','deep segmented hooked bill'))
        plate=any(s in name for s in ('swept crown scale','swept nape scale','temple overlap','cervical overlap','scaffold curved brow plate'))
        if not(cage or plate):continue
        bpy.context.view_layer.update();before=bounds(o)
        if cage:
            # Dense 1C section rings already constrain the hook; one level
            # rounds cross-section/ring faceting without changing its anchors.
            m=o.modifiers.new('Milestone2 bounded cage contour','SUBSURF')
            m.subdivision_type='CATMULL_CLARK';m.levels=1;m.render_levels=1
            cages.append(o.name)
        else:
            # SIMPLE adds face resolution without rounding mechanical rims.
            # Smooth shading retains individual seams and plate silhouettes.
            m=o.modifiers.new('Milestone2 plate face resolution','SUBSURF')
            m.subdivision_type='SIMPLE';m.levels=1;m.render_levels=1
            # Put subdivision before the retained finite plate return.
            idx=list(o.modifiers).index(m)
            if idx:o.modifiers.move(idx,0)
            plates.append(o.name)
        for p in o.data.polygons:p.use_smooth=True
        o['cg2Region']=o.get('cg1cRegion');o['cg2ContourRefined']=True
        bpy.context.view_layer.update();after=bounds(o);delta=max(abs(after[j][k]-before[j][k]) for j in range(2) for k in range(3))
        changed.append({'name':o.name,'maximumBoundsDelta':round(delta,6)})
    return {'module':'cinematic-cg-2-head','era':era,'smoothedCages':cages,
            'plateFaceRefinements':len(plates),'changes':changed,
            'anchorDelta':[0,0,0],'headSizeTransform':1,
            'deviations':'One subdivision level locally softens cage ring corners; no object transforms, source replacement or optic/material edits.',
            'limits':['Mechanical plate silhouettes deliberately retained','Eye/cheek polish deferred to Milestone3','Final artistic likeness remains owner judgment']}
