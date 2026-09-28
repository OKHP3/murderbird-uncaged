"""Alignment v4 authored head geometry, executed in the build script namespace.

All profiles below are qualitative interpretations of the July head reference.
They preserve the v3 bill apex and pivot centres; they are not source metrology.
Expected globals are documented by the caller (bpy, math, Vector, geometry
helpers, owners, materials, controls, parts, and control_records).
"""

# Replace only visible head/optic meshes. Fixed empties and internal
# processing/power assemblies stay untouched.
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
    """Catmull-Rom interpolation for authored 2D/3D open profile rows."""
    t = max(0.0, min(1.0, t))*(len(rows)-1)
    i = min(int(t), len(rows)-2)
    u = t-i
    p0 = rows[max(0, i-1)]; p1 = rows[i]
    p2 = rows[i+1]; p3 = rows[min(len(rows)-1, i+2)]
    return tuple(.5*(2*p1[k]+(-p0[k]+p2[k])*u+
        (2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+
        (-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u*u*u)
        for k in range(len(p1)))

def _raised_rail(name, path, side, owner, reg='head', role='edge',
                 eras=ALL, along=42, around=12):
    """Build a forged ribbon with a shallow crown and thin edge depth.

    Rows are (y,z,surface_lift,half_width,X_depth). The width follows the
    cheek curve in profile; the small proud crown gives a real but restrained
    cross-section. These are plate bands, not round cables.
    """
    vertices=[]; faces=[]; across=7
    for j in range(along+1):
        y,z,lift,radius,depth=_open_spline(path,j/along)
        eps=1/along
        prev=_open_spline(path,max(0,j/along-eps))
        nxt=_open_spline(path,min(1,j/along+eps))
        dy=nxt[0]-prev[0]; dz=nxt[1]-prev[1]
        mag=max(1e-8,math.hypot(dy,dz)); ty=dy/mag; tz=dz/mag
        for k in range(across+1):
            u=k/across
            # Slightly cambered face; forged ribbon edges lie on the skull.
            off=(2*u-1)*radius
            crown=depth*math.sin(math.pi*u)
            vertices.append((side*(_side_width(y,z)+lift+crown),
                             y-tz*off,z+ty*off))
    for j in range(along):
        for k in range(across):
            a=j*(across+1)+k; b=a+1
            faces.append((a,b,b+across+1,a+across+1))
    obj=wm(name,vertices,faces,owner,reg,role,eras)
    for face in obj.data.polygons: face.use_smooth=True
    solid=obj.modifiers.new('Thin forged ribbon return','SOLIDIFY');solid.thickness=.004;solid.offset=-.25
    bevel(obj,.0008)
    control(name+' centerline',[_side_project(side,p[0],p[1],p[2]) for p in path],owner,
            'shaped-forged-ribbon')
    return obj

def _sculpted_eye_ring(side):
    """A thin annular forged bezel leaves the complete optic aperture clear."""
    n=64; verts=[]; faces=[]
    for i in range(n):
        a=math.tau*i/n
        for ry,rz,lift in [(.076,.080,.010),(.061,.065,.013)]:
            y=_eye_y+ry*math.cos(a); z=_eye_z+rz*math.sin(a)
            verts.append(_side_project(side,y,z,lift))
    for i in range(n):
        a=2*i; b=2*((i+1)%n)
        faces.append((a,b,b+1,a+1))
    obj=wm('Forged orbital bezel '+str(side),verts,faces,head,'optic','bearing')
    solid=obj.modifiers.new('Orbital bezel depth','SOLIDIFY');solid.thickness=.004;solid.offset=-.2
    bevel(obj,.0007)

# Skull shell and fuller swept temporal backing close the former open helmet
# gaps while leaving the eye and curved throat aperture visibly open.
shell('V4 cranial inner shell',_head_sections,crown,'head',1.72,math.tau-1.72,'recess')
for z,cy,rx,ry in _head_sections:
    control(f'V4 skull section {z:.3f}',
        [envelope(_head_sections,z,math.tau*k/24) for k in range(24)],
        crown,'cross-section',True)
_temporal=[(-.405,1.947),(-.300,1.965),(-.185,1.940),(-.090,1.876),
           (-.060,1.790),(-.090,1.704),(-.180,1.625),(-.285,1.626),
           (-.326,1.705),(-.312,1.823)]
for _side in (-1,1):
    patch('Continuous temporal backing '+str(_side),_temporal,
        lambda y,z,s=_side:_side_project(s,y,z,.010),crown,'head','frame',
        thickness=.012,sub=7)
    control('Temporal backing profile '+str(_side),
        [_side_project(_side,y,z,.010) for y,z in _temporal],crown,'closed-backing',True)
    # Continuous orbital bridge joins the crown-side bed to the brow and cere.
    # Its lower edge stays above the optic's outer bezel.
    _bridge=[(-.493,1.883),(-.465,1.929),(-.407,1.946),(-.347,1.936),
             (-.302,1.905),(-.284,1.875),(-.331,1.861),(-.384,1.873),
             (-.437,1.870)]
    patch('Crown to orbital bridge '+str(_side),_bridge,
          lambda y,z,s=_side:_side_project(s,y,z,.016),crown,'head','frame',
          thickness=.009,sub=7)

# Crown roof remains close to v3's envelope, now built as short overlapping
# laminae rather than three broad smooth panels.
_roof=[(-.454,1.860,.065),(-.370,1.931,.111),(-.272,1.965,.123),
       (-.161,1.960,.114),(-.049,1.914,.081),(.015,1.852,.031)]
def _roof_point(x,y,raise_z=0):
    z,w=sample([(p[0],p[1],p[2]) for p in _roof],y)
    return (x,y,z-.034*(x/max(.025,w))**2+raise_z)
# The buried continuous roof bed closes seams between exposed cap laminae.
_roof_outline=[(-.063,-.454),(.063,-.454),(.111,-.370),(.123,-.272),
              (.114,-.161),(.081,-.049),(.031,.015),(-.031,.015),
              (-.081,-.049),(-.114,-.161),(-.123,-.272),(-.111,-.370)]
patch('Continuous cranial roof bed',_roof_outline,
      lambda x,y:_roof_point(x,y,-.003),crown,'head','frame',
      thickness=.010,sub=8)
for i,(y0,y1,w0,w1) in enumerate([
    (-.452,-.331,.065,.103),(-.382,-.258,.101,.121),
    (-.306,-.182,.119,.112),(-.226,-.102,.109,.078),
    (-.144,-.022,.075,.030)]):
    outline=[(-w0,y0),(w0*.78,y0+.012),(w0,y0+.030),
             (w1,y1-.025),(w1*.38,y1),(-w1*.56,y1-.004),
             (-w1,y1-.038),(-w0*.76,y0+.025)]
    project=lambda x,y:_roof_point(x,y,.004)
    patch(f'Compact swept crown lamina {i}',outline,project,crown,'head',
          'plate',thickness=.009,sub=8)
    control(f'Crown lamina edge {i}',[project(x,y) for x,y in outline],crown,
            'overlapping-crown-lamina',True)
    for x in (-w0*.62,w0*.62):
        fastener('Crown lamina root pin',_roof_point(x,y0+.024,.009),(0,0,1),
                 crown,'head',.0028)

# An overlapping fan of short leaf plates follows the bowed cranium. Rows are
# staggered, and each free edge sweeps aft with a crowned surface profile.
_blade_rows=[
    (1.919,[-.361,-.258,-.154,-.050],.052),
    (1.858,[-.326,-.223,-.120,-.017],.061),
    (1.795,[-.287,-.184,-.081],.067),
    (1.735,[-.243,-.140],.057),
]
for _side in (-1,1):
    for row,(z,centres,length) in enumerate(_blade_rows):
        for col,y in enumerate(centres):
            # Rounded, tapered feather form; its point sweeps back along the
            # skull instead of dropping as a rectangular hanging block.
            spread=.014 if row<2 else .012
            outline=[(y-.018,z+.006),(y-.002,z+.016),(y+.020,z+.013),
                     (y+.034,z-.004),(y+length*.58,z-length*.46),
                     (y+length,z-length*.60),(y+length*.88,z-length*.82),
                     (y+length*.42,z-length*.70),(y+.014,z-length*.34),
                     (y-.012,z-length*.18)]
            def project(yy,zz,s=_side,zr=z,ln=length):
                lift=.012+.010*max(0,min(1,(zr-zz)/ln))
                return _side_project(s,yy,zz,lift)
            patch(f'Swept temporal lamina {_side} {row} {col}',outline,project,
                  crown,'head','plate',thickness=.007,sub=5)
            control(f'Temporal lamina edge {_side} {row} {col}',
                    [project(y,z) for y,z in outline],crown,'swept-lamina',True)
            fastener('Temporal lamina root pin',project(y-.010,z+.004),
                     (_side,0,.12),crown,'head',.0028)

# The brow makes the crown-to-cere transition continuous around the eye.
for _side in (-1,1):
    _raised_rail('Shaped orbital brow ribbon '+str(_side),[
        (-.486,1.876,.016,.016,.004),(-.457,1.913,.017,.018,.004),
        (-.409,1.929,.017,.018,.004),(-.355,1.923,.016,.017,.004),
        (-.311,1.898,.015,.015,.004),(-.289,1.872,.014,.012,.003)],
        _side,crown,'head','edge',along=40)

# Recessed optic hardware and two nested curved cheek arches replace the
# broad flat cutout. The negative space below the optic narrows at the pivot,
# opens into a shallow crescent toward the cere, then tapers at its forward end.
for _side in (-1,1):
    _sculpted_eye_ring(_side)
    wr('Inset passive optic housing',(_side*.108,_eye_y,_eye_z),
       (_side*.123,_eye_y,_eye_z),.043,head,'optic','recess',sides=48)
    wr('Seated Advanced optic',(_side*.119,_eye_y,_eye_z),
       (_side*.125,_eye_y,_eye_z),.036,bpy.data.objects['builder-optics'],
       'optic','optic','builder',sides=40)
    _raised_rail('Outer sculpted cheek ribbon '+str(_side),[
        (-.470,1.839,.025,.017,.004),(-.464,1.767,.025,.018,.004),
        (-.433,1.704,.026,.017,.004),(-.400,1.670,.024,.016,.004),
        (-.363,1.646,.020,.014,.004),(-.337,1.624,.016,.010,.003)],
        _side,head,'head','edge',along=42)
    _raised_rail('Inner nested cheek ribbon '+str(_side),[
        (-.285,1.839,.030,.010,.003),(-.282,1.778,.030,.011,.003),
        (-.294,1.716,.030,.011,.003),(-.323,1.681,.027,.010,.003),
        (-.356,1.660,.023,.009,.003),(-.348,1.646,.018,.007,.003)],
        _side,head,'head','bearing',along=38)
    # Small swept cere lip ties the two arches into the upper bill root.
    _raised_rail('Cere cheek transition '+str(_side),[
        (-.449,1.852,.014,.012,.003),(-.474,1.829,.016,.012,.004),
        (-.491,1.797,.016,.010,.004),(-.479,1.765,.014,.009,.003)],
        _side,bill,'head','edge',along=28)
    wr('Coaxial mandible journal',_jp+Vector((_side*.075,0,0)),
       _jp+Vector((_side*.119,0,0)),.032,head,'head','bearing',sides=32)
    wr('Mandible journal cap',_jp+Vector((_side*.120,0,0)),
       _jp+Vector((_side*.126,0,0)),.023,jaw,'head','edge',sides=24)
    for y,z in [(-.400,1.775),(-.347,1.686),(-.448,1.810)]:
        fastener('Recessed cheek arch fixing',_side_project(_side,y,z,.030),
                 (_side,0,0),head,'head',.003)

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
