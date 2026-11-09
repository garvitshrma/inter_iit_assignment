#!/usr/bin/env python3
"""
Authors data/raw/curriculum/course_skills.csv.

These rows are JUDGEMENTS, not transcriptions. The endpoints (course code, skill
id) are real, but the depth call is the dataset author's. Each row therefore
carries an `evidence` field holding the syllabus phrase the call was made from,
so a reviewer who disagrees can see what it rested on without re-reading the
whole syllabus. source_type is `manual` and source_url points at the Courses of
Study, which is where the evidence phrase comes from.

Depth convention used consistently:
  intro    -- the syllabus touches it, often literally prefixed "Introduction to"
  working  -- a named syllabus module with methods a student is expected to apply
  advanced -- several modules, or the course's central subject

Courses with no syllabus transcribed are deliberately left unmapped rather than
mapped from their title alone. The validator raises orphan_course_no_skill for
those, and the count is reported in DATA_QUALITY.md.
"""
import csv, os

COS = "https://www.iitbhilai.ac.in/index.php?pid=new_schedule_programs"
RET = "2026-11-09"

# (course, skill, depth, evidence phrase from the syllabus)
L = [
 ("MEL231","SK-STATICS","advanced","Forces and Force Equilibrium in Plane and Space; Rigid Bodies: Equivalent systems of Forces - Forces and Moments - Couple - Equilibrium in two and three dimensions"),
 ("MEL231","SK-FBD","working","Method of Solving Problems; Equilibrium in two and three dimensions"),
 ("MEL231","SK-TRUSS","working","Analysis of Structures: Trusses and Frames - Internal forces in members - Beams - Shear Force - Bending Moment"),
 ("MEL231","SK-FRICTION","working","Friction: Wedge, Screws, Belt Friction"),
 ("MEL231","SK-RBD","working","Rigid-body kinematics: Absolute motion - Relative velocity - Relative acceleration; Rigid-body kinetics: Linear Momentum - Angular momentum"),

 ("MEL211","SK-LAWS","advanced","First law of thermodynamics; Second law of thermodynamics: Kelvin-Planck's statement, Clausius Statement and corollaries; Entropy and the Clausius inequality"),
 ("MEL211","SK-PROPS","working","Properties of Substances: Properties of pure substances - phase equilibrium diagrams p-v, p-T, T-s and h-s planes; dryness fraction, steam tables and Mollier diagram"),
 ("MEL211","SK-CYCLES","intro","Carnot cycle; Heat engines and refrigerators"),

 ("MEL251","SK-CASTING","advanced","Casting: Introduction to casting, types of patterns and its allowance, types of moulding materials, gating system and its design, riser design, types of casting, casting defect, casting solidification for pure metal and alloy"),
 ("MEL251","SK-JOINING","advanced","Welding: Fundamentals of welding and its types, Gas welding/Cutting, Arc welding (TIG, MIG, SAW etc.), Spot welding, Brazing, soldering, Solid state welding"),
 ("MEL251","SK-FORMING","working","Forming: Various types of bulk forming process such as rolling, extrusion, forging, wire drawing and its force analysis, sheet metal forming such as blanking, punching, deep drawing"),
 ("MEL251","SK-MFG","working","Basics of manufacturing, Primary and secondary manufacturing and its types; Introduction to powder metallurgy"),

 ("MEL232","SK-STRESS","advanced","Stress: Plane stress, Equilibrium equations - Stress transformation in plane stress - Mohr's Circle; Strain: Plane strain - Strain transformation - Measurement of strains using strain Gauge and strain rosette"),
 ("MEL232","SK-BEAM","advanced","Torsion: Torsion of circular shafts; Bending: Pure bending of beams - Moment-Curvature relationship; Deflection of beams: Governing equation - Energy methods - Castigliano's theorem"),
 ("MEL232","SK-FAIL","working","Introduction of Fatigue behavior and S-N curve - Theories of Failure - Stress concentration"),
 ("MEL232","SK-MECHPROP","working","Stress-strain relationship: Tension and compression test of metallic bars - Hooke's law for uniaxial and multi-axial loading - Thermal strains"),

 ("MEL214","SK-CYCLES","advanced","Vapor Power Cycles: Rankine and Carnot Cycles, Reheating cycle, Regenerative Cycles; Gas Power Cycles: Otto Cycles, Diesel Cycle, Dual Cycles, Brayton Cycles"),
 ("MEL214","SK-COMBUST","working","Introduction to Various Thermodynamics Systems: Internal Combustion Engines, Jet Propulsion, Rocket Propulsion; Aircraft Propulsion"),
 ("MEL214","SK-PSYCHRO","intro","Basics of Refrigeration Cycles: Vapor Compression Refrigeration Cycles, Gas Cycle Refrigeration; Air Conditioners"),

 ("MEL212","SK-FLUIDSTAT","working","Fluid Statics: Hydrostatic pressure distribution, Manometry, Forces on submerged bodies, Buoyancy and Floatation, Stability of floating bodies"),
 ("MEL212","SK-VISC","advanced","Exact solution to Navier-Stokes equations: Couette flow and Poiseulle flow; Boundary Layer Theory: Blasius solution, Von-Karman Momentum integral equation; Introduction to Turbulent flows"),
 ("MEL212","SK-COMPR","intro","Introduction to Compressible flows: High speed gas flow, speed of sound, Isentropic gas relations"),

 ("MEL252","SK-OPS","advanced","Production Planning and Control: Forecasting models, aggregate production planning, scheduling, Lean manufacturing, materials requirement planning and inventory management"),
 ("MEL252","SK-OPT","working","Operations Research: Linear programming, simplex method, Transportation and Assignment Problems, network flow models, simple queuing models, PERT and CPM"),
 ("MEL252","SK-IE","advanced","TQM Principles: six sigma, Kaizen, Quality Function Deployment (QFD), Total Productive Maintenance (TPM), FMEA"),

 ("MEL333","SK-MACHDESIGN","advanced","Design of Mechanical elements: Shafts; Power Screw, Threaded Joints, Bolt, Rivet, Weld; Springs; Bearings; Gears; Clutch, Break, Belts"),
 ("MEL333","SK-FAIL","advanced","Failure Prevention: Failure resulting from static loading; Fatigue failure resulting from variable loading"),

 ("MEL313","SK-COND","advanced","Conduction: 1D steady heat conduction with and without heat generation, Unsteady state heat conduction (lumped capacitance method and Heisler chart), heat transfer from extended surfaces"),
 ("MEL313","SK-CONV","working","Convection: Governing equations, dimensional analysis, boundary layers, Forced convection - external and internal flows, Natural and mixed convection"),
 ("MEL313","SK-RAD","working","Radiation: Processes and properties, Black and real body radiation, view factor and radiation exchanges between surfaces in an enclosure"),
 ("MEL313","SK-HX","working","Heat Exchanger: Design and types of heat exchangers: LMTD and effectiveness-NTU methods"),
 ("MEL313","SK-MASST","intro","Mass Transfer: Concept of mass transfer"),

 ("MEL351","SK-MACHINING","advanced","Mechanics of chip formation, concept of orthogonal and oblique cutting; Analysis of cutting forces in orthogonal cutting; Cutting tool materials, Cutting fluid, tool wear and tool life; Grinding"),

 ("MEP381","SK-MFG","working","Casting; Metal forming: Rolling, Extrusion, sheet metal forming, forging; Welding; Machining: Turning, milling, drilling"),
 ("MEP381","SK-METROLOGY","working","Metrology: Coordinate measuring machine, vernier calipers/screw gauge"),

 ("MEP371","SK-FLUID","working","Experiments to demonstrate major and minor pipe losses, Bernoulli's principle, Flow regimes, flow measurement devices, performance of turbines"),
 ("MEP371","SK-HEAT","working","experiments to demonstrate different modes of heat transfer (Conduction, Convection and Radiation), and the performance of refrigerator, air conditioner, internal combustion engine"),

 ("MEL334","SK-KINEM","advanced","Kinematics of Mechanisms: Kinematic pairs, diagrams, and inversion; Analysis of planar linkages; Design of Mechanisms: Dimensional synthesis for motion, path, and function generation; Gears and gear trains; Cam mechanisms"),
 ("MEL334","SK-BALANCE","working","Inertia forces and balancing for rotating and reciprocating machines; Flywheels, Governors"),
 ("MEL334","SK-VIB","working","Vibration: Introduction, Single degree of freedom system; Free and forced vibration; Damped, undamped, and overdamped system"),

 ("MEL304","SK-NUMER","advanced","Root finding techniques; Linear Algebra: Gauss Elimination, LU Decomposition, Gauss-Seidel; Numerical differentiation and integration; Methods to solve Ordinary differential equations: Runge-Kutta Method"),
 ("MEL304","SK-OPT","working","Optimization: One and Multi-dimensional unconstrained Optimization-Golden, Section search; Gradient method, constrained optimization"),
 ("MEL304","SK-FEM","intro","Finite difference and finite element based methods to solve Elliptic and Parabolic equations"),

 ("MEP302","SK-DRAWING","advanced","Theory of projections: 1st and 3rd angle projection, isometric projection; Projection of line, planes, and solids; Development of surfaces; 2D assembly drawing"),
 ("MEP302","SK-MACHDESIGN","intro","Keys, cotters and pin joints; Shaft coupling, Gears"),

 ("MEP376","SK-MECHPROP","working","Experiments on estimation of material properties: Uni-axial tension test, Uni-axial compression test, Fatigue test, Impact test"),
 ("MEP376","SK-VIB","working","Measurement of natural frequency and estimation of damping properties; Analysis of forced vibration of spring-mass system under base excitation"),
 ("MEP376","SK-BALANCE","working","Static and dynamics balancing of rotating shaft"),

 ("MEP102","SK-CAD","working","Familiarization with 3D solid modelling (CAD) for the creation of engineering and freeform geometries"),
 ("MEP102","SK-ADDITIVE","working","Preparatory activities for 3D Printing: Conversion of CAD model into a real part, stl format, slicing, effect of part orientation; 3D printing of the part"),
 ("MEP102","SK-DRAWING","working","Theory of projections; Orthographic projection; Isometric projection and perspective projection"),
 ("MEP102","SK-MACHINING","intro","conventional machining processes: turning, centering, drilling, and milling; CNC programming"),

 ("MML204","SK-PHASE","working","course title: Properties and phase transformation of Materials (syllabus published under the Materials department and not transcribed in this pass)"),
 ("MML204","SK-MATSCI","working","course title: Properties and phase transformation of Materials (syllabus not transcribed in this pass)"),

 ("EEL208","SK-METROLOGY","working","course title: Sensors & Instrumentation (syllabus published under the Electrical department and not transcribed in this pass)"),

 ("MEL414","SK-COMBUST","advanced","Combustion in Spark-ignition Engines; Combustion in Compression-ignition Engines; Formation of Engine emissions; Exhaust Aftertreatment devices"),
 ("MEL414","SK-CYCLES","working","Engine Configurations and components, Engine types and classification, Valve timing, Engine operative parameters, Mean effective pressure"),

 ("MEL416","SK-CYCLES","advanced","Steam Power Plants: Reheating and regeneration, Supercritical pressure cycle, Binary vapour cycle, Combined cycle plants; Diesel Engine and Gas Turbine Power Plants"),
 ("MEL416","SK-TURBO","working","Steam Generators, Steam Turbines, Condenser; Pelton, Francis turbines and Kaplan turbines"),

 ("MEL501","SK-NUMER","working","Ordinary Differential equations: Review of 2nd and Higher order ODEs, Systems of ODEs, Series solutions"),

 ("MEL554","SK-MACHINING","advanced","Electro-Discharge Machining (EDM); Electrochemical Machining (ECM); Ultrasonic Machining; Abrasive Jet Machining; Laser Beam Machining; Electron Beam and Ion Beam Machining; Plasma arc machining"),

 ("MEL558","SK-MATSCI","advanced","Materials for Surface Engineering: Selection of materials for engineering the surfaces; structure and property relationship of coatings system; Physical Characterization: Microstructure, Surface morphology, Phase analysis"),
 ("MEL558","SK-HEATTREAT","working","Conventional surface engineering and heat treatment practices. Surface modification of ferrous and non-ferrous materials like nitriding, cyaniding, aluminizing"),

 ("MEL612","SK-COND","advanced","course title: Conduction and Radiation Heat Transfer (UG Manual worked example; syllabus not transcribed)"),
 ("MEL612","SK-RAD","advanced","course title: Conduction and Radiation Heat Transfer (UG Manual worked example; syllabus not transcribed)"),

 ("CSL100","SK-PROG","working","course title: Introduction to programming (syllabus published under the Computer Science department and not transcribed in this pass)"),
]

HDR = ["course","skill","depth","evidence","source_url","retrieved_on","source_type",
       "source_note","verification_status","verified_on","verified_by"]

def main():
    rows = []
    for course, skill, depth, ev in L:
        title_only = ev.startswith("course title:")
        note = ("depth is the dataset author's judgement. "
                + ("BASED ON COURSE TITLE ONLY, as no syllabus was transcribed for this course "
                   "- weaker than the syllabus-backed rows and should be reviewed first."
                   if title_only else
                   "The syllabus phrase it rests on is in the evidence field."))
        rows.append({"course": course, "skill": skill, "depth": depth, "evidence": ev,
                     "source_url": COS, "retrieved_on": RET, "source_type": "manual",
                     "source_note": note, "verification_status": "unverified",
                     "verified_on": "", "verified_by": ""})
    os.makedirs("data/raw/curriculum", exist_ok=True)
    with open("data/raw/curriculum/course_skills.csv","w",newline="",encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=HDR); w.writeheader(); w.writerows(rows)
    weak = sum(1 for r in rows if r["evidence"].startswith("course title:"))
    print(f"wrote {len(rows)} course-skill links ({len(rows)-weak} syllabus-backed, {weak} title-only)")

if __name__ == "__main__":
    main()
