"""Connected facial frame on frozen integrated04; July controls head identity only.
Depth, hidden intersections and plate layout are editable CG proposals, not metrology.
apply preserves all receiving mesh/UV/face/slot/transform data; superseded head is hidden.
"""
import bpy
import math
import json
from mathutils import Vector


def apply(scene, root_path=None, era='builder'):
    if era not in ('maker', 'mechanic', 'builder', 'advanced'):
        raise ValueError(era)
    if any(o.get('cgSupervisedHead05') for o in scene.objects):
        raise RuntimeError('Reload frozen integrated04 before applying head05')
    frame = scene.objects['CG2b head frame'].matrix_world.copy()
    visible = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render]
    def role_graph(family):
        for o in visible:
            families = json.loads(o.get('cgSurfaceFamilies', '[]'))
            if family in families:
                i = families.index(family)
                if i < len(o.data.materials) and o.data.materials[i]:
                    return o.data.materials[i]
        raise RuntimeError('Required receiving family graph absent: ' + family)
    mats = {r: role_graph(f) for r, f in [('armor','head-armor'),('inner','black-iron'),('steel','machined-steel'),('edge','worn-bronze')]}
    awakened = era in ('builder', 'advanced')
    # All optical graphs are independently authored and explicitly protected from finish routing.
    for role in ('glass','optic','iris','ring-warm','ring-hot','core'):
        m = bpy.data.materials.new('CGH05 protected ' + role + ' ' + era)
        m.use_nodes = True
        bs = m.node_tree.nodes.get('Principled BSDF')
        bs.inputs['Base Color'].default_value = (.006,.010,.009,1)
        bs.inputs['Metallic'].default_value = .35
        bs.inputs['Roughness'].default_value = .22
        if role == 'glass':
            bs.inputs['Base Color'].default_value = (.83,.88,.87,1)
            bs.inputs['Transmission Weight'].default_value = 1
            bs.inputs['IOR'].default_value = 1.46
            bs.inputs['Metallic'].default_value = 0
            bs.inputs['Roughness'].default_value = .065
        elif awakened and role not in ('optic',):
            color,strength = {'iris':((.32,.057,.003,1),.22),'ring-warm':((.64,.095,.004,1),.55),'ring-hot':((.9,.23,.013,1),.9),'core':((.63,.16,.006,1),.65)}[role]
            bs.inputs['Base Color'].default_value = color
            bs.inputs['Emission Color'].default_value = color
            bs.inputs['Emission Strength'].default_value = strength
            bs.inputs['Metallic'].default_value = .18
        m['cg2aPreserveMaterial'] = True
        m['opticEra'] = era
        mats[role] = m
    family = {'armor':'head-armor','inner':'black-iron','steel':'machined-steel','edge':'worn-bronze','glass':'protected-glass','optic':'protected-optic','iris':'protected-optic','ring-warm':'protected-optic','ring-hot':'protected-optic','core':'protected-optic'}
    # Keep the proven deep hooked upper bill untouched. Hide only head04 members being replaced.
    retained = 'CGH04 nine section convex hooked upper bill'
    if retained not in scene.objects or scene.objects[retained].hide_render:
        raise RuntimeError('Frozen head04 volumetric bill must be present and visible')
    hidden = []
    for o in visible:
        if o.get('cgSupervisedHead04') and o.name != retained:
            o.hide_render = True
            o.hide_set(True)
            hidden.append(o.name)
    made = []
    def p(px, py, depth):
        return Vector((depth, (788-px)*.0012+.005, (188-py)*.0012+.020))
    def mesh(name, vs, fs, role='armor', sheet=0, bevel=.00035):
        d = bpy.data.meshes.new('CGH05 '+name)
        d.from_pydata(vs, [], fs)
        d.update()
        o = bpy.data.objects.new(d.name, d)
        scene.collection.objects.link(o)
        o.matrix_world = frame.copy()
        o['cgSupervisedHead05'] = True
        o['cg1cRegion'] = 'head'
        o['cg2bRegion'] = 'head'
        o['surfaceRole'] = role
        o['cgSurfaceFamilies'] = json.dumps([family[role],'black-iron','worn-bronze'])
        o['exteriorEras'] = 'maker,mechanic,builder'
        o['cgConstructionStatus'] = 'Connected curved facial frame CG proposal; owner likeness pending'
        if family[role].startswith('protected-'):
            o['cgProtectedMaterialSlots'] = json.dumps([0])
        for mat in (mats[role],mats['inner'],mats['edge']):
            d.materials.append(mat)
        uv = d.uv_layers.new(name='formed-head05')
        for f in d.polygons:
            f.use_smooth = True
            for li in f.loop_indices:
                q = d.vertices[d.loops[li].vertex_index].co
                uv.data[li].uv = (q.y*2+.5,q.z*2+.5)
        if sheet:
            so = o.modifiers.new('formed sheet edge return','SOLIDIFY')
            so.thickness = sheet
            so.offset = -1
            so.material_offset = 1
            so.material_offset_rim = 2
        if bevel:
            b = o.modifiers.new('small formed edge radius','BEVEL')
            b.width = bevel
            b.segments = 3
        made.append(o)
        return o
    def spline(stations, subdivisions=5):
        out=[]
        for i in range(len(stations)-1):
            a=stations[max(0,i-1)]; b=stations[i]; c=stations[i+1]; d=stations[min(len(stations)-1,i+2)]
            for j in range(subdivisions):
                t=j/subdivisions
                out.append([.5*((2*bb)+(-aa+cc)*t+(2*aa-5*bb+4*cc-dd)*t*t+(-aa+3*bb-3*cc+dd)*t*t*t) for aa,bb,cc,dd in zip(a,b,c,d)])
        out.append(list(stations[-1]))
        return out
    def band(name, stations, side, role='armor', n=24):
        # Closed elliptic sections follow the tangent, with many longitudinal support loops.
        # Stations: source x/y, half band height, half depth, transverse offset.
        ss=spline(stations)
        vs=[]
        for i,q in enumerate(ss):
            ahead=ss[min(i+1,len(ss)-1)];behind=ss[max(i-1,0)]
            v=Vector((-(ahead[1]-behind[1]),ahead[0]-behind[0]));v.normalize()
            for k in range(n):
                a=k*math.tau/n
                vs.append(p(q[0]+v.x*q[2]*math.cos(a),q[1]+v.y*q[2]*math.cos(a),side*(q[4]+q[3]*math.sin(a))))
        fs=[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(len(ss)-1) for k in range(n)]
        fs.extend([tuple(range(n-1,-1,-1)),tuple((len(ss)-1)*n+k for k in range(n))])
        return mesh(name,vs,fs,role,bevel=0)
    # Recessed skull terminates on the curved cheek boundary; never across the aperture.
    vault=[(570,173,24,.020),(611,162,58,.073),(664,143,78,.108),(714,143,86,.137),(763,149,85,.150),(809,167,69,.148),(854,187,46,.124),(892,211,20,.090)]
    ss=spline(vault)
    vs=[];n=48
    for px,cy,ry,w in ss:
        for k in range(n):
            a=k*math.tau/n
            vs.append(p(px,cy+ry*math.cos(a),w*math.sin(a)))
    fs=[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(len(ss)-1) for k in range(n)]
    fs.extend([tuple(range(n-1,-1,-1)),tuple((len(ss)-1)*n+k for k in range(n))])
    mesh('curved recessed vault above cheek opening',vs,fs,'inner',bevel=0)
    def ring(name,cx,cy,rings,side,role='steel',n=96):
        vs=[];loops=[]
        for r,d in rings:
            if abs(r)<1e-8:
                loops.append([len(vs)])
                vs.append(p(cx,cy,side*d))
            else:
                loops.append(list(range(len(vs),len(vs)+n)))
                vs.extend(p(cx+r*math.cos(k*math.tau/n),cy+r*math.sin(k*math.tau/n),side*d) for k in range(n))
        fs=[]
        for aa,bb in zip(loops,loops[1:]):
            if len(aa)==len(bb)==1:
                continue  # two axial poles enclose no surface
            for k in range(n):
                if len(aa)==1:
                    fs.append((aa[0],bb[(k+1)%n],bb[k]))
                elif len(bb)==1:
                    fs.append((aa[k],aa[(k+1)%n],bb[0]))
                else:
                    fs.append((aa[k],aa[(k+1)%n],bb[(k+1)%n],bb[k]))
        if side<0:fs=[tuple(reversed(f)) for f in fs]
        return mesh(name,vs,fs,role,bevel=0)
    def leaf(name, ax,ay,bx,by,depth,width,side,lift=.01):
        vx,vy=bx-ax,by-ay;le=math.hypot(vx,vy);nx,ny=-vy/le,vx/le
        vs=[];rows=17;cols=9
        for j in range(rows):
            t=j/(rows-1)
            w=width*(.75+.33*math.sin(math.pi*t))*(1-t**2.3)+.18
            # Smooth camber over both axes; tapered roots and tip, no transverse flat saddle.
            for k in range(cols):
                u=k/(cols-1)*2-1
                curve=7*math.sin(math.pi*t)
                vs.append(p(ax+vx*t+nx*(w*u+curve),ay+vy*t+ny*(w*u+curve),side*(depth+lift*math.sin(math.pi*t)+.012*(1-u*u)-.026*t)))
        return mesh(name,vs,[(j*cols+k,j*cols+k+1,(j+1)*cols+k+1,(j+1)*cols+k) for j in range(rows-1) for k in range(cols-1)],sheet=.0022)
    for side,label in [(-1,'L'),(1,'R')]:
        # Three nested curved bands connect posterior pivot, orbital underside and bill root.
        band('substantial curved cheek frame '+label,[(662,197,16,.013,.120),(689,201,21,.015,.151),(719,224,19,.012,.159),(755,246,16,.011,.159),(796,254,14,.010,.153),(829,247,17,.011,.144),(856,228,22,.014,.131),(885,220,17,.014,.111)],side)
        band('nested cheek lower return '+label,[(670,237,18,.012,.130),(693,259,17,.013,.145),(728,280,14,.010,.140),(761,303,12,.010,.127),(794,337,10,.008,.112),(813,369,7,.006,.090)],side,'inner')
        # A substantial root transitions continuously into a tapered curved mandible.
        band('formed lower mandible with deep root '+label,[(668,252,24,.017,.118),(691,279,24,.016,.127),(724,300,21,.015,.121),(758,326,19,.013,.108),(785,357,16,.012,.092),(803,386,12,.009,.076),(826,409,9,.007,.052),(850,421,5,.004,.026),(875,422,.65,.0008,.002)],side)
        band('nested mandible upper fold '+label,[(684,270,12,.010,.145),(717,289,12,.011,.142),(754,318,11,.010,.129),(782,350,9,.008,.110),(801,381,7,.007,.090),(824,407,4,.004,.061),(859,420,.5,.001,.020)],side,'edge')
        # Overlapping asymmetrical formed orbital plates blend into brow and cheek.
        for j,(a0,a1) in enumerate([(-174,-100),(-105,-28),(-34,44),(39,116),(111,184)]):
            vs=[];rows=8;cols=25
            for q in range(rows):
                t=q/(rows-1)
                for k in range(cols):
                    a=math.radians(a0+(a1-a0)*k/(cols-1))
                    outer=76+9*math.sin(a-.4)
                    r=49+(outer-49)*t
                    d=.168-.022*t*t+.003*math.sin(math.pi*t)
                    vs.append(p(788+r*math.cos(a),188+r*math.sin(a),side*d))
            mesh('interleaved orbital cheek plate '+label+str(j),vs,[(q*cols+k,q*cols+k+1,(q+1)*cols+k+1,(q+1)*cols+k) for q in range(rows-1) for k in range(cols-1)],sheet=.0022)
        # Rim is inside the broad housing; glass recessed .011m below neighboring plates.
        ring('integrated optical seat '+label,788,188,[(53,.166),(50,.168),(46,.165),(43,.162),(42,.148)],side,'inner')
        ring('thin inset retaining lip '+label,788,188,[(48,.165),(47,.167),(44,.166),(43,.163)],side,'edge')
        ring('dark optical backplate '+label,788,188,[(42,.146),(0,.146)],side,'optic')
        ring('broad restrained awakened iris '+label,788,188,[(36,.148),(0,.148)],side,'iris')
        for j,(r,w) in enumerate([(11,1.4),(18,1.2),(25,1.3),(31,1.1),(35,.8)]):
            ring('nested warm optic ring '+label+str(j),788,188,[(r-w,.1495+j*.00018),(r,.150+j*.00018),(r+w,.1495+j*.00018)],side,'ring-hot' if j in (0,2) else 'ring-warm')
        ring('restrained pupil '+label,788,188,[(9,.151),(0,.151)],side,'core')
        ring('recessed optical glass '+label,788,188,[(42,.153),(35,.156),(22,.158),(0,.159),(0,.156),(22,.155),(35,.153),(42,.150),(42,.153)],side,'glass')
        # The upper diagonal brow is a single continuous curved sweep into the beak root.
        band('continuous swept diagonal brow '+label,[(673,55,13,.009,.099),(707,68,16,.009,.123),(746,91,18,.010,.143),(785,115,19,.010,.157),(822,138,19,.010,.165),(858,165,18,.012,.149),(882,188,15,.013,.127),(906,216,10,.012,.103)],side)
        # Continuous bill-root return, replacing the broad segmented saddle.
        band('curved bill root side return '+label,[(858,169,14,.012,.136),(880,188,15,.013,.129),(898,215,18,.014,.113),(913,238,16,.014,.101),(916,258,12,.011,.096)],side)
        # Dense unequal crown leaves sweep posteriorly; varied lengths and overlapping roots.
        leaves=[(740,79,617,90,.132,14),(720,64,598,98,.117,15),(692,73,562,122,.104,13),(724,103,617,135,.143,14),(685,104,547,162,.120,15),(655,119,537,188,.105,13),(713,132,615,175,.151,14),(681,148,560,219,.133,14),(647,156,537,243,.115,13),(704,168,635,210,.156,15),(677,184,567,269,.141,14),(629,190,547,285,.111,13),(659,222,578,311,.130,14),(620,237,574,329,.108,13),(681,245,635,337,.137,14),(650,263,629,356,.125,13),(703,268,698,355,.143,13),(615,280,599,347,.098,11)]
        for j,(ax,ay,bx,by,d,w) in enumerate(leaves):
            leaf('swept overlapping crown '+label+' %02d'%j,ax,ay,bx,by,d,w,side)
        # Recessed posterior bearings stay within cheek/crown rather than floating in the opening.
        for j,(x,y,r,d) in enumerate([(652,169,23,.131),(682,230,20,.155),(618,222,16,.116)]):
            ring('nested posterior pivot '+label+str(j),x,y,[(r,d),(r*.86,d+.003),(r*.62,d+.003),(r*.48,d),(0,d)],side,'steel')
    # Roof armor consists of unequal narrow longitudinal leaves following the vault.
    # Each leaf has a rounded cross-section, tapered width, and tiny raised crest.
    def roof_y(x):
        stations=[(560,143),(600,101),(645,73),(680,54),(720,58),(765,71),(810,89),(850,122),(898,174)]
        for (x0,y0),(x1,y1) in zip(stations,stations[1:]):
            if x<=x1:
                t=max(0,min(1,(x-x0)/(x1-x0)))
                return y0+(y1-y0)*t
        return stations[-1][1]
    roof_leaves=[(858,686,-.114,.029),(827,626,-.088,.030),(787,578,-.064,.027),(745,551,-.045,.026),(873,704,-.040,.023),(838,652,-.010,.027),(803,606,.019,.026),(762,557,.041,.025),(857,679,.064,.025),(816,616,.086,.027),(782,564,.110,.025),(730,546,.124,.023)]
    for j,(ax,bx,offset,width) in enumerate(roof_leaves):
        vs=[];rows=25;cols=13
        for r in range(rows):
            t=r/(rows-1);px=ax+(bx-ax)*t
            ww=width*(.86+.20*math.sin(math.pi*t))*(1-.96*t**2)+.0003
            center=offset*(1-.45*t)
            for k in range(cols):
                u=k/(cols-1)*2-1;d=center+u*ww
                py=roof_y(px)+44*(d/.155)**2-4.5*math.sin(math.pi*t)-2.5*(1-u*u)
                vs.append(p(px,py,d))
        mesh('interleaved longitudinal roof feather %02d'%j,vs,[(r*cols+k,r*cols+k+1,(r+1)*cols+k+1,(r+1)*cols+k) for r in range(rows-1) for k in range(cols-1)],sheet=.0022)
    bpy.context.view_layer.update()
    return {'module':'cg-supervised-head05','era':era,'new_mesh_count':len(made),'hidden_originals':hidden,'retained_bill':retained,'lens_recess_from_neighbor_m':.009,'optic_diameter_source_px':96,'source_head_span_px':435,'lower_cheek_opening':'true unfilled aperture; nested bands surround but never membrane-fill it','material_binding':'ordered cgSurfaceFamilies and explicit protected primary optical slots; material-name independent','below_junction_changes':False,'depth_status':'inferred CG dimensions, not source measurement','artistic_acceptance':'pending'}
