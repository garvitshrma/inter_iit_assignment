"""
Schema definitions.

Every entity carries provenance (source_url, retrieved_on, source_type) plus a
verification field, because Part D of the brief asks how a teammate could verify
a sample of records against sources -- that is easier to answer if verification
state lives in the data rather than in a promise in the README.

SOURCE_TYPES deviates from the brief's three values by adding "illustrative".
Rationale: during a one-day build some rows are unavoidably placeholder. A
pipeline that cannot tell placeholder rows from retrieved ones will eventually
push fabricated records into an embedding index. Marking them explicitly lets
the exporter refuse to ship them unless a human opts in (see stage_export).
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields as dc_fields
from typing import Optional

SOURCE_TYPES = ("official", "open-licence", "manual", "illustrative")
VERIFICATION_STATES = ("unverified", "human_verified", "disputed")
PREREQ_KINDS = ("hard", "recommended", "concurrent")
SKILL_DEPTHS = ("intro", "working", "advanced")
SKILL_ORIGINS = ("syllabus_phrase", "author_inferred")
COURSE_TYPES = ("core", "elective", "open", "programme-core", "institute-core",
                "non-graded")
MODES = ("lecture", "lecture-tutorial", "lecture-lab", "lab", "project", "unknown")


@dataclass
class Provenance:
    """Attached to every record. retrieved_on is an ISO date (YYYY-MM-DD)."""
    source_url: Optional[str] = None
    retrieved_on: Optional[str] = None
    source_type: str = "illustrative"
    source_note: Optional[str] = None
    verification_status: str = "unverified"
    verified_on: Optional[str] = None
    verified_by: Optional[str] = None


@dataclass
class Course:
    code: str
    title: str
    dept: Optional[str] = None
    credits: Optional[float] = None
    # Indian curricula express load as Lecture-Tutorial-Practical. Collapsing to a
    # single integer loses the information the brief asks for under "mode", so both
    # are kept and credits is checked against the L-T-P sum by the validator.
    credit_structure: Optional[str] = None
    # Preserved verbatim when normalisation could not read a number, so the
    # validator can name the offending value rather than just its absence.
    credits_raw: Optional[str] = None
    semester_offered: Optional[int] = None
    course_type: Optional[str] = None
    mode: str = "unknown"
    objectives: Optional[str] = None
    syllabus_text: Optional[str] = None
    programme: Optional[str] = None
    # The institute publishes an "Overlap with" line per course and enforces a 25%
    # ceiling (UG Manual 2.2.6). Not in the brief's schema, but it is published
    # data that directly constrains what a student may register for, so dropping
    # it would lose a real eligibility rule.
    overlap_with: Optional[str] = None
    prov: Provenance = field(default_factory=Provenance)


@dataclass
class PrerequisiteEdge:
    course: str
    requires: str
    kind: str = "hard"
    prov: Provenance = field(default_factory=Provenance)


@dataclass
class Skill:
    id: str
    name: str
    level: Optional[str] = None
    parent_skill: Optional[str] = None
    # Honesty marker: a skill lifted verbatim from a syllabus is source-traced; a
    # skill the author invented to organise the taxonomy is a judgement call and
    # must not be presented as retrieved data.
    origin: str = "author_inferred"
    prov: Provenance = field(default_factory=Provenance)


@dataclass
class CourseSkillLink:
    course: str
    skill: str
    depth: str = "intro"
    evidence: Optional[str] = None
    prov: Provenance = field(default_factory=Provenance)


@dataclass
class AcademicRule:
    id: str
    category: str
    text: str
    numeric_limit: Optional[float] = None
    unit: Optional[str] = None
    applies_to: Optional[str] = None
    clause_ref: Optional[str] = None
    prov: Provenance = field(default_factory=Provenance)


@dataclass
class Resource:
    id: str
    title: str
    provider: Optional[str] = None
    # The brief asks for "licence" as one field. Split, because NPTEL states
    # "CC BY-NC-SA" with no version and no linked deed, while MIT OCW states
    # CC BY-NC-SA 4.0 with a deed URL. One string would force a guess.
    licence_name: Optional[str] = None
    licence_version: Optional[str] = None
    licence_url: Optional[str] = None
    licence_verified_on: Optional[str] = None
    fmt: Optional[str] = None
    duration_value: Optional[float] = None
    duration_unit: Optional[str] = None
    url: Optional[str] = None
    instructor: Optional[str] = None
    host_institute: Optional[str] = None
    description: Optional[str] = None
    prov: Provenance = field(default_factory=Provenance)


@dataclass
class ResourceSkillLink:
    resource: str
    skill: str
    level: str = "intro"
    prov: Provenance = field(default_factory=Provenance)


@dataclass
class Chunk:
    chunk_id: str
    parent_id: str
    parent_type: str
    chunk_type: str
    text: str
    token_estimate: int
    ordinal: int
    filter_metadata: dict = field(default_factory=dict)
    prov: Provenance = field(default_factory=Provenance)


ENTITY_CLASSES = {
    "course": Course,
    "prerequisite_edge": PrerequisiteEdge,
    "skill": Skill,
    "course_skill_link": CourseSkillLink,
    "academic_rule": AcademicRule,
    "resource": Resource,
    "resource_skill_link": ResourceSkillLink,
}


def flatten(rec) -> dict:
    """Flatten a dataclass record (with nested Provenance) into one dict row."""
    out = {}
    for f in dc_fields(rec):
        val = getattr(rec, f.name)
        if f.name == "prov":
            for pf in dc_fields(val):
                out[pf.name] = getattr(val, pf.name)
        else:
            out[f.name] = val
    return out


def field_names(cls) -> list:
    names = []
    for f in dc_fields(cls):
        if f.name == "prov":
            names.extend(pf.name for pf in dc_fields(Provenance))
        else:
            names.append(f.name)
    return names
