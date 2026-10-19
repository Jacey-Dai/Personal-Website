import test from 'node:test';
import assert from 'node:assert/strict';
import { places, utilityPages, projectTemplate } from '../src/content.js';

test('all required destinations have unique stable routes and readable content', () => {
  assert.deepEqual(places.map(p => p.id), ['about','projects','experience','beyond','currently']);
  assert.equal(new Set(places.map(p => p.id)).size, places.length);
  for (const p of places) {
    for (const key of ['name','label','preview','title','description']) assert.ok(p[key]?.trim(), `${p.id}: ${key}`);
    assert.ok(p.sections.length);
    for (const [heading, text] of p.sections) { assert.ok(heading.trim()); assert.ok(text.trim()); }
  }
  assert.ok(utilityPages.resume.text.includes('not added'));
  assert.ok(utilityPages.contact.text.includes('not published'));
  assert.equal(projectTemplate.length, 6);
});
