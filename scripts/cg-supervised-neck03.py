"""Source-led curved neck and convex breast visual proposal.
API apply(scene, root_path=None, era='builder'). Source meshes remain retained.
Only front breast/neck and their central mechanism are superseded; no head,
lateral flank, shield, stance, source UV or anchor editing. Not engineering.
"""
import math, json
import bpy, bmesh
from mathutils import Vector


def apply(scene, root_path=None, era='builder'):
    if any(o.get('cgSupervisedNeck03') for o in scene.objects):
        raise RuntimeError('Reload preserved attempt01 before applying neck03')
    originals=list(scene.objects); made=[]; hidden=[]; mats={}
    for o in originals:
        if o.type=='MESH' and o.data.materials and o.get('cg1cRegion') in ('neck','body'):
            mats.setdefault(o.get('surfaceRole','armor'),o.data.materials[0])
    armor=mats.get('armor',mats.get('plate'));iron=mats.get('inner');bronze=mats.get('rivet',mats.get('bearing'))
    coll=bpy.data.collections.new('CG neck03 curved plate construction');scene.collection.children.link(coll)
    for o in originals:
        if o.type!='MESH' or o.hide_render:continue
        n=o.name
        replace=(o.get('cg1cRegion')=='neck' and o.get('surfaceRole')=='plate') or n.startswith('CG supervised breast throat') or n.startswith('CG2b sternal strap') or n.startswith('CG2b 0 irregular breast') or n=='CG2b tapered anterior breast backing'
        # Compact posterior copies occasionally retain anterior naming; do not
        # retire these side/back envelope meshes or any lateral machinery.
        if replace:
            o.hide_render=True;o.hide_set(True);o['cgNeck03Retained']=True;hidden.append(n)
    def mesh(name,vs,fs,uv,region='body',family=None,indices=None):
        d=bpy.data.meshes.new('CGN03 '+name);d.from_pydata(vs,[],fs);d.update()
        o=bpy.data.objects.new('CGN03 '+name,d);coll.objects.link(o)
        o['cgSupervisedNeck03']=True;o['cg1cRegion']=region;o['cg2bRegion']=region
        o['surfaceRole']='plate' if region=='neck' else 'armor';o['exteriorEras']='maker,mechanic,builder'
        o['cgConstructionStatus']='Source-led CG inference; likeness acceptance pending'
        families=family or ['head-armor' if region=='neck' else 'breast-armor','black-iron','worn-bronze']
        o['cgSurfaceFamilies']=json.dumps(families)
        mapping={'head-armor':armor,'breast-armor':armor,'black-iron':iron,'worn-bronze':bronze}
        for f in families:d.materials.append(mapping[f])
        layer=d.uv_layers.new(name='neck03-formed-sheet-uv')
        for p in d.polygons:
            p.use_smooth=True;p.material_index=indices[p.index] if indices else 0
            for li in p.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
        bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(d);bm.free()
        made.append(o);return o
    # Unified front surface: tight curved neck, generous convex breast, tapered
    # lower end. This is an envelope, never a single visible smooth bib.
    sections=[(.745,-.017,.095,.149),(.825,-.025,.151,.223),(.925,-.035,.197,.290),
              (1.025,-.049,.224,.326),(1.130,-.060,.228,.329),(1.225,-.080,.209,.279),
              (1.300,-.105,.128,.149),(1.365,-.083,.103,.110),(1.430,-.062,.089,.103),
              (1.495,-.078,.098,.109),(1.560,-.114,.110,.115)]
    def section(z):
        z=max(sections[0][0],min(sections[-1][0],z))
        for k,(p,q) in enumerate(zip(sections,sections[1:])):
            if p[0]<=z<=q[0]:
                t=(z-p[0])/(q[0]-p[0]);out=[]
                for i in range(1,4):
                    prev=sections[max(0,k-1)][i];nxt=sections[min(len(sections)-1,k+2)][i]
                    out.append(.5*((2*p[i])+(-prev+q[i])*t+(2*prev-5*p[i]+4*q[i]-nxt)*t*t+(-prev+3*p[i]-3*q[i]+nxt)*t*t*t))
                return out
        return list(sections[-1][1:])
    def surf(a,z,lift=0):
        cy,rx,ry=section(z);return Vector(((rx+lift)*math.sin(a),cy-(ry+lift)*math.cos(a),z))
    leaf=[(-.36,.0),(.34,.0),(.48,.15),(.49,.35),(.40,.62),(.22,.88),(.025,1),(-.13,.96),(-.34,.77),(-.46,.51),(-.49,.26),(-.45,.10)]
    framing=[(-.44,0),(.33,0),(.49,.13),(.43,.43),(.29,.72),(.09,.98),(-.20,.91),(-.40,.72),(-.48,.47),(-.49,.20)]
    def sheet(name,sample,outline=leaf,region='body',thick=.0028):
        n=len(outline);vs=[];uv=[];fs=[];inds=[]
        for r in (1,.82,.61,.40,.20,.055):
            for u,v in outline:
                uu=u*r;vv=.43+(v-.43)*r
                vs.append(tuple(sample(uu,vv,.0006*(1-r))));uv.append((uu+.5,vv))
        for j in range(5):
            for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i));inds.append(0)
        fs.append(tuple(range(5*n,6*n)));inds.append(0)
        for u,v in outline:vs.append(tuple(sample(u,v,-thick)));uv.append((u+.5,v))
        fs.append(tuple(reversed(range(6*n,7*n))));inds.append(1)
        for i in range(n):fs.append((i,6*n+i,6*n+(i+1)%n,(i+1)%n));inds.append(1)
        o=mesh(name,vs,fs,uv,region,indices=inds)
        b=o.modifiers.new('restrained sheet boundary bevel','BEVEL');b.width=.00045;b.segments=2
        return o
    # Dark recess only below the armor, cut into separate partial sectors. No
    # visible complete barrel or sealed continuous projecting throat shell.
    for a0,a1 in [(-1.17,-.47),(-.47,.34),(.34,1.17)]:
        vs=[];uv=[];fs=[]
        for j in range(41):
            z=.752+j*.808/40
            for i in range(15):vs.append(tuple(surf(a0+(a1-a0)*i/14,z,-.024)));uv.append((i/14,j/40))
        for j in range(40):
            for i in range(14):k=j*15+i;fs.append((k,k+1,k+16,k+15))
        mesh('recessed anterior mechanism backing '+str(a0),vs,fs,uv,family=['black-iron'])
    # Neck leaves deliberately stagger downward and outward; each is an
    # independent editable formed plate, not circumferential rings.
    neckcourses=[(1.559,.080,[(-.67,.055),(-.10,.057),(.51,.060),(1.64,.044),(2.24,.050),(2.89,.057),(3.51,.052),(4.05,.042)]),
                 (1.514,.087,[(-.88,.048),(-.26,.055),(.35,.060),(1.62,.045),(2.30,.050),(2.96,.057),(3.59,.052),(4.10,.042)]),
                 (1.468,.095,[(-.98,.046),(-.39,.054),(.24,.067),(1.58,.045),(2.26,.052),(2.92,.058),(3.56,.050),(4.07,.042)]),
                 (1.420,.101,[(-.89,.043),(-.22,.059),(.43,.065),(1.55,.048),(2.22,.054),(2.87,.060),(3.48,.052),(4.07,.043)]),
                 (1.370,.115,[(-.83,.046),(-.11,.065),(.55,.078),(1.50,.049),(2.16,.055),(2.79,.061),(3.40,.054),(4.03,.045)]),
                 (1.319,.129,[(-.53,.076),(.08,.084),(.69,.078),(1.45,.046),(2.13,.060),(2.80,.066),(3.47,.055),(4.09,.045)])]
    for row,(z,length,entries) in enumerate(neckcourses):
        for col,(a,w) in enumerate(entries):
            # Anterior left channel opens into central receiver chain.
            if col==0 and row in (2,3):continue
            def sample(u,v,e,a=a,z=z,w=w,length=length,row=row,col=col):
                zz=z-v*(min(length,max(.018,z-1.300)) if col>=3 else length)+u*.010;rx=section(zz)[1]
                aa=a+u*w/max(.082,rx)+(.15 if col<3 else -.10)*v
                return surf(aa,zz,.007+.0018*(5-row)+e+.0015*math.sin(v*math.pi))
            ob=sheet('tapered cervical leaf %d-%d'%(row,col),sample,region='neck');ob['plateCourse']=row
    # Breast courses vary scale/shape and fan around a dark anterior channel.
    # Rows connect directly into the neck leaves and broaden only through the
    # natural convex upper breast; no abrupt collar at z1.30.
    courses=[(1.327,.111,[(-.09,.078),(.49,.086),(.97,.068)]),
             (1.276,.125,[(-.33,.079),(.15,.087),(.64,.084),(1.02,.065)]),
             (1.214,.136,[(-.46,.088),(-.05,.103),(.38,.098),(.83,.094),(1.12,.072)]),
             (1.149,.141,[(-.46,.098),(-.04,.104),(.41,.103),(.85,.105)]),
             (1.081,.134,[(-.50,.099),(-.06,.099),(.37,.100),(.78,.101),(1.13,.074)]),
             (1.012,.145,[(-.71,.095),(-.28,.102),(.15,.103),(.58,.111),(1.01,.087)]),
             (.944,.136,[(-.75,.087),(-.32,.099),(.13,.098),(.57,.099),(1.02,.074)]),
             (.878,.125,[(-.73,.070),(-.26,.087),(.20,.093),(.70,.083),(1.10,.062)]),
             (.820,.090,[(-.65,.062),(-.12,.082),(.45,.078),(.97,.061)])]
    for row,(z,length,entries) in enumerate(courses):
        for col,(a,w) in enumerate(entries):
            z0=z+.015*math.sin(col*2.0+row*.77);length=length*(.92+.11*math.sin(row*1.61+col*1.7))
            def sample(u,v,e,a=a,z=z0,w=w,length=length,row=row,col=col):
                zz=z-length*v+u*.013;rx=section(zz)[1]
                aa=a+u*w/max(.11,rx)+(.08+.04*math.sin(row*1.8+col))*v
                return surf(aa,zz,.010+(8-row)*.0011+e+.0016*math.sin(math.pi*v))
            ob=sheet('convex breast formed leaf %d-%d'%(row,col),sample,outline=framing if (row+col)%3==0 else leaf);ob['plateCourse']=row
    # Unequal formed channel boundaries, nestled into breast curvature. The
    # source has framing plates near receivers, rather than broad smooth straps.
    for j,(z,a,w,length) in enumerate([(1.445,-1.02,.041,.087),(1.365,-1.07,.046,.112),
                                      (1.272,-.99,.063,.127),(1.171,-.91,.075,.139),
                                      (1.062,-.98,.078,.143),(.941,-1.02,.077,.138)]):
        def sample(u,v,e,z=z,a=a,w=w,length=length,j=j):
            zz=z-length*v+u*.008;rx=section(zz)[1]
            return surf(a+u*w/max(.09,rx)+.11*v,zz,.010+e)
        sheet('receiver framing leaf '+str(j),sample,framing,region='neck' if z>1.34 else 'body')
    def tube(name,pts,r,family='black-iron',region='body'):
        vs=[];uv=[];fs=[];n=12
        for j,p in enumerate(pts):
            p=Vector(p);t=(Vector(pts[min(len(pts)-1,j+1)])-Vector(pts[max(0,j-1)])).normalized()
            u=t.cross(Vector((0,0,1)))
            if u.length<.01:u=t.cross(Vector((0,1,0)))
            u.normalize();w=t.cross(u).normalized()
            for i in range(n):vs.append(tuple(p+r*(u*math.cos(i*2*math.pi/n)+w*math.sin(i*2*math.pi/n))));uv.append((i/n,j/(len(pts)-1)))
        for j in range(len(pts)-1):
            for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        fs.append(tuple(range(n-1,-1,-1)));fs.append(tuple((len(pts)-1)*n+i for i in range(n)))
        return mesh(name,vs,fs,uv,region,family=[family])
    # Continuous curved linkage routes occupy the open channel and enter each
    # receiver. They are recessed, never a protruding accordion neck.
    for k in range(3):
        pts=[]
        for j in range(48):
            z=.94+j*.60/47;a=-.75+k*.09+.07*math.sin(j/47*math.pi)
            pts.append(surf(a,z,-.010-k*.003))
        tube('curved front transmission link '+str(k),pts,.0045 if k==1 else .0035,region='neck')
    def annulus(name,z,a,rad,depth,family='worn-bronze'):
        c=surf(a,z,.003);normal=Vector((math.sin(a),-math.cos(a),0));u=Vector((math.cos(a),math.sin(a),0));v=Vector((0,0,1));vs=[];uv=[];fs=[]
        for j,(r,d) in enumerate([(rad,0),(rad,depth),(rad*.61,depth),(rad*.61,0)]):
            for i in range(40):
                angle=i*2*math.pi/40;vs.append(tuple(c+normal*d+r*(u*math.cos(angle)+v*math.sin(angle))));uv.append((i/40,j/3))
        for j in range(4):
            for i in range(40):fs.append((j*40+i,j*40+(i+1)%40,((j+1)%4)*40+(i+1)%40,((j+1)%4)*40+i))
        return mesh(name,vs,fs,uv,'neck' if z>1.31 else 'body',family=[family])
    for j,(z,a,r) in enumerate([(1.483,-.86,.019),(1.380,-.79,.021),(1.266,-.68,.026),(1.145,-.73,.029),(1.029,-.80,.024)]):
        annulus('recessed transmission receiver '+str(j),z,a,r,.006)
        annulus('receiver dark inner race '+str(j),z,a,r*.73,.008,'black-iron')
        # One connected dog-leg per receiver supplies scale and function cues.
        pts=[surf(a-.02,z+.037,-.003),surf(a+.055,z+.018,-.001),surf(a+.07,z-.017,-.002),surf(a+.14,z-.039,-.006)]
        tube('receiver connected crank '+str(j),pts,.005,'worn-bronze','neck' if z>1.31 else 'body')
    bpy.context.view_layer.update()
    return {'module':'cg-supervised-neck03','era':era,'newMeshCount':len(made),'hiddenRetainedMeshes':hidden,
            'sourceStatus':'Pinned pixels control visual proposal; unseen construction inferred',
            'surfaceSections':sections,'changes':['Unequal tapered curved neck leaves widen into convex breast','Substantial individual breast plates wrap recessed front mechanism','Unequal receiver framing leaves and connected curved linkages'],
            'limits':['Not final source likeness','Breast layering remains a simplified CG interpretation','Hidden rear construction inferred','Materials carried from receiving graphs; root owns finish','No engineering, browser parity or owner acceptance claim']}
