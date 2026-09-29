"""Standalone read-only recursive Form01→Form02 foot equality check."""
from pathlib import Path
import bpy,json,hashlib,math
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise AssertionError(message)
def material_signature(material):
    nodes, links = [], []
    if material.use_nodes and material.node_tree:
        for node in material.node_tree.nodes:
            inputs = []
            for socket in node.inputs:
                if not socket.enabled or not hasattr(socket, "default_value"):
                    continue
                value = socket.default_value
                try:
                    value = [float(component) for component in value]
                except TypeError:
                    value = float(value) if isinstance(value, (int, float)) else str(value)
                inputs.append([socket.identifier, value])
            nodes.append({"name": node.name, "type": node.bl_idname,
                          "inputs": sorted(inputs, key=lambda item: item[0])})
        for link in material.node_tree.links:
            links.append([link.from_node.name, link.from_socket.name,
                          link.to_node.name, link.to_socket.name])
    payload = {
        "diffuseColor": [float(c) for c in material.diffuse_color],
        "metallic": float(material.metallic), "roughness": float(material.roughness),
        "useNodes": bool(material.use_nodes),
        "nodes": sorted(nodes, key=lambda item: item["name"]), "links": sorted(links),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def modifier_signature(obj):
    fields = {
        "SOLIDIFY": ("thickness", "offset", "use_rim", "use_even_offset", "use_quality_normals",
                     "material_offset", "material_offset_rim"),
        "BEVEL": ("width", "segments", "limit_method", "angle_limit", "offset_type", "profile",
                  "miter_outer", "affect", "harden_normals", "loop_slide", "clamp_overlap"),
        "WEIGHTED_NORMAL": ("keep_sharp", "weight", "thresh", "mode", "use_face_influence"),
    }
    records = []
    for modifier in obj.modifiers:
        require(modifier.type in fields, f"Unreviewed guard modifier type: {obj.name}/{modifier.type}")
        require(not (hasattr(modifier, "object") and modifier.object) and
                not (hasattr(modifier, "collection") and modifier.collection),
                f"Guard modifier has an external object/collection dependency: {obj.name}/{modifier.name}")
        values = {}
        for key in fields[modifier.type]:
            if not hasattr(modifier, key):
                continue
            value = getattr(modifier, key)
            if isinstance(value, (int, float, bool, str)):
                values[key] = value
            else:
                try:
                    values[key] = [float(component) for component in value]
                except TypeError:
                    values[key] = str(value)
        records.append({"name": modifier.name, "type": modifier.type,
                        "showViewport": modifier.show_viewport, "showRender": modifier.show_render,
                        "values": values})
    return records



def desc(o):
 while o:
  if o.name in ['left-foot','right-foot']:return True
  o=o.parent
 return False
def matrix(m):return [[float(c) for c in row] for row in m]
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def collect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();meshes={};nodes={}
 for o in bpy.data.objects:
  if not desc(o):continue
  common={'parent':o.parent.name if o.parent else None,'localMatrix':matrix(o.matrix_local),'worldMatrix':matrix(o.matrix_world),'props':{k:repr(o[k]) for k in o.keys()},'visibility':[o.hide_viewport,o.hide_render,o.hide_select,o.hide_get()]}
  if o.type=='EMPTY':nodes[o.name]=common
  elif o.type=='MESH':
   m=o.data;ev=o.evaluated_get(dg);em=ev.to_mesh();world=[list(ev.matrix_world@v.co) for v in em.vertices];assert all(math.isfinite(c) for p in world for c in p),o.name
   payload={**common,'vertices':[list(v.co) for v in m.vertices],'edges':[list(e.vertices) for e in m.edges],'faces':[[list(f.vertices),f.material_index,f.use_smooth] for f in m.polygons],'materialNames':[a.name if a else None for a in m.materials],'materialDefinitions':[material_signature(a) if a else None for a in m.materials],'modifiers':modifier_signature(o),'evaluatedWorldVertices':world,'evaluatedFaces':[[list(f.vertices),f.material_index] for f in em.polygons]}
   meshes[o.name]=digest(payload);ev.to_mesh_clear()
 return meshes,nodes
paths=[ROOT/'assets/models/whole-character-v28/attempt-form01/murderbird-whole-character-v28.blend',ROOT/'assets/models/whole-character-v28/attempt-form02/murderbird-whole-character-v28.blend'];expected=['a956aa9982d3e32c79433fb68b673f0d4f23a06b4c1f70838dbe835459c0c978','838a86b16766ddd4491c9f1cbe6a7aa0039c2b9e8514a04eb710d1e9b2f9bd9d'];receipts=[ROOT/'assets/audit/whole-character-v28'/a/'receipt.json' for a in ['attempt-form01','attempt-form02']];receiptHashes=[sha(p) for p in receipts];assert [sha(p) for p in paths]==expected
a,an=collect(paths[0]);b,bn=collect(paths[1]);assert a==b;assert an==bn;assert len(a)==94 and len(an)==18;assert [sha(p) for p in paths]==expected;assert [sha(p) for p in receipts]==receiptHashes
out={'status':'PASS all recursive foot meshes/nodes exactly equalForm01; no motion/art acceptance','sourceSHA256':sha(Path(__file__)),'natives':[{'path':str(p),'sha256':v} for p,v in zip(paths,expected)],'builderReceipts':[{'path':str(p),'sha256':v} for p,v in zip(receipts,receiptHashes)],'recursiveFootMeshCount':len(a),'changedFootMeshes':[],'exactFootNodeCount':len(an),'footNodes':sorted(an),'footMeshSignatures':a,'checks':'Exact unrounded raw/evaluated geometry,topology,materialslots+definitions,modifiers,era/customprops,local/worldrest,parenting,visibility. Foot subtree only.','form02BuilderScope':'Corrected predicate now records76protected/18declaredrevised vsV27; separateForm01→Form02 check verifies all94unchanged.','limits':['Read-only saved-rest subtree comparison only; no collision/grounded motion/physics or likeness approval.']}
(OUT/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'meshesExact':len(a),'nodesExact':len(an),'changed':0}))
