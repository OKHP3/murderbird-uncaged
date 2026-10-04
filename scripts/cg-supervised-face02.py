"""Second bounded face/throat proposal; apply to supervised attempt01 native.
Source-directed inferred geometry, not owner-approved likeness or engineering.
All receiving meshes are preserved; superseded parts are hidden, never deleted.
"""
import math
import bpy
from mathutils import Vector, Matrix


def apply(scene, root_path=None, era='builder'):
    if any(o.get('cgSupervisedFace02') for o in scene.objects):
        raise RuntimeError('Reload attempt01 before applying face02')
    frame=scene.objects['CG2b head frame'].matrix_world.copy()
    made=[];hidden=[]
    def mat_from(name): return scene.objects[name].data.materials[0]
    mats={'plate':mat_from('CGH01 swept crown leaf 0 0'),
          'bill':mat_from('CGH01 formed bill L 0 0'),
          'inner':mat_from('CGH01 recessed cranial structure'),
          'bearing':mat_from('CGH01 jaw tendon L 0')}
    for o in list(scene.objects):
        if o.type!='MESH' or o.hide_render: continue
        n=o.name
        replace=(n.startswith(('CGH01 swept lower jaw','CGH01 open cheek arch','CGH01 jaw tendon','CGH01 orbital brow','CGH01 swept crown leaf','CGH01 forehead saddle','CG supervised breast throat course')))
        if n.startswith('CGH01 curved cervical leaf'):
            # Replace front throat courses, retaining back and exposed machinery.
            replace=int(n.split()[-1])<3
        if replace:
            o.hide_render=True;o.hide_set(True);o['cgFace02Superseded']=True;hidden.append(n)
    def mesh(name,vs,fs,role='plate',region='head',tf=None,thick=.0025):
        d=bpy.data.meshes.new('CGF02 '+name);d.from_pydata(vs,[],fs);d.update()
        o=bpy.data.objects.new('CGF02 '+name,d);scene.collection.objects.link(o)
        o.matrix_world=frame.copy() if tf is None else tf
        o['cgSupervisedFace02']=True;o['cg1cRegion']=region;o['cg2bRegion']=region;o['surfaceRole']=role
        o['exteriorEras']='maker,mechanic,builder';o['cgConstructionStatus']='inferred visual proposal; owner review pending'
        d.materials.append(mats[role]);d.materials.append(mats['inner'])
        uv=d.uv_layers.new(name='face02-form-uv')
        for p in d.polygons:
            p.use_smooth=True
            for li in p.loop_indices:
                v=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(.5+v.y*2,.5+v.z*2)
        if thick:
            so=o.modifiers.new('formed plate return','SOLIDIFY');so.thickness=thick;so.offset=-1;so.material_offset=1;so.material_offset_rim=1
            be=o.modifiers.new('cut edge radius','BEVEL');be.width=.0005;be.segments=2
        made.append(o);return o
    def patch(name,fn,role='plate',region='head',tf=None,nx=9,ny=25,thick=.0025):
        vs=[fn(i/(nx-1),j/(ny-1)) for j in range(ny) for i in range(nx)]
        fs=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
        return mesh(name,vs,fs,role,region,tf,thick)
    def sec(ss,t):
        q=max(0,min(len(ss)-1-1e-7,t*(len(ss)-1)));i=int(q);t=q-i
        a,b,c,d=ss[max(0,i-1)],ss[i],ss[i+1],ss[min(len(ss)-1,i+2)]
        return Vector([(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t)*.5 for k in range(len(a))])
    def ribbon(name,path,width,role='plate',region='head',tf=None):
        def f(u,t):
            p=sec(path,t);d=sec(path,min(1,t+.002))-sec(path,max(0,t-.002));v=Vector((0,-d.z,d.y)).normalized()
            return p+v*((u-.5)*2*width*(.72+.28*math.sin(math.pi*t)))+Vector((math.copysign(.003*math.sin(math.pi*u),p.x),0,0))
        return patch(name,f,role,region,tf)
    def tube(name,path,r,role='bearing',region='head',tf=None):
        def f(u,t):
            p=sec(path,t);d=(sec(path,min(1,t+.002))-sec(path,max(0,t-.002))).normalized()
            v=d.cross(Vector((1,0,0))).normalized();w=d.cross(v)
            return p+r*(v*math.cos(u*2*math.pi)+w*math.sin(u*2*math.pi))
        return patch(name,f,role,region,tf,nx=13,ny=31,thick=0)
    # Crown shares the previous swept volume but uses individually tapered
    # short clusters with staggered ends, not broad continuous hair-like sheets.
    skull=[(-.171,.075,.073,.064),(-.125,.053,.127,.107),(-.055,.032,.163,.142),(.045,.028,.176,.149),(.135,.005,.133,.130),(.215,-.030,.073,.087),(.253,-.073,.012,.030)]
    def shell(t,a,extra):
        y,z,rx,rz=sec(skull,t);return Vector(((rx+extra)*math.sin(a),y,z+(rz+extra)*math.cos(a)))
    for row in range(6):
        for col in range(11):
            ac=(col-5)*.235+(row%2)*.102;start=.012+row*.145+(col%3)*.010
            def f(u,t,ac=ac,start=start,row=row,col=col):
                wid=.142*(1-.97*t**2.6);tt=min(.991,start+(.24+.025*(col%2))*t)
                p=shell(tt,ac+(u-.5)*2*wid+.028*t,.009+row*.001+.005*math.sin(math.pi*t))
                p.y+=.026*t*t;p.z+=.010*t*t;return p
            patch('swept crown cluster %02d %02d'%(row,col),f,nx=7,ny=17)
    patch('forehead diagonal saddle',lambda u,t:shell(.004+.41*t,(u-.5)*(.42-.14*t),.020),nx=9,ny=29,thick=.004)
    for side,label in ((-1,'L'),(1,'R')):
        def points(seq): return [(side*x,y,z) for x,y,z in seq]
        # Source's characteristic curved diagonal plate wraps beneath the optic
        # and climbs to the bill root; it is a substantial connected cheek form.
        path=points([(.166,.107,.071),(.195,.078,.058),(.206,.054,.007),(.208,.015,-.049),(.199,-.035,-.057),(.156,-.098,-.008),(.111,-.157,.064)])
        ribbon('sinuous brow billroot bridge '+label,path,.019)
        # Upper orbital plate follows the actual optic without moving its center.
        def brow(u,t,side=side):
            a=.06+math.pi*.96*t;r=.059+u*.027
            return (side*(.193+.005*math.sin(math.pi*u)),.003+r*math.cos(a),.017+r*math.sin(a))
        patch('orbital eyebrow shield '+label,brow,nx=7,ny=33,thick=.003)
        # Connected cheek web; the aperture is now bounded by curved construction.
        ribbon('cheek jaw hinge arch '+label,points([(.163,.128,-.014),(.181,.110,-.062),(.178,.073,-.092),(.163,.020,-.111),(.134,-.025,-.150),(.084,-.074,-.207),(.036,-.141,-.260)]),.015,'plate')
        # Rounded hook under jaw descends toward bill tip instead of a spear.
        jaw=[(.126,-.079,.105,.024),(.070,-.119,.096,.023),(.010,-.151,.080,.023),(-.048,-.190,.058,.023),(-.087,-.250,.041,.020),(-.142,-.274,.016,.010),(-.179,-.258,.001,.001)]
        def mandible(u,t,side=side):
            y,z,rx,rz=sec(jaw,t);a=side*(u*math.pi);return (rx*math.sin(a),y,z+rz*math.cos(a))
        patch('descending curved mandible '+label,mandible,'bill',nx=15,ny=45)
        for k in range(2):
            tube('internal mandibular linkage '+label+str(k),points([(.135-k*.014,.091,-.068),(.136-k*.013,.030,-.093),(.108-k*.012,-.030,-.142),(.065-k*.008,-.075,-.211),(.025,-.136,-.258)]),.0045,'bill')
        # Bill-root cheek cover: broad curved plate decreases in transverse width
        # toward the hooked tip, integrating the eye plate and upper bill shell.
        rootpath=points([(.119,-.141,.091),(.124,-.174,.052),(.112,-.202,.007),(.091,-.220,-.047),(.071,-.239,-.094)])
        ribbon('billroot lateral face plate '+label,rootpath,.027,'plate')
        # Nested circular jaw journal joins the two source-directed cheek plates.
        for k,(radius,role) in enumerate(((.020,'bill'),(.013,'bearing'))):
            def ann(u,t,side=side,radius=radius):
                a=t*math.pi*2;r=radius+u*.005
                return (side*(.191+k*.003),.085+r*math.cos(a),-.036+r*math.sin(a))
            patch('cheek hinge annulus '+label+str(k),ann,role,nx=5,ny=41,thick=.003)
        # A formed nostril opening on the lateral root plate, with recessed dark
        # interior and a real raised oval rim (no detached scattered fasteners).
        def nostril(u,t,side=side):
            a=t*math.pi*2;r=.010+u*.004
            return (side*(.128+.002*math.sin(math.pi*u)),-.178+r*.78*math.cos(a),.039+r*1.22*math.sin(a))
        patch('billroot oval aperture rim '+label,nostril,'bill',nx=5,ny=33)
    # Continuous throat-to-upper-breast profile. Coordinates blend directly into
    # retained breast surfaces below; original root/head transforms are untouched.
    sections=[(1.570,-.218,.097),(1.510,-.211,.106),(1.450,-.204,.108),(1.390,-.227,.119),(1.330,-.287,.145),(1.265,-.346,.183),(1.198,-.380,.203),(1.140,-.391,.203)]
    def throat(t,a):
        z,front,rx=sec(sections,t)
        return Vector((rx*math.sin(a),front+.115*(1-math.cos(a)),z))
    ident=Matrix.Identity(4)
    for row in range(9):
        count=5 if row<4 else 7
        for col in range(count):
            ac=(col-(count-1)/2)*(.47 if row<4 else .36)+(row%2)*.055
            start=row*.103
            def leaf(u,t,ac=ac,start=start,row=row):
                tt=min(.998,start+.184*t);w=(.285 if row<4 else .252)*(1-.95*t**3)
                p=throat(tt,ac+(u-.5)*2*w+.035*t)
                p.y-=.007+(9-row)*.002+.010*math.sin(math.pi*t);p.z-=.014*t*t;return p
            patch('linked throat breast lamella %02d %02d'%(row,col),leaf,'plate','neck',ident,nx=7,ny=21)
    # Each lateral throat rail follows the widening cuirass, giving a connected
    # structural edge without closing the existing machinery slot.
    for side,label in ((-1,'L'),(1,'R')):
        path=[]
        for i in range(7):
            p=throat(.18+.80*i/6,side*1.10);p.y+=.008;path.append(p)
        tube('throat to breast side rail '+label,path,.007,'bill','neck',ident)
    # Enforce era optic emission canon on copied material graphs only.
    copies={}
    for o in scene.objects:
        if o.type!='MESH' or o.hide_render: continue
        for i,m in enumerate(o.data.materials):
            if not m or 'amber' not in m.name: continue
            if m.name not in copies:
                n=m.copy();n.name='CGF02 optic '+era+' '+m.name
                bs=n.node_tree.nodes.get('Principled BSDF')
                if bs and era!='builder':
                    bs.inputs['Emission Strength'].default_value=0;bs.inputs['Base Color'].default_value=(.006,.010,.008,1)
                copies[m.name]=n
            o.data.materials[i]=copies[m.name]
    bpy.context.view_layer.update()
    return {'module':'cg-supervised-face02','era':era,'new_mesh_count':len(made),'hidden_preserved_meshes':hidden,
            'unchanged_anchors':['CG2b head frame','CG2b neck root','CG2b neck head'],
            'changes':['curved diagonal brow to billroot plate','descending hooked lower mandible','connected cheek aperture and hinge','short tapered crown clusters','continuous throat and upper breast lamellae'],
            'limits':['inferred construction and unseen surfaces','owner artistic acceptance unknown','browser parity not tested in worker']}
