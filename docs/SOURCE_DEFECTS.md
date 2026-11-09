# Defects in the official source documents

Nine problems found while transcribing IIT Bhilai's *Courses of Study* (Oct 2026)
and *UG Manual*.

Each one is transcribed **as printed**. Repairs live in
`data/raw/curriculum/corrections.csv` with a reason, so the defect stays visible
instead of being quietly smoothed over.

## 1. `MEP376` requires `ME334`, which doesn't exist

> `Pre-requisite(s): MEL232, ME334 - concurrent`

No course `ME334` appears anywhere in the document. The validator catches it. The
only course one character away is `MEL334 Theory of Mechanisms and Machines`,
whose vibration and dynamics content matches this lab's experiments, so it's
treated as a dropped "L" and **remapped** in `corrections.csv`.

## 2. `MEL414` requires `MEL111`, which doesn't exist

> `Pre-requisite(s): MEL111 or equivalent` · `Overlap with: MEL111 (5%)`

`MEL111` appears nowhere in 208 pages except these two lines. No candidate can be
identified without guessing, so the edge is **dropped**, not remapped.

## 3. `MEL212` has two different L-T-P values

| Where | Value |
|---|---|
| Structure table, p.32 | `3-1-0-4` |
| Course descriptions | `4 Credits (3-0-1)` |

Credits agree at 4; the tutorial/practical split doesn't. The structure table is
used. A buddy saying "this course has a lab" would be wrong under one reading.

## 4. `MEL304` differs between the two documents

| Where | Credits | Prerequisites |
|---|---|---|
| Courses of Study | `3-0-1-3.5` | `MAL100`, `MAL101` |
| UG Manual §2.2.6 example | `3.0 Credits (3-0-0)` | `Nil` |

The UG Manual instance is a formatting example, not the catalogue entry, so the
Courses of Study wins. Worth flagging because a scraper treating both as
authoritative would take whichever it read last.

## 5. `MEL416` states its prerequisite in prose, breaking the manual's own rule

> `Pre-requisite(s): Thermodynamics (MEL211)`

UG Manual §2.2.5(i) says prerequisites "shall be defined only in terms of the
other course code(s)". The document breaks its own rule. `MEL211` was extracted.

## 6. `MEL501` declares an overlap above the institute's own limit

> `MEL501 Advanced Engineering Mathematics` · `Overlap with: MEL304 (30%)`

UG Manual §2.2.6 bars registering for a course overlapping more than **25%** with
something already credited. `MEL304` is a **core** course for Mechanical, so
every student who passes it is ineligible for `MEL501` — a programme elective.

Neither document states this on its own. It only appears when you join them, and
it's the most useful thing in the dataset.

## 7. `MEL558` declares overlap against a retired code

> `Overlap with: Old MT503 (10%)`

`MT503` isn't in the current Courses of Study, so the overlap rule can't be
checked mechanically for this course.

## 8. Three different words for "no prerequisite"

`None`, `Nil` and `NA` all appear, meaning the same thing. Normalised to one
absent state. A parser treating `NA` as a course code would create a dangling
edge.

## 9. There is no Minor programme

The brief asks for "minor eligibility (CGPA or other criteria)". The UG Manual has
**no Minor at all** — the only "minor" in 40 pages is "minor/major project".

The closest thing is **BTech Honours** (§3.2.2): registrable at the end of the
fifth semester, "depending on their academic performance, interest, and
evaluation", with **no numeric CGPA threshold given**. Stored as `RULE-HONOURS`.

So `minor_eligibility` is empty because the rule doesn't exist, not because it
was missed. No threshold was invented to fill the brief's shape.
