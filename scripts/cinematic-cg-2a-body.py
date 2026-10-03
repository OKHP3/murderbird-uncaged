"""Replace padded armor with thin forged leaf sheets on current posed geometry."""
import math
import bpy
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    collection=bpy.data.collections.new('CG2a thin body shield armor hardware');scene.collection.children.link(collection)
    plates=hardware=0;max_boundary=max_vertex=0.;skipped=[];normal_slots={}
    objects=list(scene.objects)
    for obj in objects:
        if obj.get('cg1cRegion') in ('body','wing'):
            key=(obj.get('cg1cRegion'),obj.get('surfaceRole'))
            if obj.type=='MESH' and obj.data.materials:normal_slots.setdefault(key,list(obj.data.materials))
    def newmesh(name,vs,fs,uv,region,role):
        nonlocal hardware
        data=bpy.data.meshes.new(name);data.from_pydata([tuple(v) for v in vs],[],fs);data.update()
        obj=bpy.data.objects.new(name,data);collection.objects.link(obj)
        obj['cg1cRegion']=region;obj['cg2aRegion']=region;obj['surfaceRole']=role;obj['exteriorEras']='maker,mechanic,builder'
        for material in normal_slots.get((region,role),normal_slots.get((region,'plate'),[])):data.materials.append(material)
        layer=data.uv_layers.new(name='leaf-uv')
        for face in data.polygons:
            for li in face.loop_indices:layer.data[li].uv=uv[data.loops[li].vertex_index]
        hardware+=1;return obj
    # Taper the lower metal leaf, keeping the fixed root and large form intact.
    outline=[(-.40,0),(.40,0),(.48,.24),(.40,.65),(.20,.90),(0,1.025),(-.20,.92),(-.40,.65),(-.48,.24)]
    for obj in objects:
        region=obj.get('cg1cRegion')
        if region not in ('body','wing') or obj.get('surfaceRole')!='plate' or obj.type!='MESH' or obj.get('cg2aThinLeaf'):continue
        old=obj.data
        if len(old.vertices)!=28:
            skipped.append(obj.name);continue
        world=[obj.matrix_world@v.co for v in old.vertices]
        normal=Vector()
        for i,f in enumerate(old.polygons):
            if i%3!=2:normal+=(obj.matrix_world.to_3x3().inverted().transposed()@f.normal)*f.area
        if normal.length<1e-8:skipped.append(obj.name);continue
        normal.normalize();top=(world[0]+world[1])/2
        u=(world[1]-world[0]).normalized();v=(world[5]-top);v-=u*v.dot(u);v.normalize()
        # Retain the existing major sheet location but remove artificial M3 inflation.
        crown=float(obj.get('cg3CrownPeak',0));centre=world[18]-normal*crown
        width=max(.012,(world[2]-world[8]).length/.98);height=max(.018,(world[5]-top).dot(v))
        # Gentle cylindrical bend across the leaf is metal curvature, not a pillow dome.
        def sheet(a,b,under=False):
            bend=-.0020*(a/.5)**2+.00025*math.sin(b*math.pi)
            return centre+u*(a*width)+v*((b-.4)*height)+normal*(bend-(.00135 if under else 0))
        coords=outline+[(a*.52,.4+(b-.4)*.52) for a,b in outline]+[(0,.4)]+outline
        proposed=[sheet(a,b,i>18) for i,(a,b) in enumerate(coords)]
        # Bound every change to 0.009 visual study units in visual study units, including sheet roots.
        for i,p in enumerate(proposed):
            delta=p-world[i]
            if delta.length>.009:proposed[i]=world[i]+delta.normalized()*.009
            displacement=(proposed[i]-world[i]).length
            max_vertex=max(max_vertex,displacement)
            if i<9:max_boundary=max(max_boundary,displacement)
        faces=[]
        for i in range(9):
            j=(i+1)%9
            faces.extend([(i,j,9+j,9+i),(18,9+i,9+j),(i,19+i,19+j,j)])
        if (proposed[1]-proposed[0]).cross(proposed[2]-proposed[0]).dot(normal)<0:faces=[tuple(reversed(f)) for f in faces]
        data=bpy.data.meshes.new(obj.name+' forged leaf');data.from_pydata([tuple(obj.matrix_world.inverted()@p) for p in proposed],[],faces);data.update()
        for mat in old.materials:data.materials.append(mat)
        uv=data.uv_layers.new(name='leaf-uv')
        for index,face in enumerate(data.polygons):
            # Smooth only the two top-sheet faces per sector. Keep the thin
            # sidewall discontinuity sharp, with no geometry inflation.
            face.use_smooth=index%3!=2
            for li in face.loop_indices:
                a,b=coords[data.loops[li].vertex_index];uv.data[li].uv=(a+.5,1-b)
        obj.data=data;obj['cg2aThinLeaf']=True;obj['cg2aRegion']=region;plates+=1
        # Real thin lower rim, sharp normals and a continuous dark underlap shadow.
        edge=proposed[2:9];ev=[];eu=[]
        for i,p in enumerate(edge):
            toward=(centre-p);toward-=normal*toward.dot(normal)
            if toward.length:toward.normalize()
            ev.extend([p+normal*.0005,p+toward*.0012+normal*.00055]);eu.extend([(i/6,0),(i/6,1)])
        ef=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(6)]
        newmesh(obj.name+' sharp metal rim',ev,ef,eu,region,'edge')
        seam=[p-normal*.0010 for p in edge];sv=[]
        for p in seam:sv.extend([p,p-normal*.0018])
        newmesh(obj.name+' dark underlap',sv,ef,eu,region,'inner')
        # Sparse normalised-UV rivet seats, avoiding a tidy uniform gold grid.
        if plates%3==0:
            base=sheet(-.19,.22)+normal*.0007;r=.0018 if region=='wing' else .0022
            vs=[];uvs=[]
            for radius,depth in ((r,0),(r*.76,.0010)):
                for i in range(10):
                    angle=i*math.tau/10;vs.append(base+u*radius*math.cos(angle)+v*radius*math.sin(angle)+normal*depth);uvs.append((.5+.5*math.cos(angle),.5+.5*math.sin(angle)))
            fs=[(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]+[tuple(range(10,20))]
            newmesh(obj.name+' countersunk rivet head',vs,fs,uvs,region,'rivet')
    # Earlier rolled pipes looked like upholstered piping; retire only their render copies.
    retired=0
    for obj in objects:
        if obj.get('cg1cRegion') in ('body','wing') and 'thin rolled edge' in obj.name:
            obj.hide_render=True;obj.hide_set(True);obj['cg2aReplacedPiping']=True;retired+=1
    return {'module':'cg2a-body','platesRebuilt':plates,'newHardwareMeshes':hardware,'retiredRoundPiping':retired,'maximumBoundaryDisplacement':max_boundary,'maximumVertexDisplacement':max_vertex,'skipped':skipped,'methods':['Bounded thin bent leaf topology with smooth sheet interiors and sharp sidewalls; M3 crown inflation removed','Tapered teardrop tails; physical rolled rim ribbons, dark underlaps and sparse countersunk heads','Existing plate materials inherited; new detail inherits era-matched edge/inner/rivet materials; all meshes have UVs'],'limits':['Boundary correction capped at .009 visual units; major volumes, stance, head, neck, hip and foot anchors unchanged','No balance or fabrication claim; integrated render must assess metal read and any local facet seams']}
