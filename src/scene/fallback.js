// Illustrated fallback for browsers and preview environments without WebGL.
// Shares the anatomy controls with the Three.js exhibit.
export function createIllustratedExhibit(container, updateMarker) {
  container.innerHTML = `
    <svg class="fallback-bird" viewBox="0 0 800 570" role="img" aria-label="Illustrated mechanical MurderBird with bronze beak, green wings, jointed legs and chest cavity">
      <defs>
        <radialGradient id="bg"><stop stop-color="#445044"/><stop offset="1" stop-color="#28322b"/></radialGradient>
        <linearGradient id="brass" x2="1" y2="1"><stop stop-color="#e9b77b"/><stop offset=".48" stop-color="#ac704a"/><stop offset="1" stop-color="#634932"/></linearGradient>
        <linearGradient id="wing" x2="1" y2="1"><stop stop-color="#9bab8d"/><stop offset=".5" stop-color="#556b5b"/><stop offset="1" stop-color="#293d34"/></linearGradient>
        <radialGradient id="eye"><stop stop-color="#e6aa67"/><stop offset=".55" stop-color="#3a2b25"/><stop offset="1" stop-color="#101c1b"/></radialGradient>
        <filter id="shade"><feGaussianBlur stdDeviation="13"/></filter>
        <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><path d="M0 0v8" stroke="#ede1bf" stroke-opacity=".12" stroke-width="2"/></pattern>
      </defs>
      <ellipse cx="400" cy="512" rx="210" ry="24" fill="#080c09" opacity=".55" filter="url(#shade)"/>
      <ellipse cx="400" cy="509" rx="181" ry="17" fill="#b18a60" opacity=".55"/>
      <path d="M250 474V103Q400 -5 550 103V474" fill="none" stroke="#b7be9a" stroke-opacity=".17" stroke-width="2"/>
      <path d="M218 474V127Q400 -30 582 127V474" fill="none" stroke="#b7be9a" stroke-opacity=".13" stroke-width="2"/>
      <g class="bird-figure">
        <g fill="none" stroke="#b98b62" stroke-width="8" stroke-linecap="round">
          <path d="M365 377l-23 55 13 58M435 377l23 55-13 58"/>
          <path d="M342 432l-12 44M458 432l12 44"/>
        </g>
        <g stroke="#d1a676" stroke-width="3" fill="#4b4f44">
          <circle cx="342" cy="432" r="15"/><circle cx="458" cy="432" r="15"/>
          <circle cx="342" cy="432" r="7" fill="#c58b58"/><circle cx="458" cy="432" r="7" fill="#c58b58"/>
        </g>
        <g fill="none" stroke="#bd9268" stroke-width="7" stroke-linecap="round">
          <path d="M355 489l-39 13m39-13-4 17m4-17 30 13M445 489l-39 13m39-13 4 17m-4-17 30 13"/>
        </g>
        <g fill="#526556" stroke="#bd9268" stroke-width="2">
          <path d="M377 351q-74 60-98 105 66-28 111-71z"/>
          <path d="M388 348q-40 88-38 128 40-45 57-91z"/>
          <path d="M421 351q74 60 98 105-66-28-111-71z"/>
        </g>
        <path d="M338 243q-52 8-77 88 3 56 45 90 20-28 59-53z" fill="url(#wing)" stroke="#b99368" stroke-width="3"/>
        <path d="M462 243q52 8 77 88-3 56-45 90-20-28-59-53z" fill="url(#wing)" stroke="#b99368" stroke-width="3"/>
        <g fill="#73876f" stroke="#baa180" stroke-width="1.5">
          <path d="M300 298q-51 73-18 137 32-31 52-89z"/>
          <path d="M319 318q-37 82-8 128 38-36 42-88z"/>
          <path d="M338 338q-21 79-1 121 35-50 37-100z"/>
          <path d="M500 298q51 73 18 137-32-31-52-89z"/>
          <path d="M481 318q37 82 8 128-38-36-42-88z"/>
          <path d="M462 338q21 79 1 121-35-50-37-100z"/>
        </g>
        <path d="M400 222q-56 1-79 68-22 71 15 116 66 37 128 0 37-45 15-116-23-67-79-68" fill="#39473e" stroke="#bf9569" stroke-width="3"/>
        <path d="M400 240q-59 2-57 69l11 69q46 34 92 0l11-69q2-67-57-69" fill="url(#brass)" stroke="#e1b77e" stroke-width="3"/>
        <path d="M400 240q-59 2-57 69l11 69q46 34 92 0l11-69q2-67-57-69" fill="url(#hatch)"/>
        <path d="M350 283q50 29 100 0m-98 26q48 26 96 0m-91 27q43 22 86 0" fill="none" stroke="#5d4938" stroke-opacity=".7" stroke-width="3"/>
        <g class="fallback-core">
          <ellipse cx="400" cy="316" rx="48" ry="66" fill="#e2c9a0" stroke="#bc875b" stroke-width="7"/>
          <ellipse cx="400" cy="316" rx="22" ry="30" fill="#efac68" opacity=".85"/>
          <ellipse cx="400" cy="316" rx="12" ry="17" fill="#fff3c9"/>
          <path d="M368 271l64 90m0-90-64 90" stroke="#996b4b" stroke-width="5" opacity=".8"/>
        </g>
        <path d="M370 243q-15-34-14-60l20-23 48 1 20 23q1 26-14 60" fill="#667a64" stroke="#c59967" stroke-width="3"/>
        <path d="M354 175q-17-24-5-46 19-35 54-34 35 0 50 32 11 25-9 48l-24 23-43-1z" fill="url(#wing)" stroke="#c69b6e" stroke-width="4"/>
        <path d="M355 123q36-33 83 1l-5 28q-35 15-72 0z" fill="url(#brass)" stroke="#edbe86" stroke-width="2"/>
        <path d="M365 107l-19-48 30 25 2-42 27 39 18-36 4 53" fill="#7b9179" stroke="#bb9367" stroke-width="3"/>
        <path d="M376 162q-25 7-51 18l26 15 32-9m41-24q25 7 51 18l-26 15-32-9" fill="url(#brass)" stroke="#e1ae74" stroke-width="2"/>
        <circle cx="370" cy="155" r="14" fill="url(#eye)" stroke="#e9bf83" stroke-width="4"/>
        <circle cx="430" cy="155" r="14" fill="url(#eye)" stroke="#e9bf83" stroke-width="4"/>
        <circle cx="373" cy="152" r="3" fill="#fff3cc"/><circle cx="433" cy="152" r="3" fill="#fff3cc"/>
        <path d="M379 172l21 14 21-14-21 69z" fill="url(#brass)" stroke="#eac18b" stroke-width="3"/>
        <path d="M400 241l-6 11 10-2" fill="none" stroke="#4b3f35" stroke-width="3"/>
      </g>
    </svg>`;
  const bird = container.querySelector('.bird-figure');
  const svg = container.querySelector('svg');
  let angle = 0, open = false, pointer = null, zoom = 1;
  const points = { beak: [400, 214], joint: [458, 432], core: [400, 316], eye: [430, 155] };
  function draw() {
    bird.style.transform = `translateX(${angle * 12}px) scale(${zoom * (1 - Math.abs(angle) * .2)}, ${zoom})`;
    update();
  }
  function update() {
    const rect = svg.getBoundingClientRect();
    // SVG uses xMidYMid meet; allow for the letterbox area on narrow viewports.
    const scale = Math.min(rect.width / 800, rect.height / 570);
    const offsetX = (rect.width - 800 * scale) / 2, offsetY = (rect.height - 570 * scale) / 2;
    Object.entries(points).forEach(([id, [x, y]]) => {
      updateMarker(id,
        offsetX + (400 + (x - 400) * zoom * (1 - Math.abs(angle) * .2) + angle * 12) * scale,
        offsetY + (285 + (y - 285) * zoom) * scale,
        id !== 'core' || open);
    });
  }
  container.addEventListener('pointerdown', event => {
    if (event.target.closest('.marker')) return;
    pointer = { x: event.clientX, angle };
    container.setPointerCapture(event.pointerId);
  });
  container.addEventListener('pointermove', event => {
    if (!pointer) return;
    angle = Math.max(-1, Math.min(1, pointer.angle + (event.clientX - pointer.x) / 300));
    draw();
  });
  container.addEventListener('pointerup', () => pointer = null);
  container.addEventListener('pointercancel', () => pointer = null);
  container.addEventListener('wheel', event => {
    event.preventDefault();
    zoom = Math.max(.82, Math.min(1.3, zoom - event.deltaY * .001));
    draw();
  }, { passive: false });
  update();
  return {
    resize: update,
    select() {},
    setSection(value) { open = value; container.classList.toggle('section-open', value); update(); },
    react() { bird.animate([{ transform: 'rotate(-2deg)' }, { transform: 'rotate(2deg)' }, { transform: 'rotate(0)' }], { duration: 350, iterations: 2 }); },
    reset() { angle = 0; zoom = 1; draw(); },
  };
}