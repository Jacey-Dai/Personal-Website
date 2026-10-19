import './styles.css';
import { places, projectTemplate, utilityPages } from './content.js';
import { worldSvg } from './world.js';

const dialog = document.querySelector('#detail');
const content = document.querySelector('#detail-content');
const visited = new Set();
let returnFocus;
try { JSON.parse(sessionStorage.getItem('island-visits') || '[]').forEach(id => visited.add(id)); } catch { /* Storage is optional. */ }

document.querySelector('#island-art').innerHTML = worldSvg;
document.querySelector('#navigation').innerHTML = ['about','projects','experience','beyond','resume','contact'].map(id => `<a href="#${id}">${places.find(p => p.id === id)?.label || utilityPages[id].title.replace('Let’s connect.', 'Contact')}</a>`).join('');
document.querySelector('#places').innerHTML = places.map(p => `<a class="place place-${p.id} ${p.color}" href="#${p.id}" data-place="${p.id}"><span class="place-number">${p.number}</span><span><strong>${p.name}</strong><span class="place-category">${p.label}<span class="visit-mark" aria-label="Visited"> ✓</span></span></span><span class="place-arrow" aria-hidden="true">↗</span><span class="place-preview">${p.preview}</span></a>`).join('');

function updateVisits() {
  document.querySelectorAll('[data-place]').forEach(el => el.classList.toggle('visited', visited.has(el.dataset.place)));
  document.querySelector('#visit-count').textContent = `${places.filter(p => visited.has(p.id)).length} / 5 places explored`;
  try { sessionStorage.setItem('island-visits', JSON.stringify([...visited])); } catch { /* Continue without persistence. */ }
}

function renderRoute() {
  const id = location.hash.slice(1);
  const place = places.find(p => p.id === id);
  const utility = utilityPages[id];
  if (!place && !utility) {
    if (dialog.open) dialog.close();
    return;
  }
  if (!dialog.open) returnFocus = document.activeElement;
  if (place) {
    visited.add(id);
    content.innerHTML = `<p class="eyebrow">${place.number} / ${place.name} · ${place.label}</p><h2 id="detail-title">${place.title}</h2><p class="detail-intro">${place.description}</p><p class="placeholder-note">CONTENT PLACEHOLDERS · NOT A RECORD OF REAL EXPERIENCE</p>${place.sections.map(([title,text])=>`<section class="content-section"><h3>${title}</h3><p>${text}</p></section>`).join('')}${id === 'projects' ? `<details class="project-template"><summary>Preview the project case-study structure</summary>${projectTemplate.map(title=>`<section class="content-section"><h3>${title}</h3><p>[To add: verified project content.]</p></section>`).join('')}</details>` : ''}${id === 'about' ? '<div class="detail-actions"><a href="#resume">Resume ↗</a><a href="#contact">Contact & social links ↗</a></div>' : ''}`;
  } else {
    content.innerHTML = `<p class="eyebrow">DIRECT ACCESS</p><h2 id="detail-title">${utility.title}</h2><p class="detail-intro">${utility.text}</p><p class="placeholder-note">AWAITING VERIFIED PERSONAL CONTENT</p>`;
  }
  if (!dialog.open) dialog.showModal();
  content.scrollTop = 0;
  dialog.scrollTop = 0;
  document.querySelector('#close-detail').focus();
  updateVisits();
}

function closeDetails() { location.hash = ''; }
document.querySelector('#close-detail').addEventListener('click', closeDetails);
dialog.addEventListener('cancel', event => { event.preventDefault(); closeDetails(); });
dialog.addEventListener('close', () => { if (returnFocus instanceof HTMLElement) returnFocus.focus({preventScroll:true}); });
window.addEventListener('hashchange', renderRoute);
updateVisits();
renderRoute();
