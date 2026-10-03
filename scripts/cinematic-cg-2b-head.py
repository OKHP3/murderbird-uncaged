"""Milestone 2b avian head silhouette proposal from the posed 2a character.
The retained 2a meshes are hidden, never removed. Rebuilt forms are an editable
CG proposal guided by the locked full-bird canon and July HEAD only reference.
"""
import math
import bpy
from mathutils import Vector,Matrix


def apply(scene, scaffold_path=None, era='builder'):
    originals=list(scene.objects);materials={};hidden=[];added=[];anchors={}
    lenses=[o for o in originals if o.type=='MESH' and 'CG1c recessed optic' in o.name and not o.hide_render]
    if len(lenses)!=2:raise RuntimeError('2b head expects two posed 2a optic landmarks')
    frame=lenses[0].matrix_world.to_quaternion().to_matrix().to_4x4()
    frame.translation=(lenses[0].matrix_world.translation+lenses[1].matrix_world.translation)*.5
    for o in originals:
        if o.type=='MESH' and o.get('cg1cRegion') in ('head','neck'):
            if o.data.materials:materials.setdefault(o.get('surfaceRole'),o.data.materials[0])
            if not o.hide_render:hidden.append(o.name)
            o.hide_render=True;o.hide_set(True);o['cg2bSuperseded']=True
    def mesh(name,verts,faces,role='plate',region='head',transform=frame,smooth=True,uv=None):
        d=bpy.data.meshes.new('CG2b '+name);d.from_pydata(verts,[],faces);d.update()
        o=bpy.data.objects.new('CG2b '+name,d);scene.collection.objects.link(o);o.matrix_world=transform
        o['cg1cRegion']=region;o['cg2bRegion']=region;o['surfaceRole']=role
        o['exteriorEras']='maker,mechanic,builder';o['cg2bConstruction']='inferred avian silhouette proposal'
        mat=materials.get(role,materials.get('plate'))
        if mat:o.data.materials.append(mat)
        layer=d.uv_layers.new(name='cg2b-uv')
        for p in d.polygons:
            p.use_smooth=smooth
            for li in p.loop_indices:
                vi=d.loops[li].vertex_index;v=d.vertices[vi].co
                layer.data[li].uv=uv[vi] if uv else ((v.y+.65)/1.1,(v.z+.40)/.80)
        added.append(o);return o
    def catmull(a,b,c,d,t):
        return [(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t)*.5 for k in range(len(a))]
    def loft(name,sections,role='plate',region='head',transform=frame,radial=64):
        rings=[]
        for i in range(len(sections)-1):
            a=sections[max(0,i-1)];b=sections[i];c=sections[i+1];d=sections[min(len(sections)-1,i+2)]
            for j in range(6):
                q=catmull(a,b,c,d,j/6);q[2]=max(.001,q[2]);q[3]=max(.001,q[3]);rings.append(q)
        rings.append(sections[-1]);v=[];uv=[]
        for j,(y,z,rx,rz) in enumerate(rings):
            for i in range(radial):
                a=i*2*math.pi/radial;v.append((rx*math.sin(a),y,z+rz*math.cos(a)));uv.append((i/radial,j/(len(rings)-1)))
        f=[(j*radial+i,j*radial+(i+1)%radial,(j+1)*radial+(i+1)%radial,(j+1)*radial+i) for j in range(len(rings)-1) for i in range(radial)]
        f.extend([tuple(range(radial-1,-1,-1)),tuple((len(rings)-1)*radial+i for i in range(radial))])
        return mesh(name,v,f,role,region,transform,uv=uv)
    # Distinct rounded cranial mass and forehead step. The bill is a separate
    # deep convex hook, not a continuation of the forehead-to-nose taper.
    skull_sections=[(.245,-.035,.014,.020),(.205,0,.080,.085),(.155,.025,.135,.130),
        (.075,.035,.176,.150),(.005,.030,.187,.155),(-.080,.023,.170,.141),
        (-.145,.043,.129,.115),(-.174,.067,.084,.074)]
    skull=loft('broad avian cranial shell',skull_sections)
    upper_sections=[(-.145,.045,.108,.092),(-.215,.028,.100,.098),
        (-.278,-.035,.082,.088),(-.320,-.120,.057,.083),
        (-.333,-.209,.027,.061),(-.305,-.278,.0015,.003)]
    # Keep the separate upper hook, but shorten its forward projection about
    # the beak root: it should read as a predatory bill, not a giant toy snout.
    upper_sections=[(-.145+(y+.145)*.88,z,rx,rz) for y,z,rx,rz in upper_sections]
    bill=loft('deep upper hooked bill backing',upper_sections,'inner')
    lower_sections=[(.075,-.102,.117,.030),(.017,-.108,.109,.027),
        (-.066,-.097,.089,.022),(-.145,-.084,.064,.020),
        (-.228,-.137,.026,.012),(-.271,-.166,.0015,.002)]
    lower_sections=[(y if y>-.145 else -.145+(y+.145)*.88,z,rx,rz) for y,z,rx,rz in lower_sections]
    jaw=loft('separate upturned lower mandible',lower_sections,'bill')
    # Overlapping major bill sheets create actual longitudinal and diagonal
    # seams instead of coloring a single smooth toy-like hook. They sit only
    # .002 above the backing and keep the revised silhouette.
    def bill_point(t,angle,offset=.002):
        u=min(len(upper_sections)-1-1e-6,max(0,t*(len(upper_sections)-1)))
        j=int(u);q=catmull(upper_sections[max(0,j-1)],upper_sections[j],upper_sections[j+1],upper_sections[min(len(upper_sections)-1,j+2)],u-j)
        y,z,rx,rz=q
        return Vector(((rx+offset)*math.sin(angle),y,z+(rz+offset)*math.cos(angle)))
    for side,label in ((-1,'L'),(1,'R')):
        for course in range(3):
            for band in range(3):
                v=[];nx=8;ny=15
                for j in range(ny):
                    tt=j/(ny-1)
                    for i in range(nx):
                        aa=.06+band*(math.pi-.12)/3+i/(nx-1)*(math.pi-.12)/3
                        # Diagonal joints at course boundaries; all strips
                        # remain within the actual hook surface.
                        t=min(.988,max(.010,.01+(course+tt)*.325+.027*math.sin(aa)))
                        aa+=.006 if i==0 else -.006 if i==nx-1 else 0
                        v.append(bill_point(t,side*aa))
                f=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
                o=mesh('segmented bill sheet %s %s %s'%(label,course,band),v,f,'bill')
                o.modifiers.new('bill sheet return','SOLIDIFY').thickness=.0015
    # Wide temporal face landmarks and a dark cheek aperture framed by a thin
    # curved structural plate. The later facial worker owns the iris/hardware.
    for side,label in ((-1,'L'),(1,'R')):
        verts=[];count=48
        for i in range(count):
            a=i*2*math.pi/count
            for r in (.051,.075):
                y=.003+r*math.cos(a);z=.017+r*math.sin(a)
                x=side*(.187-.22*(y*y+z*z)+.005)
                verts.append((x,y,z))
        faces=[(2*i,2*((i+1)%count),2*((i+1)%count)+1,2*i+1) for i in range(count)]
        o=mesh('optic temple plate '+label,verts,faces,'plate')
        o.modifiers.new('temple plate return','SOLIDIFY').thickness=.003
        # A recessed eye floor gives the shape checkpoint a readable avian eye
        # without imposing the later glass or era-specific artistic treatment.
        verts=[(side*.187,.003,.017)]+[(side*.187,.003+.049*math.cos(i*2*math.pi/48),.017+.049*math.sin(i*2*math.pi/48)) for i in range(48)]
        o=mesh('optic receiving floor '+label,verts,[(0,i+1,(i+1)%48+1) for i in range(48)],'inner')
        o['cg2bReceivingFloor']=True
        # Flattened cheek recess is below and behind the eye, distinct from the
        # bill-root. Its aperture/back is explicit for the facial worker.
        yz=[(.113,-.040),(.045,-.070),(-.040,-.106),(-.026,-.141),(.070,-.137),(.137,-.081)]
        v=[(side*.153,y,z) for y,z in yz]
        o=mesh('cheek aperture shadow '+label,v,[(0,1,2,3,4,5)],'inner')
        o['cg2bCheekCavity']=True
        rim=[]
        for j,(y,z) in enumerate(yz):
            cy=.05;cz=-.09
            for scale in (1,1.14):rim.append((side*.159,cy+(y-cy)*scale,cz+(z-cz)*scale))
        faces=[(2*i,2*((i+1)%6),2*((i+1)%6)+1,2*i+1) for i in range(6)]
        o=mesh('curved cheek and jaw receiver '+label,rim,faces,'plate')
        o.modifiers.new('formed cheek return','SOLIDIFY').thickness=.004
    # Swept tapered crown scales emphasize a rear-flowing bird crown rather
    # than a spherical armored mammal skull. Only major layering is supplied.
    def surface(y,angle,extra=0):
        sec=skull_sections
        if y>=sec[0][0]:q=sec[0]
        elif y<=sec[-1][0]:q=sec[-1]
        else:
            for a,b in zip(sec,sec[1:]):
                if b[0]<=y<=a[0]:
                    t=(y-a[0])/(b[0]-a[0]);q=[a[k]*(1-t)+b[k]*t for k in range(4)];break
        return Vector(((q[2]+extra)*math.sin(angle),y,q[1]+(q[3]+extra)*math.cos(angle)))
    for course in range(3):
        yc=-.025+course*.074
        for col in range(7):
            center=(col-3)*.32;v=[];nx=5;ny=8
            for j in range(ny):
                t=j/(ny-1);y=yc-.047+t*.135
                width=.24*(1-.82*t*t)
                for i in range(nx):
                    a=center+(i/(nx-1)-.5)*2*width
                    p=surface(min(.231,y),a,.008+.006*math.sin(math.pi*t))
                    # Rear tip sails backwards instead of wrapping down into
                    # the skull, creating the swept canon crest silhouette.
                    if y>.202:p.y=y+.028*t;p.z+=.038*t
                    v.append(p)
            f=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
            o=mesh('swept crown armor %02d %02d'%(course,col),v,f,'plate')
            o.modifiers.new('crown sheet thickness','SOLIDIFY').thickness=.0025
    # Side nape feather plates continue the swept crown around the broad
    # rear skull, removing the bare toy-helmet flank without widget detail.
    for side,label in ((-1,'L'),(1,'R')):
        for course in range(4):
            yc=.100+course*.035
            for col in range(4):
                ac=side*(1.10+col*.31);v=[];nx=5;ny=7
                for j in range(ny):
                    t=j/(ny-1);y=min(.242,yc-.028+t*.099)
                    width=.225*(1-.97*t*t)
                    for i in range(nx):
                        aa=ac+(i/(nx-1)-.5)*2*width
                        v.append(surface(y,aa,.004+.005*math.sin(math.pi*t)))
                f=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
                o=mesh('swept nape side %s %s %s'%(label,course,col),v,f,'plate')
                o.modifiers.new('nape formed sheet','SOLIDIFY').thickness=.0025
    # Neck uses the previously approved shoulder/root and head-junction anchor.
    # An avian thick rear neck, not a stretched hose or mammalian muzzle neck.
    neck_root=Vector((0,-.105,1.30));neck_head=frame@Vector((0,.145,-.10))
    neck_sections=[]
    for j in range(9):
        t=j/8;p=neck_root.lerp(neck_head,t)
        # loft's axis is Y, so construct the vertical neck separately below.
        neck_sections.append((p,.115-.015*t))
    v=[];count=48
    for p,r in neck_sections:
        for i in range(count):
            a=i*math.pi/24;v.append((r*math.sin(a),p.y-r*math.cos(a),p.z))
    f=[(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(8) for i in range(count)]
    neck=mesh('short continuous cervical inner',v,f,'inner','neck',Matrix.Identity(4))
    # Sparse, broad overlapping cervical courses; small machinery belongs to
    # the later head/neck hardware pass, not this silhouette correction.
    for course in range(4):
        t=.15+course*.225;p=neck_root.lerp(neck_head,t);r=.120-.015*t
        for col in range(8):
            ac=(col+(course%2)*.5)*math.pi/4;v=[];nx=5;ny=6
            for j in range(ny):
                q=j/(ny-1);tt=min(1,max(0,t+(q-.5)*.30));center=neck_root.lerp(neck_head,tt)
                width=.45*(1-.6*q*q)
                for i in range(nx):
                    a=ac+(i/(nx-1)-.5)*2*width
                    rr=r+.005*math.sin(math.pi*q)
                    v.append((rr*math.sin(a),center.y-rr*math.cos(a),center.z))
            f=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
            o=mesh('cervical scale %02d %02d'%(course,col),v,f,'plate','neck',Matrix.Identity(4))
            o.modifiers.new('neck sheet thickness','SOLIDIFY').thickness=.003
    def anchor(name,local,side=None,world=False):
        o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.empty_display_type='ARROWS';o.empty_display_size=.03
        if world:o.matrix_world=Matrix.Translation(Vector(local))
        else:
            o.matrix_world=frame@Matrix.Translation(Vector(local))
            if side is not None:o.matrix_world=o.matrix_world@Matrix.Rotation(side*math.pi/2,4,'Y')
        o['cg2bAnchor']=True;o['cg1cRegion']='head' if 'neck root' not in name else 'neck'
        anchors[name]=[round(x,6) for x in o.matrix_world.translation]
        return o
    anchor('CG2b head frame',(0,0,0))
    for side,label in ((-1,'L'),(1,'R')):
        o=anchor('CG2b optic '+label,(side*.194,.003,.017),side);o['opticOuterRadius']=.050;o['opticCoreMaxRadius']=.030
        anchor('CG2b cheek '+label,(side*.151,.055,-.090),side)
        anchor('CG2b brow '+label,(side*.172,-.027,.092),side)
    anchor('CG2b neck root',neck_root,world=True);anchor('CG2b neck head',neck_head,world=True)
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(p) for o in added for p in o.bound_box]
    bounds=[[round(min(p[k] for p in pts),6) for k in range(3)],[round(max(p[k] for p in pts),6) for k in range(3)]]
    return {'module':'cinematic-cg-2b-head','source':'3df3cb18ebdcdc522eb6a388a170df912b299d89',
        'hiddenOriginalMeshes':len(hidden),'addedMeshes':len(added),'anchors':anchors,'headNeckBounds':bounds,
        'upperBillTipWorld':list(frame@Vector((0,upper_sections[-1][0],upper_sections[-1][1]))),
        'hookProjectionMultiplier':.88,'jawRevision':'raised compact mandible; deliberate dark mouth slit',
        'lowerJawTipWorld':list(frame@Vector((0,lower_sections[-1][0],lower_sections[-1][1]))),
        'changes':['Distinct deeper hooked upper bill and separate upturned lower mandible','Broad cranial and optic-temple mass with forehead step','Swept crown instead of round cap','Dark cheek aperture and shorter thick mechanical neck'],
        'deviations':['Rebuilt cranial/bill envelope deliberately replaces rejected 2a snout','Major source landmarks are retained as posed starting frame; exact skull shape is a new CG proposal'],
        'limits':['No facial iris/glass or extensive machinery in this form pass','Hidden rear surfaces inferred','Owner artistic acceptance still required']}
