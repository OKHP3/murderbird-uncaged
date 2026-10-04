"""Head07 source-partition proposal. Original datablocks and pose preserved.
July controls head only. Depth, joins and back surfaces are inferred CG.
"""
import bpy,json,math
from mathutils import Vector

def apply(scene,root_path=None,era='builder'):
    if any(o.get('cgSupervisedHead07') for o in scene.objects):raise RuntimeError('Reload completed06')
    frame=scene.objects['CG2b head frame'].matrix_world.copy()
    visible=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
    def family_mat(f):
        for o in visible:
            fs=json.loads(o.get('cgSurfaceFamilies','[]'))
            if f in fs and fs.index(f)<len(o.data.materials):return o.data.materials[fs.index(f)]
        raise RuntimeError(f)
    mats={f:family_mat(f) for f in ('head-armor','black-iron','machined-steel','worn-bronze')}
    hidden=[]
    patterns=('connected under-eye bill-root cheek sheet','thin orbital cheek sheet','swept overlapping dorsal brow plate','formed bill saddle side panel','pointed overlapping dorsal sheet','swept overlapping frontal saddle sheet')
    for o in visible:
        if (o.get('cgSupervisedHead06') and any(a in o.name for a in patterns)) or o.name in ('CGH04 nine section convex hooked upper bill','CGH04 eight section bill root saddle'):
            o.hide_render=True;o.hide_set(True);hidden.append(o.name)
    made=[]
    def p(x,y,d):
        return Vector((d,(788-x)*.0012+.005,(188-y)*.0012+.020))
    def mesh(name,vs,fs,role='head-armor',sheet=0,bevel=.00035):
        d=bpy.data.meshes.new('CGH07 '+name);d.from_pydata(vs,[],fs);d.update()
        o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.matrix_world=frame.copy()
        o['cgSupervisedHead07']=True;o['head07LocalPlateUV']=True;o['cg1cRegion']='head';o['cg2bRegion']='head'
        o['surfaceRole']=role;o['cgSurfaceFamilies']=json.dumps([role,'black-iron','worn-bronze'])
        o['exteriorEras']='maker,mechanic,builder';o['cgConstructionStatus']='Source-relative thin formed head sheets; inferred CG depth; owner likeness pending'
        for f in (role,'black-iron','worn-bronze'):d.materials.append(mats[f])
        uv=d.uv_layers.new(name='head07-local-plate-uv')
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
    def panel(name,outline,side,dep,role='head-armor'):
        # Broad curved polygon triangulated as concentric inset rows.
        cx=sum(q[0] for q in outline)/len(outline);cy=sum(q[1] for q in outline)/len(outline)
        vs=[];n=len(outline);rows=9
        for j in range(rows):
            t=.001+(1-.001)*j/(rows-1)
            for x,y in outline:
                xx=cx+(x-cx)*t;yy=cy+(y-cy)*t
                dd=dep(xx,yy) if callable(dep) else dep
                vs.append(p(xx,yy,side*(dd+.002*(1-t*t))))
        fs=[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(rows-1) for k in range(n)]
        fs.append(tuple(range(n-1,-1,-1)))
        return mesh(name,vs,fs,role,sheet=.002,bevel=.0003)
    def aperture(name,outline,side):
        # Intersect rays with asymmetric boundary; circular inner loop is an
        # actual opening, not a disk or a washer attached above the cheek.
        cx,cy=788,188;n=128;rows=10;vs=[]
        for j in range(rows):
            t=j/(rows-1)
            for k in range(n):
                a=math.tau*k/n;dx,dy=math.cos(a),math.sin(a);hits=[]
                for (ax,ay),(bx,by) in zip(outline,outline[1:]+outline[:1]):
                    ex,ey=bx-ax,by-ay;den=dx*ey-dy*ex
                    if abs(den)<1e-9:continue
                    qx,qy=ax-cx,ay-cy;r=(qx*ey-qy*ex)/den;u=(qx*dy-qy*dx)/den
                    if r>0 and 0<=u<=1:hits.append(r)
                rr=min(hits) if hits else 78
                rr=max(rr,52);rad=49+(rr-49)*t
                xx,yy=cx+rad*dx,cy+rad*dy
                depth=.174-.019*t+.004*math.sin(math.pi*t)
                vs.append(p(xx,yy,side*depth))
        mesh(name,vs,[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(rows-1) for k in range(n)],sheet=.0025)
        # Aperture wall joins retained optical seat, staying outside radius42.
        vs=[p(cx+r*math.cos(k*math.tau/n),cy+r*math.sin(k*math.tau/n),side*d) for r,d in [(49,.174),(48.8,.169),(48.2,.158)] for k in range(n)]
        mesh('short enclosed aperture return '+name,vs,[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(2) for k in range(n)],'black-iron',bevel=.0002)
    def browdepth(x,y):
        stations=[(568,191,23,.022),(598,184,60,.068),(646,173,87,.110),(695,164,99,.134),(744,164,101,.153),(792,177,90,.159),(838,198,72,.149),(875,219,48,.113),(900,230,26,.073)]
        for aa,bb in zip(stations,stations[1:]):
            if x<=bb[0]:
                t=max(0,min(1,(x-aa[0])/(bb[0]-aa[0])));cy=aa[1]+(bb[1]-aa[1])*t;rad=aa[2]+(bb[2]-aa[2])*t;w=aa[3]+(bb[3]-aa[3])*t
                return w*math.sqrt(max(.003,1-((y-cy)/rad)**2))+.006
        return .12
    cheek=[(673,204),(686,189),(712,191),(736,164),(757,132),(793,126),(830,142),(858,177),(877,213),(899,237),(881,278),(850,253),(817,260),(780,266),(743,255),(716,240),(697,220)]
    brow=[(661,54),(688,48),(739,69),(788,94),(829,121),(858,155),(851,184),(823,171),(792,145),(753,121),(713,96),(684,80)]
    for side,label in [(-1,'L'),(1,'R')]:
        aperture('broad unequal aperture cheek '+label,cheek,side)
        panel('diagonal supraorbital brow '+label,brow,side,browdepth)
        panel('jaw root cheek bearing bridge '+label,[(661,216),(684,220),(703,243),(729,263),(719,282),(694,268),(676,249),(656,246)],side,.152,'black-iron')
        panel('seated jaw root face '+label,[(674,252),(702,262),(734,292),(761,318),(750,333),(718,309),(687,286),(666,270)],side,.145)
    skull=[(568,191,23,.022),(598,184,60,.068),(646,173,87,.110),(695,164,99,.134),(744,164,101,.153),(792,177,90,.159),(838,198,72,.149),(875,219,48,.113),(900,230,26,.073)]
    from mathutils.bvhtree import BVHTree
    oldvault=scene.objects['CGH04 nine section cranial vault']
    bv=BVHTree.FromPolygons([v.co for v in oldvault.data.vertices],[list(f.vertices) for f in oldvault.data.polygons])
    def vault(px,depth):
        hit=bv.ray_cast(p(px,-800,depth),Vector((0,0,-1)))
        if hit[0] is not None:return 188-(hit[0].z-.020)/.0012-3.2

        for a,b in zip(skull,skull[1:]):
            if px<=b[0]:
                t=max(0,min(1,(px-a[0])/(b[0]-a[0])));cy=a[1]+(b[1]-a[1])*t;rad=a[2]+(b[2]-a[2])*t;wid=a[3]+(b[3]-a[3])*t
                return cy-rad*math.sqrt(max(0,1-(depth/wid)**2))-2.4
        return 218
    # Small, unequal pointed leaves fitted to receiving loft, no saddle blanket.
    courses=[(865,775,-.080,.031),(842,721,-.111,.024),(814,678,-.078,.023),(773,636,-.040,.023),(724,590,-.004,.022),(674,567,.020,.021),(794,669,.010,.025),(843,744,.033,.024),(867,793,.063,.025),(815,699,.092,.022),(769,630,.063,.026),(737,616,-.090,.024),(700,582,-.047,.026),(654,565,.052,.020),(848,756,-.018,.020),(888,822,.012,.025),(899,817,-.056,.022),(895,804,-.024,.024),(902,827,.009,.024),(891,798,.042,.023),(877,773,.082,.022),(881,759,-.094,.024),(795,657,-.122,.021),(788,674,.126,.022),(681,564,-.014,.027),(624,558,.012,.022)]
    for j,(ax,bx,offset,width) in enumerate(courses):
        vs=[];rows=23;cols=9
        for q in range(rows):
            t=q/(rows-1);x=ax+(bx-ax)*t;w=width*(.84+.20*math.sin(math.pi*t))*max(.007,1-t**1.6);center=offset*(1-.40*t)
            for k in range(cols):
                u=k/(cols-1)*2-1;d=center+u*w;y=vault(x,d)-1.4*math.sin(math.pi*t)-.4*(1-u*u)
                vs.append(p(x,y,d))
        mesh('irregular fitted swept crown %02d'%j,vs,[(q*cols+k,q*cols+k+1,(q+1)*cols+k+1,(q+1)*cols+k) for q in range(rows-1) for k in range(cols-1)],sheet=.0015)
    bill=[(158,878,13,.111),(174,893,18,.113),(204,903,21,.107),(220,909,23,.110),(237,916,27,.108),(266,921,40,.101),(298,919,49,.085),(332,918,51,.065),(366,927,37,.047),(397,925,27,.032),(430,910,16,.015),(460,885,.8,.0012)]
    def section(y):
        for a,b in zip(bill,bill[1:]):
            if y<=b[0]:
                t=max(0,min(1,(y-a[0])/(b[0]-a[0])));return [a[k]+(b[k]-a[k])*t for k in range(1,4)]
        return bill[-1][1:]
    for name,y0,y1 in [('upper root collar',158,238),('overlapping bill side shell',236,336),('terminal hook shell',333,460)]:
        rows=65;n=96;vs=[];fs=[]
        for j in range(rows):
            y=y0+(y1-y0)*j/(rows-1);cx,rad,wid=section(y)
            for k in range(n):
                a=math.tau*k/n;vs.append(p(cx+rad*math.cos(a),y,(wid+(.0012 if name=='upper root collar' else .0005 if name=='overlapping bill side shell' else 0))*math.sin(a)))
        for j in range(rows-1):
            for k in range(n):
                ids=(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k)
                if name=='overlapping bill side shell':
                    y=y0+(y1-y0)*(j+.5)/(rows-1);cx,rad,wid=section(y);a=math.tau*(k+.5)/n;px=cx+rad*math.cos(a)
                    if (px-916)**2+(y-255)**2<9**2:continue
                fs.append(ids)
        mesh(name,vs,fs,sheet=.0018)
    for side,label in [(-1,'L'),(1,'R')]:
        n=64;vs=[p(916+r*math.cos(k*math.tau/n),255+r*math.sin(k*math.tau/n),side*d) for r,d in [(11,.106),(9,.109),(8,.103),(8,.094)] for k in range(n)]
        mesh('recessed root side port rim '+label,vs,[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(3) for k in range(n)],'black-iron',bevel=.0002)
        vs=[p(916+r*math.cos(k*math.tau/n),255+r*math.sin(k*math.tau/n),side*.092) for r in (8,0) for k in range(n)]
        mesh('dark recessed root side port '+label,vs,[(k,(k+1)%n,n+(k+1)%n,n+k) for k in range(n)],'black-iron',bevel=0)
    bpy.context.view_layer.update()
    return {'module':'cg-supervised-head07','era':era,'new_mesh_count':len(made),'hidden_originals':hidden,'retained_optics':'all CGH05 optic meshes and center unchanged; aperture radius49 outside optic07 radius42','construction':'broad curved aperture cheek, diagonal brow, fitted irregular crown leaves, three separated bill shells, cheek-seated jaw root','material_binding':'receiving metal05 graphs; ordered cgSurfaceFamilies and head07-local-plate-uv','below_junction_changes':False,'pose_changes':False,'source_status':'source-traced organization; depths and joins inferred','artistic_acceptance':'pending'}
