"""Angle the retained cervical arch and scale the cranial castings around their attachment."""
import bpy
from mathutils import Vector, Matrix
ATLAS=Vector((0,-.11437,1.56159))
ADVANCE=Vector((0,-.075,-.021))
HEAD_SCALE=1.165
def apply_reach():
    # Both sides of the cranial bearing follow the new rest joint. The floor/pelvis are untouched.
    skull_xform=Matrix.Translation(ATLAS+ADVANCE) @ Matrix.Scale(HEAD_SCALE,4) @ Matrix.Translation(-ATLAS)
    for obj in list(bpy.context.scene.objects):
        if obj.type!='MESH' or obj.hide_render or not obj.visible_get(): continue
        tag=obj.get('fc_region',obj.get('cg1cRegion',''))
        if tag=='head':
            obj.matrix_world=skull_xform @ obj.matrix_world
        if tag=='neck':
            if obj.data.users>1: obj.data=obj.data.copy()
            world=obj.matrix_world.copy();inv=world.inverted()
            for vertex in obj.data.vertices:
                v=world@vertex.co
                t=min(1,max(0,(v.z-1.29)/.278))
                t=t*t*(3-2*t)
                # Widen the socket as it joins the larger head bearing.
                v.x*=1+(HEAD_SCALE-1)*t*.67
                v+=ADVANCE*t
                vertex.co=inv@v
            obj.data.update()
    bpy.context.view_layer.update()
    return tuple(ATLAS+ADVANCE)
