"""V23 coordinated rest envelope and four short rigid cervical links.

The envelope is an authored reconstruction from the owner whole-bird image.
Coordinates describe the editable proposal, not dimensions recovered from art.
All exterior plates belong to one rigid part. Motion clearance is not implied.
"""
from pathlib import Path
import bpy, bmesh, math, json, runpy
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ((.78,-.165,.125,.170),(.87,-.247,.139,.210),
 (.99,-.365,.128,.252),(1.12,-.425,.095,.280),
 (1.245,-.417,.038,.258),(1.335,-.382,-.035,.205),
 (1.410,-.352,-.106,.145),(1.48,-.379,-.160,.116),
 (1.555,-.428,-.213,.109),(1.635,-.446,-.256,.100))
JOINTS = (('neck',(0,-.188,1.335)),
 ('cervical-mid-a',(0,-.229,1.410)),
 ('cervical-mid-b',(0,-.270,1.480)),
 ('cervical-upper',(0,-.321,1.550)))
ERAS='maker,mechanic,builder'

def apply():
    lib=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v21-envelope.py'))
    for fn in ('sample','envelope_point','guard','tube','bearing'):
        lib[fn].__globals__['PROFILE']=PROFILE
    guard,tube,bearing,point=(lib[n] for n in ('guard','tube','bearing','envelope_point'))
    skin=bpy.data.objects['V21 lower swept throat keel'].data.materials[0]
    frame=bpy.data.objects['V21 cervical root load bow -1'].data.materials[0]
    metal=bpy.data.objects['V21 intermediate passive journal -1'].data.materials[0]
    original={o.name:o.matrix_world.copy() for o in bpy.data.objects}
    staged=[];added=[]
    # A new torso/neck is constructed together. Preserve legacy head, feet,
    # shoulders and era machinery for a comparison with a known input.
    for o in list(bpy.data.objects):
        if o.type!='MESH' or not o.parent: continue
        par=o.parent.name
        if par in ('neck','cervical-upper','cervical-joint-cover','breastplate') or (par=='body' and o.get('region')=='breast'):
            staged.append({'name':o.name,'parent':par,'role':o.get('surfaceRole')})
            bpy.data.objects.remove(o,do_unlink=True)
    cover=bpy.data.objects.get('cervical-joint-cover')
    if cover:
        assert len(cover.children)==0
        bpy.data.objects.remove(cover,do_unlink=True)
    parent=bpy.data.objects['body']
    for name,pos in JOINTS:
        o=bpy.data.objects.get(name)
        if o is None:
            o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o)
        o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4)
        o.matrix_world=Matrix.Translation(pos);bpy.context.view_layer.update()
        o['cervicalPitchWeight']=.25;o['constructionClass']='proposed-passive'
        o['articulationRole']='Rigid serial neck hinge; independent yaw at root'
        parent=o
    head=bpy.data.objects['head'];head.parent=parent
    head.matrix_parent_inverse=Matrix.Identity(4);head.matrix_world=original['head']
    # Preserve exact world rests for all retained descendants after reparenting.
    def depth(o):
        n=0
        while o.parent:n+=1;o=o.parent
        return n
    for o in sorted(bpy.data.objects,key=depth):
        if o.name in original and o.name not in dict(JOINTS):o.matrix_world=original[o.name]
    bpy.context.view_layer.update()
    def add(o,region=None):
        o['geometryStatus']='V23 coordinated construction proposal; clearance requires review'
        o['proposal']=True;o['constructionClass']='inherited-passive'
        if region:o['region']=region
        added.append(o.name);return o
    # Tapered access door. Large central plates give way to narrow curved side
    # courses, with a shaped lower edge exposing the load-bearing pelvis.
    add(guard('V23 recessed breast door',1.354,.840,0,1.17,'breastplate',skin,off=-.006,wall=.004,tip_depth=.012,edge_slope=0),'breast')
    courses=((1.361,1.292,5),(1.304,1.233,6),(1.247,1.175,6),
             (1.188,1.111,7),(1.128,1.053,7),(1.067,.990,6),
             (1.004,.926,5),(.941,.865,4))
    for row,(top,bottom,count) in enumerate(courses):
        for k in range(count):
            a=-1.17+2.34*k/count;b=-1.17+2.34*(k+1)/count
            centre=(a+b)/2; topz=top-.015*abs(math.sin(centre))
            # Slight alternating boundary sweep belongs to fabricated plates.
            add(guard(f'V23 breast formed course {row+1:02} plate {k+1:02}',topz,bottom,centre,(b-a)/2,
                'breastplate',skin,off=.035-row*.0046,wall=.0035,
                sweep=.012*math.sin(row+k),tip_depth=.025,edge_slope=.012),'breast')
    for side in (-1,1):
        add(guard(f'V23 fixed side receiving liner {side}',1.356,.887,side*1.67,.57,
            'body',skin,off=-.019,wall=.004,tip_depth=.005,edge_slope=0),'breast')
        for row,(top,bottom) in enumerate(((1.355,1.195),(1.212,1.050),(1.066,.907))):
            add(guard(f'V23 fixed thoracic side {side} {row}',top,bottom,side*1.63,.46,
                'body',skin,off=-.009,wall=.004,coverage=(side*1.11,side*2.16) if side>0 else (-2.16,-1.11),tip_depth=.022),'breast')
    add(guard('V23 lower sternal return',.893,.787,0,1.27,'body',skin,off=-.019,wall=.004,tip_depth=.006),'breast')

    # Four small motion units sit within the throat curve, instead of two
    # oversized collar receivers. Diagonal overlapping terminal guards are
    # independently rigid, never a sheet spanning moving parents.
    spans=((1.425,1.320),(1.495,1.399),(1.565,1.469),(1.644,1.539))
    sectors=((-1.22,-.74),(-.72,-.25),(-.23,.23),(.25,.72),(.74,1.22),
             (1.245,1.82),(1.84,2.45),(-2.45,-1.84),(-1.82,-1.245),(2.47,math.tau-2.47))
    for idx,((owner,pos),(top,bottom)) in enumerate(zip(JOINTS,spans)):
        for k,(a,b) in enumerate(sectors):
            centre=(a+b)/2
            add(guard(f'V23 cervical {idx+1} directional guard {k+1}',top,bottom,centre,(b-a)/2,
                owner,skin,off=.005+idx*.002,wall=.0035,coverage=(a,b),
                tip_depth=.018 if k<5 else .022,edge_slope=.012),'neck')
        dest=Vector(JOINTS[idx+1][1]) if idx<3 else original['head'].translation
        for side in (-1,1):
            start=Vector(pos);start.x=side*.053;end=dest.copy();end.x=side*.053
            add(tube(f'V23 cervical {idx+1} load link {side}',[start,start.lerp(end,.5),end],.0105,owner,frame),'neck')
            add(bearing(f'V23 cervical {idx+1} distal race {side}',side*.071,dest.y,dest.z,.024,.010,owner,metal,thick=.013),'neck')
        driven=JOINTS[idx+1][0] if idx<3 else 'head'
        add(tube(f'V23 cervical {idx+1} captive pin',[(-.083,dest.y,dest.z),(.083,dest.y,dest.z)],.0085,driven,metal,'bearing'),'neck')
    # Fixed root, two torso spines and actual attachment into shoulder frames.
    root=Vector(JOINTS[0][1]);hinge=original['breastplate'].translation
    for side in (-1,1):
        add(bearing(f'V23 root fixed journal {side}',side*.075,root.y,root.z,.028,.011,'body',metal),'breast')
        add(tube(f'V23 root load fork {side}',[(side*.075,root.y,root.z),(side*.123,-.167,1.28),tuple(point(1.19,side*1.15,-.043))],.015,'body',frame),'breast')
        add(tube(f'V23 thoracic formed rib {side}',[tuple(point(z,side*.90,-.043)) for z in (.89,.98,1.10,1.21,1.29)],.014,'body',frame),'breast')
        mantle=original['left-mantle' if side>0 else 'right-mantle'].translation
        add(tube(f'V23 shoulder load link {side}',[(side*.10,-.188,1.31),(side*.19,-.065,1.29),mantle],.015,'body',frame),'breast')
        add(bearing(f'V23 breast opening bearing {side}',side*.155,hinge.y,hinge.z,.021,.008,'body',metal),'breast')
        add(tube(f'V23 breast hinge fixed fork {side}',[(side*.155,hinge.y,hinge.z),(side*.178,-.035,.910)],.012,'body',frame),'breast')
        add(tube(f'V23 breast moving return {side}',[(side*.155,hinge.y,hinge.z),tuple(point(.912,side*.70,-.010))],.010,'breastplate',frame),'breast')
    add(tube('V23 root captive shaft',[(-.093,root.y,root.z),(.093,root.y,root.z)],.009,'neck',metal,'bearing'),'neck')
    add(tube('V23 breast opening captive shaft',[(-.181,hinge.y,hinge.z),(.181,hinge.y,hinge.z)],.0065,'breastplate',metal,'bearing'),'breast')

    # Close the chopped upper mantle with a deliberately arched shoulder crown.
    # These plates attach only to the mantle; the neck side remains separate.
    for side in (-1,1):
        owner='left-mantle' if side>0 else 'right-mantle'
        # High inner attachment slopes out/down toward the existing fan.
        for row in range(3):
            for col in range(5):
                verts=[];faces=[];rows=12;cols=12
                for j in range(rows+1):
                    t=j/rows;v=(row+t*.98)/3
                    for k in range(cols+1):
                        u=(col+k/cols*.96)/5
                        ang=-1.46+2.92*u
                        x=side*(.145+.185*v+.027*math.sin(math.pi*v))
                        y=-.037+.169*math.sin(ang)
                        z=1.325+.123*math.cos(ang)*(1-.43*v)-.025*v
                        z-=.009*math.sin(math.pi*k/cols)**2*t
                        verts.append((x,y,z))
                for j in range(rows):
                    for k in range(cols):
                        a=j*(cols+1)+k;faces.append((a,a+1,a+cols+2,a+cols+1))
                obj=lib['mesh_object'](f'V23 shoulder arch {side} {row} {col}',verts,faces,owner,skin,'plate','Rigid arched mantle cap; no bridge to neck')
                bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
                for f in obj.data.polygons:f.use_smooth=True
                m=obj.modifiers.new('Finite shoulder wall','SOLIDIFY');m.thickness=.0035;m.offset=-1
                add(obj,'mantle')
    body=bpy.data.objects['body']
    body['cervicalLayoutV2']=json.dumps({'schema':1,'pitchJoints':[n for n,p in JOINTS],
      'weights':[.25]*4,'rootYaw':'neck','headOwner':'head','status':'proposed rigid serial articulation'},separators=(',',':'))
    body['v23ConstructionStatus']='Coordinated rest envelope; era sockets, all movement clearances and likeness are not yet accepted.'
    bpy.context.view_layer.update()
    return {'profile':PROFILE,'joints':JOINTS,'removed':staged,'added':added,
      'construction':'Four short rigid cervical links; separate opening tapered breast; arched mantle caps; passive internal support.',
      'changedPivots':['neck','cervical-upper'],'newPivots':['cervical-mid-a','cervical-mid-b'],
      'removedPivot':'cervical-joint-cover','reparented':['cervical-upper','head'],
      'limits':['Rest-envelope proposal; staggered plate overlaps require motion checks.',
                'Era hardware sockets inherited from V21 are not regenerated by this module.',
                'Head rest, leg/foot geometry, existing left-right restrictions preserved.']}
