# MurderBird executable delegation series — October 5, 2026

The reviewed results are now 30 bounded work packets. They preserve all 62 source task records: 59 unfinished, partial, unverified or conditional records, one closed delivery and two passing maintenance obligations. All 52 PRD criteria, F01–F10 and T01–T18 remain mapped. The frozen October 5 review ledger is unchanged; this program is a continuation layer.

[Machine assignments](program.json) · [Current execution receipt](execution-receipt.json) · [New findings and follow-on tasks](new-findings.md) · [Original five-pass review](../evaluations/windows-five-pass-review-2026-10-05.md)

## Authority, models and budgets

The owner explicitly allocated a maximum of 30 delegate threads × 2,000,000 tokens, plus 20,000,000 for this architect: 80,000,000 total. These are ceilings, not targets. The architect native goal is active at 20,000,000. Routine extraction, deterministic checks and handoffs use `gpt-6-luna` with low effort; bounded diagnosis/code/geometry duties use the same model with medium effort. No heavier model is selected by default. A specific demonstrated failure, rather than an entire program, would justify reassignment.

After two startup runs exhausted 30,000/35,000 native caps before producing artifacts, subsequent packet goals register a 1,500,000 native ceiling with 500,000 headroom below the per-thread owner maximum. Work still has a 20-minute checkpoint, at most 12 bounded tool calls, at most two focused attempts and short outputs. Smaller native checkpoint targets in the machine file are estimates informed by observed usage, not mandatory spending or false billing caps. A final in-flight step can cross a native cap; each actual outcome remains recorded.

The observable unit is `native_goal`. Provider-total and billing counters are unavailable and remain null. The program does not guarantee a provider-total/billing ceiling. Root monitors real goal counters and records incomplete runs, pending approvals and reused-thread cumulative usage. Never equate an allocated ceiling with consumed tokens.

## Dispatch and integration

Run at most three workers concurrently. Root owns main, Git refs/index, integration, app/browser sessions, release decisions and external writes. Workers use isolated checkouts and disjoint packet folders, never child delegates. A writable checkout must be inside its native project workspace; otherwise the worker uses its own outputs directory and root imports reviewed files. No broad filesystem escalation is needed for these packet artifacts.

The first tranche selects MB-P01/02/03 preflight, MB-P04 strict diagnosis, MB-P05 the connected-head contract, and MB-P17/19/23/24 current control/fallback/media source diagnostics. This tranche creates verifiable evidence and executable future assignments. It does not silently select a new modeling or mechanics phase. The pending first control thread consumes a slot until actually ended; the root-completed 15-case synthetic control drill does not claim an actual thread stop.

Every artifact has an exact base SHA, owned files, checks actually run, native usage and remaining product gates. Root checks the output independently before marking the preparation slice verified. A completed worker or source test does not close a product criterion. Preserve original binaries and failed receipts; source likeness remains UNMET, artistic acceptance PENDING, PRD NOT SCORED and strict normal failure open at 2e-5.

## Executable commands

From the repository root:

```powershell
node scripts/delegation-program.mjs check
node scripts/delegation-program.mjs status
node scripts/delegation-program.mjs ready
node scripts/delegation-program.mjs prompt MB-P17 <isolated-checkout>
node scripts/delegation-program.mjs followup MB-P23 <isolated-checkout> <completed-thread-id>
node --test tests/delegation-program.test.mjs
node assets/audit/delegation-series-2026-10-05/packets/mb-p03/control-drill.mjs
```

The prompt commands return structured arguments for the native Codex `create_thread` or `send_message_to_thread` tool. They do not pretend that a shell script can invoke those app tools or stop billing. Root resolves the local project ID with `list_projects` and keeps it, thread IDs, machine paths and actual usage in Git-ignored `.local/delegation-series-20261005/state.json`. The public receipt is a dated sanitized snapshot, not a live controller.

The guard refuses a fourth worker, a 31st new thread, unverified prerequisites, unselected future phases, main as a worker checkout, overlapping ownership, unknown cumulative usage or excessive reuse. Initial failed/replaced runs count toward the 30-thread maximum. A genuinely completed thread may receive another duty only within its cumulative 2,000,000 ceiling; this avoids creating extra threads merely to fill all packet slots.

## Assignable packets

All packets default to a 1,500,000 native outer goal and a 20-minute checkpoint. The specific closure evidence and conditional implementation dependencies are in `program.json`. Dependencies below are packet preparation dependencies; the original product-task dependencies and postflight slices remain separately preserved.

| Packet | Owned duty / source tasks | Effort | Preparation predecessors | Completion boundary |
|---|---|---|---|---|
| MB-P01 — Reference and criterion freeze | MB-T013 | low | None | Existing reference/source identity and criterion coverage; never likeness acceptance. |
| MB-P02 — Retained gain custody | MB-T015, MB-T036, MB-T038 | low | None | Custody preflight now; visible successor preservation remains a postflight gate. |
| MB-P03 — Budget and owned-stop drill | MB-T062 | medium | None | Native counter and simulated owned-stop control slice; actual provider billing remains unknown. |
| MB-P04 — Strict normal diagnosis | MB-T018 | medium | MB-P01, MB-P02, MB-P03 | A reproduced diagnosis or explicit NOT RUN; no threshold relaxation, silent repair or acceptance. |
| MB-P05 — Connected-head implementation contract | MB-T001 | medium | MB-P01, MB-P02, MB-P03 | A concrete implementation contract. Modeling remains a separately selected visible checkpoint, with owner acceptance pending. |
| MB-P06 — Hooked bill and cheek construction | MB-T002, MB-T003 | medium | MB-P05 | Depends on selected visual scope, pinned base and budget monitor. Source dimensions inferred from images remain proposals. |
| MB-P07 — Swept crown and recessed optic | MB-T004, MB-T005 | medium | MB-P05, MB-P06 | Coherent-head identity and MB-P06 cheek relationship; no isolated tone variant can close this packet. |
| MB-P08 — Neck, breast and regional edges | MB-T007, MB-T008, MB-T021 | medium | MB-P06, MB-P07 | Head assembly check first; preserve retained gains and source body scope. |
| MB-P09 — Folded shield-wings and rear | MB-T009, MB-T010, MB-T016 | medium | MB-P08 | Owner chronology choice when consequential; wings remain folded and flightless. |
| MB-P10 — Broad short hooked talons | MB-T011 | medium | MB-P01, MB-P02, MB-P03 | Root selects bounded visual increment; no locomotion or engineering claims. |
| MB-P11 — Matched views and browser parity | MB-T014, MB-T019 | medium | MB-P01, MB-P03 | Capture contract is ready now. Candidate comparisons require MB-P04, MB-P15 and exact integrated assets; do not use future images as preflight. |
| MB-P12 — Whole-bird and owner review | MB-T006, MB-T012, MB-T020 | medium | MB-P06, MB-P07, MB-P08, MB-P09, MB-P10, MB-P11, MB-P13, MB-P14, MB-P15, MB-P16 | Agent can prepare/review evidence; only the owner supplies artistic acceptance. No fresh score without the full defined evaluation. |
| MB-P13 — Maker finish and optic rules | MB-T022, MB-T025 | medium | MB-P07, MB-P08 | Preserve geometry and reference-scoped era identity; no global tint substitute. |
| MB-P14 — Mechanic repair and wear history | MB-T023, MB-T027 | medium | MB-P09, MB-P13 | Uncertain construction/history remains proposed; chronological owner decision cannot be invented. |
| MB-P15 — Advanced inheritance and PBR response | MB-T024, MB-T026 | medium | MB-P13, MB-P14 | No exposure/camera changes to conceal mismatch; compare scope separately from source equality. |
| MB-P16 — Reproducible editable asset delivery | MB-T028 | low | MB-P04, MB-P11, MB-P15 | Root integrates first. No candidate promotion into runtime without the release checks and applicable scope. |
| MB-P17 — Current exhibit controls and identity | MB-T030, MB-T031, MB-T032, MB-T037 | low | None | Current source/local checks now. Actual rendered/mobile/cache behavior remains separately measured; enclosure successor views require candidate. |
| MB-P18 — Visitor inspection and restoration | MB-T033, MB-T034, MB-T058 | medium | MB-P17 | Current V37 diagnostics independent of successor rig; meaningful new cavities remain conditional on assembly contracts. |
| MB-P19 — Fallback and calm-state coverage | MB-T035, MB-T039 | low | None | Source/local results only until rendered evidence is captured; no new state falsely inherits historical pass. |
| MB-P20 — Keyboard and focus handoff | MB-T040 | low | None | Agent evidence can identify defects; human keyboard completion requires an executed named browser/session. |
| MB-P21 — Screen-reader handoff | MB-T041 | low | None | Requires actual assistive technology/user result; DOM or source inspection alone cannot pass. |
| MB-P22 — Physical touch and narrow devices | MB-T042 | low | MB-P17, MB-P19 | Physical device required; desktop emulation cannot close this criterion. |
| MB-P23 — Theme playback and readable lyrics | MB-T043 | low | None | Audible full/loop listening and human keyboard remain unrun until actual observations; preserve synthesized-vocalist status and historical music. |
| MB-P24 — Existing video and story controls | MB-T044 | low | None | Current video is independent of new creative delivery; source inspection is distinct from observed playback. |
| MB-P25 — Performance, transfer and memory | MB-T045, MB-T046 | medium | MB-P17, MB-P19, MB-P22 | Physical hardware/GPU required; headless/software renderer results cannot certify sustained hardware performance. |
| MB-P26 — Motion references and future assembly scope | MB-T017, MB-T057, MB-T059, MB-T060 | low | MB-P01, MB-P02 | No animation/fitment implementation or engineering certification. Later mechanics selection remains owner-gated after artistic acceptance. |
| MB-P27 — Current Maker and Mechanic diagnostics | MB-T047, MB-T048, MB-T049 | medium | MB-P17, MB-P26 | Do not implement absent controls, substitute static CG, or transfer a V37 result to successor motion. Full certification remains conditional. |
| MB-P28 — Current Advanced presence and contact | MB-T050, MB-T051, MB-T052 | medium | MB-P17, MB-P26 | Current source/local evidence only until timed rendered observation. New motion/rig implementation remains separately selected. |
| MB-P29 — Current locomotion and interruptions | MB-T053, MB-T054, MB-T055, MB-T056 | medium | MB-P17, MB-P26 | Current V37 read-only selection needs delivered baseline only; it never closes an unimplemented successor. |
| MB-P30 — Preserved Replit history triage | MB-T061 | low | MB-P01, MB-P02 | No reset/force-push or private archive publication; actual remote inventory/API auth requires root-owned Replit Free browser/connection verification. |

## Gates that remain real

- The connected-head contract is a preparation deliverable. Bill/cheek/crown/optic/body material work must begin as a selected bounded visual checkpoint with actual owned stop controls, fixed cameras, no more than two designs and the retained-gain preservation checks.
- Agent evidence cannot supply owner likeness or shoulder chronology decisions. The per-era decision packet records the owner response when supplied; it does not manufacture acceptance.
- Human keyboard, actual screen-reader, physical touch, audible listening and sustained hardware-GPU observations require their named conditions. Source checks, emulation and headless results remain separate evidence.
- Current V37 T03–T12 diagnosis needs the delivered baseline and supported-control inventory, independently of successor rigs. Missing capabilities are gaps; a current V37 pass cannot close future CG motion.
- Mechanics/fitment is a separately scoped later proposal. No engineering certification, normal-threshold relaxation, new dependency, paid Replit mode or Replit publication is selected.
- Replit 17-commit/all-ref triage and both connector authorizations remain separate remote duties. No reset, force-push or claim of parent synchronization follows from the clean isolated preview.

Next action: root reviews each selected packet, records factual completion and new findings, and dispatches the next ready bounded duty within the active-worker/thread/cumulative-budget guards. See the execution receipt for actual completed work and the remaining queue.
