import test from 'node:test';
import assert from 'node:assert/strict';
import { places, utilityPages, projectTemplate } from '../src/content.js';
import { profile, education, experience } from '../src/profile.js';
import { existsSync } from 'node:fs';

test('all required destinations have unique stable routes and readable content', () => {
  assert.deepEqual(places.map(p => p.id), ['about','projects','experience','beyond','currently']);
  assert.equal(new Set(places.map(p => p.id)).size, places.length);
  for (const p of places) {
    for (const key of ['name','label','preview','title','description']) assert.ok(p[key]?.trim(), `${p.id}: ${key}`);
    assert.ok(p.sections.length);
    for (const [heading, text] of p.sections) { assert.ok(heading.trim()); assert.ok(text.trim()); }
  }
  assert.ok(utilityPages.resume.text.includes('PDF'));
  assert.ok(utilityPages.contact.text.includes('email'));
  assert.ok(existsSync(new URL(`../public/${profile.resume}`, import.meta.url)));
  assert.equal(new URL(profile.linkedin).hostname, 'www.linkedin.com');
  assert.equal(new URL(profile.github).pathname, '/Jacey-Dai');
  assert.equal(education.length, 2);
  assert.equal(experience.length, 4);
  assert.equal(projectTemplate.length, 6);
});
