"""V24 body-fixed receiving cheeks beneath the inherited moving mantle.

Owner whole-bird image controls the layered breast/shoulder relationship.
Hidden supports are proposed passive construction, not recovered engineering.
No change to mantle pivots, travel restrictions, or existing wing geometry.
"""
from pathlib import Path
import bpy, bmesh, math, runpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
PROFILE=((.78,-.165,.125,.170),(.87,-.247,.139,.210),(.99,-.365,.128,.252),
 (1.12,-.425,.095,.280),(1.245,-.417,.038,.258),(1.335,-.382,-.035,.205),
 (1.410,-.352,-.106,.145),(1.48,-.379,-.160,.116),(1.555,-.428,-.213,.109),(1.635,-.446,-.256,.100))
# Native coordinates describe a proposed fitted receiving edge, not image dimensions.
TOP=((.188,-.242,1.333),(.205,-.180,1.365),(.211,-.096,1.395),(.224,-.022,1.384),(.227,.040,1.333))

def curve(points,t):
    s=max(0,min(1,t))*(len(points)-1);i=min(int(s),len(points)-2);q=s-i
    a,b,c,d=[Vector(points[k]) for k in (max(0,i-1),i,i+1,min(i+2,len(points)-1))]
    return .5*(2*b+(-a+c)*q+(2*a-5*b+4*c-d)*q*q+(-a+3*b-3*c+d)*q*q*q)

def apply(envelope_helper=None):
    lib=runpy.run_path(str(envelope_helper or ROOT/'scripts/regions/whole-character-v21-envelope.py'))
    for n in ('sample','envelope_point','guard','tube','bearing'):lib[n].__globals__['PROFILE']=PROFILE
    point=lib['envelope_point'];removed=[];added=[]
    skin=bpy.data.objects['V23 fixed thoracic side 1 0'].data.materials[0]
    frame=bpy.data.objects['V23 shoulder load link 1'].data.materials[0]
    metal=bpy.data.objects['V23 root fixed journal 1'].data.materials[0]
    def add(o,role):
        o['region']='breast';o['surfaceRole']=role;o['geometryStatus']='V24 fitted shoulder receiver proposal; movement clearance requires review'
        o['constructionClass']='inherited-passive';o['exteriorEras']='maker,mechanic,builder';o['proposal']=True
        added.append(o.name);return o
    for side in (-1,1):
        for n in (f'V23 fixed thoracic side {side} 0',f'V23 fixed side receiving liner {side}'):
            o=bpy.data.objects[n];removed.append({'name':n,'owner':o.parent.name});bpy.data.objects.remove(o,do_unlink=True)
        # Lower backing follows the inherited torso. The shoulder-root service
        # slot above remains open to actual load links and a concentric journal.
        add(lib['guard'](f'V24 lower side receiving liner {side}',1.215,.887,side*1.67,.57,
            'body',skin,off=-.022,wall=.004,tip_depth=.005,edge_slope=0),'plate')
        verts=[];faces=[];rows=20;cols=32
        for j in range(rows+1):
            t=j/rows
            for k in range(cols+1):
                u=k/cols;top=curve(TOP,u);top.x*=side
                angle=side*(1.11+1.18*u)
                bottom=point(1.192-.010*math.sin(math.pi*u),angle,-.007)
                p=top.lerp(bottom,t)
                # A modest formed crown, never a stretched sheet spanning owners.
                p.x+=side*.006*math.sin(math.pi*t)*math.sin(math.pi*u)
                verts.append(tuple(p))
        for j in range(rows):
            for k in range(cols):
                a=j*(cols+1)+k;faces.append((a,a+1,a+cols+2,a+cols+1))
        o=lib['mesh_object'](f'V24 rising thoracic receiving cheek {side}',verts,faces,'body',skin,'plate',
          'Finite body-fixed tapered cheek rises beneath the independent mantle; no metal bridge across pivot')
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        if sum(f.normal.x for f in bm.faces)*side<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
        bm.to_mesh(o.data);bm.free()
        for f in o.data.polygons:f.use_smooth=True
        q=o.modifiers.new('Finite receiving cheek wall','SOLIDIFY');q.thickness=.004;q.offset=-1;q.use_even_offset=True
        q=o.modifiers.new('Receiving edge chamfer','BEVEL');q.width=.0008;q.segments=2
        add(o,'plate')
        mantle=bpy.data.objects['left-mantle' if side>0 else 'right-mantle'].matrix_world.translation
        # The shoulder bearing uses the actual existing pivot, not a decorative
        # circular part placed behind a hole. The sleeve is body-owned; shaft
        # belongs to the mantle, so each independently follows one rigid owner.
        bx=mantle.x-side*.021
        add(lib['bearing'](f'V24 fixed shoulder receiving journal {side}',bx,mantle.y,mantle.z,.045,.021,'body',metal,thick=.018),'bearing')
        add(lib['tube'](f'V24 shoulder lower load fork {side}',[tuple(point(1.075,side*1.28,-.037)),
            (side*.246,-.058,1.188),(bx,mantle.y,mantle.z)],.012,'body',frame),'frame')
        shaft=lib['tube'](f'V24 mantle captive shoulder shaft {side}',[(bx-side*.013,mantle.y,mantle.z),
            (mantle.x+side*.008,mantle.y,mantle.z)],.0195,'left-mantle' if side>0 else 'right-mantle',metal,'bearing')
        add(shaft,'bearing');shaft['region']='mantle'
    bpy.context.view_layer.update()
    return {'removed':removed,'added':added,'controllingReference':'Owner whole-bird target: layered shoulder receiving edge and exposed mechanical flank',
      'topCurveNative':TOP,'pivotPolicy':'Existing left/right mantle pivots and travel constraints unchanged',
      'attachments':'Body-fixed finite cheek, lower liner, journal and load fork; separately mantle-owned captive shaft',
      'eraEligibility':'All new parts are passive frame, bearings and guards in all three eras',
      'limits':['Hidden support arrangement is a proposed reconstruction.','Clearance is assessed separately; no dynamic simulation claim.']}
