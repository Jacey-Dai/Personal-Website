// Replace explicit placeholders with verified personal content. Never invent achievements.
export const places = [
  {
    id: "about",
    name: "Welcome Center",
    label: "About",
    number: "01",
    preview: "Meet the person behind this little world.",
    color: "coral",
    title: "Every world starts with a hello.",
    description: "This is where your introduction will live.",
    sections: [
      [
        "Your introduction",
        "[To add: preferred name, a one-line introduction, and a short About.]",
      ],
      [
        "Your direction",
        "[To add: interests, fields you work in, and opportunities you are looking for.]",
      ],
    ],
  },
  {
    id: "projects",
    name: "Project Studio",
    label: "Projects",
    number: "02",
    preview: "Ideas, experiments, and things made real.",
    color: "blue",
    title: "A home for things in the making.",
    description:
      "Selected projects will open as readable case studies, with the process visible alongside the outcome.",
    sections: [
      [
        "Selected projects",
        "[To add: 2–3 real projects. No sample achievements or invented metrics.]",
      ],
    ],
  },
  {
    id: "experience",
    name: "Experience Museum",
    label: "Experience",
    number: "03",
    preview: "The chapters and people that shaped the journey.",
    color: "yellow",
    title: "A collection of chapters.",
    description: "Work, education, and turning points, collected in one place.",
    sections: [
      [
        "Work & internships",
        "[To add: organization, role, dates, responsibilities, and verified contributions.]",
      ],
      [
        "Education",
        "[To add: school, degree, dates, and relevant learning experiences.]",
      ],
    ],
  },
  {
    id: "beyond",
    name: "Curiosity Garden",
    label: "Beyond",
    number: "04",
    preview: "The interests that keep on growing.",
    color: "green",
    title: "Room to grow a little sideways.",
    description:
      "A warmer corner for community, curiosity, and life beyond academic work.",
    sections: [
      [
        "Community & leadership",
        "[To add: clubs, volunteering, leadership roles, and the stories behind them.]",
      ],
      [
        "Small joys",
        "[To add: genuine interests, personal objects, and everyday discoveries. Baking can join when there is a story to share.]",
      ],
    ],
  },
  {
    id: "currently",
    name: "The Noticeboard",
    label: "Currently",
    number: "05",
    preview: "Learning, making, and wondering. Right now.",
    color: "pink",
    title: "The next chapter is underway.",
    description:
      "A small, easy-to-update noticeboard. Only publish what is actually happening.",
    sections: [
      ["Learning", "[To add: what you are learning now.]"],
      [
        "Making & exploring",
        "[To add: a current experiment or question, plus the date of the update.]",
      ],
    ],
  },
];

export const projectTemplate = [
  "Problem & context",
  "My role & team",
  "Methods & tools",
  "Process & key decisions",
  "Outcome & evidence",
  "Reflection & links",
];

export const utilityPages = {
  resume: {
    title: "Resume",
    text: "Resume not added yet. A direct PDF download will appear here once the real document is provided.",
  },
  contact: {
    title: "Let’s connect.",
    text: "Contact details are not published yet. Your verified email, LinkedIn, and GitHub links will appear here.",
  },
  credits: {
    title: "A world made together.",
    text: "Buildings and nature models by Quaternius, from the Medieval Village and Stylized Nature Standard packs (CC0 1.0). Scene composition, material adjustments, sea, paths, and interface created for this personal island. Personal content is still to come.",
  },
};

// Layout scaffolds, not fictional case studies or biographical records.
export const projectDrafts = [
  {
    id: "project-01",
    title: "Your first selected project",
    type: "PROJECT 01 · TO ADD",
    text: "A space for a real problem, your contribution, and the outcome.",
  },
  {
    id: "project-02",
    title: "Another idea brought to life",
    type: "PROJECT 02 · TO ADD",
    text: "A second project, with its own process, decisions, and evidence.",
  },
];
