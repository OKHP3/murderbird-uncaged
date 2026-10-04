"""Editable crown, bill-root, cheek and curved neck proposal on frozen CG2b.
apply(scene, root_path=None, era='builder') keeps source objects and anchors.
All added geometry is inferred from the pinned canon and July head pixels.
"""
import math
import bpy
from mathutils import Vector, Matrix


def apply(scene, root_path=None, era='builder'):
    if any(o.get('cgSupervisedHead01') for o in scene.objects):
        raise RuntimeError('Reload frozen CG2b before applying this module again')
    frame = scene.objects['CG2b head frame'].matrix_world.copy()
    root = scene.objects['CG2b neck root'].matrix_world.translation.copy()
    top = scene.objects['CG2b neck head'].matrix_world.translation.copy()
    originals = list(scene.objects); hidden=[]; made=[]; mats={}
    for o in originals:
        if o.type=='MESH' and not o.hide_render and o.get('cg1cRegion') in ('head','neck'):
            if o.data.materials: mats.setdefault(o.get('surfaceRole'),o.data.materials[0])
    # Optic centers, closed lenses and nested ring hardware remain in their exact
    # receiving pose. Broad old brow, cheek and neck meshes are superseded.
    optical=('optic ','orbital','lens','iris','subglass','optical','aperture','temple drive')
    for o in originals:
        if o.type!='MESH' or o.hide_render or o.get('cg1cRegion') not in ('head','neck'):continue
        retain=o.get('cg2bFace') and o.get('cg1cRegion')=='head' and any(s in o.name.lower() for s in optical)
        # An old cheek-aperture backing would seal our new open cavity.
        if 'cheek' in o.name.lower():retain=False
        if not retain:
            o.hide_render=True;o.hide_set(True);o['cgSupervisedHead01Superseded']=True;hidden.append(o.name)
    def mesh(name,v,f,role='plate',region='head',tf=None,smooth=True,uv=None):
        d=bpy.data.meshes.new('CGH01 '+name);d.from_pydata(v,[],f);d.update()
        o=bpy.data.objects.new('CGH01 '+name,d);scene.collection.objects.link(o)
        o.matrix_world=frame.copy() if tf is None else tf.copy()
        o['cgSupervisedHead01']=True;o['cg1cRegion']=region;o['cg2bRegion']=region;o['surfaceRole']=role
        o['exteriorEras']='maker,mechanic,builder';o['cgConstructionStatus']='inferred visual proposal; owner acceptance pending'
        mat=mats.get(role) or mats.get('plate')
        if mat:d.materials.append(mat)
        layer=d.uv_layers.new(name='cg-head01-uv')
        for p in d.polygons:
            p.use_smooth=smooth
            for li in p.loop_indices:
                idx=d.loops[li].vertex_index;q=d.vertices[idx].co
                layer.data[li].uv=uv[idx] if uv else (.5+q.y*2,.5+q.z*2)
        made.append(o);return o
    def patch(name,fn,role='plate',region='head',tf=None,nx=9,ny=15,thick=.003):
        v=[];uv=[]
        for j in range(ny):
            for i in range(nx):
                u=i/(nx-1);t=j/(ny-1);v.append(fn(u,t));uv.append((u,t))
        f=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
        o=mesh(name,v,f,role,region,tf,uv=uv)
        if thick:
            if mats.get('inner'):o.data.materials.append(mats['inner'])
            so=o.modifiers.new('dark formed return','SOLIDIFY');so.thickness=thick;so.offset=-1;so.material_offset=1;so.material_offset_rim=1
            b=o.modifiers.new('soft sheet edge','BEVEL');b.width=.0007;b.segments=2
        return o
    def cat(a,b,c,d,t):
        return [(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t)*.5 for k in range(len(a))]
    def section(secs,t):
        u=min(len(secs)-1-1e-5,max(0,t*(len(secs)-1)));i=int(u)
        return cat(secs[max(0,i-1)],secs[i],secs[i+1],secs[min(len(secs)-1,i+2)],u-i)
    skull=[(-.171,.075,.073,.064),(-.125,.053,.127,.107),(-.055,.032,.163,.142),(.045,.028,.176,.149),(.135,.005,.133,.130),(.215,-.030,.073,.087),(.253,-.073,.012,.030)]
    def shell(t,a,extra=0):
        y,z,rx,rz=section(skull,t)
        return Vector(((rx+extra)*math.sin(a),y,z+(rz+extra)*math.cos(a)))
    # Dark reduced inner volume under crown; its sides stop short of cheek,
    # permitting a real silhouette opening below the optic and jaw rail.
    patch('recessed cranial structure',lambda u,t:shell(t,(u-.5)*math.pi*1.15,-.012),'inner',nx=49,ny=45,thick=.005)
    # Four interleaving swept courses; width falls into a rounded pointed leaf,
    # rather than ending all rows on one clipped rectangular helmet edge.
    for course in range(5):
        start=.010+course*.17;length=.30 if course<4 else .28
        for col in range(9):
            ac=(col-4)*.27+(course%2)*.10
            leafstart=start+(col%2)*.019
            def leaf(u,t,start=leafstart,length=length,ac=ac,course=course):
                tt=min(.995,start+length*t);width=.188*(.96-.93*t*t)
                p=shell(tt,ac+(u-.5)*2*width+.045*t,.009+course*.001+.010*math.sin(math.pi*t))
                p.y+=.030*t*t;p.z+=.012*t*t*(1-abs(ac)/1.8)
                return p
            patch('swept crown leaf %d %d'%(course,col),leaf,ny=18)
    # The large top seam runs into the bill root, like the source's broad
    # forehead strap, but leaves the optic clear beneath its overhanging brow.
    patch('forehead saddle',lambda u,t:shell(.01+.42*t,(u-.5)*.43,.018+.005*math.sin(math.pi*t)),ny=18,thick=.004)
    for side,label in ((-1,'L'),(1,'R')):
        for course in range(3):
            for col in range(4):
                ac=side*(1.05+col*.29);start=.43+course*.14
                def leaf(u,t,ac=ac,start=start):
                    p=shell(min(.993,start+.39*t),ac+(u-.5)*.50*(1-.97*t*t),.006+.009*math.sin(math.pi*t))
                    p.y+=.040*t*t;p.z-=.022*t*t
                    return p
                patch('nape feather '+label+' %d %d'%(course,col),leaf,ny=16)
        # Swept eyebrow crescent with an open eye, three substantial formed
        # plates linking bill-root to the rear cranial leaves.
        for sector in range(3):
            def brow(u,t,side=side,sector=sector):
                a=.13+(sector+t)*math.pi*.29;r=.054+u*.031
                return (side*(.192+.012*math.sin(math.pi*u)),.003+r*math.cos(a),.017+r*math.sin(a))
            patch('orbital brow '+label+' '+str(sector),brow,nx=7,ny=13,thick=.004)
    upper=[(-.151,.036,.093,.086),(-.207,.018,.091,.096),(-.265,-.040,.072,.088),(-.304,-.115,.050,.077),(-.315,-.192,.024,.053),(-.289,-.255,.001,.002)]
    def bill(t,a,extra=0):
        y,z,rx,rz=section(upper,t);return Vector(((rx+extra)*math.sin(a),y,z+(rz+extra)*math.cos(a)))
    patch('deep bill inner',lambda u,t:bill(t,u*2*math.pi,-.002),'inner',nx=49,ny=45,thick=0)
    # Four unequal formed plates on each cheek of the bill. A root plate and
    # narrow tip shell provide the long hooked identity with articulated seams.
    for side,label in ((-1,'L'),(1,'R')):
        for course,(start,end) in enumerate(((.008,.28),(.26,.53),(.51,.76),(.74,.99))):
            for band in range(2):
                def sheet(u,t,side=side,start=start,end=end,band=band):
                    a=side*(.022+band*1.52+u*1.49)
                    tt=max(.002,min(.994,start+(end-start)*t+.025*math.sin(abs(a))*math.sin(math.pi*t)))
                    return bill(tt,a,.0025)
                patch('formed bill '+label+' %d %d'%(course,band),sheet,'bill',nx=9,ny=18,thick=.0022)
        # Lower jaw becomes a dark tapered S rail with an open mouth above it.
        jaw=[(.137,-.065,.103,.028),(.084,-.102,.112,.024),(.001,-.115,.100,.023),(-.079,-.116,.079,.022),(-.155,-.143,.057,.019),(-.224,-.176,.027,.012),(-.251,-.172,.001,.002)]
        def rail(u,t,side=side):
            y,z,rx,rz=section(jaw,t);a=side*(u*math.pi);return (rx*math.sin(a),y,z+rz*math.cos(a))
        patch('swept lower jaw '+label,rail,'bill',nx=13,ny=37,thick=.0025)
        # Structural cheek arcs bound open voids; no flat black aperture decal.
        cheek=[(.145,-.018),(.115,-.057),(.060,-.087),(-.012,-.098),(-.080,-.086),(-.127,-.068)]
        def cheekrail(u,t,side=side):
            y,z=section(cheek,t);width=.012+.007*math.sin(math.pi*t)
            return (side*(.177-.018*t+.006*math.sin(math.pi*u)),y,z+(u-.5)*2*width)
        patch('open cheek arch '+label,cheekrail,nx=7,ny=25,thick=.004)
    def tube(name,points,r,role='bearing',region='head',tf=None):
        v=[];f=[];n=12
        for i,p in enumerate(points):
            p=Vector(p);t=(Vector(points[min(len(points)-1,i+1)])-Vector(points[max(0,i-1)])).normalized()
            u=t.cross(Vector((0,0,1)))
            if u.length<.01:u=t.cross(Vector((0,1,0)))
            u.normalize();w=t.cross(u).normalized()
            for k in range(n):v.append(p+r*(u*math.cos(k*2*math.pi/n)+w*math.sin(k*2*math.pi/n)))
        for j in range(len(points)-1):
            for k in range(n):f.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
        f.extend([tuple(range(n-1,-1,-1)),tuple((len(points)-1)*n+k for k in range(n))])
        return mesh(name,v,f,role,region,tf)
    # Two visible cheek tendons nested behind the rail, connecting machinery
    # to mandible. Their spacing leaves daylight through the cheek opening.
    for side,label in ((-1,'L'),(1,'R')):
        for k in range(2):
            pts=[(side*(.146-k*.008),.12-.34*t,-.060-.097*t-.018*math.sin(math.pi*t)) for t in [i/28 for i in range(29)]]
            tube('jaw tendon '+label+' '+str(k),pts,.004,'inner')
    identity=Matrix.Identity(4)
    def neckcenter(t):
        p=root.lerp(top,t);p.y+=.053*math.sin(math.pi*t);return p
    def necksurface(t,a,extra=0):
        t=max(0,min(1,t));p=neckcenter(t);rx=.123-.032*math.sin(math.pi*t)-.009*t;ry=.115-.014*math.sin(math.pi*t)+.002*t
        return p+Vector(((rx+extra)*math.sin(a),-(ry+extra)*math.cos(a),0))
    # Inner spine is narrow, leaving genuine openings between shell and rods.
    tube('curved cervical spine',[neckcenter(i/30) for i in range(31)],.060,'inner','neck',identity)
    for course in range(6):
        upper_t=1.10-course*.17
        for col,ac in enumerate((-.72,0,.72,2.48,3.14,3.80)):
            def leaf(u,t,ac=ac,upper_t=upper_t,course=course):
                tt=max(0,min(1,upper_t-.27*t));width=.41*(1-.94*t*t)
                p=necksurface(tt,ac+(u-.5)*2*width,.006+.006*math.sin(math.pi*t))
                p.z-=.008*t*t;return p
            patch('curved cervical leaf %d %d'%(course,col),leaf,'plate','neck',identity,nx=7,ny=17,thick=.003)
    # Large joint journals and smooth linkage rods inhabit the two side slots.
    # They are connected construction, not scattered screws on flat armor.
    for side,label in ((-1,'L'),(1,'R')):
        for k in range(3):
            pts=[]
            for j in range(31):
                t=.02+.94*j/30;p=neckcenter(t);p.x=side*(.081+k*.010);p.y+=(-.022+k*.026)+.008*math.sin(math.pi*t);pts.append(p)
            tube('exposed curved neck linkage '+label+' '+str(k),pts,.005 if k==1 else .004,'bearing','neck',identity)
        for j in range(3):
            t=.2+j*.28;p=neckcenter(t);p.x=side*.105
            # Journal axis is transverse; annular rings have actual holes.
            tf=Matrix.Translation(p)@Matrix.Rotation(side*math.pi/2,4,'Y')
            def journal(u,t):
                a=t*2*math.pi;r=.010+u*.009;return (r*math.cos(a),r*math.sin(a),.005*math.sin(math.pi*u))
            patch('cervical journal '+label+' '+str(j),journal,'bearing','neck',tf,nx=5,ny=33,thick=.003)
    # Retained optics obey era canon when this module is used on the posed
    # Advanced input for another era. No all-over recoloring is performed.
    optical_materials={}
    for o in originals:
        if o.hide_render or not o.get('cg2bFace'):continue
        if not o.data.materials:continue
        old=o.data.materials[0]
        if 'amber' not in old.name:continue
        if old.name not in optical_materials:
            m=old.copy();m.name='CGH01 '+old.name+' '+era;bs=m.node_tree.nodes.get('Principled BSDF')
            if era!='builder':
                bs.inputs['Emission Strength'].default_value=0;bs.inputs['Base Color'].default_value=(.008,.012,.009,1)
            optical_materials[old.name]=m
        o.data.materials[0]=optical_materials[old.name]
    bpy.context.view_layer.update()
    return dict(module='cg-supervised-head-neck',era=era,hiddenRetainedMeshes=hidden,newMeshCount=len(made),
        neckRoot=list(root),neckHead=list(top),headFrame=[list(r) for r in frame],
        changes=['Interlocking swept crown and nape leaves','Open cheek arch and linked lower mandible','Unequal deep hooked bill plates rooted into forehead','Curved layered neck with open side slots and connected linkages'],
        sourcePreserved=True,bodyAndStanceChanged=False,limits=['Inferred back surfaces and construction','Source camera remains estimate','Owner likeness acceptance pending','No engineering or browser parity claim'])
