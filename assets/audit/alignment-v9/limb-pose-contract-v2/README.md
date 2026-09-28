# Neutral runtime clearance pose snapshot v2

This immutable receipt stores actual Three.js rig matrices for the declared GLB at bounded runtime samples. Each pose includes the controller state, motion metrics, and every named exported transform node's local and world matrix. Arrays are column-major, as in Three.js. Blender-to-runtime coordinates use `browser=(BlenderX, BlenderZ, -BlenderY)`; use `C^-1 * M_runtime * C` for transform conversion.

The Maker runtime has no independent head or left-mantle control: head follows the neck's parent transform, and the single wing control moves the right mantle and shield. Those limits are recorded rather than filled with artificial poses. Inspection values call the production `applyInspectionPose` helper at a fixed exported rest pose.

The samples are deterministic kinematic inputs for later geometry diagnostics. They do not establish collision clearance, continuous swept-volume safety, physical simulation, browser appearance, or owner acceptance. The JSON binds the exact model and source hashes.
