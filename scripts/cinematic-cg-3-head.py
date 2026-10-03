"""Optic/cheek detail on transformed accepted M2; existing shaders preserved."""
import math
import bpy
from mathutils import Matrix,Vector


def apply(scene, scaffold_path=None, era='builder'):
    existing=list(scene.objects);materials={}
    for o in existing:
        if o.type=='MESH' and o.get('cg1cRegion')=='head' and o.data.materials:
            materials.setdefault(o.get('surfaceRole'),o.data.materials[0])
    added=[];lenses=[]
    def finish(o,name,role,transform):
        o.name='CG3 '+name;o.matrix_world=transform@o.matrix_world
        o['cg1cRegion']='head';o['surfaceRole']=role;o['exteriorEras']='maker,mechanic,builder'
        o.data.materials.clear();o.data.materials.append(materials.get(role,materials['bearing']))
        if not o.data.uv_layers:o.data.uv_layers.new(name='cg3-uv')
        uv=o.data.uv_layers.active.data
        for poly in o.data.polygons:
            poly.use_smooth=True
            for li in poly.loop_indices:
                p=o.data.vertices[o.data.loops[li].vertex_index].co
                uv[li].uv=(.5+math.atan2(p.y,p.z)/(2*math.pi),.5+p.x*.5)
        added.append(o.name)
    for lens in existing:
        if lens.type!='MESH' or 'recessed optic' not in lens.name.lower() or lens.hide_render:continue
        old=lens.matrix_world.copy();rot=old.to_quaternion().to_matrix().to_4x4()
        rot.translation=old.translation;side=1 if old.translation.x>0 else -1
        # Restrained smaller awakened core, with curved dark surround and
        # specular metal lips supplying depth within the accepted diameter.
        lens.scale.x*=2.0;lens.scale.y*=.74;lens.scale.z*=.74;lenses.append(lens.name)
        for j,(r,t,depth,role) in enumerate(((.031,.0025,.002,'inner'),(.028,.0015,.004,'edge'),(.022,.001,.003,'bearing'))):
            bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=48,minor_segments=10,location=(side*depth,0,0),rotation=(0,math.pi/2,0))
            finish(bpy.context.object,'stepped lens seat %s %s'%(side,j),role,rot)
        # Eight tiny radial seat screws create non-emissive scale/depth cues.
        for j in range(8):
            a=j*math.pi/4
            bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=.0013,location=(side*.005,.029*math.cos(a),.029*math.sin(a)))
            finish(bpy.context.object,'lens seat screw %s %s'%(side,j),'rivet',rot)
    for o in existing:
        if 'cheek machinery bearing' not in o.name.lower() or o.hide_render:continue
        frame=o.matrix_world.copy()
        # New local concentric cheek journal; follows its existing posed axis.
        bpy.ops.mesh.primitive_torus_add(major_radius=.015,minor_radius=.002,major_segments=32,minor_segments=8,location=(0,0,.003))
        finish(bpy.context.object,'cheek recessed inner journal','inner',frame)
    return {'module':'cinematic-cg-3-head','era':era,'refinedLenses':lenses,'addedMeshes':len(added),
            'headPoseDelta':[0,0,0],'headEnvelopeTransform':1,'opticDiameterMultiplier':.74,
            'limits':['Lens curvature/specular seat is a CG glass cue; no new transmission shader','Existing era materials retain dark Maker/Mechanic optics','Cheek polish confined to existing machinery seats']}
