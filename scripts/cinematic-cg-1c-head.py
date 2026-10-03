"""Study05-anchored CG head/neck. No scene reset, cameras, export or I/O at import."""
import math,json
from pathlib import Path
import bpy
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    path=Path(scaffold_path) if scaffold_path else Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/basic-shape-study05/study.json')
    if path.is_dir():path=path/'study.json'
    if path.suffix=='.blend':path=path.with_name('study.json')
    study=json.loads(path.read_text());shapes={x['name']:x for x in study['shapes']}
    head=next(x for x in study['shapes'] if x['type']=='continuous-rounded-head')
    bill=next(x for x in study['shapes'] if x['type']=='hooked-bill-cage')
    added=[];hidden=[]
    for o in list(scene.objects):
        if o.type=='MESH' and (o.name.startswith(('H01','H03','N01','N02')) or o.get('part') in ('head','neck')):
            o.hide_render=True;o.hide_viewport=True;o['cg1cSuperseded']=True;hidden.append(o.name)
    def tag(o,region,role):
        o['cg1cRegion']=region;o['region']=region;o['surfaceRole']=role
        o['exteriorEras']='maker,mechanic,builder';o['cgVisualStudy']=True
        added.append(o.name);return o
    def mesh(name,v,f,region='head',role='plate',smooth=True):
        d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update()
        o=bpy.data.objects.new('CG1c '+name,d);scene.collection.objects.link(o);tag(o,region,role)
        for p in d.polygons:p.use_smooth=smooth
        return o
    def section_at(sec,y):
        for a,b in zip(sec,sec[1:]):
            if min(a[0],b[0])<=y<=max(a[0],b[0]):
                t=(y-a[0])/(b[0]-a[0]);return [a[k]*(1-t)+b[k]*t for k in range(1,4)]
        return sec[0][1:] if y>sec[0][0] else sec[-1][1:]
    def surface(y,a,offset=0):
        z,rx,rz=section_at(head['sections'],y)
        return Vector(((rx+offset)*math.sin(a),y,z+(rz+offset)*math.cos(a)))
    def loft(name,sec,role):
        # Higher radial resolution and smooth normals retain the exact study05
        # ring envelope; all shape-section anchors remain untransformed.
        rings=[]
        for a,b in zip(sec,sec[1:]):
            for j in range(4):
                t=j/4;rings.append([a[k]*(1-t)+b[k]*t for k in range(4)])
        rings.append(sec[-1]);v=[];n=48
        for y,z,rx,rz in rings:v.extend([(rx*math.sin(i*2*math.pi/n),y,z+rz*math.cos(i*2*math.pi/n)) for i in range(n)])
        f=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rings)-1) for i in range(n)]
        f.extend([tuple(range(n-1,-1,-1)),tuple((len(rings)-1)*n+i for i in range(n))])
        return mesh(name,v,f,role=role)
    loft('continuous skull dark cavity back',head['sections'],'inner')
    loft('deep segmented hooked bill',bill['sections'],'bill')
    def tube(name,points,radius,region='head',role='edge'):
        # Exportable mesh tube; no curve dependency in final GLB.
        vv=[];n=8
        for i,p in enumerate(points):
            p=Vector(p);t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
            t.normalize();ref=Vector((1,0,0)) if abs(t.x)<.9 else Vector((0,1,0))
            u=t.cross(ref).normalized();w=t.cross(u).normalized()
            vv.extend([p+radius*(u*math.cos(a*2*math.pi/n)+w*math.sin(a*2*math.pi/n)) for a in range(n)])
        f=[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(points)-1) for j in range(n)]
        return mesh(name,vv,f,region,role)
    def rivet(name,p,region='head',radius=.0035):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=radius,location=p)
        o=bpy.context.object;o.name='CG1c '+name;tag(o,region,'rivet');return o
    def ring(name,p,r,t,role='bearing'):
        bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=48,minor_segments=8,location=p,rotation=(0,math.pi/2,0))
        o=bpy.context.object;o.name='CG1c '+name;tag(o,'head',role)
        for poly in o.data.polygons:poly.use_smooth=True
        return o
    # Engraved/readable bill boundaries follow its original hook; raised seams
    # are a visual CG shorthand that does not change bill length or position.
    for j,(y,z,rx,rz) in enumerate(bill['sections'][1:-1]):
        pts=[((rx+.001)*math.sin(a*2*math.pi/48),y,z+(rz+.001)*math.cos(a*2*math.pi/48)) for a in range(49)]
        tube('bill engraved course '+str(j),pts,.0015,role='inner')
    for side in (-1,1):
        pts=[]
        for y,z,rx,rz in bill['sections'][:-1]:
            pts.append((side*rx*.90,y,z+rz*.40))
        tube('bill fine side seam '+str(side),pts,.0013,role='edge')
        for j,(y,z,rx,rz) in enumerate(bill['sections'][:3]):rivet('bill fastener %s %s'%(side,j),(side*(rx+.003),y,z+.016),radius=.003)
    # Swept curved crown shingles lie directly on the locked scaffold skull.
    # Each plate is a small surface grid, not a flat cut-out or large helmet.
    for row in range(5):
        yc=-.37+row*.066
        for col in range(7):
            ac=(col-3)*.34+(row%2)*.04;v=[];nu=5;nv=6
            for j in range(nv):
                t=j/(nv-1);y=min(.026,yc-.042+t*.093)
                width=.20*(1-.68*t*t)
                for i in range(nu):
                    a=ac+(i/(nu-1)-.5)*2*width
                    p=surface(y,a,.003+.007*math.sin(math.pi*t)*math.sin(math.pi*i/(nu-1)))
                    v.append(p)
            f=[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(nv-1) for i in range(nu-1)]
            o=mesh('swept crown scale %s %s'%(row,col),v,f)
            m=o.modifiers.new('small plate return','SOLIDIFY');m.thickness=.002
            rivet('crown fastener %s %s'%(row,col),surface(yc-.030,ac,.008),radius=.0028)
    # Side nape courses continue the swept crown into a plated rear skull.
    for side in (-1,1):
        for row in range(4):
            yc=-.13+row*.040
            for col in range(3):
                ac=side*(1.10+col*.33);v=[];nu=5;nv=5
                for j in range(nv):
                    t=j/(nv-1);y=min(.035,yc-.046+t*.073)
                    width=.22*(1-.65*t*t)
                    for i in range(nu):
                        angle=ac+(i/(nu-1)-.5)*2*width
                        v.append(surface(y,angle,.004+.005*math.sin(math.pi*t)))
                f=[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(nv-1) for i in range(nu-1)]
                o=mesh('swept nape scale %s %s %s'%(side,row,col),v,f)
                m=o.modifiers.new('plate return','SOLIDIFY');m.thickness=.002
                rivet('nape fastener',surface(yc-.027,ac,.010),radius=.0028)
    # Small temple overlaps run behind the optic into the existing nape,
    # leaving the lower-forward cheek cavity exposed and the eye clear.
    for side in (-1,1):
        for row in range(3):
            for col in range(2):
                yc=-.212+col*.070;ac=side*(1.38+row*.26);v=[];nu=5;nv=5
                for j in range(nv):
                    t=j/(nv-1);y=yc-.038+t*.080
                    w=.19*(1-.65*t*t)
                    for i in range(nu):
                        v.append(surface(y,ac+(i/(nu-1)-.5)*2*w,.006+.005*math.sin(math.pi*t)))
                f=[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(nv-1) for i in range(nu-1)]
                o=mesh('temple overlap %s %s %s'%(side,row,col),v,f)
                o.modifiers.new('temple plate return','SOLIDIFY').thickness=.002
                rivet('temple fastener',surface(yc-.026,ac,.013),radius=.003)
    # Circular optics are seated on either side, with shadow behind the bezel.
    for side in (-1,1):
        p=(side*.177,-.305,1.65)
        for j,(r,t,x,role) in enumerate(((.058,.006,.176,'inner'),(.053,.004,.185,'bearing'),(.039,.0025,.190,'edge'))):
            ring('optic ring %s %s'%(side,j),(side*x,p[1],p[2]),r,t,role)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(side*.188,p[1],p[2]))
        o=bpy.context.object;o.name='CG1c recessed optic '+str(side);o.scale=(.003,.033,.033);tag(o,'head','optic')
        o['opticEra']=era;o['opticCanon']='dark maker/mechanic; restrained awakened orange builder'
        # Fine iris rings sit within the original lens diameter. Their
        # metallic/dark roles keep the detail readable in all three eras.
        for j,(rr,role) in enumerate(((.027,'edge'),(.018,'bearing'),(.009,'inner'))):
            ring('iris concentric %s %s'%(side,j),(side*.192,p[1],p[2]),rr,.0012,role)
        for j in range(12):
            a=j*math.pi/6
            tube('iris radial engraving %s %s'%(side,j),[
                (side*.1925,p[1]+.020*math.cos(a),p[2]+.020*math.sin(a)),
                (side*.1925,p[1]+.026*math.cos(a),p[2]+.026*math.sin(a))],.0007,role='inner')
        # Broad but shallow orbital brow strip curves along the skull's
        # lateral surface; it replaces the suspended bent-tube silhouette.
        v=[];nu=15
        for i in range(nu):
            y=-.399+i*.174/(nu-1);cz,rx,rz=section_at(head['sections'],y)
            for j in range(3):
                z=1.692+.026*math.sin(i*math.pi/(nu-1))+j*.010
                x=rx*math.sqrt(max(.06,1-((z-cz)/rz)**2))+.005
                v.append((side*x,y,z))
        f=[(i*3+j,(i+1)*3+j,(i+1)*3+j+1,i*3+j+1) for i in range(nu-1) for j in range(2)]
        o=mesh('scaffold curved brow plate '+str(side),v,f)
        o.modifiers.new('orbital plate return','SOLIDIFY').thickness=.003
        tube('cheek fine orbital rim '+str(side),[(side*.174,-.405,1.567),(side*.174,-.35,1.558),(side*.174,-.28,1.549),(side*.174,-.23,1.570)],.004,role='edge')
        ring('cheek machinery bearing '+str(side),(side*.164,-.202,1.59),.025,.004)
        tube('lower cheek jaw '+str(side),[(side*.133,-.205,1.54),(side*.145,-.285,1.505),(side*.105,-.37,1.493),(side*.075,-.435,1.465)],.014,role='plate')
        for y,z in ((-.237,1.717),(-.36,1.733),(-.27,1.549)):
            cz,rx,rz=section_at(head['sections'],y)
            xx=rx*math.sqrt(max(.06,1-((z-cz)/rz)**2))+.009
            rivet('orbital fastener',(side*xx,y,z))
    # Short thick cervical path uses the two original capsule anchors.
    pathpts=[Vector((0,-.105,1.30)),Vector((0,-.15,1.425)),Vector((0,-.23,1.495))]
    def neckpoint(t,a,r):
        if t<.58:p=pathpts[0].lerp(pathpts[1],t/.58)
        else:p=pathpts[1].lerp(pathpts[2],(t-.58)/.42)
        return p+Vector((r*math.sin(a),-r*math.cos(a),0))
    tube('cervical dark inner path',pathpts,.080,'neck','inner')
    for row in range(5):
        t=.04+row*.205;r=.118-row*.003
        for col in range(10):
            ac=(col+(row%2)*.5)*2*math.pi/10;v=[];nu=5;nv=5
            for j in range(nv):
                q=j/(nv-1);tt=max(0,min(1,t+(q-.5)*.27));w=.32*(1-.6*q*q)
                for i in range(nu):
                    a=ac+(i/(nu-1)-.5)*w*2
                    v.append(neckpoint(tt,a,r+.006*math.sin(math.pi*q)))
            f=[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(nv-1) for i in range(nu-1)]
            o=mesh('cervical overlap %s %s'%(row,col),v,f,'neck','plate')
            m=o.modifiers.new('plate thickness','SOLIDIFY');m.thickness=.002
            rivet('neck fastener %s %s'%(row,col),neckpoint(max(0,t-.07),ac,r+.005),'neck',.003)
    return {'module':'cinematic-cg-1c-head','scaffoldRevision':study.get('revision'),
        'generatedMeshCount':len(added),'hiddenSourceCount':len(hidden),'hiddenSourceNames':hidden,
        'headLocationDelta':[0,0,0],'headSizeMultiplier':1,'neckAnchorDelta':[0,0,0],
        'scope':'continuous scaffold cages; bill seams, recessed optics, crown/cervical overlaps, cheek machinery',
        'limits':['Unseen surfaces inferred','Skull cavity back is a visual simplification','Plate skins intersect intentionally','No owner likeness acceptance claimed']}
