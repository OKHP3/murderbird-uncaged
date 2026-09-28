"""Alignment v6 orbital and brow proposal, executed in the build namespace.

Qualitative July head-only interpretation. The jaw pivot and forked lower
frame are reconstructed here; fixed v4 bill/head geometry remains inherited.
Perspective illustrations do not establish exact joint dimensions. Expected globals are documented in the caller.
"""
for _obj in list(bpy.data.objects):
    if _obj.type != 'MESH' or _obj.get('region') not in {'head', 'optic'}:
        continue
    if under(_obj, bpy.data.objects['processing']) or under(_obj, bpy.data.objects['power-core']):
        continue
    bpy.data.objects.remove(_obj, do_unlink=True)

_eye_y, _eye_z = -.369, 1.786
# Put the transverse jaw journal in the lower cheek rather than below the skull.
# This is the only changed joint; all jaws/plates are constructed from world
# profiles after setting that attachment, so metal geometry is never stretched.
_jaw_hinge_world = Vector((0, -.300, 1.704))
jaw.matrix_parent_inverse = Matrix.Identity(4)
jaw.location = head.matrix_world.inverted() @ _jaw_hinge_world
bpy.context.view_layer.update()
_jp = jaw.matrix_world.translation.copy()
_head_sections = [
    (1.575, -.15, .065, .10), (1.65, -.20, .123, .185),
    (1.74, -.25, .149, .22), (1.825, -.265, .153, .20),
    (1.915, -.24, .119, .175), (1.955, -.17, .025, .075),
]

def _side_width(y, z):
    cy, rx, ry = sample(_head_sections, z)
    q = (y-cy)/max(.05, ry)
    return rx*math.sqrt(max(.12, 1-q*q))

def _side_project(side, y, z, lift=.008):
    return (side*(_side_width(y, z)+lift), y, z)

def _open_spline(rows, t):
    t = max(0.0, min(1.0, t))*(len(rows)-1)
    i = min(int(t), len(rows)-2); u=t-i
    p0=rows[max(0,i-1)]; p1=rows[i]
    p2=rows[i+1]; p3=rows[min(len(rows)-1,i+2)]
    return tuple(.5*(2*p1[k]+(-p0[k]+p2[k])*u+
        (2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+
        (-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u*u*u)
        for k in range(len(p1)))

def _closed_strip(name, path, project, owner, role='plate', eras=ALL,
                  along=32, across=8):
    """Closed variable-section plate, with shared regular quad topology.

    Profile rows contain two surface coordinates, half width and wall depth.
    Width varies across the curve; a shallow camber is an actual cross-section.
    Both faces and edge returns are authored explicitly: no subdivided polygon
    triangles, solidify normals, or bevels at internal tessellation edges.
    """
    verts=[]; faces=[]; stride=across+1
    for skin in (0,1):
        for j in range(along+1):
            t=j/along; a,b,w,d=_open_spline(path,t)
            prev=_open_spline(path,max(0,t-1/along))
            nxt=_open_spline(path,min(1,t+1/along))
            da=nxt[0]-prev[0]; db=nxt[1]-prev[1]
            mag=max(1e-8,math.hypot(da,db))
            for k in range(stride):
                u=k/across; off=(2*u-1)*max(.001,w)
                # Rounded but substantial wall section; tips retain a finite
                # section rather than collapsing to zero-area triangles.
                crown=.0025*math.sin(math.pi*u)
                verts.append(project(a-db/mag*off,b+da/mag*off,
                                     crown if skin==0 else -max(.003,d)))
    count=(along+1)*stride
    for j in range(along):
        for k in range(across):
            a=j*stride+k; b=a+1; c=b+stride; d=a+stride
            faces.extend([(a,b,c,d),(count+d,count+c,count+b,count+a)])
        a=j*stride; b=a+stride
        faces.append((a,b,count+b,count+a))
        a=j*stride+across; b=a+stride
        faces.append((b,a,count+a,count+b))
    for k in range(across):
        faces.append((k+1,k,count+k,count+k+1))
        a=along*stride+k
        faces.append((a,a+1,count+a+1,count+a))
    obj=wm(name,verts,faces,owner,'head',role,eras)
    for face in obj.data.polygons: face.use_smooth=True
    control(name+' section centres',[project(a,b,0) for a,b,w,d in path],
            owner,'closed-variable-section')
    return obj

def _forged_band(name, path, side, owner, role='plate', lift=.018, along=40):
    return _closed_strip(name,path,
        lambda y,z,h:_side_project(side,y,z,lift+h),owner,role,along=along)

# Keep the inner support envelope, but cover it with fitted broad layers.
shell('V4 cranial inner shell',_head_sections,crown,'head',1.72,math.tau-1.72,'recess')
for z,cy,rx,ry in _head_sections:
    control(f'V4 skull section {z:.3f}',
        [envelope(_head_sections,z,math.tau*k/24) for k in range(24)],
        crown,'cross-section',True)

# Roof uses explicit swept strips with rounded shoulders and overlapping
# trailing ends. It continues aft rather than stopping at a little top grid.
_roof=[(-.465,1.867,.065),(-.370,1.938,.115),(-.272,1.970,.133),
       (-.161,1.967,.127),(-.049,1.923,.091),(.038,1.845,.033)]
def _roof_point(x,y,h=0):
    z,w=sample([(p[0],p[1],p[2]) for p in _roof],y)
    return (x,y,z-.039*(x/max(.025,w))**2+h)
for i,(y0,y1,w) in enumerate([
    (-.455,-.300,.089),(-.372,-.214,.125),(-.287,-.129,.137),
    (-.202,-.044,.127),(-.117,.031,.097)]):
    path=[(0,y0,.40*w,.008),(0,y0+.022,.90*w,.010),
          (0,(y0+y1)/2,w,.010),(0,y1-.023,.80*w,.008),
          (0,y1,.23*w,.006)]
    _closed_strip(f'Rounded swept crown lamina {i}',path,
        lambda x,y,h,ii=i:_roof_point(x,y,.008+ii*.001+h),crown)
    for x in (-w*.43,w*.43):
        fastener('Crown lamina root pin',_roof_point(x,y0+.029,.014),
                 (0,0,1),crown,'head',.0028)

for side in (-1,1):
    # Broad underlying forged temporal shell is a curved strip, not a concave
    # projected n-gon. It merges the roof, rear cap and orbital mounting bed.
    _forged_band('Continuous temporal shell '+str(side),[
        (-.252,1.923,.015,.008),(-.202,1.903,.075,.011),
        (-.174,1.865,.105,.012),
        (-.134,1.796,.119,.012),(-.136,1.706,.100,.011),
        (-.162,1.636,.068,.009)],side,crown,'frame',lift=.009)
    # Overlapping leaf-shaped laminae sweep back and down in a staggered fan.
    # The terminal section is narrow and round-ended, not a rectangular tile.
    courses=[(1.925,[-.344,-.248,-.151],.112),
             (1.865,[-.250,-.155,-.063],.119),
             (1.799,[-.221,-.126,-.035],.118),
             (1.735,[-.199,-.104,-.019],.109),
             (1.673,[-.159,-.070],.085)]
    for row,(z,centres,length) in enumerate(courses):
        for col,y in enumerate(centres):
            w=.035 if row<3 else .029
            path=[(y,z,.62*w,.008),(y+.024,z-.018,w,.009),
                  (y+length*.55,z-length*.45,.92*w,.009),
                  (y+length*.85,z-length*.70,.64*w,.007),
                  (y+length,z-length*.81,.005,.005)]
            _forged_band(f'Swept temporal lamina {side} {row} {col}',
                path,side,crown,lift=.024+(4-row)*.003,along=28)
            fastener('Temporal lamina root pin',
                _side_project(side,y+.012,z-.010,.030+(4-row)*.003),
                (side,0,.12),crown,'head',.0028)

    # July's eye is mounted within a broad irregular forged orbital plate,
    # continuous from the temporal/crown bed to the cere and bill root. Build
    # its real aperture as a regular annular grid with explicit closed returns.
    # Angularly ordered outer landmarks make a simple star-shaped boundary;
    # there are no projected polygon triangles or floating circular surround.
    # A narrower stepped mounting flange leaves the swept temporal layers
    # readable behind it. These authored landmarks replace the large round
    # saucer envelope; their dimensions remain an illustrative reconstruction.
    outer_profile=[(-.252,1.790),(-.268,1.831),(-.298,1.868),
        (-.330,1.897),(-.370,1.908),(-.419,1.891),(-.456,1.861),
        (-.477,1.824),(-.476,1.782),(-.454,1.749),(-.423,1.722),
        (-.392,1.712),(-.367,1.714),(-.326,1.724),(-.286,1.744),
        (-.258,1.763)]
    boundary=smooth_profile(outer_profile,4)
    n=len(boundary); radial=6; stride=radial+1; verts=[]; faces=[]
    for skin in (0,1):
        for i,(oy,oz) in enumerate(boundary):
            a=math.tau*i/n
            # Open the recessed primary optic aperture by roughly 22% while
            # keeping its authored center fixed. The surrounding seat, not a
            # second sensor, defines this larger passive opening.
            iy=_eye_y+.054*math.cos(a)
            iz=_eye_z+.056*math.sin(a)
            # Broad side plate covers rails (X up to .1335). Only its forward
            # outer rim tapers inward to meet the narrower bill-root assembly.
            forward=max(0,min(1,(-oy-.432)/.067))
            outer_x=max(.105,_side_width(oy,oz)+.023)-.010*forward
            for j in range(stride):
                t=j/radial; yy=iy+(oy-iy)*t; zz=iz+(oz-iz)*t
                # Recess the broad field slightly behind the distinct seat and
                # orbital support so it reads as layered construction, not a
                # smooth saucer. The outer boundary and plate envelope stay put.
                xx=.151+(outer_x-.151)*t
                xx+=.0035*math.sin(math.pi*t)
                verts.append((side*(xx-(.009 if skin else 0)),yy,zz))
    layer=n*stride
    for i in range(n):
        a=i*stride; b=((i+1)%n)*stride
        for j in range(radial):
            quad=(a+j,a+j+1,b+j+1,b+j)
            faces.append(quad if side>0 else tuple(reversed(quad)))
            back=tuple(layer+k for k in reversed(quad))
            faces.append(back if side>0 else tuple(reversed(back)))
        for j in (0,radial):
            q=(a+j,b+j,layer+b+j,layer+a+j)
            if j==radial:q=tuple(reversed(q))
            faces.append(q if side>0 else tuple(reversed(q)))
    plate=wm('Forged orbital mounting plate '+str(side),verts,faces,
             head,'head','plate')
    for face in plate.data.polygons: face.use_smooth=True
    control('Orbital mounting boundary '+str(side),
            [(side*max(.105,_side_width(y,z)+.023),y,z) for y,z in outer_profile],
            head,'irregular-orbital-plate',True)
    # Riveted perimeter establishes the mounting plate's structural boundary.
    for index in (1, 3, 6, 9, 13):
        oy, oz = outer_profile[index]
        yy = _eye_y + (oy-_eye_y)*.82
        zz = _eye_z + (oz-_eye_z)*.82
        forward = max(0,min(1,(-oy-.432)/.067))
        outer_x = max(.105,_side_width(oy,oz)+.023)-.010*forward
        xx = .159+(outer_x-.159)*.82+.0035*math.sin(math.pi*.82)
        fastener('Orbital mounting fixing '+str(side)+' '+str(index),
                 (side*xx,yy,zz),(side,0,0),head,'head',.0032)
    # Small machined bearing is seated within the plate aperture, with the
    # visible optic slightly behind the plate's outer lip. It is intentionally
    # a subordinate rim, not the mounting construction itself.
    n=64; verts=[]; faces=[]
    for skin in (0,1):
        for i in range(n):
            a=math.tau*i/n
            irregular=1+.055*math.sin(3*a+.2)+.035*math.cos(2*a-.4)
            # The forged outer flange may vary, but the machined inner seat
            # stays circular/elliptical so a rigid lens can actually seat.
            for ry,rz,x in [(.056*irregular,.059*irregular,.160),
                            (.0475,.0495,.154)]:
                verts.append((side*(x-(.005 if skin else 0)),
                    _eye_y+ry*math.cos(a),_eye_z+rz*math.sin(a)))
    layer=n*2
    for i in range(n):
        a=2*i;b=2*((i+1)%n)
        qs=[(a,b,b+1,a+1),(layer+a+1,layer+b+1,layer+b,layer+a),
            (b,a,layer+a,layer+b),(a+1,b+1,layer+b+1,layer+a+1)]
        faces.extend(qs if side>0 else [tuple(reversed(q)) for q in qs])
    bearing=wm('Recessed orbital bearing '+str(side),verts,faces,
               head,'optic','bearing')
    for face in bearing.data.polygons:face.use_smooth=True
    # The passive seated disk fills the aperture in every era. Builder optic
    # has a shallow advance and smaller face, preserving era ownership.
    wr('Seated passive optic housing '+str(side),
       (side*.141,_eye_y,_eye_z),(side*.150,_eye_y,_eye_z),
       .052,head,'optic','recess',sides=64)
    wr('Seated Advanced optic '+str(side),
       (side*.1505,_eye_y,_eye_z),(side*.153,_eye_y,_eye_z),
       .043,bpy.data.objects['builder-optics'],'optic','optic','builder',sides=48)
    # Continuous crown-to-cere brow frames the eye with substantial variable
    # width. This replaces the intersecting triangulated orbital bridge.
    _forged_band('Forged orbital brow '+str(side),[
        (-.273,1.847,.020,.010),(-.305,1.899,.032,.012),
        (-.375,1.926,.034,.012),(-.443,1.901,.027,.011),
        (-.483,1.858,.014,.008)],side,crown,'plate',lift=.030)
    # Fixed cheek supports the optic above the moving mandible. The old two
    # descending fixed arcs occupied the actual opening sweep and falsely read
    # as additional jaws; the S-shaped lower member now belongs to jaw itself.
    _forged_band('Broad swept cheek band '+str(side),[
        (-.278,1.803,.018,.012),(-.295,1.749,.019,.013),
        (-.352,1.718,.015,.011),(-.408,1.716,.011,.009),
        (-.453,1.734,.006,.007)],side,head,'plate',lift=.034)
    wr('Coaxial mandible journal',_jp+Vector((side*.075,0,0)),
       _jp+Vector((side*.119,0,0)),.032,head,'head','bearing',sides=32)
    wr('Mandible journal cap',_jp+Vector((side*.120,0,0)),
       _jp+Vector((side*.126,0,0)),.023,jaw,'head','edge',sides=24)
    for y,z in [(-.284,1.783),(-.353,1.718),(-.424,1.721)]:
        fastener('Recessed cheek fixing',_side_project(side,y,z,.043),
                 (side,0,0),head,'head',.003)

# Upper bill keeps v3's broad convex face, inner cutting profile and apex.
_outer=[(-.421,1.853),(-.493,1.837),(-.571,1.789),(-.638,1.716),
        (-.674,1.634),(-.678,1.560),(-.657,1.495),(-.622,1.463)]
_inner=[(-.420,1.706),(-.482,1.694),(-.538,1.674),(-.585,1.643),
        (-.620,1.602),(-.641,1.554),(-.642,1.503),(-.622,1.463)]
control('Upper bill convex dorsal profile',[(0,y,z) for y,z in _outer],bill)
control('Upper bill cutting profile',[(0,y,z) for y,z in _inner],bill)
def _bill_blade(t,a):
    oy,oz=curve(_outer,t); iy,iz=curve(_inner,t)
    width=curve([(.071,),(.075,),(.067,),(.052,),(.037,),(.022,),(.010,),(.0008,)],t)[0]
    cross=1-2*abs((a+math.pi)%math.tau-math.pi)/math.pi
    return (width*math.sin(a),(oy+iy)/2+(oy-iy)/2*cross,
            (oz+iz)/2+(oz-iz)/2*cross)
for index,(start,end) in enumerate([(0,.245),(.25,1)]):
    vertices=[]; faces=[]; rows=56; n=40
    for j in range(rows+1):
        for k in range(n): vertices.append(_bill_blade(start+(end-start)*j/rows,k*math.tau/n))
    for j in range(rows):
        for k in range(n):
            a=j*n+k; b=j*n+(k+1)%n
            faces.append((a,b,b+n,a+n))
    faces.extend([tuple(reversed(range(n))),tuple(rows*n+k for k in range(n))])
    obj=wm('Profiled upper bill blade '+str(index),vertices,faces,bill,'head')
    for face in obj.data.polygons: face.use_smooth=True
for _side in (-1,1):
    _cere=[(-.430,1.860),(-.466,1.866),(-.505,1.836),
           (-.521,1.800),(-.502,1.786),(-.470,1.810)]
    project=lambda y,z,s=_side:(s*(.129-.75*max(0,-y-.425)),y,z)
    patch('Cere root transition '+str(_side),_cere,project,bill,'head',
          thickness=.012,sub=5)
    control('Cere transition contour '+str(_side),
            [project(y,z) for y,z in _cere],bill,'cere-root',True)
    for t in (.07,.17):
        fastener('Bill root fixing',_bill_blade(t,_side*1.28),(_side,0,0),
                 bill,'head',.0035)

# The nasal cover overlaps the crown and bill root as one shaped rigid hood.
# This closes the central dorsal opening without changing either owner's pivot.
_nasal_profile=[(-.503,1.825,.042),(-.466,1.883,.076),
                (-.421,1.925,.086),(-.384,1.935,.070)]
def _nasal_surface(x,y,h):
    z,w=sample(_nasal_profile,y)
    return (x,y,z-.024*(x/max(.03,w))**2+h)
_closed_strip('Overlapping nasal hood',[(0,-.386,.070,.008),
    (0,-.420,.084,.008),(0,-.465,.075,.008),(0,-.502,.041,.006)],
    _nasal_surface,bill,'plate',along=24)
for y in (-.405,-.476):
    for x in (-.028,.028):
        fastener('Nasal hood fixing',_nasal_surface(x,y,.003),
                 (0,0,1),bill,'head',.0028)

# A forked lower mandible joins the real transverse journal in the cheek.
# Two substantial lateral forged members frame the opening, with a short
# distal bridge. Their opening is mechanical space, not a broad floating sheet.
# July/candidate03 guide the sweep; hinge location is an authored reconstruction.
_mandible_path = [
    (-.304,1.700,.010,.010),(-.346,1.674,.026,.010),
    (-.400,1.634,.025,.011),(-.465,1.608,.021,.010),
    (-.523,1.600,.018,.009),(-.566,1.615,.012,.007),
    (-.589,1.632,.004,.004),
]
for _side in (-1,1):
    def _mandible_project(y,z,h,s=_side):
        # Proximal arms lie beside the processing bay and engage the journal
        # cap. Their tapered distal width stays within the bill opening.
        return (s*(.128-.286*max(0,-y-.310)+h),y,z)
    _closed_strip('Forked forged mandible '+str(_side),_mandible_path,
                  _mandible_project,jaw,'plate',along=48,across=8)
    control('Forked mandible profile '+str(_side),
            [_mandible_project(y,z,0) for y,z,w,h in _mandible_path],
            jaw,'jaw-reconstruction')
_jaw_sections = [
    (-.522,1.588,.066,.008),(-.556,1.596,.059,.008),
    (-.579,1.615,.054,.006),(-.591,1.628,.050,.003),
]
_verts=[]; _faces=[]; _around=20
for y,z,w,h in _jaw_sections:
    for k in range(_around):
        a=math.tau*k/_around
        _verts.append((w*math.cos(a),y,z+h*math.sin(a)))
for j in range(len(_jaw_sections)-1):
    for k in range(_around):
        a=j*_around+k; b=j*_around+(k+1)%_around
        _faces.append((a,b,b+_around,a+_around))
_faces.extend([tuple(reversed(range(_around))),
               tuple((len(_jaw_sections)-1)*_around+k for k in range(_around))])
_keel=wm('Distal mandible bridge',_verts,_faces,jaw,'head','edge')
for face in _keel.data.polygons: face.use_smooth=True
control('Distal mandible bridge profile',[(0,y,z+h) for y,z,w,h in _jaw_sections],jaw,
        'jaw-reconstruction')
