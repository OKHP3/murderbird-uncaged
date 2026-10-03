"""Photoreal optic/cheek machinery proposal on the posed M3 head.
All new details use current object frames; original image/model files stay intact.
"""
import math
import bpy
from mathutils import Matrix,Vector


def apply(scene, scaffold_path=None, era='builder'):
    original=list(scene.objects);mats={};made=[];hidden=[];recesses=[]
    for o in original:
        if o.type=='MESH' and o.get('cg1cRegion')=='head' and o.data.materials:
            mats.setdefault(o.get('surfaceRole'),o.data.materials[0])
    glass=bpy.data.materials.new('CG2a optical glass '+era);glass.use_nodes=True
    p=glass.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(.83,.89,.87,1)
    p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.085
    p.inputs['IOR'].default_value=1.46;p.inputs['Transmission Weight'].default_value=.93
    p.inputs['Coat Weight'].default_value=.65;p.inputs['Coat Roughness'].default_value=.055
    glass['cg2aGlass']=True
    coil=bpy.data.materials.new('CG2a restrained amber coil '+era);coil.use_nodes=True
    cp=coil.node_tree.nodes.get('Principled BSDF');cp.inputs['Base Color'].default_value=(.12,.035,.003,1);cp.inputs['Metallic'].default_value=.55;cp.inputs['Roughness'].default_value=.3
    cp.inputs['Emission Color'].default_value=(1,.22,.012,1)
    cp.inputs['Emission Strength'].default_value=1.4 if era=='builder' else 0
    def finish(o,name,role,frame):
        bpy.context.view_layer.update()
        o.name='CG2a '+name;o.matrix_world=frame@o.matrix_world
        o['cg1cRegion']='head';o['surfaceRole']=role;o['exteriorEras']='maker,mechanic,builder'
        o['cg2aDetailProposal']=True
        o.data.materials.clear();o.data.materials.append(glass if role=='glass' else coil if role=='optic-ring' else mats.get(role,mats['bearing']))
        if role in ('glass','optic-ring'):o['cg2aPreserveMaterial']=True
        if not o.data.uv_layers:o.data.uv_layers.new(name='cg2a-uv')
        uv=o.data.uv_layers.active.data
        for poly in o.data.polygons:
            for i in poly.loop_indices:
                v=o.data.vertices[o.data.loops[i].vertex_index].co
                uv[i].uv=(.5+math.atan2(v.y,v.z)/(2*math.pi),.5+v.x)
        made.append(o.name);return o
    def ring(name,center,r,t,frame,role='bearing'):
        bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=64,minor_segments=10,location=center,rotation=(0,math.pi/2,0))
        o=finish(bpy.context.object,name,role,frame)
        for f in o.data.polygons:f.use_smooth=True
        return o
    def sphere(name,center,scale,frame,role):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=center)
        o=bpy.context.object;o.scale=scale;finish(o,name,role,frame)
        for f in o.data.polygons:f.use_smooth=True
        return o
    def mesh(name,v,f,frame,role):
        d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update()
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);return finish(o,name,role,frame)
    skull=next((o for o in original if 'continuous skull dark cavity back' in o.name.lower()),None)
    if skull:
        # Freeze only this already-approved evaluated skull cage before making
        # the aperture, avoiding applying a Boolean out of modifier order.
        deps=bpy.context.evaluated_depsgraph_get()
        baked=bpy.data.meshes.new_from_object(skull.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
        skull.data=baked
        for modifier in list(skull.modifiers):skull.modifiers.remove(modifier)
    # Supersede old near-flat iris graphics/seat screws with a deeper mechanism.
    for o in original:
        if any(t in o.name.lower() for t in ('iris concentric','iris radial engraving','stepped lens seat','lens seat screw')):
            o.hide_render=True;o['cg2aSuperseded']=True;hidden.append(o.name)
    for lens in original:
        if lens.type!='MESH' or 'recessed optic' not in lens.name.lower() or lens.hide_render:continue
        frame=lens.matrix_world.to_quaternion().to_matrix().to_4x4();frame.translation=lens.matrix_world.translation
        side=1 if frame.translation.x>0 else -1
        # Only a small awakened core emits; the visible iris is actual metal.
        oldradius=max(abs(lens.scale.y),abs(lens.scale.z))
        lens.scale.y*=.014/oldradius;lens.scale.z*=.014/oldradius;lens.scale.x*=.6
        lens['cg2aGlowCoreRadius']=.014
        sphere('curved clear optical glass '+str(side),(side*.006,0,0),(.006,.0275,.0275),frame,'glass')
        for j,(r,t,depth,role) in enumerate(((.034,.0028,-.004,'inner'),(.031,.0018,0,'bearing'),(.0265,.0014,.007,'edge'),(.012,.001,.004,'bearing'))):
            ring('deep optic stage %s %s'%(side,j),(side*depth,0,0),r,t,frame,role)
        # Eight overlapping iris blades; radial edges and varied depth replace
        # the undifferentiated orange disk without enlarging the optic seat.
        for j in range(8):
            a=j*math.pi/4;v=[]
            for r,theta in ((.012,a),(.025,a-.18),(.026,a+.40),(.013,a+.60)):
                v.append((side*(.0035+(j%2)*.0006),r*math.cos(theta),r*math.sin(theta)))
            o=mesh('mechanical iris blade %s %s'%(side,j),v,[(0,1,2,3)],frame,'bearing')
            o.modifiers.new('iris blade thickness','SOLIDIFY').thickness=.0006
        # Broken concentric coils provide uneven amber depth beneath glass,
        # leaving gaps/shadow between turns instead of one emissive disk.
        for course,radius in enumerate((.016,.0205,.0235)):
            for arc in range(3):
                vv=[];ff=[];count=24
                start=arc*2*math.pi/3+course*.18
                for j in range(count):
                    a=start+j*(1.68/(count-1));rr=radius+.00035*math.sin(3*a+course)
                    for k in range(6):
                        b=k*math.pi/3;t=.00065
                        vv.append((side*(.0045+t*math.sin(b)),(rr+t*math.cos(b))*math.cos(a),(rr+t*math.cos(b))*math.sin(a)))
                for j in range(count-1):
                    for k in range(6):ff.append((j*6+k,j*6+(k+1)%6,(j+1)*6+(k+1)%6,(j+1)*6+k))
                mesh('subglass amber coil %s %s %s'%(side,course,arc),vv,ff,frame,'optic-ring')
        # Upper brow hangs close over the eye with layered armored lips.
        for course in range(2):
            v=[];count=18
            for i in range(count):
                a=.17*math.pi+i*.70*math.pi/(count-1)
                for rr in (.040+course*.003,.051+course*.003):
                    v.append((side*(.005-course*.003),rr*math.cos(a),rr*math.sin(a)))
            f=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(count-1)]
            o=mesh('predatory orbital armor lip %s %s'%(side,course),v,f,frame,'plate')
            o.modifiers.new('brow returned metal','SOLIDIFY').thickness=.003
            b=o.modifiers.new('brow worn edge','BEVEL');b.width=.001;b.segments=2
        # An actual recessed oval cheek cavity within the accepted outer skull.
        # The cutter stays below the optic; its back contains gears and a rod.
        center=(side*(-.044),.018,-.092)
        if skull:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=1,location=center)
            cutter=bpy.context.object;cutter.scale=(.051,.058,.030)
            bpy.context.view_layer.update();cutter.matrix_world=frame@cutter.matrix_world
            modifier=skull.modifiers.new('CG2a recessed cheek aperture '+str(side),'BOOLEAN')
            modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
            # Apply only this visual aperture, leaving prior contour modifiers.
            bpy.context.view_layer.objects.active=skull
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.data.objects.remove(cutter,do_unlink=True);recesses.append(side)
        sphere('cheek cavity shadow back '+str(side),(side*(-.055),.018,-.092),(.009,.052,.027),frame,'inner')
        for j,(y,z,r) in enumerate(((-.009,-.092,.016),(.028,-.090,.019),(.049,-.091,.009))):
            center=(side*(-.027),y,z)
            ring('cheek gear seat %s %s'%(side,j),center,r,.002,frame)
            ring('cheek gear hub %s %s'%(side,j),center,r*.4,.0025,frame,'edge')
            teeth=14 if j!=2 else 10
            for k in range(teeth):
                a=k*2*math.pi/teeth
                bpy.ops.mesh.primitive_cube_add(size=1,location=(center[0],y+r*math.cos(a),z+r*math.sin(a)))
                o=bpy.context.object;o.scale=(.005,.005,.003);o.rotation_euler.x=a
                finish(o,'cheek gear tooth %s %s %s'%(side,j,k),'bearing',frame)
        # A slotted jaw reinforcement runs at the cavity's lower edge.
        v=[(side*(-.019),y,z) for y,z in ((-.037,-.115),(.005,-.124),(.063,-.117),(.055,-.106),(.005,-.113),(-.033,-.105))]
        o=mesh('cheek slotted lower jaw '+str(side),v,[(0,1,2,3,4,5)],frame,'plate')
        o.modifiers.new('jaw reinforcement thickness','SOLIDIFY').thickness=.003
    return {'module':'cinematic-cg-2a-head','era':era,'newMeshes':len(made),'supersededMeshCount':len(hidden),
            'cheekApertures':recesses,'headPoseDelta':[0,0,0],'headSizeTransform':1,'neckPoseDelta':[0,0,0],
            'advancedGlowCoreRadius':.014,'glass':{'transmission':.93,'roughness':.085,'ior':1.46,'coat':.65},
            'limits':['Hardware and hidden cavity forms are inferred CG proposals','No anatomical/engineering claim','Glass runtime requires glTF transmission/coat support','No final owner artistic acceptance claimed']}
