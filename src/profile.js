// Source: owner-provided resume and contact details, 2026-10-19.
// Keep personal data independent of scene and artifact rendering.
export const profile = {
  name: "Jacey Dai",
  introduction: "A background in mathematics, statistics, and data science. Currently exploring AI agents and product.",
  email: "jacey.dai827@gmail.com",
  linkedin: "https://www.linkedin.com/in/jacey-dai/",
  github: "https://github.com/Jacey-Dai",
  resume: "resume/Jacey_Dai_Resume.pdf",
  learning: "Currently exploring AI agents and product.",
  interest: "I like succulents.",
  updated: "October 19, 2026",
};

export const education = [
  { organization: "Duke University", role: "Master in Interdisciplinary Data Science", dates: "Aug. 2026 – May 2028", location: "Durham, NC", details: [] },
  { organization: "University of Illinois Urbana-Champaign", role: "Bachelor of Science in Mathematics and Statistics, Minor in Computer Science", dates: "Aug. 2022 – May 2026", location: "Champaign, IL", details: ["Dorothy E. Nowlin Scholarship Recipient, Dean’s List, James Scholar."] },
];

export const experience = [
  { organization: "Technology Services Help Desk, UIUC", role: "Technology Support Consultant", dates: "Apr. 2025 – May 2026", location: "Champaign, IL", details: [
    "Analyzed 4,000+ monthly service records using SQL and Excel to identify resolution bottlenecks, reducing average ticket first response time from 4 hours to 45 minutes.",
    "Automated weekly operational reports using Python and VBA across five service categories, eliminating 15 hours of manual effort weekly.",
    "Cross-referenced system logs with service records, identifying 500+ discrepancies and achieving 99.2% data accuracy for downstream reporting.",
    "Documented operational workflows with cross-functional teams, improving team efficiency and reducing error rates by 25%.",
  ] },
  { organization: "Illinois State Geological Survey", role: "Student Assistant, Data Analytics", dates: "Nov. 2024 – Mar. 2026", location: "Champaign, IL", details: [
    "Validated 500K+ multi-modal sensor readings using Python (Pandas, NumPy), ensuring 99.5% data integrity for downstream training and analysis.",
    "Built SQL and Python data pipelines to clean and process sensor data, reducing processing time from 8 hours to 3.2 hours.",
    "Used z-score and IQR-based anomaly detection to flag 200+ noisy or ambiguous readings.",
    "Maintained data validation protocols and documentation across multiple sources for cross-functional research collaboration.",
  ] },
  { organization: "Illinois Risk Lab, University of Illinois", role: "Research Assistant, Data Science (Cyber Risk)", dates: "Jan. 2024 – May 2024", location: "Champaign, IL", details: [
    "Built risk exposure models using logistic regression and Monte Carlo simulation on 100K+ breach records in Python and SQL, achieving 87% predictive accuracy.",
    "Benchmarked logistic regression outputs against baseline scenarios, contributing to a framework adopted by three partner organizations.",
    "Conducted P&L impact analysis across risk categories to inform model refinement and risk management strategy.",
    "Worked with faculty and industry partners on data-driven risk-mitigation recommendations.",
  ] },
  { organization: "Power Education", role: "Data Analyst Intern", dates: "May 2023 – Aug. 2023", location: "Nanjing, China", details: [
    "Analyzed 200K+ transaction records using SQL and Python, improving operational throughput by 20%.",
    "Automated daily reconciliation reports using Excel VBA, reducing manual processing from 4 hours to 10 minutes while maintaining 99% accuracy.",
    "Designed an A/B testing framework using 50K+ records with 95% statistical significance to inform process-optimization decisions.",
    "Collaborated with Engineering to translate analytical insights into process-automation recommendations.",
  ] },
];
