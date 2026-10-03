"""Editable Milestone 2b facial mechanisms; inferred CG construction, not engineering.
Runs after cinematic-cg-2b-head.py. Original receiving floors are hidden only;
no cranial, bill, crown, stance or source-reference mesh is altered.
"""
import math
import bpy
from mathutils import Matrix, Vector


def apply(scene, scaffold_path=None, era='builder'):
    original=list(scene.objects)
    names=('CG2b head frame','CG2b optic L','CG2b optic R','CG2b cheek L',
           'CG2b cheek R','CG2b brow L','CG2b brow R','CG2b neck root','CG2b neck head')
    anchors={n:scene.objects.get(n) for n in names}
    missing=[n for n,o in anchors.items() if o is None or o.type!='EMPTY']
    if missing:raise RuntimeError('Face requires unchanged 2b head anchors: '+', '.join(missing))
    if any(o.get('cg2bFace') for o in original):
        raise RuntimeError('Face already applied; reload preserved source for another study')
    frame=anchors['CG2b head frame'].matrix_world.copy()
    inherited={}
    for o in original:
        if o.type=='MESH' and o.get('cg1cRegion') in ('head','neck') and o.data.materials:
            inherited.setdefault(o.get('surfaceRole'),o.data.materials[0])
    hidden=[];made=[];counts={};custom={}
    for o in original:
        if o.get('cg2bReceivingFloor'):
            o.hide_render=True;o.hide_set(True);o['cg2bFaceSuperseded']=True;hidden.append(o.name)
    def optical_material(name,color,metal,rough,emission=0,glass=False):
        m=bpy.data.materials.new('CG2b '+name+' '+era);m.use_nodes=True
        p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
        p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        if glass:
            p.inputs['Transmission Weight'].default_value=.96
            p.inputs['IOR'].default_value=1.48;p.inputs['Coat Weight'].default_value=.75
            p.inputs['Coat Roughness'].default_value=.045
        p.inputs['Emission Color'].default_value=(1,.21,.014,1)
        p.inputs['Emission Strength'].default_value=emission
        m['cg2bFaceMaterial']=True;m['cg2aPreserveMaterial']=True
        custom[name]=m;return m
    awake=era=='builder'
    amber=optical_material('amber lens core',(.26,.058,.004) if awake else (.008,.011,.009),.15,.14,.85 if awake else 0)
    coil=optical_material('amber recessed turns',(.14,.034,.003) if awake else (.014,.015,.012),.50,.22,.18 if awake else 0)
    smoked=optical_material('optical smoked glass',(.64,.39,.16) if awake else (.065,.080,.073),0,.075,glass=True)
    aperture=optical_material('blackened optical aperture',(.015,.022,.019),.85,.32)
    def mesh(name,verts,faces,role='armor',region='head',transform=None,material=None,smooth=False):
        d=bpy.data.meshes.new('CG2b face '+name);d.from_pydata(verts,[],faces);d.update()
        o=bpy.data.objects.new('CG2b face '+name,d);scene.collection.objects.link(o)
        o.matrix_world=transform.copy() if transform is not None else frame.copy()
        o['cg1cRegion']=region;o['cg2bRegion']=region;o['surfaceRole']=role
        o['cg2bFace']=True;o['exteriorEras']='maker,mechanic,builder'
        o['cg2bConstruction']='inferred facial hardware CG proposal'
        m=material or inherited.get(role) or inherited.get('plate' if role=='armor' else role) or inherited.get('bearing')
        if m:o.data.materials.append(m)
        if material:o['cg2aPreserveMaterial']=True
        uv=d.uv_layers.new(name='cg2b-face-uv')
        # Explicit radial/projected UV coordinates, independent of source art.
        for f in d.polygons:
            f.use_smooth=smooth
            for li in f.loop_indices:
                v=d.vertices[d.loops[li].vertex_index].co
                uv.data[li].uv=(.5+v.x*3,.5+v.y*3)
        made.append(o);counts[role]=counts.get(role,0)+1;return o
    def bevel(o,width=.001,segments=2):
        b=o.modifiers.new('machined softened edge','BEVEL');b.width=width;b.segments=segments
        return o
    def tube(name,points,radius,role='bearing',transform=None,region='head',material=None,sides=8):
        v=[];f=[]
        for i,p in enumerate(points):
            p=Vector(p);a=Vector(points[max(0,i-1)]);b=Vector(points[min(len(points)-1,i+1)])
            t=(b-a).normalized();u=t.cross(Vector((0,0,1)))
            if u.length<.01:u=t.cross(Vector((0,1,0)))
            u.normalize();w=t.cross(u).normalized()
            for j in range(sides):
                q=2*math.pi*j/sides;v.append(p+radius*(math.cos(q)*u+math.sin(q)*w))
        for i in range(len(points)-1):
            for j in range(sides):f.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
        f.extend([tuple(range(sides-1,-1,-1)),tuple((len(points)-1)*sides+i for i in range(sides))])
        return mesh(name,v,f,role,region,transform,material,True)
    def arc(name,r,z,start,end,t,role='bearing',transform=None,material=None):
        n=max(12,int(abs(end-start)*20));points=[]
        for i in range(n+1):
            a=start+(end-start)*i/n;points.append((r*math.cos(a),r*math.sin(a),z))
        return tube(name,points,t,role,transform,material=material,sides=10)
    def radial_shell(name,rings,transform,role='bearing',material=None,n=80,front=False):
        v=[(r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for r,z in rings for i in range(n)]
        f=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rings)-1) for i in range(n)]
        if front or rings[-1][0]>rings[0][0]:f=[tuple(reversed(poly)) for poly in f]
        return mesh(name,v,f,role,transform=transform,material=material,smooth=True)
    def disc(name,r,z,transform,role='bearing',material=None,n=64):
        v=[(0,0,z)]+[(r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for i in range(n)]
        return mesh(name,v,[(0,i+1,(i+1)%n+1) for i in range(n)],role,transform=transform,material=material,smooth=True)
    def bolt(name,center,radius,transform,region='head'):
        tf=transform@Matrix.Translation(Vector(center));r=radius
        radial_shell(name+' recessed washer',[(r*1.35,-.0004),(r*1.35,.0008),(r,.0012)],tf,'bearing',n=24)
        radial_shell(name+' hex head',[(r,.0005),(r,.0023),(r*.64,.0023)],tf,'rivet',n=6)
        disc(name+' black hex socket',r*.47,.00235,tf,'inner',aperture,n=6)
    def head_plate(name,yz,x,side,role='armor',thickness=.003):
        v=[(side*x,y,z) for y,z in yz]
        o=mesh(name,v,[tuple(range(len(v)))],role)
        o.modifiers.new('formed plate thickness','SOLIDIFY').thickness=thickness
        bevel(o,.0012);return o
    # Each optic is a stepped blackened cup with aperture vanes and actual
    # curved glass. It occupies the existing .050 radius receiver only.
    for side,label in ((-1,'L'),(1,'R')):
        tf=anchors['CG2b optic '+label].matrix_world.copy()
        rad=float(anchors['CG2b optic '+label].get('opticOuterRadius',.050))
        sc=rad/.050
        radial_shell('optic deep socket '+label,[(.050,.000),(.050,.003),(.047,.006),(.042,.006),(.037,-.001),(.031,-.004),(.010,-.004)],tf,'inner',aperture)
        radial_shell('optic stepped metal seat '+label,[(.049,.001),(.049,.007),(.045,.008),(.043,.006),(.043,.003)],tf,'bearing')
        arc('optic worn inner rim '+label,.0385,.003,0,2*math.pi,.00115,'edge',tf)
        arc('optic outer silver seam '+label,.048,.007,0,2*math.pi,.00065,'edge',tf)
        # Broken interlocking retaining rings avoid a flat target/logo pattern.
        for j in range(3):
            for k in range(3):
                a=k*2*math.pi/3+j*.12
                arc('optic split retaining ring %s %s %s'%(label,j,k),.040+j*.002,.005+j*.0003,a,a+1.70,.00075,'bearing',tf)
        for j in range(7):
            a=j*2*math.pi/7;v=[]
            for r,q in ((.020,a+.05),(.030,a-.10),(.036,a+.20),(.035,a+.71),(.026,a+.80),(.020,a+.40)):
                v.append((r*math.cos(q),r*math.sin(q),.0004+(j%2)*.00035))
            o=mesh('overlapping optical aperture blade %s %s'%(label,j),v,[(0,1,2,3,4,5)],'bearing',transform=tf,material=aperture)
            o.modifiers.new('aperture blade metal','SOLIDIFY').thickness=.0005
        # Convex core is dark at early eras and selectively amber in Advanced.
        radial_shell('curved iris core '+label,[(0,.0000),(.003,-.0001),(.006,-.0006),(.009,-.0014),(.012,-.003)],tf,'optic',amber)
        for course,r in enumerate((.0145,.0190,.0260)):
            for k in range(3):
                a=k*2*math.pi/3+course*.29
                arc('subglass concentric broken coil %s %s %s'%(label,course,k),r,-.0020-course*.00035,a,a+1.65-course*.12,.00055+course*.00010,'optic',tf,coil)
        # Closed lens with outward front normals and inward-facing rear normals.
        # Its convex curvature catches the shared key light physically.
        rings=[]
        for j in range(17):
            r=.032*j/16;z=.0125-.0120*(j/16)**2;rings.append((r,z))
        rings.extend([(.032,-.0007),(.024,-.0010),(.016,-.0014),(.008,-.0017),(0,-.0018)])
        radial_shell('convex recessed optical glass '+label,rings,tf,'optic',smoked,front=True)
        for j in range(8):
            a=j*2*math.pi/8+.20;bolt('socket lock %s %s'%(label,j),(.046*math.cos(a),.046*math.sin(a),.007),.0015,tf)
        # Curved orbital brow and under-eye plate follow the local skull.
        # They overlap as broad curved forms instead of repeated tiny widgets.
        for course in range(2):
            yz=[]
            for j in range(18):
                a=.06*math.pi+j*.83*math.pi/17
                yz.append((.003+.063*math.cos(a),.017+(.068+course*.008)*math.sin(a)))
            for j in range(17,-1,-1):
                a=.06*math.pi+j*.83*math.pi/17
                yz.append((.003+.049*math.cos(a),.017+(.052+course*.008)*math.sin(a)))
            head_plate('overhanging curved brow %s %s'%(label,course),yz,.194+course*.002,side)
        yz=[(-.082,.067),(-.061,.072),(-.045,.040),(-.033,-.021),(-.005,-.042),(.034,-.038),(.092,-.015),(.103,-.032),(.045,-.064),(-.010,-.058),(-.061,-.028)]
        head_plate('curved underoptic cheek spar '+label,yz,.183,side)
        head_plate('rear temple crescent '+label,[(.082,.087),(.135,.069),(.166,.028),(.155,-.039),(.125,-.077),(.114,-.052),(.134,-.014),(.126,.030),(.092,.063)],.174,side)
        # Thin irregular overlapping forehead plates follow the receiving
        # cranial surface rather than forming another smooth projecting band.
        skull=next((o for o in original if o.type=='MESH' and 'broad avian cranial shell' in o.name),None)
        if skull:
            local_vertices=[frame.inverted()@skull.matrix_world@v.co for v in skull.data.vertices if (frame.inverted()@skull.matrix_world@v.co).x*side>=0]
            def skin_x(y,z):
                closest=sorted(local_vertices,key=lambda v:(v.y-y)**2+(v.z-z)**2)[:4]
                weights=[1/max(.000005,(v.y-y)**2+(v.z-z)**2) for v in closest]
                return sum(abs(v.x)*w for v,w in zip(closest,weights))/sum(weights)+.004
            shapes=[
                [(-.048,.074),(-.080,.099),(-.122,.093),(-.148,.065),(-.133,.052),(-.090,.068)],
                [(-.044,.043),(-.081,.068),(-.126,.054),(-.145,.028),(-.127,.016),(-.080,.034)],
                [(-.048,.012),(-.083,.035),(-.132,.017),(-.146,-.008),(-.129,-.021),(-.080,.000)],
                [(-.023,.079),(-.007,.099),(.038,.104),(.083,.079),(.077,.066),(.035,.086)]]
            for course,yz_skin in enumerate(shapes):
                vv=[(side*skin_x(y,z),y,z) for y,z in yz_skin]
                pp=mesh('segmented forehead bridge %s %s'%(label,course),vv,[tuple(range(len(vv)))],'armor')
                pp.modifiers.new('thin formed bridge plate','SOLIDIFY').thickness=.0018;bevel(pp,.001)
                # Separate edge tracing exposes the irregular plate perimeter.
                tube('forehead bridge edge %s %s'%(label,course),vv+[vv[0]],.00055,'edge')
                for k in (1,4):
                    q=Vector(vv[k]);tf_skin=frame@Matrix.Translation(q)@Matrix.Rotation(side*math.pi/2,4,'Y')
                    bolt('forehead seam rivet %s %s %s'%(label,course,k),(0,0,.001),.0018,tf_skin)
        # Gear trains remain inside the known cheek aperture. Disc backs,
        # faceted tooth rims and layered hubs make machinery closed solids.
        cheek=anchors['CG2b cheek '+label].matrix_world.copy()
        for j,(u,v,r) in enumerate(((-.005,-.030,.023),(.013,.006,.018),(-.017,.036,.012))):
            gtf=cheek@Matrix.Translation(Vector((u,v,.012)))
            n=16 if j<2 else 12
            rings=[(r*.77,0),(r,0),(r,.004),(r*.79,.004),(r*.38,.004),(r*.35,.007)]
            radial_shell('cheek cog body %s %s'%(label,j),rings,gtf,'bearing',n=n*4)
            disc('cheek closed cog back %s %s'%(label,j),r*.8,.0004,gtf,'inner')
            # Alternating radii create an editable closed tooth belt.
            vv=[]
            for z in (.0005,.0045):
                for k in range(n*4):
                    a=k*2*math.pi/(n*4);rr=r*(1.13 if k%4 in (1,2) else .98);vv.append((rr*math.cos(a),rr*math.sin(a),z))
            ff=[(k,(k+1)%(n*4),(k+1)%(n*4)+n*4,k+n*4) for k in range(n*4)]
            mesh('cheek gear teeth %s %s'%(label,j),vv,ff,'bearing',transform=gtf)
            arc('cheek cog concentric hub %s %s'%(label,j),r*.40,.006,0,2*math.pi,.0015,'edge',gtf)
            bolt('cheek pivot %s %s'%(label,j),(0,0,.006),.003,gtf)
        # Closed dark cheek volume behind exposed gears; no open cavern mouth.
        yz=[(.118,-.057),(.085,-.065),(.027,-.090),(-.029,-.112),(-.015,-.122),(.064,-.123),(.124,-.086)]
        head_plate('closed cheek recess backing '+label,yz,.153,side,'inner',.002)
        head_plate('jaw hardware lower rail '+label,[(.130,-.086),(.095,-.119),(.029,-.130),(-.024,-.123),(-.035,-.132),(.025,-.145),(.108,-.135),(.147,-.098)],.165,side)
        # Cable sweeps run behind the cheek rails and stay compact.
        for j in range(3):
            pts=[]
            for k in range(22):
                t=k/21;pts.append((side*(.163-j*.006),.117-.140*t,-.063-.070*t-.009*math.sin(math.pi*t)))
            tube('nested cheek cable %s %s'%(label,j),pts,.0023,'inner')
        # Existing brow/cheek anchor orientations supply outward bolt axes.
        for j,(y,z) in enumerate(((-.064,.063),(-.039,-.018),(.036,-.050),(.100,-.027),(.121,.029),(.120,-.115),(.034,-.136))):
            btf=frame@Matrix.Translation(Vector((side*(.196 if j==0 else .185 if j<4 else .176 if j==4 else .168),y,z)))@Matrix.Rotation(side*math.pi/2,4,'Y')
            bolt('broad plate fastener %s %s'%(label,j),(0,0,0),.0026,btf)
        # Exposed temple drive pair behind eye, prominent in source face.
        for j,(y,z,r) in enumerate(((.092,.028,.014),(.116,.010,.010))):
            gtf=frame@Matrix.Translation(Vector((side*.183,y,z)))@Matrix.Rotation(side*math.pi/2,4,'Y')
            radial_shell('temple drive bearing %s %s'%(label,j),[(r,0),(r,.006),(r*.64,.007),(r*.44,.004)],gtf,'bearing',n=40)
            arc('temple drive edge %s %s'%(label,j),r*.70,.006,0,2*math.pi,.0014,'edge',gtf)
            bolt('temple drive axle %s %s'%(label,j),(0,0,.005),r*.24,gtf)
    # Compact dark throat cables and spine joints between existing neck anchors.
    root=anchors['CG2b neck root'].matrix_world.translation
    top=anchors['CG2b neck head'].matrix_world.translation
    ident=Matrix.Identity(4)
    for side,label in ((-1,'L'),(1,'R')):
        for j in range(2):
            pts=[]
            for k in range(25):
                t=.16+.70*k/24;p=root.lerp(top,t)
                p.x=side*(.106+j*.008);p.y+=.046+.010*math.sin(math.pi*t);pts.append(p)
            tube('cervical cable sweep %s %s'%(label,j),pts,.0032,'inner',ident,'neck')
        for j in range(3):
            t=.26+j*.22;p=root.lerp(top,t);p.x=side*.118;p.y+=.020
            tf=Matrix.Translation(p)@Matrix.Rotation(side*math.pi/2,4,'Y')
            radial_shell('neck exposed bearing %s %s'%(label,j),[(.012,0),(.012,.004),(.009,.005),(.005,.003)],tf,'bearing',n=32)
            bolt('neck journal %s %s'%(label,j),(0,0,.003),.003,tf,'neck')
            for o in made[-4:]:o['cg1cRegion']='neck';o['cg2bRegion']='neck'
    bpy.context.view_layer.update()
    return {'module':'cinematic-cg-2b-face','era':era,'newMeshes':len(made),'roleCounts':counts,
            'hiddenReceivingFloors':hidden,'originalMeshesDeleted':0,
            'anchorNames':list(names),'opticOuterRadius':.050,'glassClearRadius':.032,
            'opticCoreRadius':.012,'advancedCoreEmission':.85 if awake else 0,
            'advancedRingEmission':.18 if awake else 0,'headPoseDelta':[0,0,0],
            'sourcePreserved':True,'opticalMaterialPreservationFlag':'cg2aPreserveMaterial=True on glass, aperture, core and amber turns','lensConstruction':'closed convex lens, outward front/rear normals, physical key-light reflection','referenceUse':'Observed locked canon and July head identity; no source artwork as textures',
            'construction':'New layered orbital/cheek plates, closed concentric lenses, gear trains and compact cervical hardware are editable CG proposals',
            'limits':['Face geometry is inferred from reference appearance, not fabrication design',
                      'Glass native rendering verified separately; browser transmission parity requires integrator check',
                      'Owner artistic likeness acceptance remains pending']}
