# MurderBird operating goal — incremental visual delivery

Owner direction, September 29, 2026: improve MurderBird's resemblance to the selected images through fast, visible, reviewable increments. Functionality is useful, but a pale, ghostlike model with the wrong character likeness is not the target. Measure progress by a visible gain in the complete bird, not worker activity, test counts, or accumulated versions.

Start from the released V37 assembly. Keep one recognizable flightless mechanical bird across Maker, Mechanic, and Advanced. Prioritize the largest visible likeness gap; a cycle may address silhouette, a body region's construction, or mechanical material response, but must show how that change improves the whole character against its controlling reference.

This is the current operating mandate for Codex, Claude, and Replit. It replaces the earlier open-ended correction loop and its blanket high-effort supervision cadence. Existing creative authority, source provenance, and repository boundaries remain in force. This mandate update changes instructions only; it does not regenerate the model or restart unattended work.

## Shape the work

- Name one integrator and assign at most three small workers. Use the lightest model capable of each bounded assignment; reserve heavier reasoning for a specific unresolved decision. Workers must own disjoint paths and use isolated checkouts when producing edits. The integrator owns integration and the shared branch; do not have workers edit overlapping files or launch additional worker trees.
- Give each task a concrete visible result and a 15–30 minute review checkpoint. For a visual change, produce a local preview or matched-view image at that checkpoint. Allow at most two focused attempts before showing the result. Continue an independently useful increment when the direction is clear; seek owner input only for a concrete artistic choice that blocks the next change. Do not turn a checkpoint into another open-ended refinement loop.
- Keep each increment small enough to review on its own. Preserve the approved reference hierarchy and source labels. V37 is approved for deployment, while final likeness remains unresolved; a preview, build, or worker opinion cannot establish owner likeness acceptance. Do not replace or repurpose source assets to make a checkpoint look complete.

## Check and integrate

- At each increment, run only the cheap check that covers the changed area: for example, inspect the changed diff and asset paths, or load the affected scene and its illustrated fallback. Report what was and was not checked.
- Run the repository-required full checks once at integration or release: for app or asset-reference changes, `npm ci`, `npm run build`, inspect `dist/`, and confirm referenced assets resolve; for scene changes, inspect both WebGL and the illustrated fallback. Run earlier only when a new failure, risk, or dependency makes it useful. A local result does not establish CI, deployment, or human acceptance.
- The integrator reviews every worker change, resolves integration deliberately, and records the resulting commit SHA. Never auto-commit another worker's changes or auto-resolve a conflict. Preserve private archives and provenance boundaries in `AGENTS.md`; only approved runtime files belong in `public/`.

## Keep remotes aligned

- Replit communication and execution use **Free mode only**. Verify Free before submitting replies or starting tasks; always decline Power or Max prompts. Do not use or recommend paid escalation or change billing. If Free cannot continue, preserve the checkpoint and report the actual limit. This owner rule supersedes any Free-first skill guidance.
- When Replit says its Agent is waiting for input but the response form is hidden, send one direct message asking it to restate the specific question and available choices. Answer the actual question within the assigned scope, then verify its visible acknowledgment. Do not guess the missing question, treat elapsed time as a response, or repeatedly start new tasks. Genuine human approval remains for the owner.
- Before starting work, integrating, or pushing, fetch GitHub and inspect the exact branch refs and worktree state. Update only by fast-forward; if that is not possible, stop and report the divergence for deliberate reconciliation. Do not force-push.
- Commit each coherent, reviewed increment locally. Push the working branch to GitHub after every completed visual checkpoint. During active work, do not let more than 30 minutes pass without a pushed coherent checkpoint or a brief explanation of what blocks it; do not push broken or private work to satisfy a timer. Confirm the branch and pushed SHA from the result; distinguish this from a merge to `main` or GitHub Pages publication.
- Keep the Replit development preview and other authorized coding systems (including Codex and Claude) aligned by having them fetch the named GitHub checkpoint branch and confirm its SHA before continuing. Replit remains a preview, not a publication destination. If GitHub is unavailable or rejects a push, keep the local commit and report the exact branch and error; do not claim other systems are aligned until their fetched SHA is confirmed.

## Checkpoint note

At each checkpoint, report the visible result, changed paths, commit SHA, checks performed, GitHub branch/SHA, confirmations from systems that fetched it, and any open visual or sync blocker. This makes the next increment start from known evidence rather than an assumed state.

Use GitHub as the exchange point. Publish a concise handoff alongside each checkpoint: controlling reference, bounded assignment, owned paths, current branch/SHA, preview or comparison, checks already completed, and next action. Other systems fetch and acknowledge that exact revision before editing. Confirm Replit directly after an integrated `main` update; do not treat a pushed branch as proof that Replit, Claude, or another host has received it.

## Active supervision

Use the reusable [Replit check-in and routing contract](replit-supervision.md) for stale assignments and hidden response cards. The integrator must inspect concrete artifacts and process state at each checkpoint; a worker marked running without a deliverable is not itself progress. Keep external reviewers scoped and adjudicate their suggestions against creative authority before implementation.
