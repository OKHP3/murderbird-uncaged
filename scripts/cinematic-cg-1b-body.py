"""Milestone 1b body study: CG coverage, no engineering or runtime promotion.
Call apply(scene) after importing the frozen attempt02 source and the head pass.
All new mesh vertices are authored in world space, with identity transforms.
"""
import math, random
import bpy
from mathutils import Vector


def apply(scene):
    rng = random.Random(10317)
    original = list(scene.objects)
    hidden = []
    for obj in original:
        region = obj.get('region', '')
        role = obj.get('surfaceRole', '')
        if obj.type == 'MESH' and not obj.get('cg1bRegion'):
            if (region in ('breast', 'shoulder', 'torso') and role in ('plate', 'liner', 'guard', 'repair')) or (region == 'lower-body-mass' and 'pelvic return' in obj.name):
                obj.hide_render = True
                obj.hide_set(True)
                obj['cg1bReplacedExterior'] = True
                hidden.append(obj.name)
    collection = bpy.data.collections.new('CG 1b body and compact shield wings')
    scene.collection.children.link(collection)
    counts = {'plate': 0, 'fastener': 0, 'frame': 0, 'liner': 0}

    def tag(obj, region, role):
        obj['cg1bRegion'] = region
        obj['region'] = 'shoulder' if region == 'wing' else 'torso' if region == 'body' else region
        obj['surfaceRole'] = role
        obj['exteriorEras'] = 'maker,mechanic,builder'
        counts[role] += 1
        return obj

    def mesh(name, vertices, faces, region, role, uv=None):
        data = bpy.data.meshes.new(name)
        data.from_pydata(vertices, [], faces)
        data.update()
        obj = bpy.data.objects.new(name, data)
        collection.objects.link(obj)
        tag(obj, region, role)
        for poly in data.polygons:
            poly.use_smooth = True
        layer = data.uv_layers.new(name='surface-uv')
        for poly in data.polygons:
            for li in poly.loop_indices:
                i = data.loops[li].vertex_index
                layer.data[li].uv = uv[i] if uv else (data.vertices[i].co.x * 2, data.vertices[i].co.z * 2)
        return obj

    def pipe(name, points, radius, region, role='frame'):
        curve = bpy.data.curves.new(name, 'CURVE')
        curve.dimensions = '3D'
        curve.resolution_u = 1
        curve.bevel_depth = radius
        curve.bevel_resolution = 2
        spline = curve.splines.new('POLY')
        spline.points.add(len(points)-1)
        for p, co in zip(spline.points, points):
            p.co = (*co, 1)
        obj = bpy.data.objects.new(name, curve)
        collection.objects.link(obj)
        return tag(obj, region, role)

    def rivet(name, point, normal, region, radius=.0024):
        # Low-poly round headed countersunk fastener, editable and exportable.
        n = Vector(normal).normalized()
        axis = Vector((0, 0, 1)) if abs(n.z) < .9 else Vector((0, 1, 0))
        u = n.cross(axis).normalized()
        v = n.cross(u).normalized()
        p = Vector(point)
        vertices = []
        for r, height in ((radius, 0), (radius * .85, radius * .42)):
            for i in range(10):
                a = i * math.tau / 10
                vertices.append(tuple(p + u * (r*math.cos(a)) + v * (r*math.sin(a)) + n*height))
        faces = [(i, (i+1)%10, (i+1)%10+10, i+10) for i in range(10)] + [tuple(range(10,20))]
        return mesh(name, vertices, faces, region, 'fastener')

    # Rounded, deep belly with compact back, preserving exposed mechanical side bays.
    # Cross sections provide screen mass without manufacturing constraints.
    zmin, zmax = .625, 1.285
    def barrel(theta, z, offset=0):
        q = max(-.998, min(.998, (z-.945)/.345))
        section = math.sqrt(max(.005, 1-q*q))
        rx = .296 * section
        ry = .335 * section
        center_y = -.094 - .025 * (z-.945)
        n = Vector((math.sin(theta), -math.cos(theta), .35*q)).normalized()
        return Vector((rx*math.sin(theta), center_y-ry*math.cos(theta), z)) + n*offset

    vertices=[]; uv=[]; faces=[]
    for j in range(29):
        z=zmin+(zmax-zmin)*j/28
        for i in range(64):
            a=math.tau*i/64
            vertices.append(tuple(barrel(a,z)))
            uv.append((i/64,j/28))
    for j in range(28):
        for i in range(64):
            a=j*64+i; b=j*64+(i+1)%64
            faces.append((a,b,b+64,a+64))
    mesh('CG1b continuous dark barrel body',vertices,faces,'body','liner',uv)

    outline=[(-.43,0),(.39,0),(.49,.17),(.49,.47),(.41,.70),(.23,.92),(.02,1),(-.20,.95),(-.40,.77),(-.50,.5),(-.49,.20)]
    def panel(name, surface, width, length, region, thickness=.0028):
        # Convex scalloped plate: curved world-space fan and physical dark edge thickness.
        points=[surface(u*width,v*length,.007+.0006*math.sin(v*math.pi)) for u,v in outline]
        center=surface(0,length*.44,.0078)
        vertices=[tuple(p) for p in points]+[tuple(center)]
        for u,v in outline:
            vertices.append(tuple(surface(u*width,v*length,.004-thickness)))
        n=len(outline); faces=[]
        for i in range(n):
            faces.append((n,i,(i+1)%n))
            faces.append((i,n+1+i,n+1+(i+1)%n,(i+1)%n))
        faces.append(tuple(range(n+1,2*n+1)))
        uv=[((u+.5),1-v) for u,v in outline]+[(.5,.56)]+[((u+.5),1-v) for u,v in outline]
        obj=mesh(name,vertices,faces,region,'plate',uv)
        # Keep thin sidewalls sharp instead of smearing their normals into a puffy scale.
        for index, poly in enumerate(obj.data.polygons):
            poly.use_smooth = index < 2*n and index % 2 == 0
        # A narrow raised rolled edge catches light; surfaceworker colors it by frame.
        pipe(name+' rolled lower edge',[tuple(p) for p in points[3:10]],.0007,region,'frame')
        return obj

    # Breast rows are visibly varied and slightly oblique, rather than broad uniform scales.
    for row in range(9):
        top=1.258-row*.068
        for col in range(7):
            theta=-1.45+col*.43+(row%2)*.17+rng.uniform(-.045,.045)
            if theta>1.46:continue
            width=.125+rng.uniform(-.017,.014)
            length=.099+rng.uniform(-.014,.012)
            shift=rng.uniform(-.010,.010)
            def surf(u,v,o,theta=theta,top=top,shift=shift):
                z=max(.632,min(1.28,top-v+u*.13+shift))
                # Width is measured along circumference, not direct x.
                q=(z-.945)/.345
                rx=max(.11,.296*math.sqrt(max(.04,1-q*q)))
                return barrel(theta+u/rx,z,o)
            panel(f'CG1b breast course {row:02d} plate {col:02d}',surf,width,length,'breast')
            if (row+col)%2==0:
                point=surf(-width*.22,length*.35,.011)
                rivet(f'CG1b breast rivet {row:02d} {col:02d}',point,(math.sin(theta),-math.cos(theta),.12),'breast')

    # Off-center dark repaired junction and strap. The seam is deliberately asymmetric.
    for side_offset in (-.018,.018):
        points=[tuple(barrel(-.57+side_offset/.25+.025*math.sin(i),1.22-i*.049,.017)) for i in range(11)]
        pipe('CG1b asymmetric breast seam margin '+str(side_offset),points,.0024,'breast','frame')
    points=[tuple(barrel(-.57+.025*math.sin(i),1.22-i*.049,.015)) for i in range(11)]
    pipe('CG1b dark exposed breast linkage',points,.006,'breast','frame')
    for i in range(9):
        z=1.19-i*.05
        point=barrel(-.57-.018/.25,z,.019)
        rivet(f'CG1b breast seam captive rivet {i}',point,(-.54,-.84,0),'breast',.003)

    # Rounded wing cap high on shoulder: compact taper, not a long flight surface.
    for side in (-1,1):
        def wing(y,z,offset=0):
            t=(z-1.02)/.272
            half=.242*math.sqrt(max(.035,1-t*t))
            center=.025+.065*(1.18-z)
            q=(y-center)/half
            bulge=.122*math.sqrt(max(.012,1-q*q)) * math.sqrt(max(.04,1-t*t))
            return Vector((side*(.259+bulge+offset),y,z))
        vertices=[]; faces=[]; uv=[]
        for j in range(33):
            z=.759+j*.527/32
            t=(z-1.02)/.272
            half=.242*math.sqrt(max(.035,1-t*t))
            center=.025+.065*(1.18-z)
            for i in range(25):
                y=center+half*(-1+2*i/24)
                vertices.append(tuple(wing(y,z)))
                uv.append((i/24,j/32))
        for j in range(32):
            for i in range(24):
                a=j*25+i
                faces.append((a,a+1,a+26,a+25) if side==1 else (a+25,a+26,a+1,a))
        mesh(f'CG1b {side} continuous shield backing',vertices,faces,'wing','liner',uv)
        for row in range(11):
            top=1.295-row*.048
            zm=top-.034
            t=(zm-1.02)/.272
            half=.23*math.sqrt(max(.04,1-t*t))
            center=.025+.065*(1.18-zm)
            cols=max(2,int(2*half/.054)+1)
            for col in range(cols):
                y=center-half+(2*half)*col/max(1,cols-1)
                # Staggered small scales form dense, overlapping scalloped courses.
                length=.080+rng.uniform(-.005,.007)
                width=.082+rng.uniform(-.006,.006)
                def surf(u,v,o,y=y,top=top):
                    z=max(.757,min(1.285,top-v))
                    t=(z-1.02)/.272
                    half=.242*math.sqrt(max(.035,1-t*t))
                    center=.025+.065*(1.18-z)
                    yy=max(center-half,min(center+half,y+u+v*.15))
                    return wing(yy,z,o)
                panel(f'CG1b {side} shield course {row:02d} plate {col:02d}',surf,width,length,'wing')
                if (col+row)%2==0:
                    point=surf(-width*.20,length*.34,.011)
                    rivet(f'CG1b {side} shield fastener {row:02d} {col:02d}',point,(side,0,.18),'wing',.0021)
        # Compact curved perimeter at rear bottom catches light and conceals backing edges.
        points=[]
        for i in range(30):
            angle=math.pi*.12+i*math.pi*1.75/29
            z=1.02+.268*math.cos(angle)
            t=(z-1.02)/.272
            half=.241*math.sqrt(max(.035,1-t*t))
            center=.025+.065*(1.18-z)
            y=center+half*(1 if math.sin(angle)>=0 else -1)
            points.append(tuple(wing(y,z,.004)))
        pipe(f'CG1b {side} rolled shield perimeter',points,.0022,'wing','frame')

    # Compact overlapping mantle closes the bare dorsal bridge between shoulder caps.
    # This is camera-facing armor continuity, not a receiving/support construction.
    for obj in original:
        if obj.type == 'MESH' and obj.get('region') == 'mantle':
            obj.hide_render=True; obj['cg1bReplacedExterior']=True
    for row in range(4):
        top=1.275-row*.050
        for col in range(9):
            theta=1.40+col*.43+(row%2)*.10
            width=.095+rng.uniform(-.014,.013);length=.085+rng.uniform(-.008,.009)
            def surf(u,v,o,theta=theta,top=top):
                z=max(.96,min(1.28,top-v)); q=(z-.945)/.345
                rx=max(.10,.296*math.sqrt(max(.04,1-q*q)))
                return barrel(theta+u/rx,z,o)
            panel(f'CG1b dorsal mantle {row:02d} {col:02d}',surf,width,length,'body')

    # Dark fine ribs beneath breast and behind shield provide continuity in all views.
    for side in (-1,1):
        for i in range(8):
            z=.70+i*.056
            points=[tuple(barrel(side*(1.45+j*.052),z+.006*math.sin(j*.4),.010)) for j in range(16)]
            pipe(f'CG1b {side} lateral dark linkage rib {i}',points,.0035,'body','frame')
    return {'module':'body-wing','hiddenOriginalSkin':len(hidden),'created':counts,'construction':'World-space dense curved scalloped courses, continuous barrel and shield backing; no engineering claims','limits':'Inferred back/hidden side details; owner likeness acceptance pending'}
