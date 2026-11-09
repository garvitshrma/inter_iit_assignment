# Defects found in the official source documents

Nine issues found while transcribing IIT Bhilai's *Courses of Study* (Oct 2026)
and *UG Manual*. Every one is recorded faithfully in the dataset — the printed
value is transcribed as printed, and any repair lives in
`data/raw/curriculum/corrections.csv` with its reason, so the defect stays
visible instead of being quietly smoothed over.

This list is the main argument that the dataset was actually read rather than
assumed.

## 1. `MEP376` names a prerequisite that does not exist — `ME334`

> `MEP376 Solid Mechanics and Dynamics Lab` … `Pre-requisite(s): MEL232, ME334 - concurrent`

`ME334` is not a course code anywhere in the Courses of Study. The validator
catches this as `prereq_target_exists`. The only course differing by one
character is `MEL334 Theory of Mechanisms and Machines`, whose vibration and
dynamics content matches this lab's experiments, so it is treated as a dropped
`L` and **remapped in `corrections.csv`**. The printed value survives in the
edge's `source_note`.

## 2. `MEL414` names a prerequisite that does not exist — `MEL111`

> `MEL414 Internal Combustion Engines` … `Pre-requisite(s): MEL111 or equivalent` · `Overlap with: MEL111 (5%)`

`MEL111` appears nowhere in the 208-page document except in these two lines. No
candidate can be identified without guessing, so the edge is **dropped**, not
remapped. Guessing here would have invented a curriculum relationship.

## 3. `MEL212` — L-T-P published two different ways

| Where | Value |
|---|---|
| Programme structure table (p.32) | `3-1-0-4` |
| Course-description section | `4 Credits (3-0-1)` |

Credits agree at 4; the tutorial/practical split does not. The structure table is
used, and the conflict is recorded in the course's `source_note`. A buddy telling
a student "this course has a lab component" would be wrong under one reading.

## 4. `MEL304` — the UG Manual and the Courses of Study disagree

| Where | Credits | Prerequisites |
|---|---|---|
| Courses of Study | `3-0-1-3.5` | `MAL100`, `MAL101` |
| UG Manual §2.2.6 worked example | `3.0 Credits (3-0-0)` | `Nil` |

The UG Manual instance is illustrative formatting rather than the authoritative
catalogue entry, so the Courses of Study values are used. Worth flagging because
a scraper treating both documents as equally authoritative would silently pick
whichever it read last.

## 5. `MEL416` states its prerequisite in prose, breaching the manual's own rule

> `Pre-requisite(s): Thermodynamics (MEL211)`

UG Manual §2.2.5(i): *"Pre-requisites shall be defined only in terms of the other
course code(s)."* The document violates its own policy here. `MEL211` was
extracted and the deviation noted.

## 6. `MEL501` declares an overlap that exceeds the institute's own ceiling

> `MEL501 Advanced Engineering Mathematics` · `Overlap with: MEL304 (30%)`

UG Manual §2.2.6 bars registering for a course with **more than 25% overlap** with
something already credited. `MEL304` is a *core* course for Mechanical
(semester 6), so every Mechanical student who passes it is ineligible for
`MEL501` — a programme elective. This is a real, mechanically derivable
eligibility conflict, and it is the single most useful thing in the dataset that
no single document states on its own.

## 7. `MEL558` declares overlap against a retired course code

> `Overlap with: Old MT503 (10%)`

`MT503` is not in the current Courses of Study, so the 25% overlap rule cannot be
checked mechanically for this course.

## 8. Inconsistent vocabulary for "no prerequisite"

`None`, `Nil` and `NA` are all used to mean the same thing across the document
(`MEL351` uses `NA`, most courses use `None`, the UG Manual example uses `Nil`).
Normalised to a single absent-prerequisite state; a naive parser treating `NA` as
a course code would produce a dangling edge.

## 9. There is no Minor programme

The brief asks for *"minor eligibility (CGPA or other criteria)"*. The UG Manual
contains **no Minor provision at all** — the only occurrence of the word "minor"
in 40 pages is "minor/major project" in the course-code table.

The analogous provision is **BTech Honours** (§3.2.2): registrable at the end of
the fifth semester, *"depending on their academic performance, interest, and
evaluation"* — with **no numeric CGPA threshold stated**. That is captured as
`RULE-HONOURS`. The `minor_eligibility` rule category is therefore empty by
fact, not by omission, and no threshold was invented to fill the brief's shape.
