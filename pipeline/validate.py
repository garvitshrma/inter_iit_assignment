"""
Stage 3: validation. Fails loudly.

Design decisions worth defending:

* Two severities. ERROR aborts the run with a non-zero exit; WARN is reported but
  does not block. A missing prerequisite target is an ERROR because it silently
  breaks eligibility reasoning. An unfilled "objectives" field is a WARN because
  the institute genuinely does not publish it for every course -- aborting on it
  would push the author toward inventing text, which is the failure mode this
  whole exercise is built to detect.

* Cycle detection reports the cycle PATH (A -> B -> C -> A), not just the fact of
  one. A bare "cycle detected" on a 200-edge graph is not actionable.

* Checks are declarative: each returns Finding objects, so the data quality
  report (Part D) is generated from the same code that enforces the rules rather
  than written by hand and left to drift.
"""
from __future__ import annotations

import datetime as _dt
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from .models import (SOURCE_TYPES, VERIFICATION_STATES, PREREQ_KINDS,
                     SKILL_DEPTHS, SKILL_ORIGINS, COURSE_TYPES, MODES)
from .normalise import code_is_canonical

ERROR = "ERROR"
WARN = "WARN"


@dataclass
class Finding:
    check: str
    severity: str
    entity: str
    record_id: str
    message: str

    def as_row(self) -> dict:
        return asdict(self)


class Validator:
    def __init__(self, dataset: Dict[str, list], today: Optional[str] = None,
                 enforce_minimums: bool = True):
        self.d = dataset
        # The brief's "at least 15 courses / 30 resources" minimums describe the
        # SUBMITTED dataset. They are meaningless for a fixture run or a --sample
        # run, so the caller switches them off rather than the check lying.
        self.enforce_minimums = enforce_minimums
        self.today = today or _dt.date.today().isoformat()
        self.findings: List[Finding] = []
        self.checks_run: List[str] = []

    # ------------------------------------------------------------------ helpers
    def _add(self, check, severity, entity, rid, msg):
        self.findings.append(Finding(check, severity, entity, str(rid), msg))

    def _rows(self, name):
        return self.d.get(name, []) or []

    @staticmethod
    def _id_of(entity: str, r) -> str:
        if entity == "course":
            return r.code
        if entity == "prerequisite_edge":
            return f"{r.course}->{r.requires}"
        if entity in ("skill", "academic_rule", "resource"):
            return r.id
        if entity == "course_skill_link":
            return f"{r.course}~{r.skill}"
        if entity == "resource_skill_link":
            return f"{r.resource}~{r.skill}"
        return "?"

    # ------------------------------------------------------------------- checks
    def check_provenance(self):
        """Every record must carry a source URL, an ISO retrieval date and a known source_type."""
        self.checks_run.append("provenance_complete")
        for entity in ("course", "prerequisite_edge", "skill", "course_skill_link",
                       "academic_rule", "resource", "resource_skill_link"):
            for r in self._rows(entity):
                rid = self._id_of(entity, r)
                p = r.prov
                # A skill the author invented has no source URL by definition; that is
                # legitimate but must be declared via origin, not left ambiguous.
                exempt = (entity == "skill" and getattr(r, "origin", None) == "author_inferred")
                if not p.source_url and not exempt:
                    self._add("provenance_complete", ERROR, entity, rid, "no source_url")
                if not p.retrieved_on and not exempt:
                    self._add("provenance_complete", ERROR, entity, rid, "no retrieved_on")
                if p.retrieved_on:
                    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(p.retrieved_on)):
                        self._add("provenance_complete", ERROR, entity, rid,
                                  f"retrieved_on not ISO-8601: {p.retrieved_on!r}")
                    elif str(p.retrieved_on) > self.today:
                        self._add("provenance_complete", ERROR, entity, rid,
                                  f"retrieved_on {p.retrieved_on} is in the future")
                if p.source_type not in SOURCE_TYPES:
                    self._add("provenance_complete", ERROR, entity, rid,
                              f"source_type {p.source_type!r} not in {SOURCE_TYPES}")
                if p.verification_status not in VERIFICATION_STATES:
                    self._add("provenance_complete", ERROR, entity, rid,
                              f"verification_status {p.verification_status!r} invalid")
                if p.verification_status == "human_verified" and not p.verified_on:
                    self._add("provenance_complete", WARN, entity, rid,
                              "marked human_verified but no verified_on date")

    def check_course_codes(self):
        self.checks_run.append("duplicate_course_code")
        self.checks_run.append("course_code_shape")
        seen = defaultdict(list)
        for c in self._rows("course"):
            seen[c.code].append(c)
            if not code_is_canonical(c.code):
                self._add("course_code_shape", WARN, "course", c.code,
                          "code does not match ^[A-Z]{2,4}[0-9]{3,4}$ after normalisation")
        for code, rows in seen.items():
            if len(rows) > 1:
                titles = sorted({r.title for r in rows})
                self._add("duplicate_course_code", ERROR, "course", code,
                          f"{len(rows)} records share this code; titles={titles}")

    def check_credits(self):
        self.checks_run.append("credits_numeric")
        self.checks_run.append("credits_match_ltp")
        for c in self._rows("course"):
            if c.credits is None and getattr(c, "credits_raw", None):
                self._add("credits_numeric", ERROR, "course", c.code,
                          f"credits value {c.credits_raw!r} is not numeric")
                continue
            if c.credits is None and c.credit_structure is None:
                self._add("credits_numeric", ERROR, "course", c.code,
                          "neither credits nor credit_structure present")
                continue
            if c.credits is not None:
                if not isinstance(c.credits, (int, float)) or isinstance(c.credits, bool):
                    self._add("credits_numeric", ERROR, "course", c.code,
                              f"credits not numeric: {c.credits!r}")
                elif c.credits < 0 or c.credits > 30:
                    self._add("credits_numeric", ERROR, "course", c.code,
                              f"credits out of plausible range: {c.credits}")
            if c.credits is not None and c.credit_structure:
                m = re.match(r"^(\d+)-(\d+)-(\d+)$", c.credit_structure)
                if m:
                    l, t, p = (int(x) for x in m.groups())
                    # Two conventions are common: L+T+P and L+T+P/2. Flag only when the
                    # stated credits match neither, so we are not asserting one convention.
                    if c.credits not in (l + t + p, l + t + p / 2):
                        self._add("credits_match_ltp", WARN, "course", c.code,
                                  f"credits {c.credits} matches neither L+T+P ({l+t+p}) "
                                  f"nor L+T+P/2 ({l+t+p/2}) for {c.credit_structure}")

    def check_semesters_and_enums(self):
        self.checks_run.append("semester_range")
        self.checks_run.append("enum_values")
        for c in self._rows("course"):
            if c.semester_offered is not None and not (1 <= int(c.semester_offered) <= 10):
                self._add("semester_range", ERROR, "course", c.code,
                          f"semester_offered {c.semester_offered} outside 1..10")
            if c.course_type is not None and c.course_type not in COURSE_TYPES:
                self._add("enum_values", ERROR, "course", c.code,
                          f"course_type {c.course_type!r} not in {COURSE_TYPES}")
            if c.mode not in MODES:
                self._add("enum_values", WARN, "course", c.code,
                          f"mode {c.mode!r} not in {MODES}")
        for e in self._rows("prerequisite_edge"):
            if e.kind not in PREREQ_KINDS:
                self._add("enum_values", ERROR, "prerequisite_edge",
                          self._id_of("prerequisite_edge", e),
                          f"kind {e.kind!r} not in {PREREQ_KINDS}")
        for l in self._rows("course_skill_link"):
            if l.depth not in SKILL_DEPTHS:
                self._add("enum_values", ERROR, "course_skill_link",
                          self._id_of("course_skill_link", l),
                          f"depth {l.depth!r} not in {SKILL_DEPTHS}")
        for s in self._rows("skill"):
            if s.origin not in SKILL_ORIGINS:
                self._add("enum_values", ERROR, "skill", s.id,
                          f"origin {s.origin!r} not in {SKILL_ORIGINS}")

    def check_referential_integrity(self):
        self.checks_run.append("prereq_target_exists")
        self.checks_run.append("link_targets_exist")
        self.checks_run.append("skill_parent_exists")
        codes = {c.code for c in self._rows("course")}
        skills = {s.id for s in self._rows("skill")}
        resources = {r.id for r in self._rows("resource")}

        for e in self._rows("prerequisite_edge"):
            rid = self._id_of("prerequisite_edge", e)
            if e.course not in codes:
                self._add("prereq_target_exists", ERROR, "prerequisite_edge", rid,
                          f"edge source {e.course!r} is not a known course")
            if e.requires not in codes:
                self._add("prereq_target_exists", ERROR, "prerequisite_edge", rid,
                          f"prerequisite {e.requires!r} names a course not in the catalogue")
            if e.course == e.requires:
                self._add("prereq_target_exists", ERROR, "prerequisite_edge", rid,
                          "course is its own prerequisite (self-loop)")

        for l in self._rows("course_skill_link"):
            rid = self._id_of("course_skill_link", l)
            if l.course not in codes:
                self._add("link_targets_exist", ERROR, "course_skill_link", rid,
                          f"course {l.course!r} not in catalogue")
            if l.skill not in skills:
                self._add("link_targets_exist", ERROR, "course_skill_link", rid,
                          f"skill {l.skill!r} not in taxonomy")
        for l in self._rows("resource_skill_link"):
            rid = self._id_of("resource_skill_link", l)
            if l.resource not in resources:
                self._add("link_targets_exist", ERROR, "resource_skill_link", rid,
                          f"resource {l.resource!r} not known")
            if l.skill not in skills:
                self._add("link_targets_exist", ERROR, "resource_skill_link", rid,
                          f"skill {l.skill!r} not in taxonomy")
        for s in self._rows("skill"):
            if s.parent_skill and s.parent_skill not in skills:
                self._add("skill_parent_exists", ERROR, "skill", s.id,
                          f"parent_skill {s.parent_skill!r} not in taxonomy")

    # --------------------------------------------------------- cycle detection
    @staticmethod
    def _find_cycles(adj: Dict[str, List[str]]) -> List[List[str]]:
        """Iterative DFS with an explicit stack; returns each cycle as a node path."""
        WHITE, GREY, BLACK = 0, 1, 2
        colour = defaultdict(int)
        cycles, on_path = [], []
        seen_signatures = set()

        for root in list(adj.keys()):
            if colour[root] != WHITE:
                continue
            stack = [(root, iter(adj.get(root, ())))]
            colour[root] = GREY
            on_path.append(root)
            while stack:
                node, it = stack[-1]
                advanced = False
                for nxt in it:
                    if colour[nxt] == GREY:
                        i = on_path.index(nxt)
                        cycle = on_path[i:] + [nxt]
                        sig = tuple(sorted(set(cycle)))
                        if sig not in seen_signatures:
                            seen_signatures.add(sig)
                            cycles.append(cycle)
                    elif colour[nxt] == WHITE:
                        colour[nxt] = GREY
                        on_path.append(nxt)
                        stack.append((nxt, iter(adj.get(nxt, ()))))
                        advanced = True
                        break
                if not advanced:
                    colour[node] = BLACK
                    stack.pop()
                    if on_path and on_path[-1] == node:
                        on_path.pop()
        return cycles

    def check_prereq_cycles(self):
        self.checks_run.append("prereq_no_cycle")
        adj = defaultdict(list)
        codes = {c.code for c in self._rows("course")}
        for e in self._rows("prerequisite_edge"):
            # Only hard and concurrent prerequisites constrain ordering. A
            # "recommended" edge forming a loop is odd but not a scheduling error.
            if e.kind in ("hard", "concurrent") and e.course in codes and e.requires in codes:
                adj[e.course].append(e.requires)
        for cyc in self._find_cycles(adj):
            self._add("prereq_no_cycle", ERROR, "prerequisite_edge", " -> ".join(cyc),
                      "prerequisite cycle: " + " -> ".join(cyc))

    def check_skill_cycles(self):
        self.checks_run.append("skill_taxonomy_no_cycle")
        adj = defaultdict(list)
        ids = {s.id for s in self._rows("skill")}
        for s in self._rows("skill"):
            if s.parent_skill and s.parent_skill in ids:
                adj[s.id].append(s.parent_skill)
        for cyc in self._find_cycles(adj):
            self._add("skill_taxonomy_no_cycle", ERROR, "skill", " -> ".join(cyc),
                      "skill parent cycle: " + " -> ".join(cyc))

    # ------------------------------------------------------- domain-level checks
    def check_licences(self):
        self.checks_run.append("resource_licence_recorded")
        seen_urls = defaultdict(list)
        for r in self._rows("resource"):
            if not r.licence_name:
                self._add("resource_licence_recorded", ERROR, "resource", r.id,
                          "no licence_name; the brief requires a licence for every external resource")
            if r.licence_name and not r.licence_verified_on:
                self._add("resource_licence_recorded", WARN, "resource", r.id,
                          "licence asserted without licence_verified_on")
            if r.url:
                seen_urls[r.url].append(r.id)
        self.checks_run.append("duplicate_resource_url")
        for url, ids in seen_urls.items():
            if len(ids) > 1:
                self._add("duplicate_resource_url", WARN, "resource", ",".join(ids),
                          f"{len(ids)} resources share URL {url}")

    def check_rules(self):
        self.checks_run.append("rule_quotable")
        for r in self._rows("academic_rule"):
            if not r.text or len(r.text.strip()) < 15:
                self._add("rule_quotable", ERROR, "academic_rule", r.id,
                          "rule text missing or too short to be quotable")
            if r.numeric_limit is not None and not r.unit:
                self._add("rule_quotable", WARN, "academic_rule", r.id,
                          f"numeric_limit {r.numeric_limit} given without a unit")
            if not r.applies_to:
                self._add("rule_quotable", WARN, "academic_rule", r.id,
                          "no applies_to; constraint checking cannot scope this rule")

    def check_coverage(self):
        """Minimums the brief states explicitly."""
        if not self.enforce_minimums:
            return
        self.checks_run.append("brief_minimums")
        n_courses = len(self._rows("course"))
        n_res = len(self._rows("resource"))
        if n_courses < 15:
            self._add("brief_minimums", ERROR, "course", "-",
                      f"brief requires at least 15 courses; dataset has {n_courses}")
        if n_res < 30:
            self._add("brief_minimums", ERROR, "resource", "-",
                      f"brief requires at least 30 open resources; dataset has {n_res}")
        self.checks_run.append("orphan_course_no_skill")
        linked = {l.course for l in self._rows("course_skill_link")}
        for c in self._rows("course"):
            if c.code not in linked:
                self._add("orphan_course_no_skill", WARN, "course", c.code,
                          "no course_skill_link; course contributes nothing to gap analysis")

    def check_illustrative(self):
        """Placeholder rows are allowed in the repo but must never leave it silently."""
        self.checks_run.append("illustrative_rows_flagged")
        for entity in ("course", "prerequisite_edge", "academic_rule", "resource",
                       "skill", "course_skill_link", "resource_skill_link"):
            ids = [self._id_of(entity, r) for r in self._rows(entity)
                   if r.prov.source_type == "illustrative"]
            if not ids:
                continue
            shown = ", ".join(ids[:5]) + (f", +{len(ids)-5} more" if len(ids) > 5 else "")
            self._add("illustrative_rows_flagged", WARN, entity, f"{len(ids)} record(s)",
                      f"source_type=illustrative: placeholders, withheld from export "
                      f"unless --allow-illustrative is passed [{shown}]")

    # -------------------------------------------------------------------- runner
    def run(self) -> List[Finding]:
        self.check_provenance()
        self.check_course_codes()
        self.check_credits()
        self.check_semesters_and_enums()
        self.check_referential_integrity()
        self.check_prereq_cycles()
        self.check_skill_cycles()
        self.check_licences()
        self.check_rules()
        self.check_coverage()
        self.check_illustrative()
        return self.findings

    @property
    def errors(self):
        return [f for f in self.findings if f.severity == ERROR]

    @property
    def warnings(self):
        return [f for f in self.findings if f.severity == WARN]
