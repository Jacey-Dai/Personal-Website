import "./styles.css";
import {
  places,
  projectTemplate,
  projectDrafts,
  utilityPages,
} from "./content.js";
import { worldArt, islandImage, mapLayout } from "./world.js";

const arrow =
  '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 15 15 5M5 5h10v10" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>';
const dialog = document.querySelector("#detail");
const content = document.querySelector("#detail-content");
const visited = new Set();
let returnFocus;
let mapScroll = 0;
let openedFromMap = false;
try {
  const saved = JSON.parse(sessionStorage.getItem("island-visits") || "[]");
  if (Array.isArray(saved))
    saved
      .filter((id) => places.some((p) => p.id === id))
      .forEach((id) => visited.add(id));
} catch {
  /* Storage is optional. */
}

document.querySelector("#island-art").innerHTML = worldArt;
// Pointer shortcuts over the buildings; the visible labels remain the accessible links.
document.querySelector("#building-targets").innerHTML = places.map(p => {
  const {x,y} = mapLayout[p.id];
  return `<a class="building-target" tabindex="-1" href="#${p.id}" data-building="${p.id}" style="left:${x-5}%;top:${y-13}%;width:12%;height:14%"></a>`;
}).join('');
document.querySelector("#navigation").innerHTML = [
  "about",
  "projects",
  "experience",
  "beyond",
  "resume",
  "contact",
]
  .map(
    (id) =>
      `<a href="#${id}" data-nav="${id}">${places.find((p) => p.id === id)?.label || (id === "resume" ? "Resume" : "Contact")}</a>`,
  )
  .join("");
const labelOffsets = {
  about: [0, 5],
  projects: [-9, 3],
  experience: [-2, -3],
  beyond: [8, 3],
  currently: [10, -1],
};
document.querySelector("#places").innerHTML = places
  .map((p) => {
    const { x, y } = mapLayout[p.id];
    const [dx, dy] = labelOffsets[p.id];
    return `<a class="place place-${p.id} ${p.color}" href="#${p.id}" data-place="${p.id}" style="--x:${x + dx}%;--y:${y + dy}%;--scene-x:${x}%;--scene-y:${y}%;--scene-image:url('${islandImage}')"><span class="mobile-scene" aria-hidden="true"></span><span class="place-number">${p.number}</span><span class="place-copy"><strong>${p.name}</strong><span class="place-category">${p.label}<span class="visit-mark" aria-label="Visited"> · visited</span></span></span><span class="place-arrow">${arrow}</span><span class="place-preview">${p.preview}</span></a>`;
  })
  .join("");

function updateVisits() {
  document
    .querySelectorAll("[data-place]")
    .forEach((el) =>
      el.classList.toggle("visited", visited.has(el.dataset.place)),
    );
  document.querySelector("#visit-count").textContent =
    `${places.filter((p) => visited.has(p.id)).length} / 5 places explored`;
  try {
    sessionStorage.setItem("island-visits", JSON.stringify([...visited]));
  } catch {
    /* Continue without persistence. */
  }
}

const section = (title, text) =>
  `<section class="content-section"><h3>${title}</h3><p>${text}</p></section>`;
function renderPlace(place, draft) {
  if (draft) {
    return `<a class="section-back" href="#projects">← All projects</a><p class="eyebrow">PROJECT CASE STUDY · STRUCTURE PREVIEW</p><h2 id="detail-title">${draft.title}</h2><p class="placeholder-note">Placeholder case study. No real project or results have been added.</p><div class="case-meta"><div><small>ROLE</small><p>To be added</p></div><div><small>TOOLS</small><p>To be added</p></div><div><small>YEAR</small><p>To be added</p></div></div><div class="case-sections">${projectTemplate.map((title, i) => `<section class="content-section"><span class="chapter-index">0${i + 1}</span><h3>${title}</h3><p>[To add: verified project content.]</p></section>`).join("")}</div>`;
  }
  const anchor = mapLayout[place.id];
  const heading = `<div class="detail-heading"><div><p class="eyebrow">${place.number} / ${place.name} · ${place.label}</p><h2 id="detail-title">${place.title}</h2><p class="detail-intro">${place.description}</p></div><div class="detail-scene" aria-hidden="true" style="--scene-image:url('${islandImage}');--scene-x:${anchor.x}%;--scene-y:${anchor.y}%"></div></div><p class="placeholder-note">CONTENT IN PROGRESS · Personal details have not been added yet.</p>`;
  if (place.id === "projects")
    return (
      heading +
      `<div class="project-grid">${projectDrafts.map((p, i) => `<a class="project-card" href="#projects/${p.id}"><div class="project-cover cover-${i}"><span aria-hidden="true">${i ? "✳" : "↗"}</span><small>YOUR PROJECT VISUAL</small></div><p class="eyebrow">${p.type}</p><h3>${p.title}</h3><p>${p.text}</p><span class="card-link">Explore case-study structure ${arrow}</span></a>`).join("")}</div><details class="project-template"><summary>Preview the project case-study structure</summary>${projectTemplate.map((title) => section(title, "[To add: verified project content.]")).join("")}</details>`
    );
  if (place.id === "experience")
    return (
      heading +
      `<div class="timeline">${place.sections.map(([title, text], i) => `<section class="timeline-entry"><span class="timeline-dot"></span><p class="eyebrow">${i === 0 ? "WORK & INTERNSHIPS" : "EDUCATION"} · DATES TO ADD</p><h3>${title}</h3><p>${text}</p><div class="record-fields"><span>Organization / school</span><span>Role / degree</span><span>Contribution / learning</span></div></section>`).join("")}</div>`
    );
  if (place.id === "beyond")
    return (
      heading +
      `<div class="garden-stories">${place.sections.map(([title, text], i) => `<section class="story-card"><span class="story-symbol" aria-hidden="true">${i ? "✿" : "◇"}</span><p class="eyebrow">${i ? "PERSONAL EXPLORATIONS" : "PEOPLE & COMMUNITY"}</p><h3>${title}</h3><p>${text}</p><small>A real story will grow here.</small></section>`).join("")}</div>`
    );
  if (place.id === "currently")
    return (
      heading +
      `<p class="update-label">LAST UPDATED · awaiting first entry</p><div class="notice-grid">${place.sections.map(([title, text], i) => `<section class="notice-card"><span class="pin" aria-hidden="true"></span><p class="eyebrow">0${i + 1} / ON THE NOTICEBOARD</p><h3>${title}</h3><p>${text}</p></section>`).join("")}</div>`
    );
  return (
    heading +
    `<div class="about-identity"><span class="identity-mark" aria-hidden="true">✧</span><div><p class="eyebrow">THE PERSON BEHIND THE ISLAND</p><h3>[Your name]</h3><p>[Your one-line introduction]</p></div></div>${place.sections.map(([title, text]) => section(title, text)).join("")}<div class="detail-actions"><a href="#resume">Resume ${arrow}</a><a href="#contact">Contact & social links ${arrow}</a></div>`
  );
}

function renderRoute() {
  const [id, child] = location.hash.slice(1).split("/");
  const place = places.find((p) => p.id === id);
  const utility = Object.hasOwn(utilityPages, id) ? utilityPages[id] : null;
  const draft =
    id === "projects" ? projectDrafts.find((p) => p.id === child) : null;
  if (!place && !utility) {
    if (dialog.open) dialog.close();
    document
      .querySelectorAll("[data-nav]")
      .forEach((el) => el.removeAttribute("aria-current"));
    return;
  }
  if (!dialog.open) {
    returnFocus = document.activeElement;
    mapScroll = window.scrollY;
    openedFromMap = true;
  }
  document.querySelector("#detail-location").textContent =
    place?.label ||
    (id === "credits" ? "Credits" : id === "resume" ? "Resume" : "Contact");
  dialog.dataset.section = id;
  if (place) {
    visited.add(id);
    content.innerHTML = renderPlace(place, draft);
  } else {
    content.innerHTML = `<p class="eyebrow">${id === "credits" ? "ABOUT THIS WORLD" : "DIRECT ACCESS"}</p><h2 id="detail-title">${utility.title}</h2><p class="detail-intro">${utility.text}</p>${id === "credits" ? '<a class="section-back" href="https://quaternius.com/">Quaternius · Asset creator ↗</a>' : '<p class="placeholder-note">AWAITING VERIFIED PERSONAL CONTENT</p>'}`;
  }
  document.querySelectorAll("[data-nav]").forEach((el) => {
    if (el.dataset.nav === id) el.setAttribute("aria-current", "page");
    else el.removeAttribute("aria-current");
  });
  if (!dialog.open) dialog.showModal();
  dialog.scrollTop = 0;
  document.querySelector("#close-detail").focus();
  updateVisits();
}

function closeDetails() {
  location.hash = "";
}
document.querySelector("#close-detail").addEventListener("click", closeDetails);
dialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeDetails();
});
dialog.addEventListener("close", () => {
  if (returnFocus instanceof HTMLElement && returnFocus !== document.body)
    returnFocus.focus({ preventScroll: true });
  if (openedFromMap) window.scrollTo({ top: mapScroll, behavior: "instant" });
  openedFromMap = false;
});
window.addEventListener("hashchange", renderRoute);
updateVisits();
renderRoute();
