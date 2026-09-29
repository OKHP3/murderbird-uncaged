/** Validate every emitted path against the release manifest and authorized sources. */
export function assertPublicationBoundary(output, allowed) {
  for (const name of output) {
    if (/^assets\/[a-zA-Z][a-zA-Z0-9_.-]*-[a-zA-Z0-9_-]{8}\.(?:js|css)$/.test(name)) allowed.add(name);
    if (/(?:^|\/)(?:\.local|provenance|context|audit|archives)(?:\/|$)|\.(?:blend|webm|zip|wav)$/i.test(name)) {
      throw new Error(`Private/source material: ${name}`);
    }
    if (!allowed.has(name)) throw new Error(`Unexpected runtime file: ${name}`);
  }
}
