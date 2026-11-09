#!/usr/bin/env python3
"""
Authors data/raw/curriculum/skills.csv -- the skill taxonomy.

This taxonomy is NOT retrieved from any institute document. It is the dataset
author's organising structure for mechanical engineering competencies, so every
row carries origin=author_inferred and no source_url. The validator exempts
author_inferred skills from the provenance requirement precisely so that this
distinction stays visible instead of being papered over with a fake citation.

Levels: foundational | intermediate | advanced.
"""
import csv, os

# (id, name, level, parent)
S = [
 ("SK-MECH", "Mechanical engineering", None, None),

 ("SK-SOLID", "Solid mechanics and structures", "foundational", "SK-MECH"),
 ("SK-STATICS", "Statics and equilibrium", "foundational", "SK-SOLID"),
 ("SK-FBD", "Free body diagrams", "foundational", "SK-STATICS"),
 ("SK-TRUSS", "Truss and frame analysis", "foundational", "SK-STATICS"),
 ("SK-FRICTION", "Friction and its applications", "foundational", "SK-STATICS"),
 ("SK-STRESS", "Stress and strain analysis", "intermediate", "SK-SOLID"),
 ("SK-BEAM", "Beam bending and torsion", "intermediate", "SK-SOLID"),
 ("SK-FAIL", "Failure theories and fatigue", "advanced", "SK-SOLID"),
 ("SK-FEM", "Finite element analysis", "advanced", "SK-SOLID"),

 ("SK-THERMAL", "Thermal and fluid sciences", "foundational", "SK-MECH"),
 ("SK-THERMO", "Thermodynamics", "foundational", "SK-THERMAL"),
 ("SK-LAWS", "Laws of thermodynamics", "foundational", "SK-THERMO"),
 ("SK-PROPS", "Properties of pure substances", "foundational", "SK-THERMO"),
 ("SK-CYCLES", "Power and refrigeration cycles", "intermediate", "SK-THERMO"),
 ("SK-PSYCHRO", "Psychrometry and air conditioning", "intermediate", "SK-CYCLES"),
 ("SK-FLUID", "Fluid mechanics", "foundational", "SK-THERMAL"),
 ("SK-FLUIDSTAT", "Fluid statics and manometry", "foundational", "SK-FLUID"),
 ("SK-VISC", "Viscous flow and boundary layers", "intermediate", "SK-FLUID"),
 ("SK-COMPR", "Compressible flow", "advanced", "SK-FLUID"),
 ("SK-TURBO", "Turbomachinery", "advanced", "SK-FLUID"),
 ("SK-HEAT", "Heat transfer", "intermediate", "SK-THERMAL"),
 ("SK-COND", "Conduction", "intermediate", "SK-HEAT"),
 ("SK-CONV", "Convection", "intermediate", "SK-HEAT"),
 ("SK-RAD", "Radiation", "intermediate", "SK-HEAT"),
 ("SK-HX", "Heat exchangers", "advanced", "SK-HEAT"),
 ("SK-MASST", "Mass transfer", "advanced", "SK-HEAT"),
 ("SK-CFD", "Computational fluid dynamics", "advanced", "SK-THERMAL"),
 ("SK-COMBUST", "Combustion and IC engines", "advanced", "SK-THERMAL"),

 ("SK-DYN", "Dynamics and control", "intermediate", "SK-MECH"),
 ("SK-RBD", "Rigid body dynamics", "intermediate", "SK-DYN"),
 ("SK-KINEM", "Kinematics of machines", "intermediate", "SK-DYN"),
 ("SK-BALANCE", "Balancing and governors", "advanced", "SK-DYN"),
 ("SK-VIB", "Mechanical vibrations", "advanced", "SK-DYN"),
 ("SK-CONTROL", "Control systems", "advanced", "SK-DYN"),
 ("SK-MECHATRON", "Mechatronics and robotics", "advanced", "SK-DYN"),

 ("SK-MFG", "Manufacturing and materials", "foundational", "SK-MECH"),
 ("SK-MATSCI", "Materials science", "foundational", "SK-MFG"),
 ("SK-CRYSTAL", "Crystal structure and defects", "foundational", "SK-MATSCI"),
 ("SK-PHASE", "Phase diagrams and transformations", "intermediate", "SK-MATSCI"),
 ("SK-MECHPROP", "Mechanical properties of materials", "intermediate", "SK-MATSCI"),
 ("SK-HEATTREAT", "Heat treatment", "intermediate", "SK-MATSCI"),
 ("SK-CASTING", "Casting processes", "intermediate", "SK-MFG"),
 ("SK-FORMING", "Metal forming", "intermediate", "SK-MFG"),
 ("SK-JOINING", "Welding and joining", "intermediate", "SK-MFG"),
 ("SK-MACHINING", "Machining and metal cutting", "intermediate", "SK-MFG"),
 ("SK-ADDITIVE", "Additive manufacturing", "advanced", "SK-MFG"),
 ("SK-METROLOGY", "Metrology and measurement", "foundational", "SK-MFG"),
 ("SK-AUTOMATION", "Manufacturing automation and CIM", "advanced", "SK-MFG"),

 ("SK-DESIGN", "Design and graphics", "foundational", "SK-MECH"),
 ("SK-DRAWING", "Engineering drawing", "foundational", "SK-DESIGN"),
 ("SK-CAD", "CAD modelling", "foundational", "SK-DESIGN"),
 ("SK-MACHDESIGN", "Machine element design", "advanced", "SK-DESIGN"),
 ("SK-DESIGNPROC", "Design process and prototyping", "intermediate", "SK-DESIGN"),

 ("SK-IE", "Industrial engineering", "intermediate", "SK-MECH"),
 ("SK-OPT", "Optimisation", "advanced", "SK-IE"),
 ("SK-OPS", "Operations and production planning", "intermediate", "SK-IE"),

 ("SK-COMPUTE", "Engineering computation", "foundational", "SK-MECH"),
 ("SK-NUMER", "Numerical methods", "intermediate", "SK-COMPUTE"),
 ("SK-PROG", "Scientific programming", "foundational", "SK-COMPUTE"),
]

HEADER = ["id", "name", "level", "parent_skill", "origin", "source_url",
          "retrieved_on", "source_type", "source_note", "verification_status",
          "verified_on", "verified_by"]

def main():
    out = os.path.join("data", "raw", "curriculum", "skills.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        for sid, name, level, parent in S:
            w.writerow({"id": sid, "name": name, "level": level or "",
                        "parent_skill": parent or "", "origin": "author_inferred",
                        "source_url": "", "retrieved_on": "", "source_type": "manual",
                        "source_note": "taxonomy node defined by dataset author; not quoted from a source",
                        "verification_status": "unverified", "verified_on": "", "verified_by": ""})
    print(f"wrote {len(S)} skills -> {out}")

if __name__ == "__main__":
    main()
