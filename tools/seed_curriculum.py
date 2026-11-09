#!/usr/bin/env python3
"""
Authors the IIT Bhilai B.Tech Mechanical Engineering curriculum and academic
rules into data/raw/, from the two official PDFs in data/raw/.

MANUAL ENTRY, DISCLOSED. The institute's robots.txt disallows automated
retrieval of iitbhilai.ac.in, so the PDFs were downloaded by a human in a
browser and the records below were transcribed from them. Every value is what
the document prints. Where the document is wrong or self-contradictory, the
value is transcribed AS PRINTED and the repair goes in corrections.csv, so the
defect stays visible. Those defects are listed at the bottom of this file.

Sources:
  Courses of Study (Oct 2026) -- data/raw/curriculum/Courses_Of_Study.pdf
    https://www.iitbhilai.ac.in/index.php?pid=new_schedule_programs
  UG Manual                   -- data/raw/rules/UG_Manual.pdf
    https://www.iitbhilai.ac.in/index.php?pid=ug_manual
"""
import csv, os

RET = "2026-11-09"
COS_URL = "https://www.iitbhilai.ac.in/index.php?pid=new_schedule_programs"
UGM_URL = "https://www.iitbhilai.ac.in/index.php?pid=ug_manual"
PROG = "B.Tech Mechanical Engineering"

# ============================ COURSES ======================================
# code, title, dept, L-T-P-C, semester, type, mode, objectives, syllabus, overlap, note
C = []

def add(code, title, dept, ltpc, sem, ctype, mode, syl="", overlap="", note="", obj=""):
    C.append(dict(code=code, title=title, dept=dept, ltpc=ltpc, sem=sem, ctype=ctype,
                  mode=mode, syllabus=syl, overlap=overlap, note=note, obj=obj))

# ---- Institute core (IC). The Courses of Study lists these in the Mechanical
# ---- programme structure but prints their syllabi under their owning
# ---- departments, which were out of scope for this programme-depth pass.
IC_NOTE = ("transcribed from the BTech Mechanical Engineering programme structure table, "
           "Courses of Study p.32; syllabus not transcribed (published under the owning "
           "department, outside this programme-depth pass)")
add("CSL100","Introduction to programming","Computer Science and Engineering","2-1-3-4.5",1,"institute-core","lecture-lab",note=IC_NOTE)
add("MAL100","Mathematics-I","Mathematics","3-1-0-4",1,"institute-core","lecture-tutorial",note=IC_NOTE)
add("CYL100","Applied Chemistry","Chemistry","3-0-0-3",1,"institute-core","lecture",note=IC_NOTE)
add("PHL101","Physics for Engineers","Physics","3-1-0-4",1,"institute-core","lecture-tutorial",note=IC_NOTE)
add("CYL101","Environmental Science","Chemistry","1-0-0-1",1,"institute-core","lecture",note=IC_NOTE)
add("CYP102","Chemistry lab","Chemistry","0-0-3-1.5",1,"institute-core","lab",
    note=IC_NOTE+"; paired alternation: a student takes one of CYP102/PHP102 in semester I and the other in semester II")
add("PHP102","Physics lab","Physics","0-0-3-1.5",2,"institute-core","lab",
    note=IC_NOTE+"; paired alternation: a student takes one of CYP102/PHP102 in semester I and the other in semester II")
add("MEP102","Digital fabrication","Mechanical Engineering","1-0.5-3-3",2,"institute-core","lecture-lab",
    syl="Theory of projections; Orthographic projection; Isometric projection and perspective projection; Familiarization with 3D solid modelling (CAD) for the creation of engineering and freeform geometries; 3D Scanning using CMM and laser scanners and their applications and Preparatory activities for 3D Printing: Conversion of CAD model into a real part, stl format ant its importance, slicing, effect of part orientation; 3D printing of the part: Introduction to additive manufacturing process; conventional machining processes: turning, centering, drilling, and milling; CNC programming, Familiarization with machining processes using tabletop reconfigurable CNC machines; Familiarization with Casting, Welding, and molding and its inspection; Laser-based manufacturing processes (Demonstration of Laser cutting machine); Introduction to the concept of Digital manufacturing and industry 4.0",
    note="syllabus transcribed from Courses of Study course-description section")
add("EEL101","Basic Electrical Engineering","Electrical Engineering","3-0-2-4",2,"institute-core","lecture-lab",note=IC_NOTE)
add("MAL101","Mathematics-II","Mathematics","3-1-0-4",2,"institute-core","lecture-tutorial",note=IC_NOTE)
add("ECL101","Basic Electronics Engineering","Electrical Engineering","3-0-2-4",2,"institute-core","lecture-lab",note=IC_NOTE)
add("BML101","Biology for Engineers","Bioscience and Biomedical Engineering","3-0-0-3",2,"institute-core","lecture",note=IC_NOTE)
add("LAL100","Introduction to Communication Skills","Liberal Arts","1-1-0-2",3,"institute-core","lecture-tutorial",note=IC_NOTE)
add("LAL101","Introduction to Finance","Liberal Arts","1-0-0-1",4,"institute-core","lecture",note=IC_NOTE)

# ---- Program linked (PL)
add("MML204","Properties and phase transformation of Materials","Materials Science and Metallurgical Engineering","3-0-0-3",3,"core","lecture",
    note="transcribed from the Mechanical programme structure table (Program linked courses), Courses of Study p.32")
add("EEL208","Sensors & Instrumentation","Electrical Engineering","3-0-0-3",6,"core","lecture",
    note="transcribed from the Mechanical programme structure table (Program linked courses), Courses of Study p.32")

# ---- Program core (PC). Syllabi transcribed verbatim from the course-description section.
add("MEL231","Engineering Mechanics","Mechanical Engineering","2-1-0-3",3,"core","lecture-tutorial",
    syl="Introduction: Mechanics - Method of Solving Problems - Forces and Force Equilibrium in Plane and Space; Rigid Bodies: Equivalent systems of Forces - Forces and Moments - Couple - Equilibrium in two and three dimensions; Distributed Forces: Center of Gravity and Centroids of Planes and Volumes - Moments of Inertia of Area, Parallel-axis Theorem; Analysis of Structures: Trusses and Frames - Internal forces in members - Beams - Shear Force - Bending Moment; Friction: Wedge, Screws, Belt Friction; Method of Virtual Work: Principle of Virtual Work and its application to solve problems of mechanics; Rigid-body kinematics: Absolute motion - Relative velocity - Relative acceleration - Rotation relative to rotating axes; Rigid-body kinetics: Linear Momentum - Angular momentum - Kinetic energy - Work and energy - Impulse and momentum; Rigid body in three-dimensions: Kinematics - Kinetics - Gyroscopes.")
add("MEL211","Thermodynamics","Mechanical Engineering","2-1-0-3",3,"core","lecture-tutorial",overlap="MML201 (15-20%); CYL504 (15-20%)",
    syl="Introductory concepts and definitions: Macroscopic and microscopic point of view, system, surroundings, boundary, thermodynamics properties, thermodynamics state and equilibrium, steady state, work interaction, various forms of work; First law of thermodynamics: Quasi-static and reversible processes; Heat interaction; Adiabatic process; Zeroth law of thermodynamics, temperature, Celsius scale of temperature, ideal gas scales of temperature, properties of fluids, internal energy, enthalpy, Carnot cycle; First law analysis for a control volume/open system, steady-state and transient processes with engineering applications; Second law of thermodynamics: Kelvin-Planck's statement, Clausius Statement and corollaries, Heat engines and refrigerators, absolute temperature scale, Second law analysis for a control volume/open system; Entropy and the Clausius inequality: Second law in terms of entropy, adiabatic-reversible-isentropic processes, entropy generation, the Gibbs equation, entropy for ideal gases, entropy change for reversible and irreversible processes, concepts of availability and exergy analysis for closed and open systems; Properties of Substances: Properties of pure substances - phase equilibrium diagrams p-v, p-T, T-s and h-s planes; dryness fraction, steam tables and Mollier diagram; Thermodynamics property relations: Maxwells relations, TdS relations, ratio of heat capacities.")
add("MEL251","Casting, Forming and Welding","Mechanical Engineering","3-0-0-3",3,"core","lecture",
    syl="Basics of manufacturing, Primary and secondary manufacturing and its types, brief overview of metals; Casting: Introduction to casting, types of patterns and its allowance, types of moulding materials, gating system and its design, riser design, types of casting such as ingot/continuous and shape casting (investment casting, die casting, sand casting, centrifugal casting etc.), casting defect, casting solidification for pure metal and alloy; Welding: Fundamentals of welding and its types, Gas welding/Cutting, Arc welding (TIG, MIG, SAW etc.), Arc characteristics, modes of metal transfer, types of power source and its characteristics, Spot welding, Brazing, soldering, Solid state welding; Forming: Stress-strain curve, Yield function, Various types of bulk forming process such as rolling, extrusion, forging, wire drawing and its force analysis, sheet metal forming such as blanking, punching, deep drawing etc. Forming defects; Introduction to powder metallurgy: Basic definition, process, application.",
    note="programme structure table prints the title as 'Casting, Forming & Welding'; the course-description section prints 'Casting, Forming and Welding'. The description-section spelling is used.")
add("MEL232","Mechanics of Solids","Mechanical Engineering","2-1-0-3",4,"core","lecture-tutorial",
    syl="Introduction: Deformable bodies - Analysis of deformable bodies - Solution of some statically indeterminate problems; Stress: Introduction to stress, Plane stress, Equilibrium equations - Stress transformation in plane stress - Mohr's Circle - Thin cylinders; Strain: Introduction to deformation and strain - Plane strain - Strain transformation - Measurement of strains using strain Gauge and strain rosette; Stress-strain relationship: Tension and compression test of metallic bars - Hooke's law for uniaxial and multi-axial loading - Thermal strains - Equations of elasticity, Introduction of Fatigue behavior and S-N curve - Theories of Failure - Stress concentration; Torsion: Torsion of circular shafts - Torsion of elastic hollow shaft - Introduction to torsion of rectangular shafts - Torsion of thin-walled shafts; Bending: Pure bending of beams - Moment-Curvature relationship - Stress-strain relation in bending - Elastic beams with transverse forces - Transverse shear stresses - Built-up beams - Composite beams; Deflection of beams: Governing equation - Deflection using the moment of integration - Method of superposition - Energy methods - Castigliano's theorem; Buckling of Columns: Stability of equilibrium - Elastic instability of flexible columns - Critical loads for different boundary conditions of columns.")
add("MEL214","Applied Thermal Engineering","Mechanical Engineering","2-1-0-3",4,"core","lecture-tutorial",overlap="MEL211 (5%)",
    syl="Introduction to Various Thermodynamics Systems: Simple Steam Power Plant, Gas Turbines, Internal Combustion Engines, Domestic Refrigerators, Air Conditioners, Jet Propulsion, Rocket Propulsion, Gas Compressors; Vapor Power Cycles: Actual vapor power cycle processes, Rankine and Carnot Cycles, Mean temperature of heat addition, Reheating cycle, Regenerative Cycles, Reheat-Regenerative Cycles, Exergy Analysis of Vapor Power Cycles, Binary Vapor Power Cycles; Gas Power Cycles: Carnot cycles, Stirling Cycles, Ericsson Cycles, Air Standard Cycles, Otto Cycles, Diesel Cycle, Dual Cycles, Comparison of Otto, Diesel and Dual Cycles, Lenoir Cycle, Atkinson Cycle, Brayton Cycles, Aircraft Propulsion; Cogeneration and Combined Cycles: Combined gas-steam power Plant, Different arrangements in combined cycles; Basics of Refrigeration Cycles: Reversed Heat Engines Cycles, Vapor Compression Refrigeration Cycles, Gas Cycle Refrigeration; Gas Compressors: Compression Processes, Work of Compression, Reciprocating compressors, Single-Stage Reciprocating Air Compressors, Volumetric Efficiency, Multistage Compression.")
add("MEL212","Fluid Mechanics","Mechanical Engineering","3-1-0-4",4,"core","lecture-tutorial",
    syl="Introduction: Basic ideas of continuum, fluid properties including viscosity, surface tension and vapour pressure; Fluid Statics: Hydrostatic pressure distribution, Manometry, Forces on submerged bodies, Buoyancy and Floatation, Stability of floating bodies, Pressure distribution in rigid body motion; Fluid Kinematics: Lagrangian and Eulerian descriptions, Deformation of fluid element, Strain rates, Vorticity, Flow description using pathline, streamline and streak line; Conservation laws: Reynolds Transport Theorem, Integral form of conservation laws - mass, linear momentum, angular momentum and energy, Differential form of conservation laws, Elementary derivation of Navier-Stokes equations, Exact solution to Navier-Stokes equations: Couette flow and Poiseulle flow etc.; Inviscid flows: Bernoulli equation and applications, overview of various losses; Plane potential flows: Streamfunction-velocity potential, superposition, source, sink, Doublet, flow past a cylinder, circulation, D'Alembert's Paradox; Dimensional analysis: Buckingham Pi theorem, dimensionless groups, similitude laws and scaling, practical applications; Boundary Layer Theory: Definition of boundary layer thickness, momentum thickness and energy thickness, Blasius solution, Von-Karman Momentum integral equation; Introduction to Turbulent flows: Basic definition and characteristics of turbulent flow, Energy Cascade, Mean and Fluctuating Components, Derivations of Reynolds Averaged Navier-Stokes Equations, Turbulent Flow through a Pipe and Channel, Moody Diagram, Hydrodynamic Smooth and Rough Pipe and Example Problems; Introduction to Compressible flows: High speed gas flow, speed of sound, One-dimensional form of the governing equations, Isentropic gas relations, Velocity measurement using a pitot tube at all Mach numbers.",
    note="SOURCE CONFLICT: the programme structure table prints L-T-P-C 3-1-0-4 while the course-description section prints '4 Credits (3-0-1)'. Credits agree at 4; the tutorial/practical split does not. The structure table is used and the conflict is reported in DATA_QUALITY.md.")
add("MEL252","Fundamentals of Industrial Engineering","Mechanical Engineering","3-0-0-3",4,"core","lecture",
    syl="Production Planning and Control: Forecasting models, aggregate production planning, scheduling, Lean manufacturing, Concurrent engineering, materials requirement planning and inventory management; Operations Research: Linear programming, simplex method etc., Transportation and Assignment Problems, network flow models, simple queuing models, PERT and CPM; TQM: Introduction, Historical Review, TQM Principles: six sigma, Kaizen etc., Quality Function Deployment (QFD), Total Productive Maintenance (TPM), FMEA, Quality Systems: Need for ISO 9000 and ISO 14000 - Concept, Requirements and Benefits, Case Studies.")
add("MEL333","Design of Machine Elements","Mechanical Engineering","3-0.5-0-3.5",5,"core","lecture-tutorial",overlap="MEL232 (10%)",
    syl="Basics: Introduction to Mechanical Engineering Design, Engineering Materials - Load and Stress Analysis, Deflection and Stiffness; Failure Prevention: Failure resulting from static loading; Fatigue failure resulting from variable loading; Design of Mechanical elements: Shafts; Power Screw, Threaded Joints, Bolt, Rivet, Weld; Springs; Bearings; Gears; Clutch, Break, Belts.")
add("MEL313","Heat and Mass Transfer","Mechanical Engineering","3-0.5-0-3.5",5,"core","lecture-tutorial",
    syl="Introduction: Rate equation and conservation of energy equations, modes of heat transfer; Conduction: 1D steady heat conduction with and without heat generation, Unsteady state heat conduction (lumped capacitance method and Heisler chart), heat transfer from extended surfaces; Convection: Governing equations, dimensional analysis, boundary layers, Forced convection - external and internal flows, Natural and mixed convection; Heat Exchanger: Design and types of heat exchangers: Analysis of heat exchanger: LMTD and effectiveness-NTU methods; Radiation: Processes and properties, Black and real body radiation, view factor and radiation exchanges between surfaces in an enclosure; Mass Transfer: Concept of mass transfer.")
add("MEL351","Machining and Machine Tools","Mechanical Engineering","3-0-0-3",5,"core","lecture",
    syl="Machining as secondary manufacturing processes, types of machining processes, types of cutting tools, Different output characteristics in machining processes; Concept of directrix and generatrix, types of surfaces generated in machining; Determination of material removal rate and machining time in different machining processes; Cutting tool geometry, concepts of master line; Mechanics of chip formation, concept of orthogonal and oblique cutting; Analysis of cutting forces in orthogonal cutting, experimental measurement of cutting force; Cutting temperature: causes, effects, measurement and control; Cutting tool materials, Cutting fluid, tool wear and tool life, role of geometrical and process parameters and cutting fluid on machinability; Machine tools: Types, mechanisms and work holding devices; Grinding: introduction and types of grinding operations, and specifications of grinding wheels.",
    note="source prints 'Prerequisite(s): NA' for this course, whereas most courses print 'None'. Treated as no prerequisite; vocabulary inconsistency reported in DATA_QUALITY.md.")
add("MEP381","Manufacturing and Metrology Lab","Mechanical Engineering","0-0-3-1.5",5,"core","lab",
    syl="Casting; Metal forming: Rolling, Extrusion, sheet metal forming, forging; Welding: Metal inert gas welding, TIG, gas welding, Spot welding, friction stir welding; Machining: Turning, milling, drilling; Metrology: Coordinate measuring machine, vernier calipers/screw gauge.")
add("MEP371","Thermal and Fluid Engineering Lab","Mechanical Engineering","0-0-3-1.5",5,"core","lab",
    syl="Experiments to demonstrate major and minor pipe losses, Bernoulli's principle, Flow regimes, flow measurement devices, performance of turbines, hydraulic/pneumatic systems will be covered under fluid mechanics and machine domain; Whereas experiments to demonstrate different modes of heat transfer (Conduction, Convection and Radiation), and the performance of refrigerator, air conditioner, internal combustion engine will be covered under the domain of thermal engineering.")
add("MEL334","Theory of Mechanisms and Machines","Mechanical Engineering","3-0.5-0-3.5",6,"core","lecture-tutorial",
    syl="Kinematics of Mechanisms: Kinematic pairs, diagrams, and inversion; Mobility and range of movement; Displacement, velocity, and acceleration; Analysis of planar linkages; Design of Mechanisms: Dimensional synthesis for motion, path, and function generation; Gears and gear trains; Cam mechanisms, Cam profile synthesis; Dynamics of Machines: Dynamic force analysis; Inertia forces and balancing for rotating and reciprocating machines; Flywheels, Governors; Vibration: Introduction, Single degree of freedom system; Free and forced vibration; Damped, undamped, and overdamped system.")
add("MEL304","Applied Numerical Methods","Mechanical Engineering","3-0-1-3.5",6,"core","lecture-lab",overlap="MAL101 (10 %)",
    syl="Mathematical modelling of some simple engineering problems. Error Analysis: Approximations and round-off errors, Taylor series, truncation errors, error propagations; Root finding techniques: Bracketing Methods-Bisection, False-Position methods; Open Methods-Fixed point, Secant and Newton-Raphson method, Roots of polynomials, rate of convergence.; Linear Algebra: Gauss Elimination, LU Decomposition, Gauss-Seidel.; Optimization: One and Multi-dimensional unconstrained Optimization-Golden, Section search; Optimization: Gradient method, constrained optimization; Curve fitting: Least-squares regression-linear, and polynomial regression; Curve fitting: Interpolation-Lagrange interpolating polynomial, Spline interpolation; Numerical differentiation and integration: Discretization and order to accuracy, Newton-cotes Integration-Trapezoidal, Simpson's rule; Numerical differentiation and integration: Romberg integration; Richardson extrapolation; Methods to solve Ordinary differential equations: Runge-Kutta Method along with its adaptive part, Methods to solve Partial differential equations: Finite difference and finite element based methods to solve Elliptic and Parabolic equations; Introduction to Artificial Neural Network.",
    note="SOURCE CONFLICT: the UG Manual's worked example in section 2.2.6 prints this course as '3.0 Credits (3-0-0)' with 'Pre-requisite(s): Nil', while the Courses of Study prints 3-0-1-3.5 with prerequisites MAL100 and MAL101. The UG Manual instance is illustrative formatting rather than the authoritative catalogue entry, so the Courses of Study values are used. Reported in DATA_QUALITY.md.")
add("MEP302","Engineering and Machine Drawing","Mechanical Engineering","0-0-4-2",6,"core","lab",overlap="MEP102 (5%)",
    syl="Engineering curves; Theory of projections: 1st and 3rd angle projection, isometric projection; Projection of line, planes, and solids; Projection of section of solids; Development of surfaces; Geometric dimensioning and tolerances: Limits, Fits, tolerances (geometric and dimensional), Tolerance stack up analysis for assembly, concept of production drawing; Keys, cotters and pin joints; Shaft coupling, Gears; 2D assembly drawing.")
add("MEP376","Solid Mechanics and Dynamics Lab","Mechanical Engineering","0-0-3-1.5",6,"core","lab",
    syl="Experiments on estimation of material properties: Uni-axial tension test, Uni-axial compression test, Fatigue test, Impact test. Experiments on measurement of stress and strain in structures: Measurement of strain in a cantilever beam using strain gauge and strain amplifier circuit, Measurement of strain for fixed-fixed beam under bending, Measurement of strains under combined bending-torsion loading, Calculation of fringe constant of a material using standard disk under compression test, Estimation of bending stresses in a beam under bending using photoelasticity setup; Experiments on dynamics and vibration of mechanical components/structures: Measurement of natural frequency and estimation of damping properties of different fluids using spring-mass system, Analysis of forced vibration of spring-mass system under base excitation, Measurement of natural frequency for torsional vibration, Static and dynamics balancing of rotating shaft, Design of four-bar mechanism for path/function generation.")
add("UGQ301","Interdisciplinary undergraduate project","Interdisciplinary","0-0-6-3",6,"core","project",
    note="transcribed from the Mechanical programme structure table; the Courses of Study prints no separate description for this project course")

# ---- Non-graded core (NC). The structure grid prints '-' for L-T-P-C.
add("NCN100","Practices for Comprehensive wellbeing","Non-graded core","",1,"non-graded","unknown",
    note="non-graded core; the semester grid prints '-' in place of an L-T-P-C value, so credits are left null. UG Manual 2.2.2(7): non-graded core requirements are earned through formal academic activity and informal co-curricular or extra-curricular activities.")
add("LAN103","Professional Ethics","Liberal Arts","",2,"non-graded","unknown",
    note="non-graded core; the semester grid prints '-' in place of an L-T-P-C value, so credits are left null.")

# ---- Program electives (PE), with syllabi from the course-description section
add("MEL414","Internal Combustion Engines","Mechanical Engineering","2.5-0.5-0-3","","elective","lecture-tutorial",overlap="MEL111 (5%)",
    syl="Introduction: Engine Configurations and components, Engine types and classification, Reciprocating and rotary engines, Valve timing, Thermochemistry of fuel-air mixtures, Engine operative parameters, Torque and power, Efficiencies, Mean effective pressure. Combustion in Spark-ignition Engines: Premixed charge combustion, SI Engine combustion conceptual models, Combustion rate characterization, Thermodynamics analysis of combustion, Flame propagation Phenomenon, Cycle to cycle variation, knocking combustion, Factors affecting Knock. Combustion in Compression-ignition Engines: Fuel injection and spray structure, CI Engine combustion conceptual model, Diesel combustion process characterization, Premixed and mixing controlled combustion, Fuel injection parameters. Engine cooling, lubrication and other systems: Air-cooled Systems, Liquid cooling systems, Function and mechanism of lubrication, Lubrication systems, Exhaust gas recirculation, Variable valve timing. Formation of Engine emissions: Sources of engine emissions, Formation of carbon monoxide, NOx Formation, Unburned hydrocarbon emissions, Soot and particulate formation, Emission Measurement. Exhaust Aftertreatment devices: Basics of catalytic exhaust treatment, Three-way catalytic converter, Diesel oxidation catalyst, Diesel Particulate filter, Regeneration, Gasoline particulate filter, NOx absorber, Selective catalytic converter.",
    note="source prints '3 Credits (2.5-0.5-0)'; credits recorded as 3. Programme electives are not pinned to a semester in the structure grid (semesters VII-VIII are shown as generic PE/OE slots), so semester_offered is null.")
add("MEL416","Power Plant Engineering","Mechanical Engineering","2-1-0-3","","elective","lecture-tutorial",overlap="MEL214 (15%)",
    syl="Economics of Power Generation: Introduction, Power plant economics, Types of power plants. Steam Power Plants: Economics of Power Generation, Reheating and regeneration, Feedwater heaters, Supercritical pressure cycle, Deaerator, Binary vapour cycle, Combined cycle plants, Coal, Coal analysis, Combustion reactions, Energy balance of steam generator. Steam Generators, Steam Turbines, Condenser: Basic types of steam generators, Fire tube and water tube boilers, Ash handling system, Feedwater treatment, Steam turbines, Condenser, Cooling towers. Diesel Engine and Gas Turbine Power Plants: Combustion in a CI engine, Performance characteristics, Supercharging, Layout of a diesel engine power plant, Gas turbine power plant, Components of gas turbine plant, gas turbine fuels, Gas turbine Materials. Nuclear and Hydroelectric Power Plants: Nuclear fusion and fission, Chain reaction, Nuclear fuels, Components of nuclear reactor, Classification of reactors, Nuclear waste and its disposal, Hydroelectric power plant classification, Pelton, Francis and Kaplan turbines. Non-conventional and Renewable Power Generation: Renewable energy sources potential, Solar power plants, Thermal energy, Wind energy, Wind power plant, Waste to power generation, Geothermal energy.",
    note="source prints '3 Credits (2-1-0)'; credits recorded as 3. SOURCE ISSUE: the prerequisite is printed as prose, 'Thermodynamics (MEL211)', whereas UG Manual 2.2.5(i) requires prerequisites to be defined only in terms of course codes. The code MEL211 was extracted; reported in DATA_QUALITY.md.")
add("MEL501","Advanced Engineering Mathematics","Mechanical Engineering","3-0-0-3","","elective","lecture",overlap="MEL304 (30%)",
    syl="Ordinary Differential equations: Review of 2nd and Higher order ODEs, Systems of ODEs, Series solutions.",
    note="source prints '3 Credits (3-0-0)'; credits recorded as 3. Syllabus transcription is partial (the description continues beyond the extracted text) and is marked incomplete in DATA_QUALITY.md. NOTE: the declared 30% overlap with MEL304 exceeds the 25% ceiling in UG Manual 2.2.6, so a Mechanical student who has credited MEL304 is not eligible for this course.")
add("MEL554","Non-Conventional Machining Processes","Mechanical Engineering","3-0-0-3","","elective","lecture",overlap="MEL351 (5%)",
    syl="Introduction to non-conventional machining, classification of non-conventional machining processes. Electro-Discharge Machining (EDM), process mechanism of material removal, parameters affecting EDM and application. Traveling Wire EDM. Electrochemical Machining (ECM), Mechanism of material removal, Tool design, Parameters affecting ECM, Applications. Electro-chemical Honing (ECH), Electrochemical Deburring (ECD), Chemical Machining. Ultrasonic Machining, Cutting Tool System Design, Mechanism of cutting, Parameters affecting USM applications. Abrasive Jet Machining, Variables of AJM, Nozzle Design, Water Jet Machining (WJM), Abrasive Water Jet Machining (AWJM). Hybrid Machining Processes: Grinding, Electrical Discharge Grinding, Electrochemical Grinding, Electrochemical Discharge Grinding. Introduction to Micromachining: Size effect, challenges in micro-scale material removal. Laser Beam Machining, Thermal and Non-thermal analysis, and applications. Electron Beam Machining and Ion Beam Machining: Mechanism, process parameters and applications. Plasma arc machining, applications, Plasma arc surfacing.",
    note="source prints '3 Credits (3-0-0)'; credits recorded as 3.")
add("MEL558","Surface Engineering","Mechanical Engineering","3-0-0-3","","elective","lecture",overlap="Old MT503 (10%)",
    syl="Introduction to surface engineering - Concept and Importance. Surface Degradation: Causes, types and consequences of surface degradation. Classification of surface modification techniques, advantages and their limitations. Materials for Surface Engineering: Selection of materials for engineering the surfaces for specific applications, structure and property relationship of coatings system. Conventional surface engineering and heat treatment practices. Surface modification of ferrous and non-ferrous materials like nitriding, cyaniding, aluminizing etc. Techniques of thin film coatings; Vapour deposition processes: Chemical Vapour Deposition of different types of coatings. Vacuum Evaporation Deposition, Cathodic Arc Evaporation Deposition, sputtering and its advancements. Thermal Spraying methods: Classifications, Flame and plasma spraying, HVOF, cold spray techniques and its variants. Electroplating, Electroless coating, laser, Electron beam and Microwave assisted Surface Engineering, Friction Surfacing and Friction stir processing. Physical Characterization: Microstructure, Surface morphology, Phase analysis, Determination of Crystallite size in coatings. Mechanical Characterization: Determination of thickness of coating, coating hardness, Adhesion of surface coating, Surface roughness. Performance evaluation of coating: Friction and wear performance, Evaluation of corrosion resistance, Assessment of oxidation resistance, Applications of tribological coatings.",
    note="source prints '3 Credits (3-0-0)'; credits recorded as 3. SOURCE ISSUE: the overlap is declared against 'Old MT503', a course code absent from the current Courses of Study, so the 25% overlap rule cannot be mechanically checked for this course.")
add("MEL612","Conduction and Radiation Heat Transfer","Mechanical Engineering","3-0-0-3","","elective","lecture",
    note="transcribed from the UG Manual worked example in section 2.2.5, which prints '3 Credits (3-0-0)' and 'Pre-requisite(s): MEL313 or equivalent'. Included because it is the institute's own documented example of a prerequisite relationship. Syllabus not transcribed.")

HDR_C=["code","title","dept","credits","credit_structure","semester_offered","course_type","mode",
       "objectives","syllabus_text","programme","overlap_with","source_url","retrieved_on",
       "source_type","source_note","verification_status","verified_on","verified_by"]

def course_rows():
    for c in C:
        base = ("transcribed by hand from the official PDF (robots.txt disallows automated "
                "retrieval of iitbhilai.ac.in)")
        note = f"{base}; {c['note']}" if c["note"] else base
        yield {"code": c["code"], "title": c["title"], "dept": c["dept"],
               "credits": c["ltpc"], "credit_structure": "",
               "semester_offered": c["sem"], "course_type": c["ctype"], "mode": c["mode"],
               "objectives": c["obj"], "syllabus_text": c["syllabus"], "programme": PROG,
               "overlap_with": c["overlap"], "source_url": COS_URL, "retrieved_on": RET,
               "source_type": "manual", "source_note": note,
               "verification_status": "unverified", "verified_on": "", "verified_by": ""}

# ======================== PREREQUISITES (as printed) ========================
# (course, requires, kind, note)
P = [
 ("MEL304","MAL100","hard","printed as 'Pre-requisite(s): MAL100-Mathematics-I, MAL101-Mathematics-II'"),
 ("MEL304","MAL101","hard","printed as 'Pre-requisite(s): MAL100-Mathematics-I, MAL101-Mathematics-II'"),
 ("MEP376","MEL232","hard","printed as 'Pre-requisite(s): MEL232, ME334 - concurrent'"),
 ("MEP376","ME334","concurrent","printed VERBATIM as 'ME334 - concurrent'. ME334 is not a course code in the Courses of Study; see corrections.csv"),
 ("MEL414","MEL111","hard","printed as 'Pre-requisite(s): MEL111 or equivalent'. MEL111 does not appear as a course anywhere in the Courses of Study; see corrections.csv"),
 ("MEL416","MEL211","hard","printed as prose, 'Pre-requisite(s): Thermodynamics (MEL211)'; the code was extracted"),
 ("MEL612","MEL313","hard","printed in the UG Manual worked example, section 2.2.5, as 'Pre-requisite(s): MEL313 or equivalent'"),
]
HDR_P=["course","requires","kind","source_url","retrieved_on","source_type","source_note",
       "verification_status","verified_on","verified_by"]

# ============================ CORRECTIONS ==================================
CORR=[
 dict(entity="prerequisite_edge", match_course="MEP376", match_requires="ME334",
      action="remap", new_value="MEL334",
      reason="ME334 is not a course code in the Courses of Study. The only course whose "
             "code differs by the missing 'L' is MEL334 Theory of Mechanisms and Machines, "
             "whose vibration and dynamics content matches this lab's experiments. Treated "
             "as a typographical omission of the 'L' in the published document."),
 dict(entity="prerequisite_edge", match_course="MEL414", match_requires="MEL111",
      action="drop", new_value="",
      reason="MEL111 appears nowhere in the Courses of Study except as this course's "
             "prerequisite and overlap. No candidate course can be identified without "
             "guessing, so the edge is omitted rather than remapped. The printed value is "
             "preserved in prerequisites.csv source_note and reported in DATA_QUALITY.md."),
]
HDR_CORR=["entity","match_course","match_requires","action","new_value","reason",
          "source_url","retrieved_on","source_type","verification_status"]

# ============================ ACADEMIC RULES ================================
# id, category, text (verbatim or close paraphrase marked as such), limit, unit, applies_to, clause
R = [
 ("RULE-CREDIT-TOTAL","credit_requirement","The minimum credit requirement for the award of the BTech degree is 144 credits plus 12 non-graded core units.",144,"credits","BTech all programmes","2.4.1"),
 ("RULE-CREDIT-IC","credit_requirement","Institute core (IC) courses: 40.5 credits.",40.5,"credits","BTech all programmes","2.4.1"),
 ("RULE-CREDIT-PL","credit_requirement","Program linked (PL) courses: 3 to 7 credits. Credit requirements for PC, PL and PE courses can be different for different BTech programs.",7,"credits (upper bound of stated range 3-7)","BTech all programmes","2.4.1"),
 ("RULE-CREDIT-PC","credit_requirement","Program core (PC) courses: 46.5 to 57.5 credits.",57.5,"credits (upper bound of stated range 46.5-57.5)","BTech all programmes","2.4.1"),
 ("RULE-CREDIT-PE","credit_requirement","Program elective (PE) courses: 21 to 25 credits.",25,"credits (upper bound of stated range 21-25)","BTech all programmes","2.4.1"),
 ("RULE-CREDIT-OE","credit_requirement","Open elective (OE) courses: 15 credits.",15,"credits","BTech all programmes","2.4.1"),
 ("RULE-CREDIT-LA","credit_requirement","Liberal art (LA) courses: 10 credits.",10,"credits","BTech all programmes","2.4.1"),
 ("RULE-CREDIT-NC","credit_requirement","Non-graded core (NC) courses: 12 units.",12,"non-graded units","BTech all programmes","2.4.1"),
 ("RULE-ME-CREDIT-PC","credit_requirement","For BTech in Mechanical Engineering the programme-specific minimum credits are: Institute core 40.5, Program linked 6, Program core 48.5, Program elective 24, Open elective 15, Liberal art 10, Non-graded core 12 units, for a minimum of 144 credits plus 12 non-graded core units.",48.5,"credits (program core, Mechanical)","BTech Mechanical Engineering","Courses of Study p.32"),
 ("RULE-LOAD-RANGE","credit_limit","In general a student has to register for the nominal load as per the semester wise program curriculum of the discipline. Overload/underload can only be permitted from third semester onwards. BTech students may be allowed to register for 15 to 21 credits from their third semester onwards by the concerned DUGC conveners on case to case basis.",21,"credits per semester (upper bound; lower bound 15)","BTech students, semester 3 onwards","2.4.2"),
 ("RULE-LOAD-SEM8","credit_limit","In the eighth regular semester, BTech students may be allowed to register up to a minimum of 9 credits by the concerned DUGC conveners subject to fulfilling the credit requirements.",9,"credits","BTech students, semester 8","2.4.2"),
 ("RULE-LOAD-OVERLOAD-FROM","credit_limit","Overload/underload can only be permitted from third semester onwards.",3,"semester (earliest)","BTech all programmes","2.4.2"),
 ("RULE-PREREQ-F","prerequisite","Each course, other than 100 level courses, may have specified pre-requisite(s) in terms of other course(s). A student who has obtained F grade in the pre-requisite(s) specified will not be eligible to register for the course.",None,"","all courses above 100 level","2.2.5"),
 ("RULE-PREREQ-CODE","prerequisite","Pre-requisites shall be defined only in terms of the other course code(s).",None,"","all courses","2.2.5 (i)"),
 ("RULE-PREREQ-CLEAR","prerequisite","A precedent course defined as a prerequisite for a course must be cleared before the dependent course can be taken.",None,"","all courses","2.2.5 (ii)"),
 ("RULE-OVERLAP-25","overlap","A student is not permitted to earn credits by registering for a course having more than 25% overlap with other approved courses which is already credited by the student. If a course (course X) has more than 25% overlapping content with another course (course Y) which is already credited by the student, then a student is not eligible to register for the course (course X).",25,"percent overlap (maximum)","all courses","2.2.6"),
 ("RULE-MOOC-CREDITS","mooc_credit","Students can register for MOOC/NPTEL courses worth 6 credits in their entire UG curriculum. A student shall be allowed to opt a maximum of 6 credits from MOOC based portals for considering against credit transfer during his/her entire program.",6,"credits (entire programme)","BTech students","3.2.1"),
 ("RULE-MOOC-CATEGORY","mooc_credit","Grade based course from MOOC based portals shall be considered for UG students (BTech Program) under Open Elective (OE) or Program Elective (PE).",None,"","BTech students","3.2.1"),
 ("RULE-MOOC-PERMISSION","mooc_credit","Student shall take prior permission from their respective DUGC convener for registering to a grade based course from MOOC. The students shall make their request for credit transfer before commencement of the course.",None,"","BTech students","3.2.1"),
 ("RULE-MOOC-EQUIVALENCE","mooc_credit","14 weeks/42 hours course shall be considered as equivalent to a full-semester course equivalent to 3 credits of IIT Bhilai.",3,"credits per 14 weeks / 42 hours","MOOC-based courses","3.2.1"),
 ("RULE-MOOC-OVERLAP","mooc_credit","The department shall look into the course content to decide the appropriateness of the course to consider as PE. Overlapping of course content shall not be allowed.",None,"","MOOC-based courses","3.2.1"),
 ("RULE-MOOC-CODE","mooc_credit","A course code with a common numeral (495) shall be used for this purpose (Sample course codes: CSL495, MEL495). The title of the course shall carry a prefix 'MOOC-based (XXX):' followed by the course title as mentioned in the MOOC portal, where XXX is replaced with the name of the portal from which the MOOC course is being credited (e.g. NPTEL).",495,"course numeral","MOOC-based courses","3.2.1"),
 ("RULE-MOOC-INSTRUCTOR","mooc_credit","The respective DUGC convener shall act as the instructor in-charge for any proposed MOOC-based course and is responsible for evaluation and grading of the same. Approval of course will be semester specific.",None,"","MOOC-based courses","3.2.1"),
 ("RULE-NPTEL-V-CODE","mooc_credit","Course code letter V denotes lecture courses on special topics by external experts or NPTEL courses (at most 1-3 credits). These courses shall run for duration not less than 1 month. BTech students can take such courses maximum of 6 credits during the entire program.",6,"credits (entire programme)","BTech students","2.2.3, Table 3"),
 ("RULE-CGPA-DEGREE","graduation","A candidate is eligible for the award of BTech degree only if his/her CGPA is greater than or equal to 4.5 and fulfills the minimum number of course credits.",4.5,"CGPA (minimum)","BTech students","2.3.4"),
 ("RULE-CGPA-FIRSTCLASS","graduation","For the purpose of employment or requirement of any external body, IIT Bhilai graduate having 6 (Six) CGPA and above be taken as First Class.",6.0,"CGPA","IIT Bhilai graduates","2.3.4"),
 ("RULE-PROBATION-SGPA","probation","If SGPA falls below 4.5, he/she will be put on academic probation and intimation has to be sent by the academic office to the department where the student is registered. He/she will be allowed to register for the next semester only if CGPA is greater than or equal to 4.0.",4.5,"SGPA (threshold)","BTech students","2.3.6 (a)"),
 ("RULE-PROBATION-CGPA","probation","If, in the subsequent semesters, CGPA is greater than or equal to 4.0 but less than 4.5, he/she will be put on academic probation. He/she may be allowed to register for the next semester on the recommendation of DUGC with the approval of IUGC.",4.0,"CGPA (lower bound of probation band 4.0-4.5)","BTech students","2.3.6 (b)"),
 ("RULE-TERMINATION","termination","A student will normally not be allowed to register and program will be auto terminated if his/her CGPA falls below 4.0, or his/her CGPA falls below 4.5 for three consecutive semesters.",4.0,"CGPA (minimum)","BTech students","2.3.6 (d)"),
 ("RULE-AUDIT","audit","A student has the option of auditing upto 3 credits in a semester with consent from the course instructor(s). Grades obtained in audit courses are not counted for computing SGPA/CGPA although the grade earned by the student is reflected in the grade card or transcript. However, a pass grade (other than F grade) is essential for completing an audit course.",3,"credits per semester","all students","2.3.1"),
 ("RULE-CREDIT-EXPIRY","credit_validity","The credits earned for the course or thesis are valid for up to seven years only (irrespective of whether the student was on leave or not) and shall not be counted towards the requirements of the degree if they are acquired earlier than seven years or more. The credits earned more than seven years back are deemed expired and must be earned again.",7,"years","all students","2.3.1"),
 ("RULE-GRADE-IMPROVE","grade_improvement","A student is allowed to improve his/her grade (other than F) by repeating the course or replacing it with another course if it is an elective course. The course grade improvement can be carried out for a maximum of three courses (where the student was awarded C or less and CGPA is less than or equal to 5) in the program such that it does not lead to any increase in the semester load.",3,"courses (maximum, entire programme)","all students","2.3.5"),
 ("RULE-HONOURS","honours","A student at the end of 5th semester can register for BTech Honours (Course based/Thesis based) depending on their academic performance, interest, and evaluation. BTech (Honours) is an enhanced BTech degree wherein a student takes additional courses/project in his/her own discipline or another discipline.",5,"semester (earliest registration)","BTech students","3.2.2"),
 ("RULE-OE-PURPOSE","open_elective","Open elective courses are meant to widen the knowledge beyond the parent discipline and broaden the horizon by exposing the problems/areas in other disciplines.",None,"","all students","2.2.2 (5)"),
 ("RULE-NC-EARNING","non_graded","Non-graded core (NC) courses are mandatory requirements and can be earned through formal academic activity and informal co-curricular or extra-curricular activities.",None,"","all students","2.2.2 (7)"),
]
HDR_R=["id","category","text","numeric_limit","unit","applies_to","clause_ref","source_url",
       "retrieved_on","source_type","source_note","verification_status","verified_on","verified_by"]


def write(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"wrote {len(rows):4d} rows -> {path}")


def main():
    write("data/raw/curriculum/courses.csv", HDR_C, list(course_rows()))
    write("data/raw/curriculum/prerequisites.csv", HDR_P,
          [{"course": c, "requires": r, "kind": k, "source_url": COS_URL, "retrieved_on": RET,
            "source_type": "manual", "source_note": n, "verification_status": "unverified",
            "verified_on": "", "verified_by": ""} for c, r, k, n in P])
    write("data/raw/curriculum/corrections.csv", HDR_CORR,
          [dict(x, source_url=COS_URL, retrieved_on=RET, source_type="manual",
                verification_status="unverified") for x in CORR])
    write("data/raw/rules/academic_rules.csv", HDR_R,
          [{"id": i, "category": cat, "text": t,
            "numeric_limit": "" if lim is None else lim, "unit": u, "applies_to": ap,
            "clause_ref": cl, "source_url": UGM_URL if not cl.startswith("Courses") else COS_URL,
            "retrieved_on": RET, "source_type": "manual",
            "source_note": "quoted from the UG Manual PDF, downloaded by a human in a browser "
                           "(robots.txt disallows automated retrieval)" if not cl.startswith("Courses")
                           else "transcribed from the Courses of Study PDF",
            "verification_status": "unverified", "verified_on": "", "verified_by": ""}
           for i, cat, t, lim, u, ap, cl in R])
    print(f"\ncourses: {len(C)}  prereq edges: {len(P)}  corrections: {len(CORR)}  rules: {len(R)}")


if __name__ == "__main__":
    main()
