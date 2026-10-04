"""Source-landmark head reconstruction on preserved supervised attempt01.
July HEAD ONLY supplies contours; transverse depth is an editable CG proposal.
"""
import math
import json
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


def apply(scene, root_path=None, era='builder'):
    if any(o.get('cgSupervisedHead03') for o in scene.objects):
        raise RuntimeError('Reload preserved attempt01 before applying head03')
    if any(o.get('cgSupervisedFace02') for o in scene.objects):
        raise RuntimeError('Head03 must not receive rejected face02')
    frame=scene.objects['CG2b head frame'].matrix_world.copy()
    mats={}
    for role,name in {'plate':'CGH01 swept crown leaf 0 0','bill':'CGH01 formed bill L 0 0','inner':'CGH01 recessed cranial structure','bearing':'CGH01 jaw tendon L 0'}.items():
        mats[role]=scene.objects[name].data.materials[0]
    # Copy the existing role graph for warm cut edges; original materials untouched.
    edge=mats['plate'].copy();edge.name='CGH03 inherited warm cut edge'
    bs=edge.node_tree.nodes.get('Principled BSDF')
    if bs:
        for l in list(bs.inputs['Base Color'].links):edge.node_tree.links.remove(l)
        bs.inputs['Base Color'].default_value=(.18,.105,.039,1)
        bs.inputs['Metallic'].default_value=.8;bs.inputs['Roughness'].default_value=.42
    mats['edge']=edge
    optic=mats['inner'].copy();optic.name='CGH03 recessed lens '+era
    bs=optic.node_tree.nodes.get('Principled BSDF')
    if bs:
        for socket in ('Base Color','Emission Color','Emission Strength'):
            for l in list(bs.inputs[socket].links):optic.node_tree.links.remove(l)
        bs.inputs['Base Color'].default_value=(.08,.024,.004,1) if era=='builder' else (.006,.009,.008,1)
        bs.inputs['Emission Color'].default_value=(.9,.18,.012,1)
        bs.inputs['Emission Strength'].default_value=.9 if era=='builder' else 0
        bs.inputs['Metallic'].default_value=.65;bs.inputs['Roughness'].default_value=.23
    mats['optic']=optic
    hidden=[];made=[]
    for o in list(scene.objects):
        if o.type=='MESH' and not o.hide_render and o.get('cg1cRegion')=='head':
            o.hide_render=True;o.hide_set(True);hidden.append(o.name)
    def point(px,py,depth,side=1):
        return Vector((side*depth,(788-px)*.0012+.005,(188-py)*.0012+.020))
    def mesh(name,vs,fs,role='plate',thickness=.003,bevel=.0006,smooth=False):
        d=bpy.data.meshes.new('CGH03 '+name);d.from_pydata(vs,[],fs);d.update()
        o=bpy.data.objects.new('CGH03 '+name,d);scene.collection.objects.link(o);o.matrix_world=frame.copy()
        o['cgSupervisedHead03']=True;o['cg1cRegion']='head';o['cg2bRegion']='head';o['surfaceRole']=role
        o['exteriorEras']='maker,mechanic,builder';o['cgConstructionStatus']='source contour, inferred transverse depth; owner acceptance pending'
        d.materials.append(mats[role]);d.materials.append(mats['inner']);d.materials.append(edge)
        o['cgSurfaceFamilies']=json.dumps([{'plate':'head-armor','bill':'head-armor','inner':'black-iron','bearing':'machined-steel','edge':'worn-bronze','optic':'protected-optic'}[role],'black-iron','worn-bronze'])
        uv=d.uv_layers.new(name='source-head03-form')
        for p in d.polygons:
            p.use_smooth=smooth
            for li in p.loop_indices:
                q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(q.y*2+.5,q.z*2+.5)
        if thickness:
            so=o.modifiers.new('dark cut thickness','SOLIDIFY');so.thickness=thickness;so.offset=-1;so.material_offset=1;so.material_offset_rim=2
        if bevel:
            b=o.modifiers.new('restrained edge','BEVEL');b.width=bevel;b.segments=2
            b.affect='EDGES'
            w=o.modifiers.new('hard surface normals','WEIGHTED_NORMAL');w.keep_sharp=True;w.weight=35
        made.append(o);return o
    def plate(name,poly,side,depth=.16,role='plate',thickness=.003):
        vs=[point(x,y,depth(x,y) if callable(depth) else depth,side) for x,y in poly]
        # Triangulate in source plane, retaining inferred 3D thickness separately.
        flat=[Vector((x,y,0)) for x,y in poly];tris=tessellate_polygon([flat])
        fs=[tuple(v if isinstance(v,int) else flat.index(v) for v in tri) for tri in tris]
        if side<0:fs=[tuple(reversed(f)) for f in fs]
        return mesh(name,vs,fs,role,thickness)
    def annulus(name,cx,cy,inner,outer,depth,side,role='bearing',segments=80):
        vs=[]
        for r,xoff in [(inner,0),(outer,0)]:
            for k in range(segments):
                a=2*math.pi*k/segments;vs.append(point(cx+r*math.cos(a),cy+r*math.sin(a),depth+xoff,side))
        fs=[(k,(k+1)%segments,(k+1)%segments+segments,k+segments) for k in range(segments)]
        return mesh(name,vs,fs,role,.0025,.00045)
    # Side vault is four separate plated sectors surrounding a large true orbital seat.
    orbit=(788,188)
    for side,label in [(-1,'L'),(1,'R')]:
        for j,(a0,a1) in enumerate([(-158,-90),(-90,-16),(-16,56),(56,135),(135,202)]):
            vs=[]
            for r,dep in [(59,.164),(84,.146)]:
                for k in range(18):
                    a=math.radians(a0+(a1-a0)*k/17);vs.append(point(788+r*math.cos(a),188+r*math.sin(a),dep,side))
            mesh('layered orbital vault '+label+str(j),vs,[(i,i+1,i+19,i+18) for i in range(17)],'plate',.005)
        for n,ri,ro,d,role in [('outer seat',50,60,.165,'edge'),('recess groove',46,51,.162,'inner'),('machined inner seat',39,46,.169,'bearing'),('lens retaining rim',34,39,.172,'edge')]:
            annulus(n+' '+label,788,188,ri,ro,d,side,role)
        # Lens surface and concentric restrained emission sit behind thin metal rims.
        vs=[point(788,188,.164,side)]+[point(788+34*math.cos(k*math.tau/80),188+34*math.sin(k*math.tau/80),.166,side) for k in range(80)]
        mesh('dark recessed optic '+label,vs,[(0,k+1,(k+1)%80+1) for k in range(80)],'optic',0,0)
        for rad in [21,27,31]:annulus('optic concentric engraving '+label+str(rad),788,188,rad,rad+1.2,.169,side,'edge')
        # One sloping forehead plate: unmistakably ABOVE the optic.
        plate('diagonal forehead brow '+label,[(675,52),(695,48),(761,70),(827,95),(871,126),(899,160),(858,157),(847,182),(819,163),(790,139),(755,115),(736,89)],side,lambda x,y:.11+.00047*(y-50),'plate',.004)
        plate('bill root saddle '+label,[(869,159),(895,163),(923,190),(942,222),(915,215),(884,237),(869,269),(853,277),(826,261),(844,237),(857,211)],side,lambda x,y:.159-.00043*(x-860),'bill',.004)
        # Convex leaf bill: deep broad root, rounded front, backward pointed tip.
        bill=[(916,220),(940,233),(956,261),(968,293),(972,324),(967,356),(955,387),(934,414),(912,438),(885,460),(899,425),(899,395),(887,369),(872,349),(857,337),(866,310),(877,280),(888,251),(900,231)]
        plate('broad leaf upper bill '+label,bill,side,lambda x,y:max(.018,.127-(x-916)*.00105-(y-235)*.00027),'bill',.004)
        plate('upper bill root overlay '+label,[(887,226),(911,215),(935,226),(944,247),(920,236),(903,253),(892,281),(883,312),(870,336),(857,328),(867,294)],side,lambda x,y:.147-(x-885)*.001-.00015*(y-226),'plate',.003)
        # Distinct lower cheek hardware, tucked into skull. Aperture remains real.
        plate('articulated cheek sweep '+label,[(667,188),(690,181),(712,186),(729,207),(748,226),(774,237),(807,241),(838,232),(855,219),(852,242),(825,257),(795,264),(758,260),(729,249),(707,228),(687,211)],side,.175,'plate',.004)
        plate('cheek rear jaw carrier '+label,[(667,222),(683,222),(687,251),(713,279),(733,294),(719,309),(689,291),(662,265),(653,248)],side,.149,'plate',.004)
        jaw=[(676,263),(698,271),(731,291),(764,313),(792,340),(809,371),(825,395),(847,410),(876,423),(851,426),(826,419),(806,405),(791,382),(777,354),(754,334),(725,316),(697,305),(679,293),(666,277)]
        plate('nested curved lower mandible '+label,jaw,side,lambda x,y:.126-.00023*(y-265),'bill',.003)
        plate('mandible warm inset rail '+label,[(699,291),(731,303),(765,325),(786,350),(800,380),(817,405),(837,416),(819,411),(801,389),(786,363),(764,337),(730,315),(705,308)],side,lambda x,y:.131-.00023*(y-265),'edge',.0015)
        # Rear round mechanisms are tucked between individual feather ends.
        for k,(cx,cy,rad,d) in enumerate([(654,161,26,.139),(691,154,20,.146),(680,232,23,.161),(621,212,19,.111),(623,285,17,.096)]):
            annulus('posterior gear outer '+label+str(k),cx,cy,rad*.67,rad,d,side,'plate')
            annulus('posterior gear warm ring '+label+str(k),cx,cy,rad*.45,rad*.62,d+.003,side,'edge')
            annulus('posterior gear inner '+label+str(k),cx,cy,rad*.10,rad*.45,d+.005,side,'bearing')
        # Individually traced pointed crown feathers; all overlap the rear vault.
        feathers=[[(702,67),(675,65),(627,80),(594,101),(645,96),(687,85)],[(731,84),(702,78),(661,99),(619,118),(685,108),(712,100)],[(671,93),(633,96),(580,121),(550,136),(606,126),(651,112)],[(636,117),(599,126),(559,155),(530,183),(582,164),(620,143)],[(724,107),(699,111),(672,138),(647,157),(688,149),(714,130)],[(611,148),(580,166),(552,193),(535,215),(573,195),(600,180)],[(630,171),(607,181),(581,216),(555,246),(594,229),(618,204)],[(592,214),(574,239),(555,272),(550,306),(576,282),(598,247)],[(617,236),(602,257),(590,293),(585,327),(607,310),(626,275)],[(647,266),(631,288),(629,328),(642,362),(651,329),(656,295)],[(669,293),(655,315),(664,353),(693,385),(688,350),(684,322)],[(600,279),(580,301),(587,340),(610,370),(613,337)],[(704,313),(693,334),(710,367),(744,393),(734,358)]]
        for k,p in enumerate(feathers):
            plate('pointed crown contour '+label+' %02d'%k,p,side,lambda x,y:.12-abs(y-180)*.00033+(x-630)*.00011,'plate',.003)
    # Broad transverse cap joins the two source-contour sides, using five unequal
    # tapering plates. This is inferred depth, not a copied July body feature.
    for k,(start,end,z0,z1,w0,w1) in enumerate([(705,786,64,86,.08,.12),(654,751,76,105,.105,.13),(601,712,103,124,.10,.13),(566,676,132,154,.075,.12),(550,635,172,192,.06,.115)]):
        vs=[]
        for j in range(17):
            t=j/16;px=start+(end-start)*t;py=z0+(z1-z0)*t;w=w0+(w1-w0)*t
            for i in range(15):
                u=(i/14-.5)*2;v=point(px,py+18*u*u,w*u);vs.append(v)
        mesh('transverse crown pointed plate '+str(k),vs,[(j*15+i,j*15+i+1,(j+1)*15+i+1,(j+1)*15+i) for j in range(16) for i in range(14)],'plate',.003)
    # Narrow midline bill surface connects side leaves without a bulbous hook.
    outline=[(916,220,.127),(940,233,.097),(956,261,.074),(968,293,.050),(972,324,.035),(967,356,.027),(955,387,.024),(934,414,.022),(912,438,.018),(885,460,.003)]
    vs=[]
    for px,py,w in outline:
        for i in range(13):
            u=i/12*2-1;vs.append(point(px+6*(1-u*u),py,w*u))
    mesh('connected bill leading ridge',vs,[(j*13+i,j*13+i+1,(j+1)*13+i+1,(j+1)*13+i) for j in range(len(outline)-1) for i in range(12)],'bill',.003)
    bpy.context.view_layer.update()
    return {'module':'cg-supervised-head03','era':era,'new_mesh_count':len(made),'hidden_originals':hidden,'head_frame':[list(r) for r in frame],'source_landmarks':'assets/audit/cg-supervised-head03/source-plan.md','transverse_depth':'inferred CG proposal','face02_applied':False,'artistic_acceptance':'pending','below_junction_changes':False}
