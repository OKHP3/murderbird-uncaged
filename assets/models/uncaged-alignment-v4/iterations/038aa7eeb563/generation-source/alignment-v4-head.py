"""Alignment v4 authored head geometry, executed in the build namespace.

Qualitative July-reference interpretation; fixed pivots and bill apex remain
source authority. Expected globals are documented in the caller.
"""
for _obj in list(bpy.data.objects):
    if _obj.type != 'MESH' or _obj.get('region') not in {'head', 'optic'}:
        continue
    if under(_obj, bpy.data.objects['processing']) or under(_obj, bpy.data.objects['power-core']):
        continue
    bpy.data.objects.remove(_obj, do_unlink=True)

_eye_y, _eye_z = -.369, 1.786
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

    # A continuous closed socket has its optic aperture at the same X as its
    # recessed lens. The variable outer boundary merges rear temple, brow and
    # cere; it is a structural shaped socket, not an independent washer.
    n=96; verts=[]; faces=[]
    for skin in (0,1):
        for i in range(n):
            a=math.tau*i/n; ca=math.cos(a); sa=math.sin(a)
            ry=.071 if ca>0 else .064
            rz=.066 if sa>0 else .061
            oy=_eye_y+ry*ca; oz=_eye_z+rz*sa
            outer_x=.149+.003*sa
            for ring in (0,1,2):
                if ring==0: yy,zz,xx=oy,oz,outer_x
                elif ring==1:
                    yy=_eye_y+.048*ca; zz=_eye_z+.049*sa; xx=.154
                else:
                    yy=_eye_y+.0385*ca; zz=_eye_z+.0405*sa; xx=.151
                verts.append((side*(xx-(.007 if skin else 0)),yy,zz))
    layer=n*3
    for i in range(n):
        a=i*3; b=((i+1)%n)*3
        for ring in (0,1):
            faces.extend([(a+ring,b+ring,b+ring+1,a+ring+1),
                (layer+a+ring+1,layer+b+ring+1,layer+b+ring,layer+a+ring)])
        faces.extend([(b,a,layer+a,layer+b),
                      (a+2,b+2,layer+b+2,layer+a+2)])
    socket=wm('Continuous shaped optic socket '+str(side),verts,faces,
              head,'optic','bearing')
    for face in socket.data.polygons: face.use_smooth=True
    # The passive seated disk fills the aperture in every era. Builder optic
    # has a shallow advance and smaller face, preserving era ownership.
    wr('Seated passive optic housing '+str(side),
       (side*.141,_eye_y,_eye_z),(side*.150,_eye_y,_eye_z),
       .0405,head,'optic','recess',sides=64)
    wr('Seated Advanced optic '+str(side),
       (side*.1505,_eye_y,_eye_z),(side*.153,_eye_y,_eye_z),
       .033,bpy.data.objects['builder-optics'],'optic','optic','builder',sides=48)
    # Continuous crown-to-cere brow frames the eye with substantial variable
    # width. This replaces the intersecting triangulated orbital bridge.
    _forged_band('Forged orbital brow '+str(side),[
        (-.273,1.847,.018,.010),(-.305,1.899,.029,.012),
        (-.375,1.926,.031,.012),(-.443,1.901,.025,.011),
        (-.483,1.858,.013,.008)],side,crown,'plate',lift=.027)
    # July cheek is an S-swept forged plate: broad beneath the rear socket,
    # curving forward into a narrowed mandible-like free end. Its nested inner
    # leaf repeats the sweep, rather than making a second hanging U-shaped rail.
    _forged_band('Broad swept cheek band '+str(side),[
        (-.280,1.799,.029,.014),(-.294,1.743,.034,.015),
        (-.341,1.709,.031,.013),(-.398,1.685,.028,.012),
        (-.448,1.679,.021,.010),(-.482,1.656,.012,.008),
        (-.520,1.658,.003,.004)],side,head,'plate',lift=.034)
    _forged_band('Nested cheek mandible leaf '+str(side),[
        (-.278,1.734,.014,.010),(-.306,1.696,.016,.011),
        (-.354,1.678,.016,.010),(-.401,1.659,.014,.008),
        (-.447,1.637,.009,.006),(-.495,1.638,.003,.004)],
        side,head,'edge',lift=.043)
    # Solid infraorbital/cere saddle backs the visible cheek-to-bill seam,
    # concealing retained processing rails while preserving their ownership.
    # This closes the mounting gap; the mouth/throat aperture remains open.
    _closed_strip('Fitted infraorbital cere saddle '+str(side),[
        (-.415,1.856,.022,.009),(-.437,1.820,.030,.010),
        (-.446,1.776,.028,.010),(-.431,1.738,.017,.008)],
        lambda y,z,h,ss=side:(ss*(.142+h),y,z),head,'frame',along=30)
    _forged_band('Cere cheek transition '+str(side),[
        (-.452,1.858,.021,.009),(-.480,1.826,.023,.010),
        (-.487,1.786,.017,.008),(-.469,1.760,.009,.006)],
        side,bill,'plate',lift=.022,along=24)
    wr('Coaxial mandible journal',_jp+Vector((side*.075,0,0)),
       _jp+Vector((side*.119,0,0)),.032,head,'head','bearing',sides=32)
    wr('Mandible journal cap',_jp+Vector((side*.120,0,0)),
       _jp+Vector((side*.126,0,0)),.023,jaw,'head','edge',sides=24)
    for y,z in [(-.290,1.764),(-.354,1.704),(-.424,1.660)]:
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

# A slender swept lower crescent has a visibly separate inner contour and a
# slow section taper into its upturned tip. Jaw pivot and apex remain fixed.
_mandible=[(-.339,1.617),(-.389,1.624),(-.440,1.615),(-.490,1.592),
           (-.536,1.564),(-.578,1.543),(-.615,1.551),(-.628,1.568),
           (-.604,1.526),(-.565,1.513),(-.518,1.526),(-.472,1.548),
           (-.424,1.570),(-.374,1.573),(-.325,1.586)]
def _jaw_width(y,z):
    return max(.012,.076-.25*max(0,-y-.38))
side_plate('Swept crescent mandible',_mandible,_jaw_width,jaw,'head',
           thickness=.012,role='plate')
_jaw_sections=[(-.350,1.584,.070,.023),(-.392,1.584,.069,.022),
    (-.435,1.574,.061,.020),(-.478,1.551,.050,.017),
    (-.520,1.532,.037,.014),(-.560,1.521,.025,.010),
    (-.594,1.527,.015,.007),(-.620,1.547,.006,.004)]
_verts=[]; _faces=[]; _around=16
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
_keel=wm('Mandible tapered sculpted keel',_verts,_faces,jaw,'head','edge')
for face in _keel.data.polygons: face.use_smooth=True
control('Mandible inner contour',[(0,y,z+h) for y,z,w,h in _jaw_sections],jaw,
        'curved-taper')
