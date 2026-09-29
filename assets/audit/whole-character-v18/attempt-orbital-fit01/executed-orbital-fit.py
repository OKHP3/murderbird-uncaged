"""Reseat passive orbital fittings and fit the leading crown lamina on V17.

Authored reconstruction, not recovered engineering. Existing optics, bill,
jaw, pivot transforms, neutral materials and historical guides remain exact.
"""
import math
import bpy
from mathutils import Vector


def _world_points(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def _translate_mesh(obj, delta):
    inv = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        vertex.co = inv @ (obj.matrix_world @ vertex.co + Vector(delta))
    obj.data.update()


def apply():
    changed = []
    records = []
    for side in (-1, 1):
        race = bpy.data.objects[f'Orbital passive retaining race {side}']
        points = _world_points(race)
        center = Vector((sum(p.y for p in points)/len(points), sum(p.z for p in points)/len(points)))
        inv = race.matrix_world.inverted()
        # Keep the recessed bearing seat; narrow the projecting outer collar.
        for vertex in race.data.vertices:
            p = race.matrix_world @ vertex.co
            direction = Vector((p.y-center.x, p.z-center.y))
            r = direction.length
            new_radius = .0575 + (r-.0575) * (.0095/.0135)
            direction *= new_radius/r
            p.y = center.x+direction.x; p.z = center.y+direction.y
            vertex.co = inv @ p
        race.data.update();changed.append(race.name)
        # Existing bridges continue to meet the now narrower collar.
        for number in (1, 2, 3):
            bridge=bpy.data.objects[f'Orbital support bridge {side} {number}']
            inv=bridge.matrix_world.inverted()
            for vertex in bridge.data.vertices:
                p=bridge.matrix_world @ vertex.co
                r=math.hypot(p.y-center.x,p.z-center.y)
                blend=max(0.,min(1.,(.092-r)/.022))
                if blend:
                    dr=.004*blend
                    p.y=center.x+(p.y-center.x)*(r-dr)/r
                    p.z=center.y+(p.z-center.y)*(r-dr)/r
                    vertex.co=inv@p
            bridge.data.update();changed.append(bridge.name)
        # Two staggered fittings occupy the rear orbital arc instead of being
        # stacked beneath the crown's foremost edge. They remain passive.
        for number,angle,radius in ((1,.22,.097),(2,.54,.104)):
            form=bpy.data.objects[f'Passive orbital attachment form {side} {number}']
            points=_world_points(form)
            mean=sum(points,Vector())/len(points)
            target=Vector((side*.150,center.x+radius*math.cos(angle),center.y+radius*math.sin(angle)))
            delta=target-mean
            _translate_mesh(form,delta);changed.append(form.name)
            records.append({'name':form.name,'worldCenterM':list(target),'worldTranslationM':list(delta),
              'functionStatus':'passive attachment form; specific function unknown'})
        # Re-form the leading swept crown piece as a raised overlapping shingle;
        # retain its entire profile and matched root fixing, rather than cut it.
        lamina=bpy.data.objects[f'Swept temporal lamina {side} 0 0']
        pin_name='Temporal lamina root pin' if side==-1 else 'Temporal lamina root pin.014'
        for obj in (lamina,bpy.data.objects[pin_name]):
            _translate_mesh(obj,(0.,.006,.025));changed.append(obj.name)
    bpy.context.view_layer.update()
    return {'region':'head','changed':changed,'added':[],'removed':[], 'newPivots':[],
      'construction':'Compact collar, seated bridge inner ends, staggered rear-arc passive fittings and raised leading temporal shingle/root fixing. All dimensions are reconstruction choices.',
      'passiveFittingSeats':records,'leadingCrownTranslationM':[0,.006,.025],
      'preserved':['existing mesh identities and owners','recessed optic/bearing/housing geometry','bill, jaw and cheek geometry','all 52 rigid nodes/transforms','materials and 462 historical guides'],
      'limits':['Discrete motion fit requires separate confirmation.','Passive fitting function remains unknown.','No owner likeness approval or physical engineering validation.']}
