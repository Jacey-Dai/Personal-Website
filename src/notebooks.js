import {
  places,
  projectDrafts,
  projectTemplate,
  utilityPages,
} from "./content.js";
import { profile, education, experience } from "./profile.js";

const resumeUrl = `${import.meta.env?.BASE_URL ?? "/Personal-Website/"}${profile.resume}`;
const contactLinks = () => links([
  [`mailto:${profile.email}`, "Email", profile.email],
  [profile.linkedin, "LinkedIn", "linkedin.com/in/jacey-dai"],
  [profile.github, "GitHub", "github.com/Jacey-Dai"],
]);
const records = (items) => items.map((item) => `<section class="paper-section"><h3>${item.organization}</h3><p><strong>${item.role}</strong></p><p>${item.dates} · ${item.location}</p><ul>${item.details.map((detail) => `<li>${detail}</li>`).join("")}</ul></section>`).join("");

const pending =
  '<p class="content-pending">Personal content has not been added yet. These are clearly marked placeholders.</p>';
const ruled = (title, text) =>
  `<section class="paper-section"><h3>${title}</h3><p>${text}</p></section>`;
const links = (items) =>
  `<div class="file-index">${items.map(([url, title, description], i) => `<a href="${url}"><span class="file-number">0${i + 1}</span><span><strong>${title}</strong><small>${description}</small></span><span aria-hidden="true">→</span></a>`).join("")}</div>`;
const wrap = (theme, eyebrow, title, body) => ({
  theme,
  title,
  html: `<article class="artifact artifact-${theme}"><header class="artifact-heading"><p class="eyebrow">${eyebrow}</p><h2 id="reader-title">${title}</h2></header>${body}</article>`,
});

export function artifactFor(roomId, key) {
  const place = places.find((p) => p.id === roomId);
  if (key === "resume" || key === "contact" || key === "credits") {
    const page = utilityPages[key];
    return wrap(
      "guestbook",
      key === "credits"
        ? "THE ISLAND / MAKING OF"
        : "WELCOME CENTER / " + (key === "resume" ? "BROCHURE" : "LETTERS"),
      page.title,
      `<p class="paper-lead">${page.text}</p>${key === "credits" ? '<p><a class="paper-link" href="https://quaternius.com/">Quaternius · Asset creator</a></p>' : key === "resume" ? `<p><a class="paper-link" href="${resumeUrl}" target="_blank" rel="noopener">Open resume PDF ↗</a></p><p><a class="paper-link" href="${resumeUrl}" download="Jacey_Dai_Resume.pdf">Download resume ↓</a></p>` : contactLinks()}`,
    );
  }
  if (roomId === "projects") {
    const draft = projectDrafts.find((p) => p.id === key);
    if (draft)
      return wrap(
        "blueprint",
        `PROJECT STUDIO / BLUEPRINT ${key.endsWith("01") ? "01" : "02"} / TO ADD`,
        draft.title,
        `${pending}<div class="blueprint-meta"><div>ROLE<span>To be added</span></div><div>TOOLS<span>To be added</span></div><div>YEAR<span>To be added</span></div></div><div class="process-strip"><span>Question</span><i>→</i><span>Experiment</span><i>→</i><span>Outcome</span></div>${projectTemplate.map((title, i) => `<section class="paper-section"><span class="section-number">0${i + 1}</span><h3>${title}</h3><p>[To add: verified project content.]</p></section>`).join("")}<a class="paper-link" href="#projects/index">← Back to the project files</a>`,
      );
    return wrap(
      "blueprint",
      "PROJECT STUDIO / FILE INDEX",
      "On the workbench.",
      `${pending}${links(projectDrafts.map((p) => [`#projects/${p.id}`, p.title, p.text]))}<p class="paper-footnote">Each blueprint opens a case study: problem, role, tools, decisions, outcome, and reflection.</p>`,
    );
  }
  if (roomId === "experience") {
    if (key === "index")
      return wrap(
        "archive",
        "EXPERIENCE MUSEUM / CATALOGUE",
        "The collected chapters.",
        `${links([
          ["#experience/work", "Work & internships", "Open the work archive"],
          ["#experience/education", "Education", "Open the learning exhibit"],
        ])}`,
      );
    const item = place.sections[key === "education" ? 1 : 0];
    return wrap(
      "archive",
      `EXPERIENCE MUSEUM / ${key === "education" ? "EXHIBIT 02" : "ARCHIVE 01"}`,
      item[0],
      `${records(key === "education" ? education : experience)}<p class="paper-footnote">From my resume.</p><a class="paper-link" href="#experience/index">← Archive catalogue</a>`,
    );
  }
  if (roomId === "beyond") {
    if (key === "curiosities") return wrap("journal", "CURIOSITY GARDEN / SMALL JOYS", "A little room for succulents.", `${ruled("Small joys", profile.interest)}<a class="paper-link" href="#beyond/index">← Garden journal</a>`);
    if (key === "index")
      return wrap(
        "journal",
        "CURIOSITY GARDEN / FIELD JOURNAL",
        "Things worth growing.",
        `${links([
          [
            "#beyond/community",
            "People & community",
            "Clubs, volunteering, and leadership",
          ],
          [
            "#beyond/curiosities",
            "Small curiosities",
            "Interests, explorations, and everyday discoveries",
          ],
        ])}`,
      );
    const item = place.sections[key === "community" ? 0 : 1];
    return wrap(
      "journal",
      "CURIOSITY GARDEN / A PAGE FROM THE JOURNAL",
      item[0],
      `<div class="journal-sprig" aria-hidden="true"><svg viewBox="0 0 80 100"><path d="M40 95V16M40 55Q4 57 12 24Q42 24 40 55M40 75Q76 75 68 42Q40 42 40 75" fill="#afc3a2" stroke="#6f8c70" stroke-width="2"/></svg></div>${pending}${ruled("A story to plant", item[1])}${ruled("Why it matters", "[To add: a personal reflection, real detail, or small discovery.]")}<p class="journal-note">Room for the things that grow outside a job title.</p><a class="paper-link" href="#beyond/index">← Garden journal</a>`,
    );
  }
  if (roomId === "currently") {
    if (key === "index")
      return wrap(
        "notice",
        "THE NOTICEBOARD / ALL NOTES",
        "A few things in progress.",
        `${links([
          ["#currently/learning", "Learning", "Read the learning note"],
          ["#currently/making", "Making & exploring", "Read the making note"],
        ])}<p class="paper-footnote">Learning note updated: ${profile.updated}.</p>`,
      );
    const item = place.sections[key === "learning" ? 0 : 1];
    return wrap(
      "notice",
      "TAKEN FROM THE NOTICEBOARD",
      item[0],
      `<span class="paper-pin" aria-hidden="true"></span>${key === "learning" ? "" : pending}<p class="paper-lead">${item[1]}</p><p class="paper-footnote">${key === "learning" ? `Last updated: ${profile.updated}.` : "Last updated: to be added."}</p><a class="paper-link" href="#currently/index">← All pinned notes</a>`,
    );
  }
  return wrap(
    "guestbook",
    "WELCOME CENTER / THE GUESTBOOK",
    `Hello, I’m ${profile.name}.`,
    `<p class="paper-lead">${profile.introduction}</p>${ruled("Education", "Studying Interdisciplinary Data Science at Duke University, with a background in Mathematics and Statistics from the University of Illinois Urbana-Champaign.")}<div class="guestbook-links"><a href="#resume">Pick up a resume brochure →</a><a href="#contact">Leave a little hello →</a></div>${contactLinks()}`,
  );
}
