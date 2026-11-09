# SOURCES

Every record in this dataset carries `source_url`, `retrieved_on` and
`source_type`. This file is the human-readable index of those sources. It is
**generated** by `tools/make_sources.py` from the raw CSVs, so it cannot drift
away from the data.

`source_type` values: `official` (institute publication), `open-licence`
(openly licensed third-party content), `manual` (typed in by a human from a
document they opened), `illustrative` (placeholder written to exercise the
pipeline — withheld from export unless `--allow-illustrative` is passed).

## robots.txt and polite retrieval

Checked before any retrieval, because the brief requires scraping to be polite
and legal.

| Domain | Finding | Consequence for this dataset |
|---|---|---|
| `www.iitbhilai.ac.in` | **Automated retrieval disallowed.** The fetch layer refused `/robots.txt` and every page under the domain with `robots_disallowed`. | No scraping of the institute site. Course and rule records must be entered by a human from documents opened in a browser, with `source_type=manual` and the published page recorded as `source_url`. |
| `archive.nptel.ac.in` | Retrieval permitted; static HTML and PDFs. | Used as the primary NPTEL source. Syllabus PDFs parse cleanly and state title, coordinators, institute and duration. |
| `onlinecourses.nptel.ac.in` | Retrieval permitted, but pages are client-side rendered. | Most course pages return a `Loading...` shell with no metadata. Only `noc25_me78` returned content. These rows are therefore recorded as `tier=listing_only` with `duration_value` left null. |
| `ocw.mit.edu` | Retrieval permitted; terms page readable. | Licence verified directly. Course search results are JS-rendered, so course URL/title pairs were taken from the provider's own indexed listings. |
| `swayam.gov.in` | Not used. | Its licence could not be verified within the time window. An unverifiable licence is worse than a smaller dataset, so SWAYAM is excluded entirely rather than guessed at. |

No rate limiting was required: retrieval totalled a few dozen requests spread
over the working session, well below any crawl-delay concern.

## Licence verification

Licences were read from each provider's own terms page, not assumed.

| Provider | Stated licence | Where verified | Note |
|---|---|---|---|
| MIT OpenCourseWare | Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) | <https://ocw.mit.edu/pages/privacy-and-terms-of-use/> | Version explicit; deed linked from the page. |
| NPTEL | "Creative Commons Attribution-NonCommercial-ShareAlike CC BY-NC-SA" | Footer of <https://nptel.ac.in/> | **No version is stated and no deed is linked.** `licence_version` is therefore left blank. Recording "4.0" would be a fabrication. |

Both licences are NonCommercial and ShareAlike. Any downstream product built on
this data must respect both terms — relevant if the eventual learning buddy is
ever commercial.

## Institute sources (course catalogue and academic rules)

| Source URL | Retrieved | source_type | Records |
|---|---|---|---:|
| https://www.iitbhilai.ac.in/index.php?pid=new_schedule_programs | 2026-11-09 | `manual` | 42 |
| https://www.iitbhilai.ac.in/index.php?pid=ug_manual | 2026-11-09 | `manual` | 34 |

## Open learning resources

56 resources. Every URL below was returned by a retrieval against the provider on the retrieval date shown; none were recalled from memory or constructed by editing another URL.

### MIT OpenCourseWare — 20 resources

Licence applied to all MIT OpenCourseWare rows: **CC BY-NC-SA 4.0** ([deed](https://creativecommons.org/licenses/by-nc-sa/4.0/)), verified 2026-11-09.

| ID | Title | Tier | Duration | Retrieved | URL |
|---|---|---|---|---|---|
| `RES-OCW-001` | 2.51 Intermediate Heat and Mass Transfer | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-51-intermediate-heat-and-mass-transfer-fall-2008/ |
| `RES-OCW-002` | 2.051 Introduction to Heat Transfer | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-051-introduction-to-heat-transfer-fall-2015/ |
| `RES-OCW-003` | 2.43 Advanced Thermodynamics | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-43-advanced-thermodynamics-spring-2024/ |
| `RES-OCW-004` | 2.26 Compressible Fluid Dynamics | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-26-compressible-fluid-dynamics-spring-2004/ |
| `RES-OCW-005` | 2.61 Internal Combustion Engines | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-61-internal-combustion-engines-spring-2017/ |
| `RES-OCW-006` | 2.003SC Engineering Dynamics | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-003sc-engineering-dynamics-fall-2011/ |
| `RES-OCW-007` | 2.003J Dynamics and Vibration | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-003j-dynamics-and-vibration-13-013j-fall-2002/ |
| `RES-OCW-008` | 1.050 Solid Mechanics | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/1-050-solid-mechanics-fall-2004/ |
| `RES-OCW-009` | 2.002 Mechanics and Materials II | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-002-mechanics-and-materials-ii-spring-2004/ |
| `RES-OCW-010` | 2.007 Design and Manufacturing I | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-007-design-and-manufacturing-i-spring-2009/ |
| `RES-OCW-011` | 2.008 Design and Manufacturing II | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-008-design-and-manufacturing-ii-spring-2025/ |
| `RES-OCW-012` | 2.72 Elements of Mechanical Design | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-72-elements-of-mechanical-design-spring-2009/ |
| `RES-OCW-013` | 2.04A Systems and Controls | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-04a-systems-and-controls-spring-2013/ |
| `RES-OCW-014` | 2.004 Systems, Modeling, and Control II | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-004-systems-modeling-and-control-ii-fall-2007/ |
| `RES-OCW-015` | 2.14 Analysis and Design of Feedback Control Systems | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-14-analysis-and-design-of-feedback-control-systems-spring-2014/ |
| `RES-OCW-016` | 2.737 Mechatronics | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-737-mechatronics-fall-2014/ |
| `RES-OCW-017` | 2.000 How and Why Machines Work | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-000-how-and-why-machines-work-spring-2002/ |
| `RES-OCW-018` | 2.017J Design of Electromechanical Robotic Systems | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-017j-design-of-electromechanical-robotic-systems-fall-2009/pages/syllabus/ |
| `RES-OCW-019` | 2.141 Modeling and Simulation of Dynamic Systems | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/2-141-modeling-and-simulation-of-dynamic-systems-fall-2006/pages/calendar/ |
| `RES-OCW-020` | 16.810 Engineering Design and Rapid Prototyping | listing only | not stated | 2026-11-09 | https://ocw.mit.edu/courses/16-810-engineering-design-and-rapid-prototyping-january-iap-2005/ |

### NPTEL — 36 resources

Licence applied to all NPTEL rows: **CC BY-NC-SA (version not stated by provider)**, verified 2026-11-09.

| ID | Title | Tier | Duration | Retrieved | URL |
|---|---|---|---|---|---|
| `RES-NPT-001` | Engineering Mechanics | page read | not stated | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/112103108.pdf |
| `RES-NPT-002` | Dynamics of Machines | page read | 45 hours | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/112104114.pdf |
| `RES-NPT-003` | Design of Machine Elements | page read | not stated | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/112105124.pdf |
| `RES-NPT-004` | Fundamentals of Manufacturing Processes | page read | 12 weeks | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/112107219.pdf |
| `RES-NPT-005` | Principles of Physical Metallurgy | page read | 44 hours | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/113105023.pdf |
| `RES-NPT-006` | Applied Thermodynamics | page read | 12 weeks | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/112103307.pdf |
| `RES-NPT-007` | Heat and Mass Transfer | page read | 42 hours | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/112101097.pdf |
| `RES-NPT-008` | Introduction to Materials Science and Engineering | page read | 40 hours | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/113106032.pdf |
| `RES-NPT-009` | Thermodynamics | page read | 12 weeks | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc25_me78/preview |
| `RES-NPT-010` | Basics of Mechanical Engineering - 3 | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc25_me168/preview |
| `RES-NPT-011` | Fundamentals of Heat Transfer | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/e-learning/preview/noc25_me171 |
| `RES-NPT-012` | Thermal Engineering: Basic and Applied | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc25_me77/preview |
| `RES-NPT-013` | Computational Fluid Dynamics and Heat Transfer | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc22_me101/preview |
| `RES-NPT-014` | Conduction and Convection Heat Transfer | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc22_me63/preview |
| `RES-NPT-015` | Convective Heat Transfer | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/e-learning/preview/noc21_me19 |
| `RES-NPT-016` | Vibrations of Structures | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc21_me42/preview |
| `RES-NPT-017` | Introduction to Mechanical Vibration | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc22_me76/preview |
| `RES-NPT-018` | Fundamentals of Manufacturing Processes (online) | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc25_me119/preview |
| `RES-NPT-019` | Theory of Production Processes | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc23_me126/preview |
| `RES-NPT-020` | Manufacturing Process Technology I & II | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc26_me47/preview |
| `RES-NPT-021` | Manufacturing Processes - Casting and Joining | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/e-learning/preview/noc26_me118 |
| `RES-NPT-022` | Introduction to Materials Science and Engineering (online) | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc25_mm17/preview |
| `RES-NPT-023` | Phase Transformation in Materials | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc25_me61/preview |
| `RES-NPT-024` | Materials Science and Engineering | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc24_mm12/preview |
| `RES-NPT-025` | Dynamic Behaviour of Materials | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc22_me115/preview |
| `RES-NPT-026` | Applied Thermodynamics (online) | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc21_me119/preview |
| `RES-NPT-027` | Robotics | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc21_me76/preview |
| `RES-NPT-028` | Mechanical Measurement Systems | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc20_me57/preview |
| `RES-NPT-029` | Robotics and Control: Theory and Practice | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc20_me03/preview |
| `RES-NPT-030` | Microrobotics | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc25_me177/preview |
| `RES-NPT-031` | Measurement and Instrumentation | listing only | not stated | 2026-11-09 | https://onlinecourses.nptel.ac.in/noc26_ee01/preview |
| `RES-NPT-032` | NOC: Automation in Manufacturing | listing only | not stated | 2026-11-09 | https://archive.nptel.ac.in/courses/112/103/112103293/ |
| `RES-NPT-033` | Design of Machine Elements I (course archive) | listing only | not stated | 2026-11-09 | https://archive.nptel.ac.in/courses/112/105/112105124/ |
| `RES-NPT-034` | Advanced Manufacturing Processes | listing only | not stated | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/112107077.pdf |
| `RES-NPT-035` | Computational Heat Transfer and Fluid Flow | listing only | not stated | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/112108091.pdf |
| `RES-NPT-036` | Basics of Mechanical Engineering - 1 | listing only | not stated | 2026-11-09 | https://archive.nptel.ac.in/content/syllabus_pdf/112104526.pdf |

## Author-defined content (no source URL, by design)

- `data/raw/curriculum/skills.csv` — the skill taxonomy. Every row carries `origin=author_inferred`. These nodes are the dataset author's organising structure, not quotations from any institute or provider document. The validator exempts `author_inferred` skills from the provenance requirement so that this stays visible rather than being hidden behind a placeholder citation.
- `data/raw/resources/resource_skills.csv` and `data/raw/curriculum/course_skills.csv` — mappings. The endpoints are real; the *depth* and *level* judgements are the author's, and each row's `source_note` says so. Where a judgement was made from a specific syllabus phrase, that phrase is stored in the link's `evidence` field.
