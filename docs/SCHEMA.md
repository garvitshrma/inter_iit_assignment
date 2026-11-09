# Part B — Schema, and why it differs from the starting point

The brief's table was the starting point. Everything below is either an addition
or a change, with the reason. Entity definitions live in `pipeline/models.py`;
this file is the argument for them.

## Universal provenance block

Every entity carries `source_url`, `retrieved_on`, `source_type` — as the brief
requires — plus three fields it does not ask for:

| Field | Why |
|---|---|
| `source_note` | Free text recording *how* a record was obtained: which PDF page a table came from, whether a resource page was actually opened or only listed, whether a number was derived. Without it, two rows with identical provenance triples can have very different trustworthiness and nothing records the difference. |
| `verification_status` (`unverified` / `human_verified` / `disputed`), `verified_on`, `verified_by` | Part D asks how a teammate could verify a sample of records. That is far easier to answer if verification is a field rather than a promise. A reviewer flips rows to `human_verified` as they check them, and the validator warns on any row marked verified without a date — so the audit trail cannot be half-filled. |

### `source_type` gains a fourth value: `illustrative`

The brief lists `official` / `open-licence` / `manual`. In a one-day build some
rows are unavoidably placeholder, and a pipeline that cannot distinguish a
placeholder from a retrieved record will eventually push fabricated data into an
embedding index — the precise failure this assignment is designed to detect.

So placeholders are marked `illustrative`, and the exporter **refuses to write
them** to `data/processed/` unless `--allow-illustrative` is passed; when it is,
they go to separate `*_illustrative.csv` files. Fabrication is made structurally
hard rather than merely discouraged.

## Changes by entity

### Course
- **`credit_structure` added alongside `credits`.** Indian curricula express load
  as Lecture–Tutorial–Practical ("3-1-0"). The integer alone loses the information
  the brief asks for under *mode*. Both are kept, and the validator cross-checks
  them. It flags a mismatch only when `credits` matches **neither** `L+T+P` nor
  `L+T+P/2`, because institutes differ on how practicals are weighted and
  asserting one convention would be a guess.
- **`credits_raw` added.** When normalisation cannot read a number, the original
  string is preserved so the validator can report *"credits value `'three'` is not
  numeric"* rather than the downstream symptom *"no credits present"*. The brief
  names non-numeric credits as a check, so the check should name the value.
- **`objectives` and `syllabus_text` kept separate.** They answer different
  questions ("what will I be able to do" vs "what topics are covered") and they
  chunk differently.
- **`programme`** is on the course, not assumed globally, so a second programme
  can be added later without a migration.

### Prerequisite edge
- **`kind` gains `concurrent`.** Real curricula have co-requisites — courses that
  must be taken in the same semester, not before. Collapsing those into
  `hard` breaks ordering logic (a co-requisite is not a predecessor); collapsing
  them into `recommended` loses the constraint entirely.
- Cycle detection runs over `hard` and `concurrent` edges only. A `recommended`
  edge forming a loop is odd but is not a scheduling error, and treating it as one
  would produce false failures on real data.

### Skill
- **`origin` added (`syllabus_phrase` / `author_inferred`).** This is the honesty
  field. The taxonomy is the author's invention; the courses and resources are
  retrieved. Those are different epistemic categories and the schema should say
  which is which. The validator exempts `author_inferred` skills from the
  provenance requirement precisely so there is no incentive to invent a citation
  for a node nobody published.
- `parent_skill` makes the taxonomy a tree, and the validator checks it for cycles
  the same way it checks prerequisites — a taxonomy loop would make any
  "what's the parent domain" traversal non-terminating.

### Course–skill link
- **`evidence` added.** The syllabus phrase the depth judgement was made from. A
  reviewer disagreeing with "advanced" can see what the call was based on without
  re-reading the whole syllabus. This is what makes the most subjective part of
  the dataset auditable.

### Academic rule
- **`numeric_limit` + `unit` split**, and `clause_ref` added. "7.0" is useless
  without knowing it is a CGPA and not a credit count; `clause_ref` lets the buddy
  cite the rule by its number, which is what makes a constraint answer credible.
- `applies_to` is required in spirit (warned on when absent) because an unscoped
  rule cannot be used for constraint checking — the buddy would not know whether
  it applies to the student asking.

### Resource
- **`licence` split into `licence_name`, `licence_version`, `licence_url`,
  `licence_verified_on`.** Forced by the data: MIT OCW states CC BY-NC-SA **4.0**
  with a linked deed; NPTEL's footer states "CC BY-NC-SA" with **no version and no
  deed**. One string would have forced either a guess ("4.0") or the loss of the
  version where it *is* known. `licence_verified_on` records when the provider's
  terms page was actually read, since licences change.
- **`duration_value` + `duration_unit`** rather than a single "duration", because
  sources state weeks, hours, or nothing at all, and mixing units in one column
  makes the field unusable for filtering.

### Chunk
- `parent_id`, `parent_type`, `chunk_type`, `ordinal`, `filter_metadata` and the
  full provenance block, as the brief asks.
- **`token_estimate`, deliberately named as an estimate** — characters ÷ 4. No
  tokenizer is used and no model is called, per the no-embeddings rule. Naming it
  `token_count` would invite someone downstream to trust it.
- **A `course_card` chunk type that has no equivalent in the source data.** It is a
  compact structured restatement of each course's facts — code, title, credits,
  semester, prerequisites, skills. This is what answers *"what are the
  prerequisites for X"* reliably; without it a retriever has to luck into the
  right syllabus fragment, and prerequisite information is scattered across the
  prerequisite table rather than present in the syllabus prose at all.

## Entities from the brief that are present but unpopulated

`Module / lesson` and `Exercise` are modelled in spirit but not populated. Module
data is only available by opening each resource's own page, which the client-side
rendering on the provider's course pages blocked (see `SOURCES.md`); exercises
were marked bonus in the brief and were not reached. Both are named in the
README's known gaps rather than stubbed with empty rows.
