"""HEAD08 actual visible backing reconstruction; original geometry preserved.
July controls head identity only. New depth and obscured construction are CG inference.
"""
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def apply(scene,root_path=None,era='builder'):
    if any(o.get('cgSupervisedHead08') for o in scene.objects):raise RuntimeError('Reload completed06')
    frame=scene.objects['CG2b head frame'].matrix_world.copy()
    visible=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
    backing=scene.objects['CGH05 curved recessed vault above cheek opening']
    assert not backing.hide_render,'Actual visible05 backing must be present'
    dg=bpy.context.evaluated_depsgraph_get();ev=backing.evaluated_get(dg);em=ev.to_mesh()
    # Transform evaluated backing into fixed head-frame local coordinates.
    inv=frame.inverted()@backing.matrix_world
    bv=BVHTree.FromPolygons([inv@v.co for v in em.vertices],[list(f.vertices) for f in em.polygons]);ev.to_mesh_clear()
    def family_mat(f):
        for o in visible:
            fs=json.loads(o.get('cgSurfaceFamilies','[]'))
            if f in fs and fs.index(f)<len(o.data.materials):return o.data.materials[fs.index(f)]
        raise RuntimeError(f)
    mats={f:family_mat(f) for f in ('head-armor','black-iron','machined-steel','worn-bronze')}
    hidden=[];patterns=('swept overlapping dorsal brow plate','formed bill saddle side panel','pointed overlapping dorsal sheet','swept overlapping frontal saddle sheet','thin orbital cheek sheet','connected under-eye bill-root cheek sheet')
    for o in visible:
        if o==backing or (o.get('cgSupervisedHead06') and any(t in o.name for t in patterns)):
            o.hide_render=True;o.hide_set(True);hidden.append(o.name)
    made=[]
    def p(x,y,d):
        return Vector((d,(788-x)*.0012+.005,(188-y)*.0012+.020))
    def mesh(name,vs,fs,role='head-armor',sheet=0,bevel=.00035):
        d=bpy.data.meshes.new('CGH08 '+name);d.from_pydata(vs,[],fs);d.update()
        o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.matrix_world=frame.copy()
        o['cgSupervisedHead08']=True;o['head08LocalPlateUV']=True;o['cg1cRegion']='head';o['cg2bRegion']='head'
        o['surfaceRole']=role;o['cgSurfaceFamilies']=json.dumps([role,'black-iron','worn-bronze'])
        o['exteriorEras']='maker,mechanic,builder';o['cgConstructionStatus']='Source-relative thin formed head sheets; inferred CG depth; owner likeness pending'
        for f in (role,'black-iron','worn-bronze'):d.materials.append(mats[f])
        uv=d.uv_layers.new(name='head08-local-plate-uv')
        ymin=min(v.co.y for v in d.vertices);ymax=max(v.co.y for v in d.vertices);zmin=min(v.co.z for v in d.vertices);zmax=max(v.co.z for v in d.vertices)
        for f in d.polygons:
            f.use_smooth=True
            for li in f.loop_indices:
                q=d.vertices[d.loops[li].vertex_index].co
                uv.data[li].uv=((q.y-ymin)/max(ymax-ymin,.00001),(q.z-zmin)/max(zmax-zmin,.00001))
        if sheet:
            so=o.modifiers.new('thin formed sheet inward return','SOLIDIFY');so.thickness=sheet;so.offset=-1;so.material_offset=1;so.material_offset_rim=2
        if bevel:
            b=o.modifiers.new('small chamfer on sheet edge','BEVEL');b.width=bevel;b.segments=2
        made.append(o);return o
    def spline(stations,n=5):
        out=[]
        for i in range(len(stations)-1):
            a=stations[max(0,i-1)];b=stations[i];c=stations[i+1];d=stations[min(len(stations)-1,i+2)]
            for j in range(n):
                t=j/n;out.append([.5*(2*bb+(-aa+cc)*t+(2*aa-5*bb+4*cc-dd)*t*t+(-aa+3*bb-3*cc+dd)*t*t*t) for aa,bb,cc,dd in zip(a,b,c,d)])
        out.append(list(stations[-1]));return out
    def strip(name,stations,side,role='head-armor',thick=.0028):
        # Eight rectilinear chamfered cross-section corners: broad plate face,
        # tiny turned rim and flat back. No elliptic tube sections.
        ss=spline(stations);section=[(-1,-.35),(-.94,0),(.94,0),(1,-.35),(1,-.65),(.94,-1),(-.94,-1),(-1,-.65)];vs=[]
        for i,q in enumerate(ss):
            aa=ss[max(0,i-1)];bb=ss[min(len(ss)-1,i+1)];v=Vector((-(bb[1]-aa[1]),bb[0]-aa[0]));v.normalize()
            for u,z in section:
                vs.append(p(q[0]+v.x*q[2]*u,q[1]+v.y*q[2]*u,side*(q[3]+z*thick)))
        n=8;fs=[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(len(ss)-1) for k in range(n)]
        fs.extend([tuple(range(n-1,-1,-1)),tuple((len(ss)-1)*n+k for k in range(n))])
        o=mesh(name,vs,fs,role,bevel=0);o['cgHeadSection']='rectilinear chamfered formed sheet';return o
    def leaf(name,ax,ay,bx,by,depth,width,side):
        vx,vy=bx-ax,by-ay;l=math.hypot(vx,vy);nx,ny=-vy/l,vx/l;vs=[];rows=19;cols=7
        for j in range(rows):
            t=j/(rows-1);w=width*(.8+.30*math.sin(math.pi*t))*max(.008,1-t**1.55)
            for k in range(cols):
                u=k/(cols-1)*2-1;bend=5*math.sin(math.pi*t)
                # Unequal swept edges and pointed free ends; slight bent-sheet
                # camber rather than rounded quill volume.
                vs.append(p(ax+vx*t+nx*(w*u+bend),ay+vy*t+ny*(w*u+bend),side*(depth+.004*math.sin(math.pi*t)+.0015*(1-u*u)-.019*t)))
        return mesh(name,vs,[(j*cols+k,j*cols+k+1,(j+1)*cols+k+1,(j+1)*cols+k) for j in range(rows-1) for k in range(cols-1)],sheet=.0018)
    stations=spline([(570,173,24,.020),(611,162,58,.073),(664,143,78,.108),(714,143,86,.137),(763,149,85,.150),(809,167,69,.148),(854,187,46,.124),(892,211,20,.090)])
    def sec(x):
        for aa,bb in zip(stations,stations[1:]):
            if x<=bb[0]:
                t=max(0,min(1,(x-aa[0])/(bb[0]-aa[0])));return [aa[k]+(bb[k]-aa[k])*t for k in (1,2,3)]
        return stations[-1][1:]
    fit_samples=[]
    def fitted(x,a,offset=.003):
        cy,rad,w=sec(x);center=p(x,cy,0);q=p(x,cy+rad*math.cos(a),w*math.sin(a));direction=(q-center).normalized()
        hit=bv.ray_cast(center+direction*.6,-direction)
        if hit[0] is not None:
            q=hit[0]+direction*offset;fit_samples.append(offset)
        else:fit_samples.append(None)
        return q
    # Each real formed plate follows the actual evaluated05 surface; overlapping
    # rows stagger their roots and taper into swept free ends. No dome added.
    for row,ax in enumerate([891,834,772,702,637]):
        for k in range(13):
            a=math.pi/2-.18+k*(math.pi+.36)/12 + (.065 if row%2 else -.025)
            start=ax-((k*13+row*7)%17);end=max(568,start-(95+(k*7)%27));rows=18;cols=7;vs=[]
            for j in range(rows):
                t=j/(rows-1);xx=start+(end-start)*t
                width=(.225+.022*((k+row)%3))*(.86+.17*math.sin(math.pi*t))*max(.006,1-t**2.1)
                for c in range(cols):
                    u=c/(cols-1)*2-1;ang=a+u*width+.12*math.sin(math.pi*t)
                    vs.append(fitted(xx,ang,.003+.0015*math.sin(math.pi*t)+row*.00035))
            mesh('actual vault swept plate %02d %02d'%(row,k),vs,[(j*cols+c,j*cols+c+1,(j+1)*cols+c+1,(j+1)*cols+c) for j in range(rows-1) for c in range(cols-1)],sheet=.0015)
    def side_surface(px,py,side,extra=.005):
        hit=bv.ray_cast(p(px,py,side*.7),Vector((-side,0,0)))
        if hit[0] is not None:return abs(hit[0].x)+extra
        return .018+extra
    for side,label in [(-1,'L'),(1,'R')]:
        line=spline([(670,59,11),(711,76,15),(754,102,18),(797,130,18),(835,156,17),(869,188,14),(901,219,12)])
        vs=[];cols=9
        for x,y,w in line:
            for c in range(cols):
                u=c/(cols-1)*2-1;py=y+w*u
                dep=side_surface(x,py,side,.009)
                # The forward end overlaps the retained bill root instead of
                # terminating as a floating visor edge.
                if x>862:dep=max(dep,.110-(x-862)*.00028)
                vs.append(p(x,py,side*dep))
        mesh('continuous diagonal supraorbital sheet '+label,vs,[(j*cols+c,j*cols+c+1,(j+1)*cols+c+1,(j+1)*cols+c) for j in range(len(line)-1) for c in range(cols-1)],sheet=.0024)
        # Unequal curved cheek around genuine aperture, rounded outer contour.
        outline=[(683,199),(707,187),(735,158),(756,131),(790,126),(827,145),(859,177),(875,216),(900,245),(875,267),(848,253),(817,259),(782,266),(745,255),(720,237),(700,215)]
        outline=spline(outline+[outline[0],outline[1]],3)[:-3]
        n=128;rows=10;vs=[]
        for j in range(rows):
            t=j/(rows-1)
            for k in range(n):
                a=math.tau*k/n;dx,dy=math.cos(a),math.sin(a);hits=[]
                for (ax,ay),(bx,by) in zip(outline,outline[1:]+outline[:1]):
                    ex,ey=bx-ax,by-ay;den=dx*ey-dy*ex
                    if abs(den)<1e-9:continue
                    qx,qy=ax-788,ay-188;rr=(qx*ey-qy*ex)/den;uu=(qx*dy-qy*dx)/den
                    if rr>0 and 0<=uu<=1:hits.append(rr)
                rr=max(52,min(hits) if hits else 70);rad=49+(rr-49)*t;px,py=788+rad*dx,188+rad*dy
                dd=(.175*(1-t)+max(.138,side_surface(px,py,side,.003))*t)
                vs.append(p(px,py,side*dd))
        mesh('rounded enclosed orbital cheek '+label,vs,[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(rows-1) for k in range(n)],sheet=.002)
        vs=[p(788+rr*math.cos(k*math.tau/n),188+rr*math.sin(k*math.tau/n),side*dd) for rr,dd in [(49,.175),(48.5,.166),(48.2,.158)] for k in range(n)]
        mesh('aperture inward return '+label,vs,[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(2) for k in range(n)],'black-iron',bevel=.0002)
    # Root collar wraps across actual forward end, adjoining retained hook.
    rows=18;cols=17;vs=[]
    for j in range(rows):
        t=j/(rows-1);py=173+69*t;cx=882+34*t;rad=18+8*t;wid=.112-.004*t
        for k in range(cols):
            a=-math.pi/2+math.pi*k/(cols-1);vs.append(p(cx+rad*math.cos(a),py,wid*math.sin(a)))
    mesh('joined bill root wrap',vs,[(j*cols+k,j*cols+k+1,(j+1)*cols+k+1,(j+1)*cols+k) for j in range(rows-1) for k in range(cols-1)],sheet=.002)
    bpy.context.view_layer.update()
    return {'module':'cg-supervised-head08','era':era,'new_mesh_count':len(made),'hidden_originals':hidden,'fit_target':backing.name,'fit_target_evaluated':True,'fit_samples':len(fit_samples),'fit_ray_misses':sum(x is None for x in fit_samples),'fit_minimum_offset':min(x for x in fit_samples if x is not None),'retained_optics':'All CGH05 optics and seat intact; new aperture inner radius49','retained_bill':'CGH04 nine section convex hooked upper bill unchanged','below_junction_changes':False,'pose_changes':False,'material_binding':'receiving metal05 graphs with ordered cgSurfaceFamilies; normalized head08-local-plate-uv','artistic_acceptance':'pending'}
