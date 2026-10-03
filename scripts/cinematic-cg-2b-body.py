"""Segmented avian breast and retained compact keel; body-only CG construction.
Source body objects are kept hidden. No camera, stance, light or material nodes change.
"""
import math, random
import bpy
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    if any(o.get('cg2bBodyOwner') for o in scene.objects):
        return {'module':'cg2b-body','disposition':'already applied; no duplicate construction'}
    rng=random.Random(2048)
    originals=[o for o in scene.objects if o.get('cg1cRegion')=='body' and not o.get('cg2bRegion')]
    materials={}
    for o in originals:
        if o.type=='MESH' and o.data.materials:
            materials.setdefault(o.get('surfaceRole'),list(o.data.materials))
    source_bounds=[]
    for o in originals:
        if o.type=='MESH' and not o.hide_render:
            source_bounds.extend([o.matrix_world@Vector(v) for v in o.bound_box])
        o['cg2bBodySourceRetained']=True;o.hide_render=True;o.hide_set(True)
    coll=bpy.data.collections.new('CG2b segmented breast and posterior keel');scene.collection.children.link(coll)
    counts={};created=[]
    def objmesh(name,vs,fs,uv,role,smooth=True):
        data=bpy.data.meshes.new(name);data.from_pydata([tuple(v) for v in vs],[],fs);data.update()
        obj=bpy.data.objects.new(name,data);coll.objects.link(obj)
        obj['cg1cRegion']='body';obj['cg2bRegion']='body';obj['cg2bBodyOwner']=True
        obj['surfaceRole']=role;obj['exteriorEras']='maker,mechanic,builder'
        key='plate' if role=='armor' else 'edge' if role=='steel' else role
        for m in materials.get(key,materials.get('inner',[])):data.materials.append(m)
        for p in data.polygons:p.use_smooth=smooth
        layer=data.uv_layers.new(name='plate-uv')
        for p in data.polygons:
            for li in p.loop_indices:layer.data[li].uv=uv[data.loops[li].vertex_index]
        counts[role]=counts.get(role,0)+1;created.append(obj);return obj
    def tube(name,points,radius,role='inner',n=10):
        pts=[Vector(p) for p in points];vs=[];fs=[];uv=[]
        for j,p in enumerate(pts):
            axis=(pts[min(j+1,len(pts)-1)]-pts[max(j-1,0)]).normalized()
            u=axis.cross(Vector((0,0,1)))
            if u.length<.01:u=axis.cross(Vector((0,1,0)))
            u.normalize();v=axis.cross(u).normalized()
            for i in range(n):
                angle=i*math.tau/n;vs.append(p+radius*(u*math.cos(angle)+v*math.sin(angle)));uv.append((i/n,j/max(1,len(pts)-1)))
        for j in range(len(pts)-1):
            for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        fs.extend([tuple(reversed(range(n))),tuple(range((len(pts)-1)*n,len(pts)*n))]);return objmesh(name,vs,fs,uv,role)
    # Same compact posterior keel, with a more tapered anterior sternal arc.
    # z, centre-y, half-width, anterior depth, posterior depth.
    profile=[(.515,.355,.009,.016,.016),(.575,.255,.072,.13,.13),
             (.650,.165,.130,.245,.245),(.735,.110,.182,.295,.300),
             (.840,.060,.219,.345,.355),(.960,.040,.244,.395,.355),
             (1.080,-.020,.247,.370,.335),(1.200,-.065,.232,.295,.285),
             (1.310,-.075,.197,.201,.205),(1.390,-.090,.025,.035,.035)]
    def section(z):
        z=max(profile[0][0],min(profile[-1][0],z))
        for i,(a,b) in enumerate(zip(profile,profile[1:])):
            if a[0]<=z<=b[0]:
                t=(z-a[0])/(b[0]-a[0]);out=[]
                for k in range(1,5):
                    m0=(b[k]-profile[max(0,i-1)][k])/(b[0]-profile[max(0,i-1)][0])
                    m1=(profile[min(len(profile)-1,i+2)][k]-a[k])/(profile[min(len(profile)-1,i+2)][0]-a[0])
                    value=(2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*(b[0]-a[0])*m0+(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*(b[0]-a[0])*m1
                    out.append(max(min(a[k],b[k]),min(max(a[k],b[k]),value)))
                return out
        return profile[-1][1:]
    def surface(theta,z,offset=0):
        cy,rx,front,back=section(z);depth=front if math.cos(theta)>=0 else back
        n=Vector((math.sin(theta),-math.cos(theta),0)).normalized()
        return Vector((rx*math.sin(theta),cy-depth*math.cos(theta),z))+n*offset
    def normal(theta):return Vector((math.sin(theta),-math.cos(theta),0))
    def patch(name,amin,amax,zmin,zmax,role='inner',offset=-.018):
        vs=[];fs=[];uv=[];na=28;nz=max(8,int((zmax-zmin)/.018))
        for j in range(nz+1):
            z=zmin+(zmax-zmin)*j/nz
            for i in range(na+1):
                a=amin+(amax-amin)*i/na;vs.append(surface(a,z,offset));uv.append((i/na,j/nz))
        for j in range(nz):
            for i in range(na):
                k=j*(na+1)+i;fs.append((k,k+na+1,k+na+2,k+1))
        mid=surface((amin+amax)/2,(zmin+zmax)/2)
        f=fs[len(fs)//2];n=(vs[f[1]]-vs[f[0]]).cross(vs[f[2]]-vs[f[0]])
        if n.dot(normal((amin+amax)/2))<0:fs=[tuple(reversed(f)) for f in fs]
        return objmesh(name,vs,fs,uv,role)
    # No continuous sealed barrel: dark backing exists only beneath plated segments.
    patch('CG2b tapered anterior breast backing',-.90,.90,.68,1.367)
    patch('CG2b compact dorsal keel backing',2.17,math.tau-2.17,.515,1.34)
    patch('CG2b low posterior counterweight continuation',0,math.tau,.515,.747)
    # Inferred rear power housing, deliberately recessed instead of a giant visible shell.
    patch('CG2b rear power envelope',1.50,math.tau-1.50,.63,.86,offset=-.045)
    raw=[(-.40,0),(.40,0),(.47,.23),(.45,.54),(.32,.79),(.12,.97),(0,1.025),(-.22,.92),(-.44,.61),(-.48,.25)]
    outline=[]
    for i,p in enumerate(raw):
        q=raw[(i+1)%len(raw)];outline.extend([p,((p[0]+q[0])/2,(p[1]+q[1])/2)])
    def plate(name,a,z,width,length,slant,material_role='armor',depth=.005):
        radius=max(.08,sum(section(z)[1:3])/2)
        def point(u,v,o):
            return surface(a+u*width/radius,max(.516,min(1.375,z-v*length+u*slant)),o+.0080*max(0,min(1,v))**1.45)
        coords=[];vs=[];n=len(outline)
        for scale in (1,.66,.33):
            for u,v in outline:
                u=u*scale;v=.43+(v-.43)*scale
                coords.append((u,v));vs.append(point(u,v,depth+.0006*(1-scale)))
        coords.append((0,.43));vs.append(point(0,.43,depth+.0007));center=3*n
        for u,v in outline:coords.append((u,v));vs.append(point(u,v,depth-.0030))
        fs=[];smooth=[]
        for ring in range(2):
            for i in range(n):
                j=(i+1)%n;fs.append((ring*n+i,ring*n+j,(ring+1)*n+j,(ring+1)*n+i));smooth.append(True)
        for i in range(n):
            j=(i+1)%n;fs.append((2*n+i,2*n+j,center));smooth.append(True)
            fs.append((i,center+1+i,center+1+j,j));smooth.append(False)
        f=fs[0];nn=(vs[f[1]]-vs[f[0]]).cross(vs[f[2]]-vs[f[0]])
        if nn.dot(normal(a))<0:fs=[tuple(reversed(f)) for f in fs]
        ob=objmesh(name,vs,fs,[(max(0,min(1,u+.5)),max(0,min(1,1-v/1.025))) for u,v in coords],material_role)
        ob['cg2bPlateAngle']=a;ob['cg2bPlateTop']=z
        inner_materials=materials.get('inner',[])
        if inner_materials:ob.data.materials.append(inner_materials[0])
        for p,s in zip(ob.data.polygons,smooth):
            p.use_smooth=s
            if not s and inner_materials:p.material_index=len(ob.data.materials)-1
        # Thin physical rim on only a selected lower arc; no upholstery piping.
        edge=[point(u,v,depth+.0005) for u,v in outline[7:17]];ev=[];eu=[]
        for i,p in enumerate(edge):
            ev.extend([p,p-normal(a)*.0014]);eu.extend([(i/(len(edge)-1),0),(i/(len(edge)-1),1)])
        ef=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(edge)-1)]
        objmesh(name+' sheet lip',ev,ef,eu,'edge',False)
        return ob,point
    # Varied, diagonal courses leave the side machinery bays open instead of sealing them.
    for zone,(amin,amax,zmax,zmin,step) in enumerate([(-.90,.90,1.357,.700,.049),(2.17,math.tau-2.17,1.31,.557,.060),(0,math.tau,.728,.534,.052)]):
        row=0;z=zmax
        while z>zmin:
            sec=section(z-.027);rad=max(.05,(sec[1]+max(sec[2],sec[3]))/2)
            spacing=.060 if zone==0 else .079
            num=max(2,int((amax-amin)*rad/spacing)+1)
            for col in range(num):
                a=amin+(amax-amin)*col/max(1,num-1)+rng.uniform(-.04,.04)+(row%2)*.035
                width=rng.uniform(.076,.111) if zone==0 else rng.uniform(.086,.12)
                length=rng.uniform(.083,.122) if zone==0 else rng.uniform(.087,.126)
                # An asymmetrical narrow sternum slit survives across multiple courses.
                slit=-.28+.055*math.sin(z*17)
                if zone==0 and abs(a-slit)<.050 and .84<z<1.25:continue
                ob,point=plate(f'CG2b {zone} irregular breast leaf {row:02d} {col:02d}',a,z+rng.uniform(-.013,.011),width,length,rng.uniform(-.025,.025))
                if (row+col+zone)%3==0:
                    pos=point(-.19,.25,.006);n=normal(a);radius=.0028 if zone==0 else .0025
                    tube(ob.name+' captive rivet',[pos,pos+n*.0015],radius,'rivet',10)
            z-=step*rng.uniform(.94,1.08);row+=1
    # Segmented prominent sternum strap and repair plates, not a symmetrical centre zipper.
    for i in range(8):
        z=1.28-i*.061;a=-.34+.045*math.sin(i*.7)
        ob,point=plate(f'CG2b sternal strap {i}',a,z,.047,.091,.012,'steel',depth=.008)
        for j in (-1,1):
            p=point(j*.22,.28,.009);tube(ob.name+' strap bolt '+str(j),[p,p+normal(a)*.0018],.0030,'rivet',10)
    # Local rim rails define purposeful open bays for the independent machinery worker.
    cavities=[]
    for side in (-1,1):
        front_a=side*1.04;back_a=side*2.15
        for label,a in [('front',front_a),('rear',back_a)]:
            points=[surface(a,.74+i*.030,-.013) for i in range(18)]
            tube(f'CG2b {side} bay {label} structural rim',points,.0045,'steel',12)
        tube(f'CG2b {side} bay low curved sill',[surface(side*(1.12+j*.07),.743,-.008) for j in range(13)],.004,'inner',12)
        cavities.append({'side':'left' if side<0 else 'right','angleRangeRadians':[front_a,back_a],'zRange':[.745,1.29],'approxOpeningCenter':list(surface(side*1.59,.965,-.006)),'depthSuggested':[-.040,-.006],'rimAnchors':[list(surface(front_a,z,-.013)) for z in (.76,.94,1.18)]+[list(surface(back_a,z,-.013)) for z in (.76,.94,1.18)],'purpose':'Exposed avian side transmission bay; add machinery behind armor, do not reseal'} )
    # Small medial posterior inlet interrupts the lower keel shell without changing its tip.
    for i in range(5):
        a=math.pi-.17+i*.082;points=[surface(a,.59,-.008),surface(a,.68,-.010)]
        tube('CG2b compact rear inlet rail '+str(i),points,.003,'inner',8)
    def bounds(vs):return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
    candidate=[o.matrix_world@Vector(v) for o in created for v in o.bound_box]
    return {'module':'cg2b-body','hiddenRetainedSourceObjects':len(originals),'counts':counts,'sourceVisibleBodyBounds':bounds(source_bounds) if source_bounds else None,'candidateBodyBounds':bounds(candidate),'constructionProfile':profile,'cavities':cavities,'stanceAnchors':'No head/neck/wing/leg/foot objects changed; existing hip/knee/hock/feet retained','visibleProposal':['Tapered asymmetric anterior breast replaces a sealed regular barrel','Small irregular thin metal courses and local stepped sternum strap','Both flank bays expose negative space for next machinery worker','Pointed compact posterior power/counterweight volume retained'],'limits':['Hidden rear topology and fictional power arrangement are creative proposals','Body-only preview may have empty side bays until machinery integration','Not a visual twin or engineering validation; root must review all integrated silhouettes']}
