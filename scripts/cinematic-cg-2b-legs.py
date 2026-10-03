"""Milestone 2b: heavy avian bearing packs, open paired actuators and armored talons.
Adds separately editable UV meshes around the exact inherited stance. Source mesh
coordinates, UVs, transforms and material slots are untouched. Only the two exposed
rounded thigh skins may be hidden; all original geometry remains in the native file.
Fictional screen construction, not a fabrication or load-bearing design.
"""
import hashlib, math, struct
import bpy
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    if any(o.get('cg2bLegOwner') for o in scene.objects):
        return {'module':'cg2b-legs','disposition':'already applied; no duplicate construction'}
    source=[o for o in scene.objects if o.type=='MESH' and (o.get('cg1cRegion') in ('leg','foot') or o.get('study_part')=='legs') and not o.get('cg2bRegion')]
    def digest(o):
        h=hashlib.sha256()
        for row in o.matrix_world:
            for v in row:h.update(struct.pack('<d',v))
        for v in o.data.vertices:
            for q in v.co:h.update(struct.pack('<d',q))
        for p in o.data.polygons:
            h.update(struct.pack('<I',len(p.vertices)))
            for q in p.vertices:h.update(struct.pack('<I',q))
            h.update(struct.pack('<I',p.material_index))
        for uv in o.data.uv_layers:
            h.update(uv.name.encode())
            for q in uv.data:
                for v in q.uv:h.update(struct.pack('<d',v))
        for m in o.data.materials:h.update((m.name if m else '<none>').encode())
        return h.hexdigest()
    original={o.name:digest(o) for o in source}
    source_visibility={o.name:o.hide_render for o in source}
    materials={}
    for o in source:
        if o.data.materials:materials.setdefault((o.get('cg1cRegion'),o.get('surfaceRole')),list(o.data.materials))
    coll=bpy.data.collections.new('CG2b heavy legs and ringed talon caps');scene.collection.children.link(coll)
    made=[];counts={};anchors={};hidden=[];talon_extent={}
    def mesh(name,vertices,faces,uvs,region,role,smooth=False):
        d=bpy.data.meshes.new(name)
        if region=='foot':vertices=[Vector((v[0],v[1],max(.0135,v[2]))) for v in vertices]
        d.from_pydata([tuple(v) for v in vertices],[],faces);d.update()
        o=bpy.data.objects.new(name,d);coll.objects.link(o)
        o['cg1cRegion']=region;o['cg2bRegion']=region;o['cg2bLegOwner']=True
        o['surfaceRole']=role;o['cg1cMaterialFamily']='machinery-steel'
        o['exteriorEras']='maker,mechanic,builder';o['era']=era
        o['cg2bConstructionStatus']='Inferred cinematic exterior proposal; stance inherited'
        key={'armor':'plate','shaft':'bearing'}.get(role,role)
        inherited=materials.get((region,key),materials.get(('leg',key),materials.get((region,'inner'),[])))
        for m in inherited:d.materials.append(m)
        layer=d.uv_layers.new(name='cg2b-leg-uv')
        for p in d.polygons:
            p.use_smooth=smooth
            for li in p.loop_indices:layer.data[li].uv=uvs[d.loops[li].vertex_index]
        made.append(o);counts[region+'/'+role]=counts.get(region+'/'+role,0)+1
        return o
    def basis(axis):
        a=Vector(axis).normalized();u=a.cross(Vector((0,0,1)))
        if u.length<.05:u=a.cross(Vector((0,1,0)))
        u.normalize();return a,u,a.cross(u).normalized()
    def tube(name,points,radii,region='leg',role='shaft',n=16,ellipse=1):
        pts=[Vector(p) for p in points];vs=[];uv=[];fs=[]
        for j,(p,r) in enumerate(zip(pts,radii)):
            a,u,v=basis(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)])
            for i in range(n):
                t=math.tau*i/n;vs.append(p+r*(u*math.cos(t)+ellipse*v*math.sin(t)));uv.append((i/n,j/max(1,len(pts)-1)))
        for j in range(len(pts)-1):
            for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        fs += [tuple(reversed(range(n))),tuple(range((len(pts)-1)*n,len(pts)*n))]
        return mesh(name,vs,fs,uv,region,role,True)
    def annulus(name,p,axis,outer,inner,depth,region='leg',role='bearing',n=32,ellipse=1):
        p=Vector(p);a,u,v=basis(axis);vs=[];uv=[];fs=[]
        # A true four-ring annular mesh, including the inner wall; no filled disk.
        for z,r in [(-depth/2,outer),(depth/2,outer),(depth/2,inner),(-depth/2,inner)]:
            for i in range(n):
                t=math.tau*i/n;vs.append(p+a*z+r*(u*math.cos(t)+ellipse*v*math.sin(t)));uv.append((i/n,(z/depth+.5)*.45+.5*(r/outer)))
        for band in range(4):
            k=(band+1)%4
            for i in range(n):fs.append((band*n+i,band*n+(i+1)%n,k*n+(i+1)%n,k*n+i))
        o=mesh(name,vs,fs,uv,region,role)
        bevel=o.modifiers.new('Fine hard manufactured ring edge','BEVEL');bevel.width=.0007;bevel.segments=2
        return o
    def prism(name,center,axis,outline,thick,region='leg',role='armor'):
        # Long axis and the y/z perpendicular span a web; thickness is x.
        c=Vector(center);a=Vector(axis).normalized();x=Vector((1,0,0));v=a.cross(x).normalized();vs=[];uv=[]
        for sign in (-1,1):
            for u,w in outline:vs.append(c+a*u+v*w+x*(thick*sign/2));uv.append((w/.12+.5,u/.25+.5))
        n=len(outline);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
        fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        o=mesh(name,vs,fs,uv,region,role)
        b=o.modifiers.new('Crisp clevis cut edge','BEVEL');b.width=.0008;b.segments=2
        return o
    def slotted_web(name,a,b,xoffset,width,region='leg'):
        # Separate rail strips and end straps form a genuinely open long aperture.
        axis=(b-a).normalized();v=axis.cross(Vector((1,0,0))).normalized();c=(a+b)/2+Vector((xoffset,0,0));length=(b-a).length
        for sign in (-1,1):
            shape=[(-length*.45,sign*width*.45),(-length*.48,sign*width*.21),(-length*.30,sign*width*.15),
                   (length*.31,sign*width*.15),(length*.47,sign*width*.24),(length*.43,sign*width*.49)]
            prism(name+' split rail '+str(sign),c,axis,shape,.009,region)
        for q in (-.43,.43):
            end=c+axis*length*q
            prism(name+' transverse strap '+str(q),end,axis,[(-.011,-width*.43),(-.011,width*.43),(.011,width*.43),(.011,-width*.43)],.010,region,'edge')
    def fastener(name,p,axis,r=.0035,region='leg'):
        p=Vector(p);a=Vector(axis).normalized()
        return tube(name,[p,p+a*.0024],[r,r*.87],region,'rivet',8)
    def center(o):return sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
    def section_centers(o,n=12):
        vs=[o.matrix_world@v.co for v in o.data.vertices]
        return [sum(vs[i:i+n],Vector())/n for i in range(0,len(vs),n)]
    for side,sgn in [('left',-1),('right',1)]:
        joints={j:center(next(o for o in source if o.name==f'CG1c {side} {j} concentric hinge')) for j in ('hip','knee','hock','ankle')}
        anchors[side]={k:list(v) for k,v in joints.items()}
        # The old rounded skin is retained but recessed from the CG presentation.
        skins=[o for o in source if o.name==f'L {side} rounded upper thigh']
        for o in skins:
            o.hide_render=True;o.hide_set(True);o['cg2bLegSkinRetained']=True;hidden.append(o.name)
        # Large side-facing industrial stacks, with actual annular recesses and
        # stepped edge profiles rather than spherical skins or toy joint balls.
        for j,r in [('hip',.068),('knee',.076),('hock',.056),('ankle',.047)]:
            p=joints[j];face=p+Vector((sgn*.055,0,0));hole=r*.35
            annulus(f'CG2b {side} {j} forged outer bearing flange',face,(1,0,0),r,hole,.015)
            annulus(f'CG2b {side} {j} dark split bearing race',face+Vector((sgn*.012,0,0)),(1,0,0),r*.87,hole*1.08,.006,role='inner')
            annulus(f'CG2b {side} {j} machined stepped front ring',face+Vector((sgn*.018,0,0)),(1,0,0),r*.82,hole*1.12,.007,role='edge')
            # A small axle through the recess leaves the dark annular gap exposed.
            tube(f'CG2b {side} {j} retained axis locking boss',[face-Vector((sgn*.004,0,0)),face+Vector((sgn*.024,0,0))],[r*.20,r*.16],role='bearing',n=12)
            annulus(f'CG2b {side} {j} boss washer',face+Vector((sgn*.020,0,0)),(1,0,0),r*.25,r*.13,.004,role='shaft',n=20)
            for i in range(6):
                t=math.tau*i/6+.16
                fastener(f'CG2b {side} {j} captive flange bolt {i}',face+Vector((sgn*.023,r*.65*math.cos(t),r*.65*math.sin(t))),(sgn,0,0),.0032 if j in ('hip','knee') else .0028)
            # The medial face is visible across the far leg in the canon angle.
            # It receives a hard stepped ring too, avoiding a smooth ball read.
            medial=p-Vector((sgn*.039,0,0))
            annulus(f'CG2b {side} {j} medial bearing flange',medial,(1,0,0),r*.91,hole,.011)
            annulus(f'CG2b {side} {j} medial recessed race',medial-Vector((sgn*.010,0,0)),(1,0,0),r*.80,hole*1.10,.006,role='inner')
            annulus(f'CG2b {side} {j} medial steel lip',medial-Vector((sgn*.014,0,0)),(1,0,0),r*.78,hole*1.15,.005,role='edge')
            for i in range(4):
                t=math.tau*i/4+.35
                fastener(f'CG2b {side} {j} medial bolt {i}',medial+Vector((-sgn*.018,r*.62*math.cos(t),r*.62*math.sin(t))),(-sgn,0,0),.0028)
            # Two clevis arms meet the nearby member with a real open central jaw.
            nextj='knee' if j=='hip' else 'hock' if j=='knee' else 'ankle' if j=='hock' else 'hock'
            axis=(joints[nextj]-p).normalized()
            for lateral in (-1,1):
                offset=Vector((sgn*(.049+lateral*.019),0,0))
                shape=[(r*.34,-r*.28),(r*1.42,-r*.24),(r*1.63,-r*.06),(r*1.40,r*.25),(r*.34,r*.30)]
                prism(f'CG2b {side} {j} clevis cheek {lateral}',p+offset,axis,shape,.010,role='bearing')
        for label,ja,jb,width in [('upper','hip','knee',.090),('shank','knee','hock',.089),('tarsus','hock','ankle',.077)]:
            a=joints[ja];b=joints[jb];axis=(b-a).normalized();v=axis.cross(Vector((1,0,0))).normalized();length=(b-a).length
            # Added external members are visibly wider than the inherited tube.
            for k,off in enumerate((-.032,.034)):
                shift=Vector((sgn*.054,0,0))+v*off
                p=a+axis*length*.15+shift;q=b-axis*length*.12+shift
                sleeve_end=p.lerp(q,.58 if k==0 else .47)
                tube(f'CG2b {side} {label} actuator barrel {k}',[p,p.lerp(sleeve_end,.08),sleeve_end],[.0145,.0155,.0135],role='inner',n=20)
                tube(f'CG2b {side} {label} exposed bright piston {k}',[sleeve_end-axis*.012,q],[.0075,.0075],role='shaft',n=16)
                for t,r in ((0,.018),(.13,.017),(.47,.016),(.59,.015)):
                    c=p.lerp(q,t)
                    if t>.5 and k==1:continue
                    annulus(f'CG2b {side} {label} barrel collar {k} {t}',c,axis,r,.011,.006,role='bearing',n=20)
                for end,pt in [('root',p),('tip',q)]:
                    annulus(f'CG2b {side} {label} actuator eye {k} {end}',pt,(1,0,0),.018,.007,.012,role='bearing',n=20)
            # A slimmer medial actuator pair completes the far leg's exposed
            # construction. Their separated barrels leave real negative gaps.
            for k,off in enumerate((-.036,.030)):
                shift=Vector((-sgn*.047,0,0))+v*off
                p=a.lerp(b,.20)+shift;q=a.lerp(b,.85)+shift;end=p.lerp(q,.50+.07*k)
                tube(f'CG2b {side} {label} medial actuator sleeve {k}',[p,end],[.0125,.012],role='inner',n=16)
                tube(f'CG2b {side} {label} medial exposed rod {k}',[end-axis*.008,q],[.006,.006],role='shaft',n=12)
                for pt,nm in [(p,'root'),(end,'seal')]:
                    annulus(f'CG2b {side} {label} medial seal {k} {nm}',pt,axis,.015,.009,.006,role='bearing',n=20)
            # Narrow tension rod sits on a third plane; it is not another sleeve.
            shift=Vector((sgn*.032,0,0))+v*.055
            p=a.lerp(b,.18)+shift;q=a.lerp(b,.85)+shift
            tube(f'CG2b {side} {label} slender tension rod',[p,q],[.0042,.0042],role='shaft',n=12)
            for t in (.10,.87):
                c=p.lerp(q,t)
                tube(f'CG2b {side} {label} tension locknut {t}',[c-axis*.004,c+axis*.004],[.0075,.0075],role='rivet',n=6)
            # The split side web is open between its rails, with the actuator
            # pair crossing the window on another depth plane.
            slotted_web(f'CG2b {side} {label} open cast web',a.lerp(b,.15),a.lerp(b,.86),sgn*.077,width)
            for t in (.23,.72):
                c=a.lerp(b,t)+Vector((sgn*.083,0,0))
                fastener(f'CG2b {side} {label} strap outer screw {t}',c,(sgn,0,0),.003)
        # Shin-to-foot split horseshoe collar; no foot anchor translation.
        ankle=joints['ankle'];foot=next(o for o in source if o.name==f'CG1c {side} plantar foot housing');plant=center(foot)
        annulus(f'CG2b {side} armored ankle ferrule',ankle+Vector((0,-.008,-.012)),(0,-.28,1),.054,.027,.017,'foot','bearing',28,.82)
        for i in range(3):
            y=plant.y-.011-i*.024;z=.095-i*.009
            strap_vs=[Vector((plant.x+dx,y+dy,z+dz)) for dz in (-.0035,.0035) for dx,dy in [(-.048,-.008),(.048,-.008),(.044,.010),(-.044,.010)]]
            mesh(f'CG2b {side} angular dorsum strap {i}',strap_vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],[(0,0),(1,0),(1,1),(0,1)]*2,'foot','armor')
            for off in (-1,1):fastener(f'CG2b {side} dorsum strap bolt {i} {off}',Vector((plant.x+off*.043,y,z+.003)),(0,0,1),.003,'foot')
        toes=[o for o in source if o.get('cg1cRegion')=='foot' and side in o.name and 'dark tendon chassis' in o.name]
        for toe in toes:
            label=toe.name.replace('CG1c ','').replace(' dark tendon chassis','');a,b=section_centers(toe);axis=(b-a).normalized()
            horizontal=Vector((axis.x,axis.y,0)).normalized();across=Vector((-horizontal.y,horizontal.x,0))
            # Deep knuckle armor has flattened plantar surfaces. The empty
            # spaces between rings are actual geometry gaps, not texture marks.
            for i in range(5):
                t=(i+1)/6;pt=a.lerp(b,t);rad=.037-i*.0019
                annulus('CG2b '+label+' deep armored knuckle '+str(i),pt,axis,rad,rad-.0065,.0155,'foot','armor',24,.72)
                annulus('CG2b '+label+' crisp ring lip '+str(i),pt+axis*.0078,axis,rad*.99,rad-.0030,.0030,'foot','edge',24,.72)
                if i%2==0:
                    fastener('CG2b '+label+' knuckle lock '+str(i),pt+Vector((0,0,rad*.73)),(0,0,1),.0025,'foot')
            for sign in (-1,1):
                # Small side linkage bars bind pairs without sealing the ring gaps.
                for i in (0,2):
                    p=a.lerp(b,(i+1)/6)+across*(.036-i*.0017)*sign
                    q=a.lerp(b,(i+2.1)/6)+across*(.034-i*.0017)*sign
                    tube('CG2b '+label+' side hinge link '+str(sign)+' '+str(i),[p,q],[.0038,.0038],'foot','bearing',10)
            # Broader curved armor cap keeps source tip/foot untouched but
            # projects a new pointed hook .025 beyond the source tip.
            old=next(o for o in source if o.name==f'CG1c {label} recurved steel talon')
            oldpts=section_centers(old);source_tip=oldpts[-1];proposal_tip=source_tip+horizontal*.025+Vector((0,0,.001))
            points=[b-axis*.007,oldpts[1]+Vector((0,0,.003)),oldpts[2]+Vector((0,0,.001)),source_tip+Vector((0,0,.003)),proposal_tip]
            radii=[.028,.027,.021,.007,.0008];vs=[];uv=[];fs=[];n=14
            for j,(pt,r) in enumerate(zip(points,radii)):
                # Flattened underside, domed blade and a narrow upper ridge.
                for k in range(n):
                    t=math.tau*k/n;h=math.sin(t);height=r*(.97 if h>=0 else .58)*h
                    pos=pt+across*(r*.87*math.cos(t))+Vector((0,0,height))
                    pos.z=max(.015,pos.z);vs.append(pos);uv.append((k/n,j/(len(points)-1)))
            for j in range(len(points)-1):
                for k in range(n):fs.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
            fs += [tuple(reversed(range(n))),tuple(range((len(points)-1)*n,len(points)*n))]
            mesh('CG2b '+label+' heavy pointed hook cap',vs,fs,uv,'foot','talon',True)
            annulus('CG2b '+label+' talon root armor cuff',b-axis*.004,axis,.032,.024,.010,'foot','bearing',24,.70)
            # A restrained blade spine makes the tapered hook read as forged metal.
            spine=[points[0]+Vector((0,0,.027)),points[1]+Vector((0,0,.027)),points[2]+Vector((0,0,.021)),points[3]+Vector((0,0,.006)),proposal_tip]
            tube('CG2b '+label+' forged hook ridge',spine,[.0015,.0015,.001,.0007,.0003],'foot','edge',6)
            talon_extent[label]={'sourceTip':list(source_tip),'addedTip':list(proposal_tip),'horizontalExtension':.025,'sourceToeEndpoints':[list(a),list(b)]}
    after={o.name:digest(o) for o in source}
    assert original==after,'Original leg/foot mesh, UV, transform or material payload changed'
    bounds={}
    for region in ('leg','foot'):
        vs=[o.matrix_world@v.co for o in made if o.get('cg2bRegion')==region for v in o.data.vertices]
        bounds[region]={'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)]}
    return {'module':'cg2b-legs','sourceObjectsRetained':len(source),'sourcePayloadPreserved':True,
            'sourcePayloadSHA256':original,'sourceVisibilityBefore':source_visibility,
            'exposedRoundedSkinsRetainedHidden':hidden,'anchorsUnchanged':anchors,
            'newMeshCounts':counts,'addedBounds':bounds,'talonExteriorProposals':talon_extent,
            'methods':['Compact stepped annular bearing packs and split articulated clevis cheeks','Wider paired actuator barrels, unequal exposed shafts, narrow tension rods and real open rail windows','Deep separate knuckle rings, broader forged talon caps and sparse fasteners'],
            'limits':['New details and .025-unit talon extension are cinematic exterior proposals inferred from the locked composite','All source leg/foot meshes, UVs, transforms, material slots and approved anchors retained','Thigh plates remain inherited; construction is not engineering validated','Final surface finish and artistic likeness require integrator and owner review']}
