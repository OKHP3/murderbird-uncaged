"""V37 unplated folded-shoulder envelope and deliberately tucked elbow study.

This is an early shape gate, not finished armor or fitted receiving construction.
Root journals and left travel stop remain; moved child joints are declared.
"""
from pathlib import Path
import math,runpy
import bpy
from mathutils import Vector
ROOT=Path(globals().get('SOURCE_ROOT','/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged'))

def surface(side,v,a):
    v=max(.0001,min(.9999,v))
    inside=.208+.020*v
    outside=.212+.191*math.sin(math.pi*v)**.72
    cy=-.036+.294*v
    ry=.011+.166*math.sin(math.pi*v)**.65
    z=1.321-.508*v+.018*math.sin(a)*math.sin(math.pi*v)
    return Vector((side*(inside+(outside-inside)*math.cos(a)),cy+ry*math.sin(a),z))

def normal(side,v,a):
    e=.00001
    n=(surface(side,v,a+e)-surface(side,v,a-e)).cross(surface(side,v+e,a)-surface(side,v-e,a)).normalized()
    if n.dot(Vector((side*math.cos(a),math.sin(a),0)))<0:n.negate()
    return n

def apply():
    h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v37-shoulder-assembly.py'))
    snap=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'))
    before=snap['scene_snapshot']()
    mat=bpy.data.objects['V28 left canopy oblique course 1 plate 4'].data.materials[0]
    frame=bpy.data.materials['Neutral / frame']
    removed=[];added=[];deltas={}
    for side,label in ((1,'left'),(-1,'right')):
        owner=label+'-mantle';child=label+'-wing-shield'
        # A shorter inward elbow gives a folded guard instead of a hanging pod.
        # The upper journal remains where the external Maker wing control acts.
        joint=bpy.data.objects[child];old=joint.matrix_world.translation.copy()
        delta=Vector((-side*.080,.070,.034));m=joint.matrix_world.copy();m.translation+=delta;joint.matrix_world=m
        bpy.context.view_layer.update();deltas[child]={'oldWorld':list(old),'newWorld':list(joint.matrix_world.translation),'delta':list(delta)}
        # Retain the upper-member journal end; reshape its complete finite distal
        # section to receive the translated child bearing, never scale the bearing.
        member=bpy.data.objects[label+' swept upper wing load member'];inv=member.matrix_world.inverted();start=bpy.data.objects[owner].matrix_world.translation
        for vert in member.data.vertices:
            p=member.matrix_world@vert.co
            t=max(0,min(1,(start.z-p.z)/(start.z-old.z)));w=t*t*(3-2*t)
            vert.co=inv@(p+delta*w)
        member.data.update()
        for o in list(bpy.data.objects):
            if o.type!='MESH' or not o.parent or o.parent.name not in (owner,child):continue
            name=o.name
            shell=(name.startswith('V28 '+label+' ') or name.startswith('V34 '+label+' shoulder crown return') or name.startswith(label+' profiled mantle backing'))
            if shell:
                removed.append(name);bpy.data.objects.remove(o,do_unlink=True)
        # Two rigid surfaces retain shoulder/elbow ownership. The shallow oblique
        # lap is provisional until the selected profile is fitted across movement.
        for name,parent,v0,v1,layer in [(f'V37 {label} shoulder silhouette shell',owner,.008,.782,0),
                                       (f'V37 {label} tucked elbow silhouette shell',child,.762,.946,.006)]:
            def fn(t,u,v0=v0,v1=v1,layer=layer):
                a=-1.52+3.04*u
                v=v0+(v1-v0)*t+.040*math.sin(a)*math.sin(math.pi*t/2)
                n=normal(side,v,a)
                return surface(side,v,a)+layer*n,n
            o=h['sheet'](name,parent,fn,mat,'envelope-study',rows=40,cols=34,wall=.006)
            o['geometryStatus']='Unplated profile study; shell lap and frame seats not yet clearance validated'
            added.append(o.name)
        # Supports are attached to real assembly owners and lead from the journal
        # structure to the shell. Exact load qualification is not claimed.
        root=bpy.data.objects[owner].matrix_world.translation.copy()
        for k,a in enumerate((-.85,.85)):
            seat=surface(side,.40,a)-normal(side,.40,a)*.006
            p0=root+Vector((side*.031,.022*(-1 if k==0 else 1),.018))
            o=h['rail'](f'V37 {label} profile canopy bow {k+1}',owner,[p0,p0.lerp(seat,.45),seat],frame,side)
            o['geometryStatus']='Proposed fixed receiving member; not qualified weld or motion clearance';added.append(o.name)
        elbow=bpy.data.objects[child].matrix_world.translation.copy()
        for k,a in enumerate((-.55,.55)):
            seat=surface(side,.86,a)
            o=h['rail'](f'V37 {label} profile elbow seat {k+1}',child,[elbow+Vector((side*.018,0,0)),seat],frame,side);added.append(o.name)
    after=snap['scene_snapshot']();changed=[n for n in before['meshes'] if n in after['meshes'] and before['meshes'][n]!=after['meshes'][n]]
    nodechanges=[n for n in before['empties'] if before['empties'][n]!=after['empties'][n]]
    assert set(nodechanges)=={'left-wing-shield','right-wing-shield','anchor-guard'},nodechanges
    allowed={'left-mantle','right-mantle','left-wing-shield','right-wing-shield'}
    assert all(before['meshes'][n]['parent'] in allowed for n in changed+removed)
    curve_changes=[n for n in before['curves'] if before['curves'][n]!=after['curves'][n]]
    assert all(before['curves'][n]['parent'] in allowed for n in curve_changes)
    return {'changedCurves':curve_changes,'curveDisposition':'Legacy non-exported curves follow their relocated rigid owners; native curve geometry/properties preserved.','region':'unplated tucked shoulder profile','status':'Early visual gate; not clearance or finished construction','changedMeshes':changed,'addedMeshes':added,'removedMeshes':removed,'changedNodes':nodechanges,'changedFootMeshes':[],'elbowRelocation':deltas,'jointInvariant':'Root shoulder journals/left travel stop exact; child bearing local geometry exact; upper load member distal section reshaped toward actual relocated elbow.','limits':['Rigid shell boundaries and supports are provisional and untested for movement.','Material finish and individual plate segmentation intentionally await profile judgment.','Envelope is a qualitative reconstruction, not measured source dimensions.']}
