import fs from 'node:fs';
const [readyPath,nonce]=process.argv.slice(2);
if (!readyPath || !nonce) throw new Error('Explicit owned readiness path and nonce required');
fs.writeFileSync(readyPath,JSON.stringify({pid:process.pid,nonce,fixture:'owned-stop-fixture'},null,2));
setTimeout(()=>process.exit(0),15000);
