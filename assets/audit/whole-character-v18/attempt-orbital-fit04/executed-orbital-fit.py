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
        for number,angle,radius in ((1,.18,.100),(2,.51,.104)):
            form=bpy.data.objects[f'Passive orbital attachment form {side} {number}']
            points=_world_points(form)
            mean=sum(points,Vector())/len(points)
            target=Vector((side*.150,center.x+radius*math.cos(angle),center.y+radius*math.sin(angle)))
            delta=target-mean
            _translate_mesh(form,delta)
            # A stepped 12 mm face stands above the retained arc backing. The
            # rear seat stays at 149 mm so this is supported, not a floating coin.
            inv=form.matrix_world.inverted()
            target_radius=.014 if number==1 else .0125
            original_radius=.010 if number==1 else .009
            for vertex in form.data.vertices:
                p=form.matrix_world@vertex.co
                p.y=target.y+(p.y-target.y)*target_radius/original_radius
                p.z=target.z+(p.z-target.z)*target_radius/original_radius
                i=vertex.index
                stand=.149 if i<40 or i==120 else .155 if i<80 else .161
                p.x=side*stand
                vertex.co=inv@p
            form.data.update();changed.append(form.name)
            records.append({'name':form.name,'worldCenterM':list(target),'worldTranslationM':list(delta),
              'functionStatus':'passive attachment form; specific function unknown'})
        # Re-form the lower leading shingle edge into a closer, rising return.
        # The high crown ridge and swept rear are retained: no whole lifted flap.
        lamina=bpy.data.objects[f'Swept temporal lamina {side} 0 0']
        pin_name='Temporal lamina root pin' if side==-1 else 'Temporal lamina root pin.014'
        for obj in (lamina,bpy.data.objects[pin_name]):
            inv=obj.matrix_world.inverted()
            for vertex in obj.data.vertices:
                p=obj.matrix_world@vertex.co
                t=max(0.,min(1.,(1.745-p.z)/.060))
                t=t*t*(3.-2.*t)
                forward=max(0.,min(1.,(-.29-p.y)/.060))
                p.z+=.034*t
                p.y+=.012*t*forward
                p.x-=side*.006*t*forward
                vertex.co=inv@p
            obj.data.update();changed.append(obj.name)
        # Form a finite underlap behind the fixed brow/arc. Corresponding
        # skins translate together; the shingle's YZ profile and wall survive.
        points=_world_points(lamina);half=len(points)//2
        assert len(points)==522, 'Expected paired 29 by 9 leading shingle skins'
        inv=lamina.matrix_world.inverted()
        for i in range(half):
            mid=(points[i]+points[i+half])*.5
            t=max(0.,min(1.,(mid.y+.285)/.035))
            t=t*t*(3.-2.*t)
            outer_limit=.114+.10*t
            outward=max(side*points[i].x,side*points[i+half].x)
            inset=max(0.,outward-outer_limit)
            for j in (i,i+half):
                q=points[j]-Vector((side*inset,0,0))
                lamina.data.vertices[j].co=inv@q
        lamina.data.update()
        pin=bpy.data.objects[pin_name];points=_world_points(pin)
        mid=sum(points,Vector())/len(points)
        _translate_mesh(pin,(side*.118-mid.x,0,0))
    bpy.context.view_layer.update()
    return {'region':'head','changed':changed,'added':[],'removed':[], 'newPivots':[],
      'construction':'Compact collar, seated bridge inner ends, staggered rear-arc passive fittings and locally returned leading temporal shingle with paired-skin inward lap and reseated root fixing. All dimensions are reconstruction choices.',
      'passiveFittingSeats':records,'leadingCrownReturn':{'maximumRiseM':.034,'maximumRearwardM':.012,'maximumInsetM':.006,'formingBlendUpperZ':1.745,'forwardUnderlapOuterLimitM':.114,'aftLapReturnBeginsY':-.285},
      'preserved':['existing mesh identities and owners','recessed optic/bearing/housing geometry','bill, jaw and cheek geometry','all 52 rigid nodes/transforms','materials and 462 historical guides'],
      'limits':['Discrete motion fit requires separate confirmation.','Passive fitting function remains unknown.','No owner likeness approval or physical engineering validation.']}
