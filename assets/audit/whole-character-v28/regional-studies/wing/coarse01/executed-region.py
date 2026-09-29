"""V28 one coordinated compact folded-wing construction proposal.
Native Z-up/-Y-front. Authored dimensions are not measurements recovered from
art. No structural hardware, named rest, body, head, runtime or material edit.
"""
import bpy,bmesh,math,json
from mathutils import Vector
OWNERS=('left-mantle','right-mantle','left-wing-shield','right-wing-shield')

def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def names(label):
    shield=[f'{label} profiled mantle backing v4 {label}-wing-shield']+[f'V21 refined {label} compact shield course {c} plate {k}' for c,N in [(1,6),(2,6),(3,5)] for k in range(1,N+1)]+[f'V21 refined {label} elbow leading return',f'V21 refined {label} curved elbow sideguard']
    mantle=[f'{label} profiled mantle backing v4 {label}-mantle']+[f'V21 refined {label} mantle course {c} plate {k}' for c,N in [(5,9),(6,7)] for k in range(1,N+1)]+[f'V21 refined {label} stout shoulder leading guard',f'V21 refined {label} curved shoulder sideguard']
    return shield+mantle
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),json.dumps(dict(o.items()),sort_keys=True,default=lambda x:list(x)))
def snap(o):return (node(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),tuple((q.name,q.type) for q in o.modifiers),o.hide_render,o.hide_viewport)

def warp(p,side,joint,kind='shield',name='',bounds=None):
    radial=math.hypot(p.y-joint.y,p.z-joint.z);seat=ease((radial-.070)/.030)
    aft=max(0,min(1,(p.y-.040)/.370));q=p.copy()
    if kind=='shield':
        # Preserve the actual X running section/lining: its previous inboard
        # taper caused the new mantle collisions. Form only the compact ends.
        w=ease((1.025-p.z)/.170)*seat
        q.z+=w*(.065*(1-aft)**2-.045*aft**1.5)
        q.y+=w*(.014*aft-.004*(1-aft))
        # Replace the level upper sleeve edge with a recessed sloping receiver.
        # The first course remains a set of directional formed plates; its
        # roots tuck behind shortened mantle ends instead of a straight cuff.
        upper=name.endswith('wing-shield') or 'shield course 1 plate' in name or 'curved elbow sideguard' in name or 'elbow leading return' in name
        if upper:
            low,high=bounds if bounds else (.855,1.083)
            floor=low+.012 if 'shield course 1 plate' in name else 1.014
            t=ease((p.z-floor)/max(.018,high-floor));withdrawal=seat*t*(.010+.024*aft)
            q.z-=withdrawal
    else:
        # Lower two mantle courses, their open liner and finite returns share
        # one curved free-edge field. Upper/root/load-seat geometry is exact.
        w=ease((1.066-p.z)/.080)*seat
        a=max(0,min(1,(p.y+.040)/.385))
        lift=.024*(1-a)**1.4+.004*math.sin(math.pi*a)
        q.z+=w*lift
        q.y+=w*.006*a*(1-a)
    return q,(q-p).length

def apply():
    bpy.context.view_layer.update();candidates=sum((names(label) for label in ('left','right')),[]);nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};original={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH'};changed=[];records=[]
    for label,side in [('left',1),('right',-1)]:
        joint=bpy.data.objects[label+'-wing-shield'].matrix_world.translation.copy();assert abs(joint.z-1.007781744)<1e-6 and abs(joint.y-.039195534)<1e-6
        for name in names(label):
            o=bpy.data.objects[name];kind='shield' if o.parent.name.endswith('wing-shield') else 'mantle';assert o.parent.name in (label+'-wing-shield',label+'-mantle');assert o.get('surfaceRole') in ('frame','plate','guard')
            pts=[o.matrix_world@v.co for v in o.data.vertices];bounds=(min(p.z for p in pts),max(p.z for p in pts));mapped=[warp(p,side,joint,kind,name,bounds) for p in pts]
            if not any(d>1e-9 for q,d in mapped):continue
            o.data=o.data.copy();o.data.name=name+' V28 folded directional hierarchy';bpy.context.view_layer.update();inv=o.matrix_world.inverted();seats=0;count=0;maximum=0
            for v,(q,d) in zip(o.data.vertices,mapped):
                if d<=1e-9:seats+=1;continue
                v.co=inv@q;count+=1;maximum=max(maximum,d)
            o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
            o['geometryStatus']='V28 folded compact shield hierarchy proposal; one coarse rest/motion gate pending'
            o['v28WingConstruction']='Coordinated aft-down shield ends, recessed sloping upper receiver/first roots, and shortened directional mantle free ends with shaped liner/returns. Actual X running section, journal passage and load machinery retained. No ring or long train.'
            changed.append(name);records.append({'name':name,'owner':o.parent.name,'modifiedVertices':count,'exactReceivingSeatVertices':seats,'maximumVertexDisplacementM':maximum})
    bpy.context.view_layer.update();assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};outside={n:s for n,s in original.items() if n not in changed};assert all(snap(bpy.data.objects[n])==s for n,s in outside.items())
    return {'region':'folded compact wing hierarchy','status':'one coarse inferred proposal; visual/clearance review required','changedMeshes':changed,'added':[],'removed':[],'changedNodes':[],'nodesExact':len(nodes),'outsideMeshesExact':len(outside),'records':records,'contract':{'actualNativeXCoordinatesExact':True,'elbowReceivingSeatExactWithinYZRadiusM':.070,'upperMantleGeometryExactAtOrAboveZ':1.066,'foreEdgeLiftControlM':.065,'aftDropControlM':.045,'upperReceiverWithdrawalControlM':[.010,.034],'mantleFreeEdgeLiftControlM':.024,'existingWallDefinitionsExact':True,'materialsAndEraTagsExact':True,'singleRigidOwners':list(OWNERS)},'preserved':['All actual bearings/races/shafts/load members and restricted anatomical left motion','Named rigid nodes/rests and head/body/feet geometry','Existing era tags, material definitions and runtime APIs'],'limits':['Authoring controls are construction proposals, not dimensions recovered from art.','Native pose screens are finite geometry evidence, not continuous collision or physics proof.','Root-to-liner comparisons do not establish fastening or engineering readiness.']}
