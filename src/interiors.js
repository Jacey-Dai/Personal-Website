import layout from "./interior-layout.json";

export const rooms = {
  about: {
    subtitle: "The reception room",
    hint: "Open the guestbook, pick up a brochure, or leave a little hello.",
    index: "story",
    action: "Open the guestbook",
    objects: [
      {
        id: "story",
        name: "The guestbook",
        detail: "About the person behind the island",
      },
      {
        id: "resume",
        name: "Resume brochure",
        detail: "A direct route to the real resume",
      },
      {
        id: "contact",
        name: "The letterbox",
        detail: "Email and social links",
      },
    ],
  },
  projects: {
    subtitle: "Inside the project studio",
    hint: "There are blueprints on the workbench. Pick one up and take a closer look.",
    index: "index",
    action: "Open the project index",
    objects: [
      {
        id: "project-01",
        name: "Blueprint 01",
        detail: "First selected project · content to add",
      },
      {
        id: "project-02",
        name: "Prototype 02",
        detail: "Second selected project · content to add",
      },
      {
        id: "index",
        name: "The project wall",
        detail: "Browse the studio’s project files",
      },
    ],
  },
  experience: {
    subtitle: "Inside the experience museum",
    hint: "Step up to an exhibit, or open the archive cabinet.",
    index: "index",
    action: "Open the archive catalogue",
    objects: [
      {
        id: "work",
        name: "Work & internships",
        detail: "Open the work archive",
      },
      {
        id: "education",
        name: "The education exhibit",
        detail: "Learning and education records",
      },
      {
        id: "index",
        name: "The archive cabinet",
        detail: "Browse the museum catalogue",
      },
    ],
  },
  beyond: {
    subtitle: "Inside the curiosity greenhouse",
    hint: "Each growing bed holds a different kind of story. The journal is on the potting bench.",
    index: "index",
    action: "Open the garden journal",
    objects: [
      {
        id: "community",
        name: "The community bed",
        detail: "Clubs, volunteering, and leadership",
      },
      {
        id: "curiosities",
        name: "The curiosity bed",
        detail: "Interests and personal explorations",
      },
      {
        id: "index",
        name: "The garden journal",
        detail: "Browse the garden’s stories",
      },
    ],
  },
  currently: {
    subtitle: "Inside the noticeboard room",
    hint: "Take a note off the board to see what is happening now.",
    index: "index",
    action: "Read the noticeboard",
    objects: [
      {
        id: "learning",
        name: "Learning note",
        detail: "What I am learning · update to add",
      },
      {
        id: "making",
        name: "Making & exploring",
        detail: "Current projects and questions · update to add",
      },
      {
        id: "index",
        name: "The update desk",
        detail: "Read all current notes",
      },
    ],
  },
};

export function renderInterior(place) {
  const room = rooms[place.id];
  return `<div class="room-introduction"><p class="eyebrow">${room.subtitle}</p><h1 id="room-title">${place.name}</h1><p>${room.hint}</p></div>
    <div class="room-scene"><img class="interior-image" src="${import.meta.env.BASE_URL}interiors/${place.id}.webp" width="1600" height="1100" alt="${room.subtitle}: a cutaway room with objects you can open." />
    <div class="room-objects">${room.objects
      .map((o) => {
        const p = layout[place.id][o.id];
        return `<a class="scene-object object-${o.id}" href="#${place.id}/${o.id}" data-object="${o.id}" aria-label="${o.name}: ${o.detail}" style="--x:${p.x}%;--y:${p.y}%"><span class="object-ring" aria-hidden="true"></span><span class="object-tooltip"><strong>${o.name}</strong><small>${o.detail}</small></span></a>`;
      })
      .join("")}</div></div>
    <div class="room-bottom"><span>Choose an object to open its story.</span><a class="room-index" href="#${place.id}/${room.index}">${room.action} <span aria-hidden="true">→</span></a></div>`;
}
