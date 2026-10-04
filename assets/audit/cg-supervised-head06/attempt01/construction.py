"""Head-only formed-sheet proposal on exact completed05. Preserve receiving data.
July source controls head identity; depth and hidden intersections are CG inference.
"""
import bpy
import json
import math
from mathutils import Vector


def apply(scene, root_path=None, era='builder'):
    if era not in ('maker','mechanic','builder','advanced'):
        raise ValueError(era)
    if any(o.get('cgSupervisedHead06') for o in scene.objects):
        raise RuntimeError('Reload completed05 before applying head06')
    frame=scene.objects['CG2b head frame'].matrix_world.copy()
    visible=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
    def family_mat(f):
        for o in visible:
            fs=json.loads(o.get('cgSurfaceFamilies','[]'))
            if f in fs and fs.index(f)<len(o.data.materials):
                return o.data.materials[fs.index(f)]
        raise RuntimeError('Receiving graph absent: '+f)
    mats={f:family_mat(f) for f in ('head-armor','black-iron','machined-steel','worn-bronze')}
    retained='CGH04 nine section convex hooked upper bill'
    assert retained in scene.objects and not scene.objects[retained].hide_render
    # Preserve every optic member, housing seat, vault and bearing. Hide only
    # receiving armor sections replaced by sheet construction; never delete.
    patterns=('substantial curved cheek frame','nested cheek lower return','formed lower mandible','nested mandible upper fold','interleaved orbital cheek plate','continuous swept diagonal brow','curved bill root side return','swept overlapping crown','interleaved longitudinal roof feather')
    hidden=[]
    for o in visible:
        if o.get('cgSupervisedHead05') and any(a in o.name for a in patterns):
            o.hide_render=True;o.hide_set(True);hidden.append(o.name)
    made=[]
    def p(x,y,d):
        return Vector((d,(788-x)*.0012+.005,(188-y)*.0012+.020))
    def mesh(name,vs,fs,role='head-armor',sheet=0,bevel=.00035):
        d=bpy.data.meshes.new('CGH06 '+name);d.from_pydata(vs,[],fs);d.update()
        o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.matrix_world=frame.copy()
        o['cgSupervisedHead06']=True;o['cg1cRegion']='head';o['cg2bRegion']='head'
        o['surfaceRole']=role;o['cgSurfaceFamilies']=json.dumps([role,'black-iron','worn-bronze'])
        o['exteriorEras']='maker,mechanic,builder';o['cgConstructionStatus']='Source-relative thin formed head sheets; inferred CG depth; owner likeness pending'
        for f in (role,'black-iron','worn-bronze'):d.materials.append(mats[f])
        uv=d.uv_layers.new(name='formed-head06-normalized')
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
    for side,label in [(-1,'L'),(1,'R')]:
        strip('connected under-eye bill-root cheek sheet '+label,[(662,198,13,.128),(690,203,16,.155),(724,227,14,.165),(761,249,12,.167),(801,256,11,.160),(837,247,14,.151),(865,225,16,.137),(894,220,12,.112),(915,247,10,.103)],side)
        strip('recessed cheek lower plated mechanism '+label,[(668,240,14,.130),(697,266,15,.148),(735,287,14,.143),(770,312,12,.127),(798,347,10,.110),(817,377,6,.089)],side,'machined-steel',.003)
        jaw=[(668,255,23,.121),(696,280,24,.130),(732,306,22,.126),(764,334,19,.111),(790,369,16,.093),(815,400,12,.066),(847,420,7,.033),(876,422,.7,.004)]
        strip('substantial swept plated mandible '+label,jaw,side,'head-armor',.004)
        strip('nested dark jaw upper folded plate '+label,[(680,269,13,.143),(715,292,14,.149),(749,317,13,.138),(778,350,11,.120),(802,383,9,.096),(827,409,5,.063),(858,422,.6,.022)],side,'black-iron',.003)
        # Jaw segmentation is overlapping formed sheets, not a gold horn.
        for j,(a,b) in enumerate([(0,3),(2,5),(4,7)]):
            sub=jaw[a:b+1];sub=[(x,y+3,w*.50,d+.005) for x,y,w,d in sub]
            strip('interleaved jaw face panel '+label+str(j),sub,side,'machined-steel',.002)
        # Flatter unequal annular sheets hug preserved optical seat.
        for j,(a0,a1) in enumerate([(-178,-107),(-112,-40),(-46,27),(21,105),(99,183)]):
            vs=[];rows=6;cols=21
            for q in range(rows):
                t=q/(rows-1)
                for k in range(cols):
                    a=math.radians(a0+(a1-a0)*k/(cols-1));outer=68+7*math.sin(a-.4);r=49+(outer-49)*t
                    vs.append(p(788+r*math.cos(a),188+r*math.sin(a),side*(.170-.010*t+.0008*math.sin(math.pi*t))))
            mesh('thin orbital cheek sheet '+label+str(j),vs,[(q*cols+k,q*cols+k+1,(q+1)*cols+k+1,(q+1)*cols+k) for q in range(rows-1) for k in range(cols-1)],sheet=.0018)
        brow=[(673,55,12,.101),(707,69,13,.126),(746,92,15,.145),(786,116,16,.160),(825,143,15,.167),(859,169,13,.150),(883,192,11,.128),(907,219,8,.105)]
        for j,(a,b) in enumerate([(0,3),(2,5),(4,7)]):
            strip('swept overlapping dorsal brow plate '+label+str(j),[(x,y-2*j,w,d+.001*j) for x,y,w,d in brow[a:b+1]],side,thick=.0025)
        strip('formed bill saddle side panel '+label,[(859,173,12,.137),(882,192,13,.132),(901,219,16,.117),(916,241,13,.105),(917,261,9,.100)],side,thick=.0025)
        leaves=[(733,79,604,99,.133,14),(708,70,573,126,.117,13),(687,96,548,164,.122,16),(721,112,613,152,.149,12),(654,124,533,199,.107,14),(686,147,557,230,.134,15),(720,148,636,191,.157,11),(648,167,541,262,.118,13),(679,185,573,287,.141,14),(628,201,550,305,.111,12),(661,224,583,329,.132,13),(698,248,654,341,.145,12),(634,258,621,354,.117,12),(609,276,594,347,.101,10)]
        for j,q in enumerate(leaves):leaf('pointed interleaved crown sheet '+label+' %02d'%j,*q,side)
    def roof_y(x):
        stations=[(560,143),(600,101),(645,73),(680,54),(720,58),(765,71),(810,89),(850,122),(898,174)]
        for (a,b),(c,d) in zip(stations,stations[1:]):
            if x<=c:return b+(d-b)*max(0,min(1,(x-a)/(c-a)))
        return 174
    for j,(ax,bx,offset,width) in enumerate([(853,688,-.114,.025),(823,620,-.080,.027),(777,570,-.052,.025),(735,545,-.026,.023),(871,710,-.028,.021),(838,663,.008,.024),(792,604,.033,.023),(751,551,.057,.021),(858,685,.075,.021),(816,623,.102,.024),(770,562,.120,.019)]):
        vs=[];rows=25;cols=9
        for q in range(rows):
            t=q/(rows-1);x=ax+(bx-ax)*t;w=width*(.84+.16*math.sin(math.pi*t))*max(.008,1-t**1.55);center=offset*(1-.45*t)
            for k in range(cols):
                u=k/(cols-1)*2-1;d=center+u*w;y=roof_y(x)+44*(d/.155)**2-3*math.sin(math.pi*t)-.6*(1-u*u)
                vs.append(p(x,y,d))
        mesh('pointed overlapping dorsal sheet %02d'%j,vs,[(q*cols+k,q*cols+k+1,(q+1)*cols+k+1,(q+1)*cols+k) for q in range(rows-1) for k in range(cols-1)],sheet=.0018)
    bpy.context.view_layer.update()
    return {'module':'cg-supervised-head06','era':era,'new_mesh_count':len(made),'hidden_originals':hidden,'retained_bill':retained,'retained_optics':'all completed05 seat/glass/iris/rings/backplate retained without mutation','construction':'thin formed sheet strips with rectilinear chamfered sections, pointed crown sheets and nested jaw panels','material_binding':'ordered cgSurfaceFamilies; root reroutes finishes','below_junction_changes':False,'pose_changes':False,'source_status':'source-relative contours; depth and obscured geometry inferred','artistic_acceptance':'pending'}
