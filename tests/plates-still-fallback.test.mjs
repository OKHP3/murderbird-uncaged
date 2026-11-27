import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

// Runs the Living Plates page script with a renderer that cannot start, as in a browser with
// WebGL turned off, and checks that the still plates, era switch and theme control still work.
const html = readFileSync(new URL('../public/plates/index.html', import.meta.url), 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const page = scripts.at(-1);

function element(id) {
  const listeners = {};
  return {
    id, style: {}, dataset: {}, attributes: {}, disabled: false, textContent: '', src: '', alt: '', title: '', paused: true,
    classList: {add() {}, remove() {}, toggle() {}},
    setAttribute(name, value) { this.attributes[name] = String(value); },
    getAttribute(name) { return this.attributes[name]; },
    addEventListener(type, fn) { (listeners[type] ||= []).push(fn); },
    fire(type) { for (const fn of listeners[type] || []) fn({preventDefault() {}}); },
    play() { this.paused = false; this.fire('play'); return Promise.resolve(); },
    pause() { this.paused = true; this.fire('pause'); },
  };
}

function run(hash = '') {
  const els = {};
  const get = id => (els[id] ||= element(id));
  const buttons = ['canon', 'maker', 'mechanic', 'advanced'].map(scene => Object.assign(element(`era-${scene}`), {dataset: {scene}}));
  const windowListeners = {};
  const location = {hash};
  const context = {
    THREE: {WebGLRenderer: function () { throw new Error('Error creating WebGL context.'); }},
    document: {getElementById: get, querySelectorAll: sel => (sel === '.eras button' ? buttons : []), createElement: () => element('x'), body: element('body')},
    location,
    history: {replaceState(_, __, next) { location.hash = next; }},
    performance: {now: () => 0},
    requestAnimationFrame() {}, setTimeout() {}, clearTimeout() {},
    console,
  };
  context.window = {
    matchMedia: () => ({matches: false, addEventListener() {}}),
    addEventListener(type, fn) { (windowListeners[type] ||= []).push(fn); },
    devicePixelRatio: 1, AudioContext: undefined,
  };
  vm.runInNewContext(page, context);
  return {get, buttons, location};
}

test('without WebGL the canon still plate shows with its label', () => {
  const {get} = run();
  assert.equal(get('fallback').style.display, 'grid');
  assert.equal(get('gl').style.display, 'none');
  assert.equal(get('still-back').src, 'img/canon-back.webp');
  assert.equal(get('still-front').src, 'img/canon-front.webp');
  assert.equal(get('title').textContent, 'The bird, as locked');
  assert.equal(get('status').textContent, '');
});

test('the era switch changes the still plate and its label', () => {
  const {get, buttons, location} = run();
  buttons[3].fire('click');
  assert.equal(get('still-front').src, 'img/builder-front.webp');
  assert.equal(get('kicker').textContent, 'Era III · 2025');
  assert.equal(buttons[3].attributes['aria-pressed'], 'true');
  assert.equal(location.hash, '#advanced');
});

test('a plate named in the address opens directly', () => {
  const {get} = run('#mechanic');
  assert.equal(get('still-back').src, 'img/mechanic-back.webp');
});

test('motion controls are disabled and the theme still plays', () => {
  const {get} = run();
  for (const id of ['depthBtn', 'restBtn', 'provokeBtn']) assert.equal(get(id).disabled, true);
  get('themeBtn').fire('click');
  assert.equal(get('themeBtn').textContent, 'Pause theme');
});
