"""CG2b folded metal shield wings. Non-wing scene objects are read-only.
The pinned composite governs visible construction; hidden surfaces are proposals.
"""
import math,random
import bpy
from mathutils import Vector


def apply(scene,scaffold_path=None,era='builder'):
    prior=[o for o in list(scene.objects) if o.type=='MESH' and
           (o.get('cg1cRegion')=='wing' or o.get('study_part')=='shoulder-wing') and not o.get('cg2bWing')]
    if any(o.get('cg2bWing') for o in scene.objects):raise RuntimeError('CG2b wing already applied; load preserved source for next attempt')
    materials={}
    for o in prior:
        role=o.get('surfaceRole','armor')
        for m in o.data.materials:
            if m:materials.setdefault(role,m)
    for m in bpy.data.materials:
        if m.get('cg2aEra')==era:
            role={'armor':'armor','steel':'edge','bronze':'rivet','machinery':'inner'}.get(m.get('cg2aFamily'))
            if role:materials[role]=m
    materials.setdefault('armor',materials.get('plate'))
    coll=bpy.data.collections.new('CG2b folded shield-wing plates');scene.collection.children.link(coll)
    made=[];counts={'armor':0,'edge':0,'inner':0,'rivet':0};rng=random.Random(20261003)

    def obj(name,vs,fs,uv,role,side,smooth=True):
        d=bpy.data.meshes.new(name);d.from_pydata([tuple(v) for v in vs],[],fs);d.update()
        o=bpy.data.objects.new(name,d);coll.objects.link(o)
        o['cg1cRegion']='wing';o['cg2bRegion']='wing';o['cg2bWing']=True;o['surfaceRole']=role;o['wingSide']=side
        o['exteriorEras']='maker,mechanic,builder';o['detailStatus']='pinned-canon visual proposal, not engineering'
        if materials.get(role):d.materials.append(materials[role])
        layer=d.uv_layers.new(name='CG2b individual leaf UV')
        sign=-1 if side=='left' else 1
        facing=next((f.normal.x for f in d.polygons if abs(f.normal.x)>.10),0)
        flip=facing*sign<0
        for f in d.polygons:
            f.use_smooth=smooth
            if flip:f.flip()
            for li in f.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
        d.update();made.append(o);counts[role]+=1;return o

    # High fixed shoulder root, widening only around the shield's middle, then
    # narrowing toward its low posterior tip. No flight/lift span or flat fan.
    sections=[(.88,.278,.190,.017,.041),(.94,.277,.151,.040,.080),
              (1.02,.270,.088,.071,.155),(1.12,.255,.018,.084,.215),
              (1.23,.232,-.031,.087,.222),(1.31,.213,-.054,.066,.167),
              (1.365,.194,-.035,.027,.075)]
    def section(z):
        if z<=sections[0][0]:return sections[0][1:]
        if z>=sections[-1][0]:return sections[-1][1:]
        for a,b in zip(sections,sections[1:]):
            if a[0]<=z<=b[0]:
                t=(z-a[0])/(b[0]-a[0]);return [a[i]*(1-t)+b[i]*t for i in range(1,5)]
    def surface(side,y,z,lift=0):
        x,cy,rx,ry=section(z);q=(y-cy)/ry
        bulge=math.sqrt(max(.035,1-min(1,q*q)))
        return Vector(((1 if side=='right' else -1)*(x+rx*bulge+lift),y,z))

    outline=[(0,.38),(.13,.47),(.29,.49),(.47,.43),(.67,.32),(.86,.18),(.97,.055),(1.035,0),(.97,-.055),(.86,-.18),(.67,-.32),(.47,-.43),(.29,-.49),(.13,-.47),(0,-.38)]
    def leaf(side,name,root,tip,width,layer):
        # Coordinates: local t down the leaf, u across it. Every feather bends
        # with the folded shield rather than being a rigid planar slab.
        ry,rz=root;ty,tz=tip;delta=Vector((ty-ry,tz-rz));length=delta.length
        along=delta.normalized();across=Vector((-along.y,along.x))
        contour=[];uv=[]
        def sample(t,u,extra=0):
            y=ry+along.x*t*length+across.x*u*width
            z=rz+along.y*t*length+across.y*u*width
            # A slight transverse fold defines sheet metal. No padded dome.
            camber=.00125*(1-min(1,(abs(u)/.49)**2))*math.sin(min(1,t)*math.pi)
            return surface(side,y,z,layer+camber+extra)
        for t,u in outline:contour.append(sample(t,u));uv.append((u+.5,1-t))
        n=len(contour);top=contour+[sample(.42,0)];topuv=uv+[(.5,.58)]
        back=[surface(side,p.y,p.z,layer-.0015) for p in contour]
        verts=top+back;uvs=topuv+uv
        faces=[(n,i,(i+1)%n) for i in range(n)]
        faces += [(i,n+1+i,n+1+(i+1)%n,(i+1)%n) for i in range(n)]
        faces += [tuple(reversed(range(n+1,2*n+1)))]
        o=obj('CG2b '+side+' '+name,verts,faces,uvs,'armor',side)
        for f in o.data.polygons[n:]:f.use_smooth=False
        bevel=o.modifiers.new('Fine forged sheet perimeter','BEVEL');bevel.width=.00035;bevel.segments=2
        # A visibly thin steel cut edge, interrupted near the feather root.
        edge=[];euv=[]
        for k,(t,u) in enumerate(outline):
            if t<.13:continue
            toward=Vector((.43-t,-u));toward.normalize()
            edge.extend([sample(t,u,.00025),sample(t+toward.x*.008,u+toward.y*.022,.00030)])
            euv.extend([(k/n,0),(k/n,1)])
        ef=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(edge)//2-1)]
        obj('CG2b '+side+' '+name+' worn cut rim',edge,ef,euv,'edge',side,False)
        return o,sample(.13,-.18,.0010)

    def rivet(side,name,p,r=.0016):
        sign=-1 if side=='left' else 1;vs=[];uv=[]
        for depth,radius in ((0,r),(.0007,r*.82)):
            for i in range(10):
                a=math.tau*i/10;vs.append(p+Vector((sign*depth,radius*math.cos(a),radius*math.sin(a))));uv.append((.5+.5*math.cos(a),.5+.5*math.sin(a)))
        fs=[(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]+[tuple(range(10,20))]
        obj('CG2b '+side+' '+name+' flush fastener',vs,fs,uv,'rivet',side,False)

    for side in ('left','right'):
        # Deeply inset segmented dark foundation stays below every thin leaf.
        vs=[];uv=[]
        for j in range(14):
            z=.92+j*(.43/13);x,cy,rx,ry=section(z)
            for i in range(17):
                angle=-1.34+i*(2.68/16)
                y=cy+ry*math.sin(angle)
                vs.append(surface(side,y,z,-.008));uv.append((i/16,j/13))
        fs=[(j*17+i,j*17+i+1,(j+1)*17+i+1,(j+1)*17+i) for j in range(13) for i in range(16)]
        obj('CG2b '+side+' inset curved shield foundation',vs,fs,uv,'inner',side)
        # Long nested terminal feathers create a folded tapered outer contour.
        for j in range(12):
            root=(-.210+j*.030,1.288-j*.009)
            tip=(-.075+j*.027,.994-j*.007+(.035 if j<2 else 0))
            width=.047+rng.uniform(-.003,.005)
            leaf(side,'long nested terminal '+str(j),root,tip,width,.006+j*.0003)
        # Progressively shorter coverts ride on different curved planes. The
        # varying overlap is deliberate; no regular square scale lattice.
        for row in range(6):
            root_z=1.334-row*.054
            _,cy,_,ry=section(root_z-.042)
            n=5 if row==0 else 8 if row<4 else 6
            for j in range(n):
                root_y=cy+(-.82+1.64*j/max(1,n-1))*ry
                root=(root_y+rng.uniform(-.009,.009),root_z+rng.uniform(-.008,.006))
                length=.088+row*.010+rng.uniform(-.012,.014)
                tip=(root[0]+.022+row*.006+rng.uniform(-.009,.009),root[1]-length)
                width=.045+rng.uniform(-.005,.009)
                o,p=leaf(side,f'overlapping covert {row} {j}',root,tip,width,.010+(5-row)*.0015)
                if (j+2*row)%4==0:rivet(side,f'covert {row} {j}',p)
        # Upper-breast shoulder courses wrap the attachment; no bare flat rim.
        for j in range(7):
            root=(-.150+j*.035,1.340+rng.uniform(-.002,.003))
            tip=(root[0]+.012,1.256+rng.uniform(-.008,.008))
            _,p=leaf(side,'shoulder overlap '+str(j),root,tip,.051,.023)
            if j%3==0:rivet(side,'shoulder '+str(j),p,.0018)

    for o in prior:
        o.hide_render=True;o.hide_set(True);o['cg2bWingRetired']=True
    bounds={}
    for side in ('left','right'):
        vertices=[o.matrix_world@v.co for o in made if o.get('wingSide')==side for v in o.data.vertices]
        bounds[side]={'min':[min(p[i] for p in vertices) for i in range(3)],'max':[max(p[i] for p in vertices) for i in range(3)]}
    return {'module':'cg2b-wing','oldWingObjectsPreservedHidden':len(prior),'newRoles':counts,'bounds':bounds,
            'shoulderRoots':{'left':[-.195,-.045,1.335],'right':[.195,-.045,1.335]},
            'methods':['Individually editable curved nested long metal feathers and variable coverts','Thin sharp cut rims, sparse flush fasteners, dark recessed underlaps','Fixed high shoulder roots; compact folded shield envelope without lift surfaces'],
            'limits':['Unseen posterior construction is a visual proposal','New outer feather coverage extends the old wing envelope locally; likeness awaits matched review','No engineering or flight claim']}
