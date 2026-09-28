import assert from 'node:assert/strict';
import test from 'node:test';
import { createIllustratedExhibit } from '../src/scene/fallback.js';

class Element {
  constructor() {
    this.hidden = false;
    this.textContent = '';
    this.style = {};
    this.attributes = new Map();
    this.listeners = new Map();
  }

  addEventListener(type, listener) {
    this.listeners.set(type, listener);
  }

  dispatch(type) {
    this.listeners.get(type)?.({ type, target: this });
  }

  setAttribute(name, value) {
    this.attributes.set(name, String(value));
  }
}

class ImageElement extends Element {
  constructor(src) {
    super();
    this.attributes.set('src', src);
    this.complete = false;
    this.naturalWidth = 0;
  }

  getAttribute(name) {
    return this.attributes.get(name) ?? null;
  }

  set src(value) {
    this.attributes.set('src', value);
    this.complete = false;
    this.naturalWidth = 0;
  }

  dispatch(type) {
    if (type === 'load') {
      this.complete = true;
      this.naturalWidth = 960;
    }
    super.dispatch(type);
  }
}

class DiagramElement extends Element {
  constructor() {
    super();
    this.note = new Element();
    this.schematic = new Map(
      ['shell', 'drive', 'power', 'mind', 'external', 'transmission'].map(name => [name, new Element()]),
    );
  }

  querySelector(selector) {
    if (selector === '.diagram-note') return this.note;
    const name = selector.match(/^\[data-schematic="([^"]+)"\]$/)?.[1];
    return name ? this.schematic.get(name) : null;
  }
}

class Container {
  set innerHTML(markup) {
    const initialSrc = markup.match(/<img src="([^"]+)"/)?.[1];
    this.image = new ImageElement(initialSrc);
    this.caption = new Element();
    this.diagram = new DiagramElement();
  }

  querySelector(selector) {
    if (selector === 'img') return this.image;
    if (selector === '.illustrated-caption') return this.caption;
    if (selector === '.assembly-diagram') return this.diagram;
    return this.diagram.querySelector(selector);
  }
}

const unavailableCaption = 'Exterior preview unavailable. The component descriptions remain available; Retry 3D also retries this image.';

test('a failed preview keeps its unavailable message across fallback updates', () => {
  const container = new Container();
  const exhibit = createIllustratedExhibit(container, () => {});
  const image = container.image;

  image.dispatch('error');
  assert.equal(image.hidden, true);
  assert.equal(container.caption.textContent, unavailableCaption);

  exhibit.resize();
  exhibit.setSection(true);
  exhibit.setSeparation(0.5);
  exhibit.setEra('builder');

  assert.equal(image.hidden, true);
  assert.equal(container.caption.textContent, unavailableCaption);
});

test('a new era preview clears the old failure state and can load', () => {
  const container = new Container();
  const exhibit = createIllustratedExhibit(container, () => {});
  const image = container.image;
  image.dispatch('error');

  exhibit.setEra('mechanic');
  assert.match(image.getAttribute('src'), /mechanic-preview\.png$/);
  assert.equal(image.hidden, false);
  assert.equal(container.caption.textContent, 'Mechanic exterior study · fixed rendered view');

  image.dispatch('load');
  assert.equal(image.complete, true);
  assert.equal(image.naturalWidth, 960);
  exhibit.resize();
  assert.equal(image.hidden, false);
  assert.equal(container.caption.textContent, 'Mechanic exterior study · fixed rendered view');
});
