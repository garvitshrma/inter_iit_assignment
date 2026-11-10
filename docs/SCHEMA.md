# Part B — Schema

The brief gave a starting table. This lists what I changed and why. The entity
definitions are in `pipeline/models.py`.

## Provenance, on every record

The brief asks for `source_url`, `retrieved_on` and `source_type`. I added three
more:

| Field | Why |
|---|---|
| `source_locator` | Where inside the source document the record is, e.g. `Courses_Of_Study.pdf p.32 (structure table), p.150 (course description)`. Added after a verification pass found the records unverifiable: `source_url` pointed at a 208-page PDF, so a reviewer had nowhere to look. Provenance that cannot be acted on is not traceability. Written by `tools/locate_in_pdf.py`, which finds each code in the PDF rather than trusting a hand-typed page number. |
| `source_note` | How the record was obtained: which PDF page, whether a web page was actually opened, whether a number was derived. Two records can have identical provenance and very different trustworthiness. |
| `verification_status` | `unverified` / `human_verified` / `disputed`. Part D asks how a teammate would verify a sample. Easier to answer if verification is a field, not a promise. |
| `verified_on`, `verified_by` | Who checked it and when, so the sample is reproducible. |

**`source_type` has a fourth value: `illustrative`.** The brief lists
`official` / `open-licence` / `manual`. Placeholder rows need their own value,
because a pipeline that can't tell a placeholder from a real record will
eventually push invented data into an embedding index. The exporter refuses to
write them unless `--allow-illustrative` is passed.

## Course

- **`credit_structure` alongside `credits`.** IIT Bhilai prints load as
  Lecture-Tutorial-Practical-Credits (`3-0-0-3`). The number alone loses whether
  a course has a lab. The validator cross-checks the two, and only complains when
  `credits` matches neither `L+T+P` nor `L+T+P/2`, since institutes weight
  practicals differently.
- **`credits_raw`.** Keeps the original string when the value isn't a number, so
  the validator can say *"credits value `'three'` is not numeric"* instead of
  *"no credits present"*.
- **`overlap_with`.** The institute publishes an overlap percentage per course and
  bars registering above 25% (UG Manual 2.2.6). Dropping it would lose a real
  eligibility rule.
- `objectives` and `syllabus_text` stay separate. They answer different questions
  and chunk differently.
- `programme` lives on the course, so a second programme can be added later.

## Prerequisite edge

- **`kind` gains `concurrent`.** Co-requisites are taken in the same semester, not
  before. Calling them `hard` breaks ordering; calling them `recommended` loses
  the constraint.
- Cycle detection covers `hard` and `concurrent` only. A `recommended` loop is odd
  but isn't a scheduling error.

## Skill

- **`origin`** is either `syllabus_phrase` or `author_inferred`. This is the
  honesty field: the taxonomy is mine, the courses are retrieved, and those are
  different kinds of claim. The validator exempts `author_inferred` skills from
  needing a source URL, so there's no incentive to invent a citation.
- `parent_skill` makes the taxonomy a tree, checked for cycles like prerequisites.

## Course-skill link

- **`evidence`** holds the syllabus phrase the depth rating came from. A reviewer
  who disagrees with "advanced" can see what it rested on. This makes the most
  subjective part of the dataset auditable.

## Academic rule

- **`numeric_limit` and `unit` are separate**, and `clause_ref` is added. "7.0" is
  useless without knowing it's a CGPA. The clause number is what makes a quoted
  rule credible.
- `applies_to` is warned on when missing, because an unscoped rule can't be used
  for eligibility checks.

## Resource

- **Licence split into `licence_name`, `licence_version`, `licence_url`,
  `licence_verified_on`.** Forced by the data: MIT OCW states CC BY-NC-SA **4.0**
  with a linked deed, NPTEL states CC BY-NC-SA with **no version**. One field
  would mean guessing.
- **`duration_value` and `duration_unit` separate**, because sources state weeks,
  hours, or nothing.

## Chunk

- Parent id, parent type, chunk type, ordinal, filter metadata and provenance, as
  the brief asks.
- **`token_estimate`, named as an estimate** (characters ÷ 4). No tokenizer, no
  model call. `token_count` would invite misplaced trust.
- **A `course_card` chunk type that isn't in the source data.** It restates each
  course's structured facts as prose. Prerequisites live in an edge table and
  appear in no sentence anywhere, so without it *"what do I need before MEL251?"*
  can't be answered by text retrieval.

## Modelled but empty

`Module` and `Exercise` are in the schema and unpopulated. Module data needs each
resource's own page, which the providers render in JavaScript. Exercises were
marked bonus and not reached. Named in the README rather than filled with blanks.
