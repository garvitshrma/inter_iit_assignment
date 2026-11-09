"""
Stages 1-2: ingest and parse/normalise.

Ingest is deliberately dumb: raw files are copied into data/raw/ and never
written to again. Everything after this point reads raw and writes elsewhere, so
a bad parse is always recoverable by re-running rather than by re-downloading.

Two parse paths exist for the course catalogue:
  * parse_curriculum_pdf -- pdfplumber table extraction, used when the institute's
    Courses-of-Study PDF is present in data/raw/curriculum/.
  * load_courses_csv     -- manual-entry CSV, used for anything the PDF does not
    expose as a table. The brief permits manual entry for small, hard-to-parse
    pieces provided it is disclosed; source_type on those rows is "manual".
"""
from __future__ import annotations

import csv
import json
import os
import re
from typing import Dict, List, Optional

from .models import (Course, PrerequisiteEdge, Skill, CourseSkillLink,
                     AcademicRule, Resource, ResourceSkillLink, Provenance)
from .normalise import (normalise_code, normalise_credits, normalise_semester,
                        normalise_text, normalise_date, normalise_enum)
from .models import COURSE_TYPES, MODES, PREREQ_KINDS, SKILL_DEPTHS, SKILL_ORIGINS

PARSE_NOTES: List[str] = []


def _note(msg: str):
    PARSE_NOTES.append(msg)


def _prov(row: dict) -> Provenance:
    retrieved, problem = normalise_date(row.get("retrieved_on"))
    if problem:
        _note(problem)
    return Provenance(
        source_url=(row.get("source_url") or "").strip() or None,
        retrieved_on=retrieved,
        source_type=(row.get("source_type") or "illustrative").strip().lower(),
        source_note=(row.get("source_note") or "").strip() or None,
        verification_status=(row.get("verification_status") or "unverified").strip().lower(),
        verified_on=(row.get("verified_on") or "").strip() or None,
        verified_by=(row.get("verified_by") or "").strip() or None,
    )


def _read_csv(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [ {(k or "").strip(): (v if v is not None else "") for k, v in r.items()}
                 for r in csv.DictReader(fh) ]


# --------------------------------------------------------------------- courses
def load_courses_csv(path: str) -> List[Course]:
    out = []
    for row in _read_csv(path):
        code = normalise_code(row.get("code"))
        if not code:
            _note(f"skipped a row in {os.path.basename(path)} with no course code")
            continue
        credits, structure, problem = normalise_credits(row.get("credits"))
        credits_raw = None
        if problem:
            _note(f"{code}: {problem}")
            credits_raw = str(row.get("credits") or "").strip() or None
        if structure is None and row.get("credit_structure"):
            structure = row["credit_structure"].strip() or None
        sem, sem_problem = normalise_semester(row.get("semester_offered"))
        if sem_problem:
            _note(f"{code}: {sem_problem}")
        ctype, ct_problem = normalise_enum(row.get("course_type"), COURSE_TYPES,
                                           aliases={"programme-elective": "elective",
                                                    "dept-elective": "elective",
                                                    "open-elective": "open"})
        if ct_problem:
            _note(f"{code}: course_type {ct_problem}")
        mode, _ = normalise_enum(row.get("mode"), MODES, default="unknown")
        out.append(Course(
            code=code, title=normalise_text(row.get("title")) or "",
            dept=normalise_text(row.get("dept")),
            credits=credits, credit_structure=structure, credits_raw=credits_raw,
            semester_offered=sem,
            course_type=ctype, mode=mode or "unknown",
            objectives=normalise_text(row.get("objectives")),
            syllabus_text=normalise_text(row.get("syllabus_text")),
            programme=normalise_text(row.get("programme")),
            overlap_with=normalise_text(row.get("overlap_with")),
            prov=_prov(row)))
    return out


CORRECTIONS_APPLIED: List[dict] = []
CORRECTIONS_UNUSED: List[dict] = []


def load_corrections(path: str) -> List[dict]:
    """
    Source documents contain real defects: a prerequisite naming a course code
    that does not exist, a credit load printed two different ways in two places.
    Silently repairing those would destroy the dataset's whole claim, and
    propagating them makes the pipeline permanently red.

    So corrections live in their own file, each with a reason and its own
    provenance. The loader applies them and stamps the original value into the
    affected record's source_note, so the repair is always visible in the data.
    Supported actions: remap (replace the value) and drop (omit the record).
    """
    rows = _read_csv(path)
    out = []
    for r in rows:
        if not (r.get("entity") or "").strip():
            continue
        r["_used"] = False
        out.append(r)
    return out


def load_prereqs_csv(path: str, corrections: Optional[List[dict]] = None) -> List[PrerequisiteEdge]:
    out = []
    for row in _read_csv(path):
        course, requires = normalise_code(row.get("course")), normalise_code(row.get("requires"))
        if not course or not requires:
            _note("skipped a prerequisite row with a blank endpoint")
            continue
        kind, problem = normalise_enum(row.get("kind"), PREREQ_KINDS, default="hard",
                                       aliases={"co-requisite": "concurrent",
                                                "corequisite": "concurrent",
                                                "soft": "recommended"})
        if problem:
            _note(f"{course}->{requires}: kind {problem}")
        prov = _prov(row)
        action = None
        for c in (corrections or []):
            if c["entity"] != "prerequisite_edge":
                continue
            if normalise_code(c.get("match_course")) != course:
                continue
            if normalise_code(c.get("match_requires")) != requires:
                continue
            c["_used"] = True
            action = (c.get("action") or "remap").strip().lower()
            if action == "drop":
                CORRECTIONS_APPLIED.append(
                    {"entity": "prerequisite_edge", "record": f"{course}->{requires}",
                     "action": "drop", "reason": c.get("reason", "")})
                _note(f"{course}->{requires}: DROPPED per corrections.csv — {c.get('reason','')}")
                break
            new = normalise_code(c.get("new_value")) or requires
            CORRECTIONS_APPLIED.append(
                {"entity": "prerequisite_edge", "record": f"{course}->{requires}",
                 "action": "remap", "from": requires, "to": new,
                 "reason": c.get("reason", "")})
            _note(f"{course}->{requires}: remapped to {new} per corrections.csv")
            prov.source_note = ((prov.source_note or "") +
                                f" | CORRECTED: source prints {requires!r}; "
                                f"remapped to {new!r} — {c.get('reason','')}").strip(" |")
            requires = new
            break
        if action == "drop":
            continue
        out.append(PrerequisiteEdge(course=course, requires=requires,
                                    kind=kind or "hard", prov=prov))
    return out


def load_rules_csv(path: str) -> List[AcademicRule]:
    out = []
    for row in _read_csv(path):
        rid = (row.get("id") or "").strip()
        if not rid:
            _note("skipped an academic rule row with no id")
            continue
        raw_limit = (row.get("numeric_limit") or "").strip()
        limit = None
        if raw_limit:
            m = re.search(r"-?\d+(?:\.\d+)?", raw_limit)
            if m:
                limit = float(m.group(0))
            else:
                _note(f"rule {rid}: numeric_limit {raw_limit!r} is not numeric; stored as null")
        out.append(AcademicRule(
            id=rid, category=(row.get("category") or "uncategorised").strip().lower(),
            text=normalise_text(row.get("text")) or "",
            numeric_limit=limit, unit=(row.get("unit") or "").strip() or None,
            applies_to=(row.get("applies_to") or "").strip() or None,
            clause_ref=(row.get("clause_ref") or "").strip() or None,
            prov=_prov(row)))
    return out


def load_skills_csv(path: str) -> List[Skill]:
    out = []
    for row in _read_csv(path):
        sid = (row.get("id") or "").strip()
        if not sid:
            continue
        origin, _ = normalise_enum(row.get("origin"), SKILL_ORIGINS, default="author_inferred")
        out.append(Skill(id=sid, name=normalise_text(row.get("name")) or sid,
                         level=(row.get("level") or "").strip() or None,
                         parent_skill=(row.get("parent_skill") or "").strip() or None,
                         origin=origin or "author_inferred", prov=_prov(row)))
    return out


def load_course_skill_csv(path: str) -> List[CourseSkillLink]:
    out = []
    for row in _read_csv(path):
        course = normalise_code(row.get("course"))
        skill = (row.get("skill") or "").strip()
        if not course or not skill:
            continue
        depth, _ = normalise_enum(row.get("depth"), SKILL_DEPTHS, default="intro")
        out.append(CourseSkillLink(course=course, skill=skill, depth=depth or "intro",
                                   evidence=normalise_text(row.get("evidence")),
                                   prov=_prov(row)))
    return out


def load_resources_csv(path: str) -> List[Resource]:
    out = []
    for row in _read_csv(path):
        rid = (row.get("id") or "").strip()
        if not rid:
            continue
        dur = (row.get("duration_value") or "").strip()
        dur_val = None
        if dur:
            m = re.search(r"\d+(?:\.\d+)?", dur)
            if m:
                dur_val = float(m.group(0))
            else:
                _note(f"resource {rid}: duration {dur!r} not numeric; stored as null")
        out.append(Resource(
            id=rid, title=normalise_text(row.get("title")) or "",
            provider=(row.get("provider") or "").strip() or None,
            licence_name=(row.get("licence_name") or "").strip() or None,
            licence_version=(row.get("licence_version") or "").strip() or None,
            licence_url=(row.get("licence_url") or "").strip() or None,
            licence_verified_on=(row.get("licence_verified_on") or "").strip() or None,
            fmt=(row.get("fmt") or "").strip() or None,
            duration_value=dur_val,
            duration_unit=(row.get("duration_unit") or "").strip() or None,
            url=(row.get("url") or "").strip() or None,
            instructor=normalise_text(row.get("instructor")),
            host_institute=(row.get("host_institute") or "").strip() or None,
            description=normalise_text(row.get("description")),
            prov=_prov(row)))
    return out


def load_resource_skill_csv(path: str) -> List[ResourceSkillLink]:
    out = []
    for row in _read_csv(path):
        res, skill = (row.get("resource") or "").strip(), (row.get("skill") or "").strip()
        if not res or not skill:
            continue
        level, _ = normalise_enum(row.get("level"), SKILL_DEPTHS, default="intro")
        out.append(ResourceSkillLink(resource=res, skill=skill,
                                     level=level or "intro", prov=_prov(row)))
    return out


# ------------------------------------------------------------------ PDF parsing
def parse_curriculum_pdf(path: str, programme: str, source_url: str,
                         retrieved_on: str) -> List[Course]:
    """
    Best-effort table extraction from an institute Courses-of-Study PDF.

    This intentionally returns only rows where a course code and a title were both
    found. Partial rows are reported in PARSE_NOTES rather than emitted with
    guessed values -- a half-parsed row that looks complete is the most dangerous
    output this pipeline could produce.
    """
    try:
        import pdfplumber
    except ImportError:
        _note("pdfplumber not installed; PDF parsing skipped")
        return []
    if not os.path.exists(path):
        return []

    courses, seen = [], set()
    code_re = re.compile(r"\b([A-Z]{2,4})\s*[-]?\s*(\d{3,4})\b")
    with pdfplumber.open(path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            for table in (page.extract_tables() or []):
                for raw_row in table:
                    cells = [(c or "").strip() for c in raw_row]
                    joined = " | ".join(cells)
                    m = code_re.search(joined)
                    if not m:
                        continue
                    code = f"{m.group(1)}{m.group(2)}"
                    if code in seen:
                        continue
                    title = None
                    for c in cells:
                        cleaned = re.sub(code_re, "", c).strip(" |-–—")
                        if len(cleaned) >= 6 and re.search(r"[A-Za-z]{4,}", cleaned):
                            title = normalise_text(cleaned)
                            break
                    if not title:
                        _note(f"page {pno}: found code {code} but no title cell; row skipped")
                        continue
                    credits = structure = None
                    for c in cells:
                        v, st, _p = normalise_credits(c)
                        if st:
                            structure = st; break
                        if v is not None and 0 < v <= 20 and c.strip() != code:
                            credits = v
                    seen.add(code)
                    courses.append(Course(
                        code=code, title=title, credits=credits,
                        credit_structure=structure, programme=programme,
                        prov=Provenance(source_url=source_url, retrieved_on=retrieved_on,
                                        source_type="official",
                                        source_note=f"pdfplumber table extraction, page {pno}")))
    _note(f"parsed {len(courses)} course rows from {os.path.basename(path)}")
    return courses


def load_dataset(raw_dir: str) -> Dict[str, list]:
    j = lambda *p: os.path.join(raw_dir, *p)
    corrections = load_corrections(j("curriculum", "corrections.csv"))
    data = {
        "course": load_courses_csv(j("curriculum", "courses.csv")),
        "prerequisite_edge": load_prereqs_csv(j("curriculum", "prerequisites.csv"), corrections),
        "academic_rule": load_rules_csv(j("rules", "academic_rules.csv")),
        "skill": load_skills_csv(j("curriculum", "skills.csv")),
        "course_skill_link": load_course_skill_csv(j("curriculum", "course_skills.csv")),
        "resource": load_resources_csv(j("resources", "resources.csv")),
        "resource_skill_link": load_resource_skill_csv(j("resources", "resource_skills.csv")),
    }
    # A correction that matched nothing is a stale repair for data that has since
    # changed. Surfaced rather than ignored, so corrections.csv cannot rot.
    for c in corrections:
        if not c["_used"]:
            CORRECTIONS_UNUSED.append(c)
            _note(f"UNUSED correction for {c['entity']} "
                  f"{c.get('match_course','')}->{c.get('match_requires','')}: "
                  f"matched no record (stale?)")
    return data
