"""
Stage 4: chunking.

Chunk sizing is deliberately conservative and rule-driven rather than uniform:

* Academic rules are NEVER split. The brief asks for rules stored as separate
  quotable entries; half a rule is worse than useless to a buddy that has to
  cite a constraint ("you may register at most ..." with the number in the next
  chunk). One rule == one chunk, regardless of length.
* Course syllabi ARE split, on sentence boundaries, with a small overlap, because
  a syllabus is prose covering several topics and a student question usually
  targets one of them.
* Every course additionally gets a "course_card" chunk: a compact, structured
  restatement of the facts (code, title, credits, semester, prerequisites). This
  is what answers "what are the prerequisites for MEL251" without the retriever
  having to luck into the right syllabus fragment.

Token counts are CHARACTER-BASED ESTIMATES (chars/4). No tokenizer is used and
no model is called, per the brief's no-embeddings rule. The field is named
token_estimate so nobody downstream mistakes it for a true count.
"""
from __future__ import annotations

import hashlib
import re
from typing import Dict, List

from .models import Chunk, Provenance

TARGET_CHARS = 1100     # ~275 token estimate
MAX_CHARS = 1600
OVERLAP_CHARS = 150
MIN_CHARS = 120         # below this, merge forward rather than emit a stub


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def _sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.;:!?])\s+|\n{2,}", text)
    return [p.strip() for p in parts if p and p.strip()]


def _pack(text: str) -> List[str]:
    """Greedy sentence packing to TARGET_CHARS with trailing overlap."""
    sents, out, buf = _sentences(text), [], ""
    for s in sents:
        if len(s) > MAX_CHARS:
            if buf:
                out.append(buf.strip()); buf = ""
            for i in range(0, len(s), TARGET_CHARS):
                out.append(s[i:i + TARGET_CHARS].strip())
            continue
        if buf and len(buf) + 1 + len(s) > TARGET_CHARS:
            out.append(buf.strip())
            tail = buf[-OVERLAP_CHARS:]
            cut = tail.find(" ")
            buf = (tail[cut + 1:] if cut != -1 else "") + " " + s
        else:
            buf = f"{buf} {s}".strip()
    if buf.strip():
        out.append(buf.strip())
    # Merge a runt tail backwards so we never emit a 20-character chunk.
    if len(out) > 1 and len(out[-1]) < MIN_CHARS:
        out[-2] = f"{out[-2]} {out.pop()}".strip()
    return out


def _cid(parent_type: str, parent_id: str, chunk_type: str, ordinal: int, text: str) -> str:
    h = hashlib.sha1(f"{parent_type}|{parent_id}|{chunk_type}|{ordinal}|{text}".encode()).hexdigest()[:10]
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(parent_id))[:40]
    return f"{parent_type}:{safe}:{chunk_type}:{ordinal:02d}:{h}"


def _prov_of(rec) -> Provenance:
    return rec.prov


def chunk_dataset(d: Dict[str, list]) -> List[Chunk]:
    chunks: List[Chunk] = []

    prereq_by_course: Dict[str, list] = {}
    for e in d.get("prerequisite_edge", []):
        prereq_by_course.setdefault(e.course, []).append(e)
    skills_by_course: Dict[str, list] = {}
    for l in d.get("course_skill_link", []):
        skills_by_course.setdefault(l.course, []).append(l)
    skill_name = {s.id: s.name for s in d.get("skill", [])}

    # ---- courses -----------------------------------------------------------
    for c in d.get("course", []):
        prereqs = prereq_by_course.get(c.code, [])
        hard = [e.requires for e in prereqs if e.kind == "hard"]
        rec = [e.requires for e in prereqs if e.kind == "recommended"]
        conc = [e.requires for e in prereqs if e.kind == "concurrent"]
        sk = [(skill_name.get(l.skill, l.skill), l.depth) for l in skills_by_course.get(c.code, [])]

        card_lines = [
            f"Course {c.code}: {c.title}.",
            f"Offered by {c.dept}." if c.dept else None,
            f"Credits: {c.credits}." if c.credits is not None else None,
            f"Load (L-T-P): {c.credit_structure}." if c.credit_structure else None,
            f"Typically offered in semester {c.semester_offered}." if c.semester_offered else None,
            f"Course type: {c.course_type}." if c.course_type else None,
            f"Mode: {c.mode}." if c.mode and c.mode != "unknown" else None,
            f"Programme: {c.programme}." if c.programme else None,
            f"Hard prerequisites: {', '.join(hard)}." if hard else "Hard prerequisites: none recorded.",
            f"Recommended background: {', '.join(rec)}." if rec else None,
            f"Co-requisites: {', '.join(conc)}." if conc else None,
            ("Skills taught: " + "; ".join(f"{n} ({dp})" for n, dp in sk) + ".") if sk else None,
        ]
        card = " ".join(x for x in card_lines if x)
        meta = {
            "programme": c.programme, "dept": c.dept, "course_code": c.code,
            "semester_offered": c.semester_offered, "course_type": c.course_type,
            "credits": c.credits, "entity": "course",
            "skill_ids": [l.skill for l in skills_by_course.get(c.code, [])],
            "hard_prereqs": hard,
        }
        chunks.append(Chunk(
            chunk_id=_cid("course", c.code, "course_card", 0, card),
            parent_id=c.code, parent_type="course", chunk_type="course_card",
            text=card, token_estimate=estimate_tokens(card), ordinal=0,
            filter_metadata=meta, prov=_prov_of(c)))

        for label, body in (("objectives", c.objectives), ("syllabus", c.syllabus_text)):
            if not body:
                continue
            for i, piece in enumerate(_pack(body)):
                txt = f"{c.code} {c.title} — {label}: {piece}"
                chunks.append(Chunk(
                    chunk_id=_cid("course", c.code, label, i, piece),
                    parent_id=c.code, parent_type="course", chunk_type=label,
                    text=txt, token_estimate=estimate_tokens(txt), ordinal=i,
                    filter_metadata=meta, prov=_prov_of(c)))

    # ---- academic rules (never split) --------------------------------------
    for r in d.get("academic_rule", []):
        txt = f"[{r.category}] {r.text}"
        if r.numeric_limit is not None:
            txt += f" (limit: {r.numeric_limit}{' ' + r.unit if r.unit else ''})"
        if r.clause_ref:
            txt += f" [clause {r.clause_ref}]"
        chunks.append(Chunk(
            chunk_id=_cid("academic_rule", r.id, "rule", 0, txt),
            parent_id=r.id, parent_type="academic_rule", chunk_type="rule",
            text=txt, token_estimate=estimate_tokens(txt), ordinal=0,
            filter_metadata={"entity": "academic_rule", "category": r.category,
                             "applies_to": r.applies_to, "numeric_limit": r.numeric_limit,
                             "unit": r.unit, "clause_ref": r.clause_ref},
            prov=_prov_of(r)))

    # ---- resources ---------------------------------------------------------
    res_skills: Dict[str, list] = {}
    for l in d.get("resource_skill_link", []):
        res_skills.setdefault(l.resource, []).append(l)
    for r in d.get("resource", []):
        sk = [skill_name.get(l.skill, l.skill) for l in res_skills.get(r.id, [])]
        lic = r.licence_name or "licence not recorded"
        if r.licence_version:
            lic += f" {r.licence_version}"
        bits = [
            f"Open learning resource: {r.title}.",
            f"Provider: {r.provider}." if r.provider else None,
            f"Host institute: {r.host_institute}." if r.host_institute else None,
            f"Instructor: {r.instructor}." if r.instructor else None,
            f"Format: {r.fmt}." if r.fmt else None,
            (f"Approximate duration: {r.duration_value} {r.duration_unit}."
             if r.duration_value is not None else "Duration: not stated by the provider."),
            f"Licence: {lic}.",
            ("Supports: " + ", ".join(sk) + ".") if sk else None,
            r.description or None,
        ]
        txt = " ".join(x for x in bits if x)
        meta = {"entity": "resource", "provider": r.provider,
                "licence_name": r.licence_name, "licence_version": r.licence_version,
                "fmt": r.fmt, "skill_ids": [l.skill for l in res_skills.get(r.id, [])],
                "host_institute": r.host_institute}
        for i, piece in enumerate(_pack(txt)):
            chunks.append(Chunk(
                chunk_id=_cid("resource", r.id, "resource_desc", i, piece),
                parent_id=r.id, parent_type="resource", chunk_type="resource_desc",
                text=piece, token_estimate=estimate_tokens(piece), ordinal=i,
                filter_metadata=meta, prov=_prov_of(r)))

    # ---- skills ------------------------------------------------------------
    by_id = {s.id: s for s in d.get("skill", [])}
    for s in d.get("skill", []):
        path, cur, guard = [], s, 0
        while cur and guard < 12:
            path.append(cur.name)
            cur = by_id.get(cur.parent_skill) if cur.parent_skill else None
            guard += 1
        txt = (f"Skill {s.id}: {s.name}."
               + (f" Level: {s.level}." if s.level else "")
               + (f" Taxonomy path: {' < '.join(path)}." if len(path) > 1 else "")
               + (" This skill node was defined by the dataset author to organise the taxonomy "
                  "and is not quoted from an institute document."
                  if s.origin == "author_inferred" else ""))
        chunks.append(Chunk(
            chunk_id=_cid("skill", s.id, "skill_node", 0, txt),
            parent_id=s.id, parent_type="skill", chunk_type="skill_node",
            text=txt, token_estimate=estimate_tokens(txt), ordinal=0,
            filter_metadata={"entity": "skill", "level": s.level,
                             "parent_skill": s.parent_skill, "origin": s.origin},
            prov=_prov_of(s)))

    return chunks
