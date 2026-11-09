#!/usr/bin/env python3
"""
Authors data/raw/resources/resources.csv and resource_skills.csv.

Manual-entry step, disclosed in the README. Every URL in this file was returned
by a retrieval against the provider on the date in RETRIEVED_ON; none were
recalled from memory or constructed by editing another URL.

Two tiers of metadata, distinguished in source_note so a reader can tell them
apart without trusting this docstring:

  tier="page_read"    -- the resource's own page/PDF was fetched and the title,
                         instructor, institute, duration and description below
                         are what that document states.
  tier="listing_only" -- only the title/URL pair was retrieved, from the
                         provider's own search listing. Duration is left null
                         rather than guessed.

Licences were checked against the provider's own terms pages, not assumed:
  * MIT OCW   -- CC BY-NC-SA 4.0, stated at /pages/privacy-and-terms-of-use/,
                 deed linked. Version is explicit.
  * NPTEL     -- footer of nptel.ac.in states "Creative Commons
                 Attribution-NonCommercial-ShareAlike CC BY-NC-SA" with NO
                 version and no linked deed. Recorded with licence_version
                 blank. Inferring "4.0" would be a fabrication.
SWAYAM is deliberately absent: its licence could not be verified in the time
window, and an unverifiable licence is worse than a smaller dataset.
"""
import csv, os

RETRIEVED_ON = "2026-11-09"
OCW = ("CC BY-NC-SA", "4.0", "https://creativecommons.org/licenses/by-nc-sa/4.0/")
NPTEL = ("CC BY-NC-SA", "", "")
LIC_SRC = {"MIT OpenCourseWare": "https://ocw.mit.edu/pages/privacy-and-terms-of-use/",
           "NPTEL": "https://nptel.ac.in/"}

# id, title, provider, fmt, dur_val, dur_unit, url, instructor, institute, desc, skills, tier, extra_note
R = [
 # ---- NPTEL syllabus PDFs: page_read, metadata is what the PDF states --------
 ("RES-NPT-001", "Engineering Mechanics", "NPTEL", "syllabus PDF + video course", None, "",
  "https://archive.nptel.ac.in/content/syllabus_pdf/112103108.pdf",
  "Dr. G. Saravana Kumar; Prof. U.S. Dixit", "IIT Guwahati",
  "Statics including forces, moments, equilibrium and free body diagrams; analysis of trusses, frames, machines, beams and cables; friction; centroids and moments of inertia; virtual work and energy methods; particle and rigid-body dynamics; an introduction to vibration.",
  [("SK-STATICS","intro"),("SK-FBD","working"),("SK-TRUSS","working"),("SK-FRICTION","working"),("SK-RBD","intro")],
  "page_read", "source states no total duration"),

 ("RES-NPT-002", "Dynamics of Machines", "NPTEL", "syllabus PDF + video course", 45, "hours",
  "https://archive.nptel.ac.in/content/syllabus_pdf/112104114.pdf",
  "Prof. Amitabha Ghosh", "IIT Kanpur",
  "Machine dynamics including rigid-body motion, gyroscopic effects, balancing of rotating bodies and engine unbalance; speed control through flywheels and governors; vibration theory for single- and multi-degree-of-freedom systems, forced and damped vibration, and approximate methods for natural frequencies.",
  [("SK-RBD","working"),("SK-BALANCE","working"),("SK-VIB","working"),("SK-KINEM","intro")],
  "page_read", "duration = sum of the 14 stated module durations (45 h); source states no overall total"),

 ("RES-NPT-003", "Design of Machine Elements", "NPTEL", "syllabus PDF + video course", None, "",
  "https://archive.nptel.ac.in/content/syllabus_pdf/112105124.pdf",
  "Prof. B. Maiti; Prof. G. Chakraborty; Prof. S.K. Roychowdhury", "IIT Kharagpur",
  "Design philosophy, materials, and the stress and strain analysis behind mechanical components, including failure theories and fatigue; applied to fasteners, keys, couplings, springs, levers, brackets, shafts, and thin and thick cylinders.",
  [("SK-MACHDESIGN","working"),("SK-STRESS","working"),("SK-FAIL","working")],
  "page_read", "source states no total duration; syllabus is 9 modules over 38 lectures"),

 ("RES-NPT-004", "Fundamentals of Manufacturing Processes", "NPTEL", "syllabus PDF + online course", 12, "weeks",
  "https://archive.nptel.ac.in/content/syllabus_pdf/112107219.pdf",
  "Prof. D.K. Dwivedi; Prof. Shamik Basak", "IIT Roorkee",
  "Manufacturing concepts, process selection and break-even analysis; casting, metal forming, joining, machining and grinding; heat treatment of steel and aluminium alloys; methods for improving surface properties including surface modification, composition changes and coatings.",
  [("SK-CASTING","working"),("SK-FORMING","working"),("SK-JOINING","working"),("SK-MACHINING","working"),("SK-HEATTREAT","intro")],
  "page_read", ""),

 ("RES-NPT-005", "Principles of Physical Metallurgy", "NPTEL", "syllabus PDF + web course", 44, "hours",
  "https://archive.nptel.ac.in/content/syllabus_pdf/113105023.pdf",
  "Prof. R.N. Ghosh", "IIT Kharagpur",
  "How microstructures form in metals and alloys during processing and how they relate to in-service properties; thermodynamics and kinetics of phase transformations; alloy design, casting, forming and heat treatment; structure-property relationships; examination tools, crystal structure and crystal defects.",
  [("SK-PHASE","working"),("SK-CRYSTAL","working"),("SK-HEATTREAT","working"),("SK-MECHPROP","intro")],
  "page_read", "duration = sum of stated per-topic hour allocations (44 h); source states no overall total"),

 ("RES-NPT-006", "Applied Thermodynamics", "NPTEL", "syllabus PDF + online course", 12, "weeks",
  "https://archive.nptel.ac.in/content/syllabus_pdf/112103307.pdf",
  "Prof. Niranjan Sahoo; Prof. Pranab K. Mondal", "IIT Guwahati",
  "Thermodynamic foundations and cycles used in power and refrigeration systems: steam and gas power cycles, refrigeration, psychrometrics, internal combustion engines, and gas turbine and aircraft/rocket propulsion cycles, with a review of basic thermodynamics.",
  [("SK-CYCLES","working"),("SK-PSYCHRO","working"),("SK-COMBUST","working"),("SK-LAWS","intro")],
  "page_read", ""),

 ("RES-NPT-007", "Heat and Mass Transfer", "NPTEL", "syllabus PDF + video course", 42, "hours",
  "https://archive.nptel.ac.in/content/syllabus_pdf/112101097.pdf",
  "Prof. S.P. Sukhatme; Prof. U.N. Gaitonde", "IIT Bombay",
  "Fundamentals of heat transfer: steady, transient and numerical conduction; radiation; forced and natural convection; heat exchangers; condensation and boiling; and mass transfer including its analogy with heat transfer.",
  [("SK-COND","working"),("SK-CONV","working"),("SK-RAD","working"),("SK-HX","working"),("SK-MASST","intro")],
  "page_read", "total duration stated as 42 hours"),

 ("RES-NPT-008", "Introduction to Materials Science and Engineering", "NPTEL", "syllabus PDF + web course", 40, "hours",
  "https://archive.nptel.ac.in/content/syllabus_pdf/113106032.pdf",
  "Dr. Ranjit Bauri", "IIT Madras",
  "History and scope of materials science; atomic structure, bonding and crystal lattices; crystal imperfections, solid solutions, phase diagrams, diffusion, phase transformations and strengthening mechanisms; classification and properties of metals, alloys, ceramics and polymers.",
  [("SK-MATSCI","intro"),("SK-CRYSTAL","working"),("SK-PHASE","working")],
  "page_read", "total duration stated as 40 hours of lectures"),

 ("RES-NPT-009", "Thermodynamics", "NPTEL", "online course (video)", 12, "weeks",
  "https://onlinecourses.nptel.ac.in/noc25_me78/preview",
  "Prof. S. R. Kale", "IIT Delhi",
  "Basic engineering thermodynamics. The provider states 12 weeks, 3 credit points, and an Undergraduate/Postgraduate level.",
  [("SK-THERMO","intro"),("SK-LAWS","working"),("SK-PROPS","working")],
  "page_read", "provider states 3 credit points and UG/PG level"),

 # ---- NPTEL, listing_only ------------------------------------------------------
 ("RES-NPT-010", "Basics of Mechanical Engineering - 3", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc25_me168/preview", "", "",
  "", [("SK-MECH","intro"),("SK-THERMO","intro")], "listing_only", ""),
 ("RES-NPT-011", "Fundamentals of Heat Transfer", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/e-learning/preview/noc25_me171", "", "",
  "", [("SK-HEAT","intro"),("SK-COND","working")], "listing_only", ""),
 ("RES-NPT-012", "Thermal Engineering: Basic and Applied", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc25_me77/preview", "", "",
  "", [("SK-CYCLES","working"),("SK-THERMO","working")], "listing_only", ""),
 ("RES-NPT-013", "Computational Fluid Dynamics and Heat Transfer", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc22_me101/preview", "", "",
  "", [("SK-CFD","advanced"),("SK-CONV","advanced")], "listing_only", ""),
 ("RES-NPT-014", "Conduction and Convection Heat Transfer", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc22_me63/preview", "", "",
  "", [("SK-COND","working"),("SK-CONV","working")], "listing_only", ""),
 ("RES-NPT-015", "Convective Heat Transfer", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/e-learning/preview/noc21_me19", "", "",
  "", [("SK-CONV","advanced")], "listing_only", ""),
 ("RES-NPT-016", "Vibrations of Structures", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc21_me42/preview", "", "",
  "", [("SK-VIB","advanced")], "listing_only", ""),
 ("RES-NPT-017", "Introduction to Mechanical Vibration", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc22_me76/preview", "", "",
  "", [("SK-VIB","intro")], "listing_only", ""),
 ("RES-NPT-018", "Fundamentals of Manufacturing Processes (online)", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc25_me119/preview", "", "",
  "", [("SK-CASTING","working"),("SK-MACHINING","working")], "listing_only", ""),
 ("RES-NPT-019", "Theory of Production Processes", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc23_me126/preview", "", "",
  "", [("SK-MACHINING","working"),("SK-FORMING","working")], "listing_only", ""),
 ("RES-NPT-020", "Manufacturing Process Technology I & II", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc26_me47/preview", "", "",
  "", [("SK-MFG","working")], "listing_only", ""),
 ("RES-NPT-021", "Manufacturing Processes - Casting and Joining", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/e-learning/preview/noc26_me118", "", "",
  "", [("SK-CASTING","working"),("SK-JOINING","working")], "listing_only", ""),
 ("RES-NPT-022", "Introduction to Materials Science and Engineering (online)", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc25_mm17/preview", "", "",
  "", [("SK-MATSCI","intro")], "listing_only", ""),
 ("RES-NPT-023", "Phase Transformation in Materials", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc25_me61/preview", "", "",
  "", [("SK-PHASE","advanced")], "listing_only", ""),
 ("RES-NPT-024", "Materials Science and Engineering", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc24_mm12/preview", "", "",
  "", [("SK-MATSCI","working")], "listing_only", ""),
 ("RES-NPT-025", "Dynamic Behaviour of Materials", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc22_me115/preview", "", "",
  "", [("SK-MECHPROP","advanced")], "listing_only", ""),
 ("RES-NPT-026", "Applied Thermodynamics (online)", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc21_me119/preview", "", "",
  "", [("SK-CYCLES","working")], "listing_only", ""),
 ("RES-NPT-027", "Robotics", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc21_me76/preview", "", "",
  "", [("SK-MECHATRON","working")], "listing_only", ""),
 ("RES-NPT-028", "Mechanical Measurement Systems", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc20_me57/preview", "", "",
  "", [("SK-METROLOGY","working")], "listing_only", ""),
 ("RES-NPT-029", "Robotics and Control: Theory and Practice", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc20_me03/preview", "", "",
  "", [("SK-MECHATRON","advanced"),("SK-CONTROL","working")], "listing_only", ""),
 ("RES-NPT-030", "Microrobotics", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc25_me177/preview", "", "",
  "", [("SK-MECHATRON","advanced")], "listing_only", ""),
 ("RES-NPT-031", "Measurement and Instrumentation", "NPTEL", "online course", None, "",
  "https://onlinecourses.nptel.ac.in/noc26_ee01/preview", "", "",
  "", [("SK-METROLOGY","working")], "listing_only",
  "listed under Electrical Engineering; included for the metrology skill it supports"),
 ("RES-NPT-032", "NOC: Automation in Manufacturing", "NPTEL", "course archive", None, "",
  "https://archive.nptel.ac.in/courses/112/103/112103293/", "", "",
  "", [("SK-AUTOMATION","working")], "listing_only", ""),
 ("RES-NPT-033", "Design of Machine Elements I (course archive)", "NPTEL", "course archive", None, "",
  "https://archive.nptel.ac.in/courses/112/105/112105124/", "", "IIT Kharagpur",
  "", [("SK-MACHDESIGN","working")], "listing_only", ""),
 ("RES-NPT-034", "Advanced Manufacturing Processes", "NPTEL", "syllabus PDF", None, "",
  "https://archive.nptel.ac.in/content/syllabus_pdf/112107077.pdf", "", "",
  "", [("SK-MFG","advanced"),("SK-ADDITIVE","intro")], "listing_only", ""),
 ("RES-NPT-035", "Computational Heat Transfer and Fluid Flow", "NPTEL", "syllabus PDF", None, "",
  "https://archive.nptel.ac.in/content/syllabus_pdf/112108091.pdf", "", "",
  "", [("SK-CFD","advanced"),("SK-NUMER","working")], "listing_only", ""),
 ("RES-NPT-036", "Basics of Mechanical Engineering - 1", "NPTEL", "syllabus PDF", None, "",
  "https://archive.nptel.ac.in/content/syllabus_pdf/112104526.pdf", "", "",
  "", [("SK-MECH","intro")], "listing_only", ""),

 # ---- MIT OpenCourseWare, listing_only unless noted ---------------------------
 ("RES-OCW-001", "2.51 Intermediate Heat and Mass Transfer", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-51-intermediate-heat-and-mass-transfer-fall-2008/", "", "MIT",
  "", [("SK-HEAT","advanced"),("SK-MASST","working")], "listing_only", ""),
 ("RES-OCW-002", "2.051 Introduction to Heat Transfer", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-051-introduction-to-heat-transfer-fall-2015/", "", "MIT",
  "", [("SK-HEAT","intro"),("SK-COND","working")], "listing_only", ""),
 ("RES-OCW-003", "2.43 Advanced Thermodynamics", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-43-advanced-thermodynamics-spring-2024/", "", "MIT",
  "", [("SK-THERMO","advanced")], "listing_only", ""),
 ("RES-OCW-004", "2.26 Compressible Fluid Dynamics", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-26-compressible-fluid-dynamics-spring-2004/", "", "MIT",
  "", [("SK-COMPR","advanced")], "listing_only", ""),
 ("RES-OCW-005", "2.61 Internal Combustion Engines", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-61-internal-combustion-engines-spring-2017/", "", "MIT",
  "", [("SK-COMBUST","advanced"),("SK-CYCLES","working")], "listing_only", ""),
 ("RES-OCW-006", "2.003SC Engineering Dynamics", "MIT OpenCourseWare", "course site with video", None, "",
  "https://ocw.mit.edu/courses/2-003sc-engineering-dynamics-fall-2011/", "", "MIT",
  "", [("SK-RBD","working"),("SK-VIB","intro")], "listing_only", ""),
 ("RES-OCW-007", "2.003J Dynamics and Vibration", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-003j-dynamics-and-vibration-13-013j-fall-2002/", "", "MIT",
  "", [("SK-RBD","working"),("SK-VIB","working")], "listing_only", ""),
 ("RES-OCW-008", "1.050 Solid Mechanics", "MIT OpenCourseWare", "course site with lecture notes", None, "",
  "https://ocw.mit.edu/courses/1-050-solid-mechanics-fall-2004/", "", "MIT",
  "", [("SK-STRESS","working"),("SK-BEAM","working"),("SK-STATICS","working")], "listing_only", ""),
 ("RES-OCW-009", "2.002 Mechanics and Materials II", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-002-mechanics-and-materials-ii-spring-2004/", "", "MIT",
  "", [("SK-MECHPROP","working"),("SK-FAIL","working")], "listing_only", ""),
 ("RES-OCW-010", "2.007 Design and Manufacturing I", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-007-design-and-manufacturing-i-spring-2009/", "", "MIT",
  "", [("SK-DESIGNPROC","working"),("SK-CAD","working")], "listing_only", ""),
 ("RES-OCW-011", "2.008 Design and Manufacturing II", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-008-design-and-manufacturing-ii-spring-2025/", "", "MIT",
  "", [("SK-MFG","working"),("SK-DESIGNPROC","working")], "listing_only", ""),
 ("RES-OCW-012", "2.72 Elements of Mechanical Design", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-72-elements-of-mechanical-design-spring-2009/", "", "MIT",
  "", [("SK-MACHDESIGN","advanced")], "listing_only", ""),
 ("RES-OCW-013", "2.04A Systems and Controls", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-04a-systems-and-controls-spring-2013/", "", "MIT",
  "", [("SK-CONTROL","intro")], "listing_only", ""),
 ("RES-OCW-014", "2.004 Systems, Modeling, and Control II", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-004-systems-modeling-and-control-ii-fall-2007/", "", "MIT",
  "", [("SK-CONTROL","working")], "listing_only", ""),
 ("RES-OCW-015", "2.14 Analysis and Design of Feedback Control Systems", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-14-analysis-and-design-of-feedback-control-systems-spring-2014/", "", "MIT",
  "", [("SK-CONTROL","advanced")], "listing_only", ""),
 ("RES-OCW-016", "2.737 Mechatronics", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-737-mechatronics-fall-2014/", "", "MIT",
  "", [("SK-MECHATRON","advanced")], "listing_only", ""),
 ("RES-OCW-017", "2.000 How and Why Machines Work", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-000-how-and-why-machines-work-spring-2002/", "", "MIT",
  "", [("SK-KINEM","intro"),("SK-CAD","intro")], "listing_only", ""),
 ("RES-OCW-018", "2.017J Design of Electromechanical Robotic Systems", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-017j-design-of-electromechanical-robotic-systems-fall-2009/pages/syllabus/", "", "MIT",
  "", [("SK-MECHATRON","working"),("SK-DESIGNPROC","working")], "listing_only",
  "URL points to the syllabus page, which is what retrieval returned"),
 ("RES-OCW-019", "2.141 Modeling and Simulation of Dynamic Systems", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/2-141-modeling-and-simulation-of-dynamic-systems-fall-2006/pages/calendar/", "", "MIT",
  "", [("SK-RBD","advanced"),("SK-NUMER","working")], "listing_only",
  "URL points to the calendar page, which is what retrieval returned"),
 ("RES-OCW-020", "16.810 Engineering Design and Rapid Prototyping", "MIT OpenCourseWare", "course site", None, "",
  "https://ocw.mit.edu/courses/16-810-engineering-design-and-rapid-prototyping-january-iap-2005/", "", "MIT",
  "", [("SK-DESIGNPROC","working"),("SK-FEM","intro"),("SK-CAD","working")], "listing_only", ""),
]

RES_HEADER = ["id","title","provider","licence_name","licence_version","licence_url",
              "licence_verified_on","fmt","duration_value","duration_unit","url",
              "instructor","host_institute","description","source_url","retrieved_on",
              "source_type","source_note","verification_status","verified_on","verified_by"]
LINK_HEADER = ["resource","skill","level","source_url","retrieved_on","source_type",
               "source_note","verification_status","verified_on","verified_by"]


def main():
    base = os.path.join("data", "raw", "resources")
    os.makedirs(base, exist_ok=True)
    res_rows, link_rows = [], []
    for (rid, title, prov, fmt, dv, du, url, instr, inst, desc, skills, tier, extra) in R:
        lic = OCW if prov == "MIT OpenCourseWare" else NPTEL
        note = f"tier={tier}; licence checked at {LIC_SRC[prov]}"
        if prov == "NPTEL":
            note += "; provider states CC BY-NC-SA with no version, so licence_version is blank"
        if tier == "listing_only":
            note += "; title/URL from provider listing, resource page not opened, duration left null"
        if extra:
            note += f"; {extra}"
        res_rows.append({
            "id": rid, "title": title, "provider": prov,
            "licence_name": lic[0], "licence_version": lic[1], "licence_url": lic[2],
            "licence_verified_on": RETRIEVED_ON, "fmt": fmt,
            "duration_value": "" if dv is None else dv, "duration_unit": du,
            "url": url, "instructor": instr, "host_institute": inst, "description": desc,
            "source_url": url, "retrieved_on": RETRIEVED_ON, "source_type": "open-licence",
            "source_note": note, "verification_status": "unverified",
            "verified_on": "", "verified_by": ""})
        for skill, level in skills:
            link_rows.append({
                "resource": rid, "skill": skill, "level": level,
                "source_url": url, "retrieved_on": RETRIEVED_ON, "source_type": "manual",
                "source_note": "mapping is the dataset author's judgement based on the "
                               "resource title and, where read, its stated outline",
                "verification_status": "unverified", "verified_on": "", "verified_by": ""})

    for path, header, rows in ((os.path.join(base, "resources.csv"), RES_HEADER, res_rows),
                               (os.path.join(base, "resource_skills.csv"), LINK_HEADER, link_rows)):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=header)
            w.writeheader(); w.writerows(rows)
        print(f"wrote {len(rows):4d} rows -> {path}")
    read = sum(1 for r in R if r[11] == "page_read")
    print(f"tiers: page_read={read}, listing_only={len(R)-read}")
    print(f"duration filled: {sum(1 for r in R if r[4] is not None)}/{len(R)}")


if __name__ == "__main__":
    main()
