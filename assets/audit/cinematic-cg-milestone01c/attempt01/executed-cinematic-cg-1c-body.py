"""CG detailing on owner-directed study05 coordinates; no scene reset or camera changes."""
from pathlib import Path
import json, math, random
import bpy
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    source=Path(scaffold_path) if scaffold_path else Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/basic-shape-study05/study.json')
    if source.suffix=='.blend':source=source.with_name('study.json')
    spec=json.loads(source.read_text());shapes=spec['shapes'];rng=random.Random(105)
    coll=bpy.data.collections.new('CG 1c body wing and avian legs');scene.collection.children.link(coll)
    counts={};mats={}
    for role,col in {'plate':(.105,.145,.13,1),'inner':(.022,.025,.027,1),'bearing':(.17,.14,.09,1),'rivet':(.25,.20,.12,1),'edge':(.07,.06,.042,1),'talon':(.16,.18,.19,1)}.items():
        m=bpy.data.materials.new('CG1c temporary '+role);m.diffuse_color=col;m.use_nodes=True
        p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=col;p.inputs['Metallic'].default_value=.72;p.inputs['Roughness'].default_value=.53;mats[role]=m
    def tag(o,region,role):
        o['cg1cRegion']=region;o['surfaceRole']=role;o['exteriorEras']='maker,mechanic,builder';o['era']=era
        o.data.materials.clear();o.data.materials.append(mats[role]);counts[region+'/'+role]=counts.get(region+'/'+role,0)+1
        return o
    def mesh(name,vs,fs,region,role,smooth=True):
        d=bpy.data.meshes.new(name);d.from_pydata([tuple(v) for v in vs],[],fs);d.update();o=bpy.data.objects.new(name,d);coll.objects.link(o);tag(o,region,role)
        for p in d.polygons:p.use_smooth=smooth
        uv=d.uv_layers.new(name='surface-uv')
        for p in d.polygons:
            for li in p.loop_indices:
                co=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(co.x*3+co.y*2,co.z*3)
        return o
    def tube(name,pts,radii,region,role,n=12):
        pts=[Vector(p) for p in pts];vs=[];fs=[]
        for j,(p,r) in enumerate(zip(pts,radii)):
            a=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized();u=a.cross(Vector((0,0,1)))
            if u.length<.1:u=a.cross(Vector((0,1,0)))
            u.normalize();v=a.cross(u).normalized()
            vs.extend([p+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n)) for i in range(n)])
        for j in range(len(pts)-1):
            for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        fs.extend([tuple(reversed(range(n))),tuple(range((len(pts)-1)*n,len(pts)*n))]);return mesh(name,vs,fs,region,role)
    def bar(name,a,b,r,region='leg',role='inner'):
        return tube(name,[a,b],[r,r],region,role)
    def ring(name,p,axis,r,thick,region='leg',role='bearing'):
        p=Vector(p);a=Vector(axis).normalized();return tube(name,[p-a*thick/2,p+a*thick/2],[r,r],region,role,20)
    def rivet(name,p,n,region,r=.0021):
        p=Vector(p);n=Vector(n).normalized();return tube(name,[p,p+n*.0018],[r,r*.8],region,'rivet',8)
    outline=[(-.40,0),(.40,0),(.49,.25),(.46,.64),(.28,.88),(0,1),(-.27,.91),(-.47,.64),(-.49,.25)]
    def plate(name,fn,w,h,region):
        vs=[fn(u*w,v*h,.0045) for u,v in outline];n=len(vs);vs+=[fn(0,h*.4,.005)];vs+=[fn(u*w,v*h,.001) for u,v in outline];fs=[]
        for i in range(n):fs.extend([(n,i,(i+1)%n),(i,n+1+i,n+1+(i+1)%n,(i+1)%n)])
        o=mesh(name,vs,fs,region,'plate')
        for i,p in enumerate(o.data.polygons):p.use_smooth=i%2==0
        # Per-plate UVs serve regional PBR maps and readable edge wear.
        for p in o.data.polygons:
            for li in p.loop_indices:
                idx=o.data.loops[li].vertex_index
                u,v=outline[idx if idx<n else idx-n-1] if idx!=n else (0,.4)
                o.data.uv_layers[0].data[li].uv=(u+.5,1-v)
        # Selected lower perimeter line catches restrained highlights, not a gold lattice.
        edge=[fn(u*w,v*h,.0053) for u,v in outline[3:8]]
        tube(name+' thin rolled edge',edge,[.00055]*len(edge),region,'edge',5)
        return o
    def interpolate(sections,z):
        z=max(sections[0][0],min(sections[-1][0],z))
        for a,b in zip(sections,sections[1:]):
            if a[0]<=z<=b[0]:
                t=(z-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in range(1,len(a))]
        return list(sections[-1][1:])
    torso=next(s for s in shapes if s['part']=='torso')['sections']
    def body(theta,z,o):
        y,rx,ry=interpolate(torso,z);n=Vector((math.cos(theta),math.sin(theta),0));return Vector((rx*math.cos(theta),y+ry*math.sin(theta),z))+n*o
    retained=[]
    for o in list(scene.objects):
        part=o.get('study_part')
        if part in ('torso','shoulder-wing'):
            tag(o,'body' if part=='torso' else 'wing','inner')
            for p in o.data.polygons:p.use_smooth=True
            retained.append(o.name)
        elif part=='legs':
            if 'rounded upper thigh' in o.name:
                tag(o,'leg','inner')
                for p in o.data.polygons:p.use_smooth=True
                retained.append(o.name)
            else:o.hide_render=True;o.hide_set(True);o['cg1cScaffoldReplaced']=True
    # Every level uses the scaffold cross-section rather than a spherical substitute.
    for row in range(12):
        z=1.36-row*.066;y,rx,ry=interpolate(torso,z-.038)
        n=max(5,int(math.tau*max(rx,ry)/.067))
        for col in range(n):
            theta=col*math.tau/n+(row%2)*math.pi/n+rng.uniform(-.025,.025)
            scale=max(.035,(rx+ry)/2)
            def fn(u,v,o,theta=theta,z=z,scale=scale):return body(theta+u/scale,max(.55,z-v+.07*u),o)
            plate(f'CG1c torso course {row:02d} {col:02d}',fn,.096+rng.uniform(-.007,.007),.103+rng.uniform(-.01,.01),'body')
            if (row+col)%3==0:rivet(f'CG1c torso captive rivet {row} {col}',fn(-.023,.032,.0058),(math.cos(theta),math.sin(theta),0),'body')
    # Asymmetric breast repair seam, exact silhouette retained.
    pts=[body(-1.85+.02*math.sin(i),1.28-i*.048,.010) for i in range(12)]
    tube('CG1c off-center dark breast linkage',pts,[.003]*len(pts),'body','inner',8)
    for i,p in enumerate(pts):rivet('CG1c seam rivet '+str(i),p,(-.27,-.96,0),'body',.0025)
    for s in [q for q in shapes if q['part']=='shoulder-wing']:
        sign=-1 if s['side']=='left' else 1;sections=s['sections']
        def wing(theta,z,o):
            x,y,rx,ry=interpolate(sections,z);n=Vector((sign*math.cos(theta),math.sin(theta),0));return Vector((sign*(x+rx*math.cos(theta)),y+ry*math.sin(theta),z))+n*o
        for row in range(9):
            z=1.337-row*.044;x,y,rx,ry=interpolate(sections,z-.029);n=max(3,int(math.pi*ry/.047))
            for col in range(n):
                a=-1.48+2.96*col/max(1,n-1)+(row%2)*.08
                def fn(u,v,o,a=a,z=z,ry=ry):return wing(max(-1.57,min(1.57,a+u/max(.045,ry))),max(.912,z-v),o)
                plate(f'CG1c {s["side"]} shield course {row} {col}',fn,.072,.078+rng.uniform(-.004,.004),'wing')
                if (col+row)%3==0:rivet(f'CG1c {s["side"]} wing rivet {row} {col}',fn(-.016,.025,.006),(sign,0,0),'wing',.0018)
    # All hinge points and planted toe endpoints come directly from study05.
    for side in ('left','right'):
        ss=[q for q in shapes if q['part']=='legs' and ('L '+side+' ') in q['name']]
        byname={q['name'].split(side+' ')[1]:q for q in ss};sgn=-1 if side=='left' else 1
        hip=Vector(byname['hip']['center']);knee=Vector(byname['knee']['center']);hock=Vector(byname['hock']['center']);ankle=Vector(byname['lower segment']['end'])
        for label,a,b,r in [('upper',hip,knee,.036),('shank',knee,hock,.031),('tarsus',hock,ankle,.024)]:
            axis=(b-a).normalized();cross=axis.cross(Vector((1,0,0))).normalized()
            bar(f'CG1c {side} {label} dark structural core',a,b,r)
            for off in (-1,1):
                shift=Vector((sgn*.026,0,0))+cross*.020*off
                bar(f'CG1c {side} {label} piston rod {off}',a+shift,b+shift,.008,role='bearing')
                bar(f'CG1c {side} {label} piston sleeve {off}',a.lerp(b,.15)+shift,a.lerp(b,.57)+shift,.014,role='inner')
            for i in range(6):
                p=a.lerp(b,(i+1)/7);ring(f'CG1c {side} {label} collar {i}',p,axis,r*1.14,.009)
        for label,p,r in [('hip',hip,.065),('knee',knee,.061),('hock',hock,.043),('ankle',ankle,.030)]:
            ring(f'CG1c {side} {label} concentric hinge',p,(1,0,0),r,.067)
            ring(f'CG1c {side} {label} inset bearing',p+Vector((sgn*.040,0,0)),(1,0,0),r*.66,.009,role='inner')
            ring(f'CG1c {side} {label} hub cap',p+Vector((sgn*.047,0,0)),(1,0,0),r*.32,.009)
            for i in range(8):
                a=i*math.tau/8;rivet(f'CG1c {side} {label} bolt {i}',p+Vector((sgn*.039,r*.8*math.cos(a),r*.8*math.sin(a))),(sgn,0,0),'leg',.0024)
        # Segmented thigh armour wraps the existing rounded taper.
        axis=(knee-hip).normalized();u=Vector((1,0,0));v=axis.cross(u).normalized()
        for row in range(5):
            t=.30+row*.14;radius=.109-row*.008
            for col in range(7):
                a=col*math.tau/7
                def fn(dx,dy,o,t=t,radius=radius,a=a):
                    theta=a+dx/radius;return hip+(knee-hip)*t+axis*dy+(u*math.cos(theta)+v*math.sin(theta))*(radius+o)
                plate(f'CG1c {side} embedded thigh plate {row} {col}',fn,.106,.070,'leg')
        pad=byname['foot pad'];p=Vector(pad['center']);tube(f'CG1c {side} plantar foot housing',[p+Vector((0,.050,0)),p+Vector((0,-.052,0))],[.045,.048],'foot','inner',16)
        for q in [q for q in ss if 'toe' in q['name']]:
            a,b=Vector(q['start']),Vector(q['end']);axis=(b-a).normalized();name=q['name'].replace('L ','CG1c ')
            tube(name+' dark tendon chassis',[a,b],[.025,.019],'foot','inner')
            for i in range(5):ring(name+' overlapping knuckle '+str(i),a.lerp(b,(i+1)/6),axis,.026-i*.001,.013,'foot')
            # Short recurved mechanical claw extends each retained toe endpoint.
            d=Vector((axis.x,axis.y,0)).normalized();pts=[b,b+d*.021+Vector((0,0,.018)),b+d*.050+Vector((0,0,.010)),b+d*.073+Vector((0,0,-.020))]
            tube(name+' recurved steel talon',pts,[.018,.015,.009,.0012],'foot','talon',12)
    return {'module':'cg1c-body','scaffoldRevision':'05','source':str(source),'counts':counts,'retainedEnvelopeMeshes':retained,'deliberateChanges':['Thin overlapping scalloped body and 1.25-size fixed-root shield armor','Embedded scaffold thighs and exact hip/knee/hock/ankle/toe anchors retained','Layered visual pistons and recurved steel talons'],'limitations':['Posterior low power/transmission mass is fictional visual rationale, not mass or balance certification','Hidden regions are inferred CG detail','No final likeness or mechanical validation claimed']}
