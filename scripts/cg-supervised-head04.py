"""Registered section-loft head study. Source depth and camera are hypotheses.
API receives completed cycle03; all original data blocks remain untouched.
"""
import bpy, math, json
from mathutils import Vector

def apply(scene, root_path=None, era='builder'):
    if any(o.get('cgSupervisedHead04') for o in scene.objects):
        raise RuntimeError('Reload frozen cycle03 before applying head04')
    frame=scene.objects['CG2b head frame'].matrix_world.copy()
    visible=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
    def role_graph(family):
        for o in visible:
            try: families=json.loads(o.get('cgSurfaceFamilies','[]'))
            except Exception: families=[]
            if family in families:
                i=families.index(family)
                if len(o.data.materials)>i and o.data.materials[i]:return o.data.materials[i]
        raise RuntimeError('Required receiving role graph absent: '+family)
    armor=role_graph('head-armor');inner=role_graph('black-iron');steel=role_graph('machined-steel');edge=role_graph('worn-bronze')
    mats={'armor':armor,'inner':inner,'steel':steel,'edge':edge}
    for role in ('glass','optic','core'):
        m=inner.copy();m.name='CGH04 '+role+' '+era
        m.node_tree.nodes.clear();out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');bs=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
        bs.inputs['Base Color'].default_value=(.012,.017,.019,1);bs.inputs['Roughness'].default_value=.17;bs.inputs['Metallic'].default_value=.15
        if role=='glass':
            bs.inputs['Base Color'].default_value=(.65,.78,.8,1);bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.46;bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.08
        if role=='core' and era in ('builder','advanced'):
            bs.inputs['Base Color'].default_value=(.8,.12,.006,1);bs.inputs['Emission Color'].default_value=(1,.2,.005,1);bs.inputs['Emission Strength'].default_value=.8
        mats[role]=m
    family={'armor':'head-armor','inner':'black-iron','steel':'machined-steel','edge':'worn-bronze','glass':'protected-glass','optic':'protected-optic','core':'protected-optic'}
    hidden=[];made=[]
    for o in visible:
        if o.get('cg1cRegion')=='head':o.hide_render=True;o.hide_set(True);hidden.append(o.name)
    def p(px,py,depth):return Vector((depth,(788-px)*.0012+.005,(188-py)*.0012+.020))
    def mesh(name,vs,fs,role='armor',sheet=0,bevel=.0007,smooth=False):
        d=bpy.data.meshes.new('CGH04 '+name);d.from_pydata(vs,[],fs);d.update()
        o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.matrix_world=frame.copy()
        o['cgSupervisedHead04']=True;o['cg1cRegion']='head';o['cg2bRegion']='head';o['surfaceRole']=role;o['cgSurfaceFamilies']=json.dumps([family[role],'black-iron','worn-bronze']);o['exteriorEras']='maker,mechanic,builder';o['cgConstructionStatus']='section-loft CG depth hypothesis; acceptance pending'
        for mat in (mats[role],inner,edge):d.materials.append(mat)
        uv=d.uv_layers.new(name='formed-head04')
        for f in d.polygons:
            f.use_smooth=smooth
            for li in f.loop_indices:
                co=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(co.y*2+.5,co.z*2+.5)
        if sheet:
            so=o.modifiers.new('formed sheet return thickness','SOLIDIFY');so.thickness=sheet;so.offset=-1;so.material_offset=1;so.material_offset_rim=2
        if bevel:
            b=o.modifiers.new('machined edge radius','BEVEL');b.width=bevel;b.segments=2
            if not smooth:
                w=o.modifiers.new('retain crease normals','WEIGHTED_NORMAL');w.keep_sharp=True
        made.append(o);return o
    def loft(name,sections,axis='vertical',role='armor',n=16):
        # Eight chamfered/convex transverse sections plus support loops. Closed
        # cross-sections, never two parallel silhouette cards.
        vs=[]
        for section in sections:
            center,other,radius,width=section[:4];offset=section[4] if len(section)>4 else 0
            for k in range(n):
                a=math.tau*k/n
                if axis=='vertical':vs.append(p(other+radius*math.cos(a),center,offset+width*math.sin(a)))
                else:vs.append(p(center,other+radius*math.cos(a),offset+width*math.sin(a)))
        fs=[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(len(sections)-1) for k in range(n)]
        fs += [tuple(range(n-1,-1,-1)),tuple((len(sections)-1)*n+k for k in range(n))]
        return mesh(name,vs,fs,role,0,.0008,True)
    # Cranial loft does not cross the lower cheek opening.
    skull=[(568,191,23,.022),(598,184,60,.068),(646,173,87,.110),(695,164,99,.134),(744,164,101,.153),(792,177,90,.159),(838,198,72,.149),(875,219,48,.113),(900,230,26,.073)]
    loft('nine section cranial vault',skull,'longitudinal','inner')
    bill=[(220,907,10,.091),(237,916,27,.108),(266,921,40,.101),(298,919,49,.085),(332,918,51,.065),(366,927,37,.047),(397,925,27,.032),(430,910,16,.015),(460,885,.8,.0012)]
    loft('nine section convex hooked upper bill',bill)
    # A separately formed saddle closes the transition above the bill root.
    loft('eight section bill root saddle',[(158,878,13,.111),(163,883,15,.114),(174,893,18,.113),(188,906,19,.107),(204,918,19,.100),(217,925,19,.092),(225,927,18,.089),(228,928,17,.088)])
    # Open lower mandible has its own continuous bowed volume, never a closing membrane.
    jaw=[(678,272,13,.116),(696,287,14,.116),(727,303,13,.106),(760,328,12,.094),(787,359,11,.081),(803,388,9,.066),(827,410,7,.047),(853,423,4,.023),(876,423,.8,.001)]
    for side,label in [(-1,'L'),(1,'R')]:
        loft('nine section independent lower mandible '+label,[(x,y,r,.009 if i<7 else .004,side*d) for i,(x,y,r,d) in enumerate(jaw)],'longitudinal')
    # Cheek arch is a joined swept rail; lower edge returns leave a real aperture.
    cheek=[(665,211,13,.122),(684,215,14,.149),(704,232,14,.160),(729,246,13,.165),(757,253,12,.166),(787,254,11,.163),(817,248,12,.155),(842,235,15,.147),(858,220,14,.138)]
    for side,label in [(-1,'L'),(1,'R')]:
        loft('nine section cheek arch with joined returns '+label,[(x,y,r,.010,side*d) for x,y,r,d in cheek],'longitudinal')
    # Four separately formed skull-conforming roof panels: pronounced convex
    # cross-sections and small seams, rather than one broad flat transverse roof.
    for j,(x0,x1,y0,y1,w0,w1) in enumerate([(675,736,53,68,.103,.133),(731,791,67,84,.130,.145),(786,844,84,110,.141,.133),(837,894,106,162,.130,.113)]):
        vs=[];cols=13;rows=6
        for r in range(rows):
            t=r/(rows-1);px=x0+(x1-x0)*t;py=y0+(y1-y0)*t;w=w0+(w1-w0)*t
            for k in range(cols):
                a=-math.pi/2+math.pi*k/(cols-1);vs.append(p(px,py+48*(1-math.cos(a)),w*math.sin(a)))
        mesh('formed dorsal panel '+str(j),vs,[(r*cols+k,r*cols+k+1,(r+1)*cols+k+1,(r+1)*cols+k) for r in range(rows-1) for k in range(cols-1)],sheet=.003)
    def ring(name,cx,cy,rings,side,role='steel',n=64,cap=False):
        vs=[p(cx+r*math.cos(k*math.tau/n),cy+r*math.sin(k*math.tau/n),side*d) for r,d in rings for k in range(n)]
        fs=[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(len(rings)-1) for k in range(n)]
        if cap:fs.append(tuple((len(rings)-1)*n+k for k in range(n)))
        if side<0:fs=[tuple(reversed(f)) for f in fs]
        return mesh(name,vs,fs,role,0,.0005,True)
    for side,label in [(-1,'L'),(1,'R')]:
        # Separate formed orbital sectors carry the seat into the cranial shell.
        for j,(a0,a1) in enumerate([(-175,-105),(-108,-35),(-38,34),(31,100),(97,177)]):
            vs=[]
            for r,d in [(53,.169),(57,.174),(68,.163),(79,.135)]:
                for k in range(13):
                    a=math.radians(a0+(a1-a0)*k/12);vs.append(p(788+r*math.cos(a),188+r*math.sin(a),side*d))
            mesh('formed orbital sector '+label+str(j),vs,[(q*13+k,q*13+k+1,(q+1)*13+k+1,(q+1)*13+k) for q in range(3) for k in range(12)],'armor',.003)
        # True cup walls. Retaining lip x=.190; lens maximum x=.175 = .015 recession.
        ring('recessed optical cup '+label,788,188,[(56,.153),(55,.165),(46,.182),(38,.190),(34,.190),(34,.163),(33,.160)],side,'inner')
        ring('retaining lip '+label,788,188,[(40,.187),(39,.191),(35,.191),(34,.188)],side,'edge')
        ring('dark optical mechanism '+label,788,188,[(32,.162),(0,.162)],side,'optic',cap=True)
        for r in (16,24,29):ring('recessed concentric mechanism '+label+str(r),788,188,[(r,.164),(r+.8,.164)],side,'steel')
        ring('small era core '+label,788,188,[(8,.166),(0,.166)],side,'core',cap=True)
        ring('solid optical glass '+label,788,188,[(33,.169),(26,.173),(15,.175),(0,.175),(0,.171),(15,.171),(26,.170),(33,.166),(33,.169)],side,'glass')
        # Narrow diagonal brow: six stations, folded cross section with real return.
        line=[(677,58,.108),(716,77,.133),(751,103,.151),(788,133,.167),(821,155,.174),(847,171,.167)]
        vs=[]
        for px,py,d in line:
            for dx,dy,dd in [(0,-9,-.008),(0,-3,0),(0,8,.005),(0,13,-.006)]:vs.append(p(px+dx,py+dy,side*(d+dd)))
        fs=[(r*4+k,r*4+k+1,(r+1)*4+k+1,(r+1)*4+k) for r in range(len(line)-1) for k in range(3)]
        mesh('narrow formed diagonal brow '+label,vs,fs,'armor',.003)
        # Interleaved rear leaves follow the skull and have a crest, side folds,
        # curved root and taper. Each is a formed sheet, not an extruded flat card.
        leaves=[(693,85,568,132,.101),(710,108,595,160,.121),(656,123,537,189,.104),(676,153,565,223,.130),(621,167,546,263,.105),(645,204,565,295,.125),(611,229,588,335,.108),(647,254,639,351,.124),(677,278,700,365,.120)]
        for j,(ax,ay,bx,by,dep) in enumerate(leaves):
            vx,vy=bx-ax,by-ay;le=math.hypot(vx,vy);nx,ny=-vy/le,vx/le;vs=[]
            for r in range(7):
                t=r/6;w=(12+7*math.sin(t*math.pi))*(1-t*.96)
                for u in (-1,-.55,0,.55,1):
                    vs.append(p(ax+vx*t+nx*w*u,ay+vy*t+ny*w*u,side*(dep+.012*math.sin(t*math.pi)+.012*(1-abs(u))-.035*t)))
            mesh('formed interleaved crown '+label+str(j),vs,[(r*5+k,r*5+k+1,(r+1)*5+k+1,(r+1)*5+k) for r in range(6) for k in range(4)],'armor',.0028)
        for j,(x,y,r,d) in enumerate([(655,168,24,.119),(679,228,22,.157),(620,218,18,.112)]):
            ring('buried posterior bearing '+label+str(j),x,y,[(r,d),(r,d+.004),(r*.7,d+.008),(r*.55,d+.004),(r*.2,d+.003)],side,'steel')
    bpy.context.view_layer.update()
    return {'module':'cg-supervised-head04','new_mesh_count':len(made),'hidden_originals':hidden,'era':era,'section_count':9,'cross_section_vertices':16,'lens_recess':.015,'sheet_thickness':.0028,'bevel':.0007,'depth_status':'inferred editable CG parameters, not source metrology','material_binding':'ordered cgSurfaceFamilies; no receiving material-name dependency','below_junction_changes':False,'artistic_acceptance':'pending'}
