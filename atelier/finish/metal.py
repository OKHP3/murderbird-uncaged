"""Apply image-based metal finish to the visible, assembled review character."""
from pathlib import Path
import hashlib
import bpy
import numpy as np

MAPS = Path(__file__).resolve().parent / "maps"
LIBRARY = {}
UV_NAME = "FirstChoiceSurface"

def family_for(obj, material):
    objname=obj.name.lower()
    name=material.name.lower() if material else ""
    if name.startswith("cgo13") or "leather" in name or "enamel" in name:  # the retained optical stack has its own radial UV set
        return None
    if obj.get("fc_region") in ("stand","saddle") or ("first choice" in name and "saddle" in name):
        if any(w in name for w in ("pin","bush","bronze","brass")): return "bronze"
        if any(w in name for w in ("seat","raw","rub","steel","wear")): return "steel"
        return "stand"
    if any(w in name for w in ("cavity","rubber","graphite","black-iron","black iron","blackened iron")):
        return "iron"
    if any(w in name for w in ("claw","talon")) or (("claw" in objname or "talon" in objname) and "bronze" not in name):
        return "talon"
    if objname.startswith("fc head"):
        if "occipital feather" in objname or "sagittal poll" in objname:
            return "mantle"
        if any(x in objname for x in ("orbital cheek","temporal casting","mandible","mandibular cover")):
            return "bronze" if "bronze" in name else "iron"
        if "nasal bridge" in objname: return "steel"
        if "hooked blade" in objname: return "bill"
        if "orbital hood" in objname or "brow" in objname: return "brow"
    if "wing-armor" in name or "mantle" in name: return "mantle"
    if "breast-armor" in name or "pectoral" in name: return "breast"
    if "crown" in name or "brow" in name or (("brow" in objname or "forehead" in objname) and "armor" in name):
        return "brow"
    if "head-armor" in name or "beak" in name or "bill" in name: return "bill"
    if any(w in name for w in ("worn-bronze","bronze","brass","gilt","copper")): return "bronze"
    if any(w in name for w in ("polished","machined","steel","nickel","rim","chrome","hammered gunmetal")): return "steel"
    return "iron"

def get_material(family):
    if family in LIBRARY: return LIBRARY[family]
    mat=bpy.data.materials.new("First Choice · "+family.title())
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    bsdf=nodes.get("Principled BSDF")
    uv=nodes.new("ShaderNodeUVMap")
    uv.uv_map=UV_NAME
    def texture(part, ext):
        node=nodes.new("ShaderNodeTexImage")
        node.image=bpy.data.images.load(str(MAPS/f"{family}-{part}.{ext}"),check_existing=True)
        node.image.colorspace_settings.name="sRGB" if part=="albedo" else "Non-Color"
        node.image.pack()
        links.new(uv.outputs["UV"],node.inputs["Vector"])
        return node.outputs["Color"]
    attribute=nodes.new("ShaderNodeVertexColor")
    attribute.layer_name="FC_Occlusion"
    multiply=nodes.new("ShaderNodeMixRGB")
    multiply.blend_type="MULTIPLY";multiply.inputs[0].default_value=1.
    links.new(texture("albedo","jpg"),multiply.inputs[1])
    links.new(attribute.outputs["Color"],multiply.inputs[2])
    links.new(multiply.outputs["Color"],bsdf.inputs["Base Color"])
    channels=nodes.new("ShaderNodeSeparateColor")
    links.new(texture("orm","png"),channels.inputs["Color"])
    links.new(channels.outputs["Green"],bsdf.inputs["Roughness"])
    links.new(channels.outputs["Blue"],bsdf.inputs["Metallic"])
    n=nodes.new("ShaderNodeNormalMap")
    n.uv_map=UV_NAME
    n.inputs['Strength'].default_value=.17 if family in ('steel','talon','bill') else .34
    links.new(texture("normal","jpg"),n.inputs["Color"])
    links.new(n.outputs["Normal"],bsdf.inputs["Normal"])
    LIBRARY[family]=mat
    return mat

def project_surface(obj):
    # A meter-consistent mapping keeps fine grain continuous across different size parts.
    mesh=obj.data
    if mesh.users>1:
        mesh=mesh.copy()
        obj.data=mesh
    uv=mesh.uv_layers.get(UV_NAME) or mesh.uv_layers.new(name=UV_NAME)
    xyz=np.empty(len(mesh.vertices)*3,'f')
    mesh.vertices.foreach_get("co",xyz)
    w=np.asarray(obj.matrix_world)
    world=xyz.reshape(-1,3).dot(w[:3,:3].T)+w[:3,3]
    normals=np.empty(len(mesh.polygons)*3,'f')
    mesh.polygons.foreach_get("normal",normals)
    normals=normals.reshape(-1,3).dot(np.linalg.pinv(w[:3,:3]))
    counts=np.empty(len(mesh.polygons),'i')
    mesh.polygons.foreach_get("loop_total",counts)
    axis=np.abs(normals).argmax(axis=1).repeat(counts)
    indices=np.empty(len(mesh.loops),'i')
    mesh.loops.foreach_get("vertex_index",indices)
    p=world[indices]
    projected=np.stack([np.where(axis==0,p[:,1],p[:,0]),np.where(axis==2,p[:,1],p[:,2])],axis=1)
    phase=int.from_bytes(hashlib.sha256(obj.name.encode()).digest()[:4],"little")
    rng=np.random.default_rng(phase)
    angle=rng.uniform(-.76,.76)
    cs,sn=np.cos(angle),np.sin(angle)
    uvcoords=(projected.dot([[cs,-sn],[sn,cs]])/rng.uniform(.32,.47)+rng.random(2)).astype('f')
    uv.data.foreach_set("uv",uvcoords.ravel())
    uv.active_render=True
    mesh.uv_layers.active=uv

def apply_finish(objects):
    for obj in objects:
        if obj.type!="MESH": continue
        slots=[s.material for s in obj.material_slots]
        if not slots: continue
        families=[family_for(obj,m) for m in slots]
        if not any(families): continue
        project_surface(obj)
        for i,f in enumerate(families):
            if f: obj.material_slots[i].material=get_material(f)
