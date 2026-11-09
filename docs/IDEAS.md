# Part E — Ideas note

## Three questions the buddy could answer well

**1. "I want to work in thermal design. Which courses do I still need, and in what order?"**

This is the join the schema was built for. The skill taxonomy gives a target set
of competencies; `course_skill_link` with its `depth` field says which courses
teach them and how deeply; `prerequisite_edge` gives a valid ordering; the
`credit_limit` rule constrains how much fits in one semester. The buddy can return
a semester-by-semester plan citing real course codes, and because every record
carries a `source_url` it can show *where* each claim came from. The `course_card`
chunk is what makes this work in retrieval — prerequisites live in an edge table,
not in syllabus prose, so without that synthesised chunk the information would be
invisible to a text retriever.

**2. "Heat Transfer didn't click for me. What free material covers the same ground?"**

`course_skill_link` and `resource_skill_link` meet at the skill, so matching
happens at competency level rather than by title similarity — a course covering
conduction, convection, radiation and heat exchangers maps to resources covering
those same nodes even when the titles share no words. Because `licence_name` is
recorded and verified, the buddy can also say whether a resource may be
redistributed, which matters the moment it is used in anything shared or
commercial (both NPTEL and MIT OCW are NonCommercial).

**3. "Can I register for Design of Machine Elements next semester?"**

Hard prerequisite edges answer the structural half, and the `prerequisite` and
`credit_limit` rules answer the policy half — quoted in full, with a clause
reference, because rules are never split across chunks. The answer is a
conditional one ("you need MEL-xxx completed, and this would put you at N
credits against a ceiling of 27, per clause 4.1"), which is the honest shape
given there is no student record in the data.

## What it could not answer

- **Anything about a specific student.** By design — the brief forbids real student
  records, so there are no grades, no completed-course lists, no CGPA. "Am I
  eligible for a Minor?" can only be answered as "the threshold is 7.0 CGPA at
  the end of semester 2, per clause X" and never as yes or no. Any eligibility
  feature has to take the student's own record as runtime input, not from here.
- **Anything about this term's actual offering.** `semester_offered` is the
  curriculum's *typical* semester, not a live timetable. Who is teaching,
  what time it meets, whether it clashes, whether seats remain, whether it is
  running at all this year — none of that is in a curriculum document.
- **Quality or difficulty judgements.** "Is this elective scoring?", "which
  professor grades easier?" Nothing in the data measures difficulty, grade
  distribution or teaching quality, and nothing should be inferred — credits are
  not difficulty.
- **Whether a particular NPTEL course will actually be accepted for credit.** The
  data can quote the MOOC-credit policy; the decision is a Department and Senate
  one against an approved equivalence list. The buddy must route this to a human
  rather than answer it.
- **Content beyond the published syllabus.** No lecture material, no past papers,
  no worked solutions. A question like "explain entropy" is a general-tutoring
  question that this knowledge base contributes nothing to beyond pointing at
  resources.

## What I would add next, in order

1. **The institute's own curriculum document, parsed** (see known gaps). Everything
   above is structurally ready and thinly populated until this lands.
2. **Module-level records.** The biggest retrieval win per unit of effort: a
   12-week course is too coarse a recommendation for a student who has one weak
   topic. `Module` is already modelled.
3. **`verification_status` driven to `human_verified` on a stratified sample** —
   say 20% of each entity — so the quality report can state a measured error rate
   instead of a field-fill percentage. Fill rate measures completeness; it says
   nothing about correctness, and correctness is what a buddy citing course codes
   actually needs.
4. **Only then, embeddings.** When that step comes, `filter_metadata` is what makes
   it usable: filtering on `programme`, `semester_offered`, `course_type` and
   `skill_ids` before the vector search keeps the buddy from recommending a
   semester-7 elective to a second-year student, which no amount of embedding
   quality would fix.
