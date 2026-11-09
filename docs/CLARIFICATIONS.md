# Clarifying questions

The brief's ground rules say to ask for clarifications any time, and that good
questions count in your favour while guessing silently does not.

These are the four places where the brief could reasonably be read more than one
way, and where the choice changes the dataset. Each one records the option taken
so that no question held up the work. The message as sent is in
`CLARIFICATIONS_TO_SEND.md`.

---

### 1. Should the skill taxonomy be our own, or mapped to a standard framework?

Our own fits one curriculum more closely. A standard framework (NBA graduate
attributes, O*NET) can be compared across institutes, which would matter if the
buddy ever covers more than one.

**Chose:** our own. All 60 skills are tagged `origin=author_inferred`, so the
taxonomy stays clearly separate from retrieved data and can be remapped later
without touching a single course or resource record.

---

### 2. Courses with no prerequisites stated anywhere — leave empty, or infer them?

Empty is honest. Inferred is more useful to someone planning a semester.

**Chose:** empty. An inferred prerequisite would be a record with no source, and
every claim in this dataset is supposed to trace back to a document. If inferred
edges turn out to be more useful than their absence, the schema can hold them
safely as `kind=recommended` with a source type of their own.

---

### 3. Does "at least 15 courses" mean 15 from the programme itself?

**Chose:** the programme's own course list, including the electives it offers —
41 courses, so the minimum is met either way. Electives from other departments
that a Mechanical student may take are in scope but were not needed.

---

### 4. Should a missing learning-objectives field be an error or a warning?

It is a warning. As an error, the pipeline would stop on data that is simply
incomplete at the source, and whoever had to clear the error would be tempted to
write objectives themselves — which is the exact problem this assignment is built
to catch.

As it turned out, IIT Bhilai's Courses of Study publishes a syllabus for each
course but no separate learning objectives at all, so the field is 0% filled
because of the source, not because of an oversight.

Raised because it is a judgement about where to apply pressure, and a reviewer
may want it stricter.

---

## Two questions answered without asking

Both came up while planning, and both were settled by building each option rather
than spending a question:

- **Full run or small sample?** (Part C allows a sample.) Both work:
  `make pipeline` runs everything, `--sample N` takes a connected subgraph, and
  `data/fixtures/sample/` shows all five stages on clearly-labelled data.
- **Quality report per entity or per field?** Per field, grouped into fully,
  partly and never filled, since what matters is *which* fields are thin. Record
  counts per entity are there too.
