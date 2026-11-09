# Part E — Ideas

## Three questions it could answer well

**"I want to work in thermal design. Which courses do I still need, and in what
order?"**

This is the join the schema was built for. The skill taxonomy gives the target
competencies, `course_skill_link` says which courses teach them and how deeply,
`prerequisite_edge` gives a valid order, and the credit-limit rule caps how much
fits in a semester. The answer can cite real course codes and show the source for
each. The `course_card` chunk is what makes it work — prerequisites live in an
edge table, not in any sentence, so without it the information is invisible to
text retrieval.

**"Heat Transfer didn't click. What free material covers the same ground?"**

`course_skill_link` and `resource_skill_link` meet at the skill, so matching
happens on competency rather than title. MEL313 and NPTEL's *Heat and Mass
Transfer* share almost no words but both map to conduction, convection, radiation
and heat exchangers. Because the licence is recorded and verified, the buddy can
also say whether the material may be redistributed — both NPTEL and MIT OCW are
NonCommercial.

**"Can I register for MEL501 next semester?"**

Hard prerequisite edges answer the structural half; the rules answer the policy
half, quoted in full with a clause number. For MEL501 the answer is **no** — it
declares 30% overlap with MEL304, a core course, and UG Manual 2.2.6 caps overlap
at 25%. Neither document says that on its own.

## What it couldn't answer

- **Anything about a specific student.** By design — no grades, no completed
  courses, no CGPA. "Am I eligible for Honours?" can only return the rule, never
  yes or no. Any eligibility feature needs the student's record at runtime.
- **This term's actual offering.** `semester_offered` is the curriculum's typical
  semester, not a timetable. Who's teaching, when it meets, whether it clashes,
  whether seats remain — none of that is in a curriculum document.
- **Difficulty or quality.** "Is this elective scoring?" Nothing here measures
  difficulty or grade distribution, and credits are not difficulty.
- **Whether a specific NPTEL course will be accepted for credit.** The data can
  quote the policy; the decision is the Department's against an approved
  equivalence list. The buddy has to route this to a human.
- **Anything beyond the published syllabus.** No lecture content, no past papers.
  "Explain entropy" is general tutoring, which this dataset doesn't help with.

## What I'd add next

1. **A second programme.** Everything is already keyed by `programme`, so this
   tests whether the schema really generalises.
2. **Module-level records.** A 12-week course is too coarse to recommend to
   someone with one weak topic. `Module` is already modelled.
3. **Verification driven up on a stratified sample.** Fill rate measures
   completeness and says nothing about correctness, and correctness is what
   matters for a buddy citing course codes.
4. **Then embeddings.** `filter_metadata` is what makes them usable: filtering on
   programme, semester and skill before the vector search is what stops a
   semester-7 elective being offered to a second-year student.
