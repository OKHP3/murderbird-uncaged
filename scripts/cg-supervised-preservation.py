"""Keep receiving packed image history intact in newly saved CG studies.

The empty collection holds explicit image ID references. It adds no geometry
and changes no receiving material graph, image bytes, or fake-user flag.
"""

import hashlib

import bpy


def packed_image_snapshot():
    return {
        image.name: {
            "source": image.source,
            "filepath": image.filepath,
            "filepath_raw": image.filepath_raw,
            "colorspace": image.colorspace_settings.name,
            "alpha_mode": image.alpha_mode,
            "fake_user": image.use_fake_user,
            "size": list(image.size),
            "packed_sha256": hashlib.sha256(
                bytes(image.packed_file.data)
            ).hexdigest(),
        }
        for image in bpy.data.images
        if image.packed_file
    }


def retain_packed_image_ids(scene):
    name = "CG supervised packed history references"
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        scene.collection.children.link(collection)
    collection["cgAuthoringGuide"] = True
    collection["purpose"] = "Preserve packed image history; no rendered objects"
    for index, image in enumerate(bpy.data.images):
        if image.packed_file:
            collection["packedImage%04d" % index] = image
    return collection


def verify_receiving_images(snapshot):
    current = packed_image_snapshot()
    missing = [name for name in snapshot if name not in current]
    changed = [
        name for name in snapshot
        if name in current and current[name] != snapshot[name]
    ]
    if missing or changed:
        raise RuntimeError(
            "Receiving packed image history changed: "
            + repr({"missing": missing, "changed": changed})
        )
    return {"receiving_images": len(snapshot), "missing": [], "changed": []}
