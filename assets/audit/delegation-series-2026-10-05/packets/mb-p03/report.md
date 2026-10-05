# MB-P03 resource-control preparation

The architect completed and independently ran the bounded control preparation after the first delegate remained pending on an outside-root write approval. That thread is still occupied; it is not reported complete or stopped. The original delegate's seven-case prototype exposed nonconfigurable caps and incomplete ownership checks. The committed implementation is the architect's correction, not a claimed completed agent output.

`node assets/audit/delegation-series-2026-10-05/packets/mb-p03/control-drill.mjs` executed 15 synthetic cases and passed. They cover configurable agent/delegate/root limits, separate accounting units, unknown counters, the 80% implementation stop and 20% closure reserve, three workers, owned thread/process request versus foreign refusal, checkpoint expiry and two no-gain attempts. The decision function never calls an external service or kills a process.

The root has an active 20,000,000 native goal allocation. Initial delegate goals of 30,000 and 35,000 exhausted during guidance startup before delivery; those runs remain incomplete. Later thread goals use 1,500,000 as an outer native cap, reserving 500,000 below the owner's 2,000,000 ceiling. Actual usage, including incomplete runs, remains in the private runtime registry. These are ceilings, not consumption targets. A final in-flight step can cross a native goal limit; early checkpoints and restricted calls reduce that exposure but do not establish a hard billing guarantee.

The operative metric is `native_goal`; provider-total usage is unknown and not added to or equated with that metric. Selecting a provider-total contract without its counter must stop implementation. The observable native contract permits only work within its own defined scope.

**Verified preparation slice:** executable control decisions and real startup-budget exhaustion observations. **Not established:** an app interrupt endpoint, an actual owned-agent/process stop, provider billing enforcement or MB-T062 product-wide closure. The app exposes no thread interrupt here. A pending approval consumes an active worker slot. Workers now write in isolated checkouts inside the project workspace or their native outputs directory; no broader permission is requested.

Read-only source diagnosis, task contracts and current media/control evidence can continue in the remaining slots. New visual implementation still requires an actual owned-stop method and reference/custody preflight. Preserve likeness UNMET, owner acceptance PENDING and the strict normal failure at 2e-5.
