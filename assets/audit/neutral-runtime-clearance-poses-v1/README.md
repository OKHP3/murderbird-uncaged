# Neutral runtime clearance pose snapshot v1

This immutable receipt stores actual Three.js rig matrices for the declared GLB at bounded runtime samples. Each pose includes controller state, motion metrics, and local/world matrices for all 264 named transforms found beneath the active runtime model at capture time. That list includes the 142 named transforms loaded from the GLB and nodes added by `createEraMechanisms`; native geometry consumers should match `path` and `name` against the declared GLB and omit added runtime nodes. Arrays are column-major, as in Three.js. Blender-to-runtime coordinates use `browser=(BlenderX, BlenderZ, -BlenderY)`; use `C^-1 * M_runtime * C` for transform conversion.

The Maker channels captured are leg, wing, tail, neck, and jaw, including the active `createEraMechanisms` layer which applies the tail pivot. Head follows the neck's parent transform; the wing input moves the right mantle/shield, with no independent left-mantle control. Inspection values call the production `applyInspectionPose` helper at a fixed exported rest pose.

The samples are deterministic kinematic inputs for later geometry diagnostics. They do not establish collision clearance, continuous swept-volume safety, physical simulation, browser appearance, or owner acceptance. The JSON binds the exact model and source hashes.
