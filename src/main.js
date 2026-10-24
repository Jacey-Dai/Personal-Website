import "./styles.css";
import { places, utilityPages } from "./content.js";
import { worldArt } from "./world.js";
import buildingLayers from "./building-layers.json";
import { rooms, renderInterior } from "./interiors.js";
import { artifactFor } from "./notebooks.js";

const storageKey = "island-building-lights-v1";
const roomDialog = document.querySelector("#room");
const readerDialog = document.querySelector("#reader");
const tooltip = document.querySelector("#map-tooltip");
const visited = new Set();
let currentRoom = null;
let mapFocus = null;
let objectFocus = null;
let peek = null;
let tooltipBuilding = null;
try {
  const saved = JSON.parse(localStorage.getItem(storageKey) || "[]");
  if (Array.isArray(saved))
    saved
      .filter((id) => places.some((p) => p.id === id))
      .forEach((id) => visited.add(id));
} catch {
  /* Exploration works without browser storage. */
}

const navigation = () =>
  ["about", "projects", "experience", "beyond", "resume", "contact"]
    .map(
      (id) =>
        `<a href="#${id}" data-nav="${id}">${places.find((p) => p.id === id)?.label || (id === "resume" ? "Resume" : "Contact")}</a>`,
    )
    .join("");
document.querySelector("#navigation").innerHTML = navigation();
document.querySelector("#room-navigation").innerHTML = navigation();
document.querySelector("#island-art").innerHTML = worldArt;
document.querySelector("#places").innerHTML = places
  .map((p) => {
    const b = buildingLayers[p.id];
    return `<a class="building" href="#${p.id}" data-place="${p.id}" aria-label="${p.name} — ${p.label}. ${p.preview}" style="left:${b.left}%;top:${b.top}%;width:${b.width}%;height:${b.height}%;--shape:${b.clip};--depth:${Math.round((b.top + b.height) * 10)}"><span class="building-surface" aria-hidden="true"></span></a>`;
  })
  .join("");
const flagColors = {
  about: "#7f9f6f",
  projects: "#c45c46",
  experience: "#5f7f9e",
  beyond: "#6f9f5f",
  currently: "#d9a441",
};
document.querySelector("#building-states").innerHTML = places
  .map((p) => {
    const b = buildingLayers[p.id];
    const [x, y] = b.roof;
    return `<g class="building-state" data-visit="${p.id}"><path class="window-light light-${p.id}" d="${b.lights}"/><g class="roof-flag" transform="translate(${x} ${y})"><path d="M0 3V-54" stroke="#5c5144" stroke-width="3.5" stroke-linecap="round"/><path class="pennant" d="M2-53Q22-63 45-50L36-31Q19-41 2-32Z" fill="${flagColors[p.id]}" stroke="#fff3d6" stroke-width="2"/></g></g>`;
  })
  .join("");

function updateBuildings() {
  document
    .querySelectorAll("[data-place]")
    .forEach((el) =>
      el.classList.toggle("is-visited", visited.has(el.dataset.place)),
    );
  document
    .querySelectorAll("[data-visit]")
    .forEach((el) =>
      el.classList.toggle("is-lit", visited.has(el.dataset.visit)),
    );
  document.querySelector("#reset-lights").hidden = visited.size === 0;
  try {
    localStorage.setItem(storageKey, JSON.stringify([...visited]));
  } catch {
    /* Optional persistence. */
  }
}

function hideTooltip() {
  tooltip.hidden = true;
  tooltipBuilding = null;
}
function showTooltip(element) {
  const p = places.find((p) => p.id === element.dataset.place);
  if (!p || roomDialog.open) return;
  tooltipBuilding = element;
  tooltip.querySelector("strong").textContent = p.name;
  tooltip.querySelector("small").textContent = p.label;
  tooltip.querySelector("p").textContent = p.preview;
  tooltip.classList.toggle("is-touch", peek === p.id);
  tooltip.hidden = false;
  const r = element.getBoundingClientRect();
  const t = tooltip.getBoundingClientRect();
  const left = Math.max(
    12,
    Math.min(innerWidth - t.width - 12, r.left + r.width / 2 - t.width / 2),
  );
  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${Math.max(95, r.top - t.height - 12)}px`;
}
function clearPeek() {
  peek = null;
  document
    .querySelectorAll(".is-peeking")
    .forEach((el) => el.classList.remove("is-peeking"));
  hideTooltip();
}
document.querySelectorAll("[data-place]").forEach((el) => {
  el.addEventListener("pointerenter", (e) => {
    if (e.pointerType !== "touch") showTooltip(el);
  });
  el.addEventListener("pointerleave", () => {
    if (peek !== el.dataset.place) hideTooltip();
  });
  el.addEventListener("focus", () => {
    if (el.matches(":focus-visible")) showTooltip(el);
  });
  el.addEventListener("blur", () => {
    if (peek !== el.dataset.place) hideTooltip();
  });
  el.addEventListener("click", (event) => {
    if (
      matchMedia("(hover: none)").matches &&
      event.detail > 0 &&
      peek !== el.dataset.place
    ) {
      event.preventDefault();
      clearPeek();
      peek = el.dataset.place;
      el.classList.add("is-peeking");
      showTooltip(el);
    }
  });
});
document.addEventListener("pointerdown", (event) => {
  if (peek && !event.target.closest(".building")) clearPeek();
});
window.addEventListener("resize", () => {
  if (tooltipBuilding) showTooltip(tooltipBuilding);
});
document.querySelector("#reset-lights").addEventListener("click", () => {
  visited.clear();
  updateBuildings();
  document.querySelector("#explore-status").textContent =
    "Island lights and flags reset.";
});
if (matchMedia("(hover: none)").matches)
  document.querySelector("#explore-hint").textContent =
    "Tap a building to discover it.";

function closeReader() {
  if (readerDialog.open) {
    readerDialog.close();
    if (objectFocus?.isConnected && roomDialog.open)
      objectFocus.focus({ preventScroll: true });
  }
}
function leaveIslandRoom() {
  closeReader();
  if (roomDialog.open) roomDialog.close();
  currentRoom = null;
  document.body.removeAttribute("data-room");
  if (mapFocus instanceof HTMLElement && mapFocus.isConnected)
    mapFocus.focus({ preventScroll: true });
  document
    .querySelectorAll("[data-nav]")
    .forEach((el) => el.removeAttribute("aria-current"));
}
function route() {
  const [id, child] = location.hash.slice(1).split("/");
  const utility = Object.hasOwn(utilityPages, id);
  const place = places.find((p) => p.id === id) || (utility ? places[0] : null);
  if (!place) {
    leaveIslandRoom();
    return;
  }
  clearPeek();
  const isNewRoom = currentRoom !== place.id;
  if (!roomDialog.open)
    mapFocus =
      document.activeElement?.closest?.(".building") ||
      document.querySelector(`[data-place="${place.id}"]`);
  if (isNewRoom) {
    closeReader();
    currentRoom = place.id;
    document.querySelector("#room-content").innerHTML = renderInterior(place);
    document.body.dataset.room = place.id;
    roomDialog.dataset.room = place.id;
  }
  if (!roomDialog.open) roomDialog.showModal();
  if (!visited.has(place.id)) {
    visited.add(place.id);
    updateBuildings();
    document.querySelector("#explore-status").textContent =
      `The ${place.name} windows are lit and its roof flag is raised.`;
  }
  const validChild =
    child &&
    (rooms[place.id].objects.some((o) => o.id === child) ||
      child === "index" ||
      ["resume", "contact", "credits"].includes(child));
  const key = utility ? id : validChild ? child : null;
  if (key) {
    if (!readerDialog.open)
      objectFocus =
        document.activeElement?.closest?.(".scene-object,.room-index") ||
        document.querySelector(".room-index");
    const book = artifactFor(place.id, key);
    readerDialog.dataset.artifact = book.theme;
    document.querySelector("#reader-content").innerHTML = book.html;
    if (!readerDialog.open) readerDialog.showModal();
    readerDialog.scrollTop = 0;
    document.querySelector("#close-reader").focus();
  } else {
    const wasReading = readerDialog.open;
    closeReader();
    if (wasReading && objectFocus?.isConnected)
      objectFocus.focus({ preventScroll: true });
    else if (isNewRoom) document.querySelector("#close-room").focus();
  }
  document.querySelectorAll("[data-nav]").forEach((el) => {
    if (el.dataset.nav === place.id) el.setAttribute("aria-current", "page");
    else el.removeAttribute("aria-current");
  });
}
document.querySelector("#close-reader").addEventListener("click", () => {
  closeReader();
  location.hash = currentRoom || "";
});
document
  .querySelector("#reader-destination")
  .addEventListener("change", (event) => {
    if (event.target.value) location.hash = event.target.value;
    event.target.value = "";
  });
readerDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  event.stopPropagation();
  closeReader();
  location.hash = currentRoom || "";
});
document.querySelector("#close-room").addEventListener("click", () => {
  location.hash = "";
});
roomDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  location.hash = "";
});
window.addEventListener("hashchange", route);
updateBuildings();
route();
