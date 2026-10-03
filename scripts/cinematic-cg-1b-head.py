"""Milestone 1b head/neck appearance study; call apply after original GLB import.
World-space edits avoid double transforms in the imported assembly hierarchy.
No engineering claim; continuous cavity backs and intersecting scale forms are CG.
"""
import math
import bpy
from mathutils import Vector, Matrix


def apply(scene):
    added=[]
    def tag(o,region,role):
        o['cg1bRegion']=region;o['region']=region;o['surfaceRole']=role
        o['exteriorEras']='maker,mechanic,builder';o['cgVisualStudy']=True
        added.append(o.name)
        return o
    def mesh(name,verts,faces,region='head',role='plate',bevel=.002):
        d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);tag(o,region,role)
        if bevel:
            m=o.modifiers.new('CG soft forged edge','BEVEL');m.width=bevel;m.segments=2
            m=o.modifiers.new('CG weighted face normals','WEIGHTED_NORMAL')
        return o
    def patch(name,yz,x,side,region='head',role='plate',depth=.009):
        # Slightly convex side plate with a closed rim, suitable for glTF export.
        n=len(yz);v=[(side*x,y,z) for y,z in yz]
        v += [(side*(x-depth),y,z) for y,z in yz]
        cy=sum(y for y,z in yz)/n;cz=sum(z for y,z in yz)/n
        v.append((side*(x+.013),cy,cz));v.append((side*(x-depth),cy,cz))
        f=[(i,(i+1)%n,2*n) for i in range(n)]
        f += [(n+i,2*n+1,n+(i+1)%n) for i in range(n)]
        f += [(i,n+i,n+(i+1)%n,(i+1)%n) for i in range(n)]
        return mesh(name,v,f,region,role)
    def ring(name,pos,radius,thickness,role='bearing',region='head'):
        bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=thickness,
            major_segments=48,minor_segments=8,location=pos,rotation=(0,math.pi/2,0))
        o=bpy.context.object;o.name=name;tag(o,region,role)
        for p in o.data.polygons:p.use_smooth=True
        return o
    def bolt(name,pos,region='head'):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.005,location=pos)
        o=bpy.context.object;o.name=name;o.scale=(.42,1,1);tag(o,region,'rivet')
        return o
    imported=list(scene.objects);changed=0
    for o in imported:
        if o.type!='MESH':continue
        region=o.get('region','');name=o.name.lower()
        head=region in ('head','head-reconstruction')
        neck=region=='neck' or 'neck-profile rigid silhouette' in name
        if not(head or neck):continue
        # Retain hierarchy/pivots while applying the edit to unique mesh vertices.
        o.data=o.data.copy();w=o.matrix_world.copy();inv=w.inverted()
        for v in o.data.vertices:
            p=w@v.co
            if head:
                p.x*=1.12;p.y=-.55+(p.y+.55)*1.035;p.z-=.075
            else:
                p.x*=1.14;p.z=1.20+(p.z-1.20)*.80
            v.co=inv@p
        o['cg1bRegion']='head' if head else 'neck';changed+=1
        if 'neck-profile rigid silhouette' in name:
            # Preserve original authoring meshes, omit the smooth stacked tube.
            o.hide_render=True;o['cg1bSuperseded']=True
        if 'optic' in name or 'optical aperture' in name:
            o['region']='head';o['surfaceRole']='recess' if 'passive' in name else o.get('surfaceRole','bearing')
    # Back the fragmented temporal framework, while keeping an intentional black
    # cheek aperture beneath the optic and around the descending lower jaw.
    for side in (-1,1):
        prefix='CG1b '+('left' if side<0 else 'right')
        patch(prefix+' temporal continuity back',[
            (-.66,1.68),(-.52,1.73),(-.38,1.69),(-.29,1.59),
            (-.34,1.48),(-.47,1.48),(-.52,1.54),(-.62,1.56)],.139,side,role='recess')
        for course in range(3):
            yy=-.43+course*.023;zz=1.69-course*.053
            patch(prefix+' curved temple overlap '+str(course),[
                (yy-.091,zz+.015),(yy-.025,zz+.035),(yy+.050,zz+.015),
                (yy+.070,zz-.025),(yy+.040,zz-.060),(yy-.035,zz-.043),
                (yy-.077,zz-.012)],.155-course*.003,side)
        patch(prefix+' orbital brow',[
            (-.706,1.675),(-.659,1.726),(-.58,1.749),(-.49,1.718),
            (-.49,1.686),(-.58,1.706),(-.651,1.691)],.178,side)
        patch(prefix+' lower orbital cheek lip',[
            (-.697,1.58),(-.656,1.595),(-.603,1.561),(-.54,1.585),
            (-.48,1.625),(-.455,1.600),(-.514,1.552),(-.595,1.537)],.177,side)
        patch(prefix+' cheek opening shadow',[
            (-.705,1.55),(-.66,1.588),(-.59,1.555),(-.52,1.546),
            (-.57,1.495),(-.684,1.450),(-.747,1.393),(-.710,1.486)],.125,side,role='recess')
        # Three rings give the circular optic a deep seated, mechanical bezel.
        for i,(rad,t,x) in enumerate(((.053,.007,.166),(.044,.004,.180),(.035,.003,.182))):
            ring(prefix+' optic bezel '+str(i),(side*x,-.597,1.617),rad,t)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,
            location=(side*.178,-.597,1.617))
        o=bpy.context.object;o.name=prefix+' inset optic lens';o.scale=(.005,.031,.031)
        tag(o,'head','optic');o['cg1bOpticCanon']='dark maker/mechanic; restrained orange builder'
        for p in o.data.polygons:p.use_smooth=True
        for y,z in ((-.670,1.707),(-.60,1.728),(-.515,1.701),(-.680,1.58),(-.54,1.575)):
            bolt(prefix+' facial fastener',(side*.188,y,z))
        # Small surface breaks on the bill root; preserve its long hook.
        patch(prefix+' bill root seam plate',[
            (-.709,1.651),(-.739,1.625),(-.759,1.590),
            (-.752,1.571),(-.729,1.605),(-.705,1.628)],.103,side,role='edge',depth=.004)
        for yy,zz in ((-.719,1.630),(-.746,1.592)):
            bolt(prefix+' bill seam rivet',(side*.113,yy,zz))
        # Rear swept plates bridge existing crown scales into the neck silhouette.
        for i in range(5):
            y=-.44+i*.020;z=1.67-i*.043
            patch(prefix+' swept nape overlap '+str(i),[
                (y-.065,z+.035),(y+.01,z+.047),(y+.068,z-.027),
                (y+.048,z-.071),(y-.025,z-.034)],.138-i*.006,side)
            bolt(prefix+' nape fastener '+str(i),(side*(.147-i*.006),y-.019,z+.014))
    # Curved broad neck underlay with shingle plates following its contour.
    # x is cross-bird, forward is -y; base connects into breast at z 1.20.
    levels=[(1.18,-.235,.167,.16),(1.26,-.29,.155,.15),
            (1.34,-.345,.14,.14),(1.42,-.39,.128,.135),(1.51,-.425,.122,.13)]
    verts=[];n=32
    for z,y,rx,ry in levels:
        verts += [(rx*math.sin(2*math.pi*i/n),y-ry*math.cos(2*math.pi*i/n),z) for i in range(n)]
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)
           for j in range(len(levels)-1) for i in range(n)]
    mesh('CG1b continuous dark cervical back',verts,faces,'neck','recess',0)
    for row in range(5):
        z=1.23+row*.065;y=-.27-row*.037
        rx=.161-row*.008;ry=.156-row*.005
        # Circumferential leaves break the hose-like stage silhouette.
        for col in range(10):
            a=2*math.pi*(col+(row%2)*.5)/10;da=.34
            points=[]
            for d,h in ((-da,.033),(0,.046),(da,.033),(da*.74,-.020),(0,-.057),(-da*.74,-.020)):
                zz=z+h;yy=y-ry*math.cos(a+d)
                points.append(((rx+.012)*math.sin(a+d),yy,zz))
            # Crown the leaf across its face: center follows the neck's
            # radial normal, rather than leaving a single flat ngon.
            v=points+[(x*.958,yy+.003,zz) for x,yy,zz in points]
            cy=sum(p[1] for p in points)/6;cz=sum(p[2] for p in points)/6
            cx=sum(p[0] for p in points)/6
            v.append((cx+.015*math.sin(a),cy-.015*math.cos(a),cz+.002))
            f=[(i,(i+1)%6,12) for i in range(6)]
            f += [tuple(range(11,5,-1))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
            leaf=mesh('CG1b cervical scale %02d %02d'%(row,col),v,f,'neck','plate',.003)
            for face in leaf.data.polygons:face.use_smooth=True
            if col in (2,3,7,8):bolt('CG1b neck scale fastener',(rx*1.075*math.sin(a),y-ry*math.cos(a),z+.022),'neck')
    return {'module':'cinematic-cg-1b-head','changedOriginalMeshes':changed,
            'addedObjects':len(added),'headTranslationZ':-.075,'headWidthMultiplier':1.12,
            'neckHeightMultiplier':.80,'scope':'CG continuity backs, heavier head, overlapping cervical scales, layered recessed optics; July bill retained',
            'tradeoff':'Intersecting visual forms; unseen joins simplified; no mechanical validation'}
