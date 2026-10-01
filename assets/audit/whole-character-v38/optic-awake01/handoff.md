# Optic-awake01 — one Advanced-only amber proposal

Root actualbrowser/owner calibration pending. Retained jaw-stock01 source; no heldbreast/crown used. Only V38 contrast / optic material5 changes: base[.22,.065,.008,1], emissive[.45,.13,.015], roughness.28, metallic.2 retained. No bloom/newlight/chestglow/laser or geometry alteration.

Native Principled BaseColor/Roughness/EmissionColor and diffusecolor/roughness mirrors match the amended JSON eraFinishes.builder profile. EmissionStrength1 remains sourceexact. Actualnative optics-only glTF export factors agree within1e-6. FinalruntimeGLB patches only material5 and its builder profile in the immutable sourceGLB, preserving all11other materialrecords, node/hierarchy/extras/mesh/accessor/buffer records and binarychunks exactly. Only two V31 Advanced optical aperture ±1 nodes use this material; exteriorEras builder/roleoptic remain exact. No earlier-era profiles added.

Native2e4b4c01f415a30ae875b772b6e15ceeedf131aae97edb272b1fe54744858355; GLBac158465fceeab967f207f0cbe820301a985dad9f17a2cf0dfba287050ca7d9b. Versionedmodel paths assets/models/whole-character-v38/optic-awake01/. Runnablewrite-once builder scripts/build-v38-optic-awake01.py pins source507a58native/0099e5GLB, records unchangednativeobject/material proofs and nativeexport correspondence. Auditincludes scope.json/receipt.json/executed-builder.py/build.log and tiny native-optic-export-check.glb.

No clayrenders because they do not display emission. Root owns actualWebGL calibration and integration. Material proposal is not ownerlikeness or wholecharacteracceptance. No app/dependency/build/test/commit/push by worker.
