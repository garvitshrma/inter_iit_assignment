# Clarifying questions

The brief invites clarifications and says good ones count. These were the
decisions where guessing silently would have been the wrong move. Each records
the assumption taken in the meantime, so the work was never blocked on an answer.

**1. Should the skill taxonomy be our own, or aligned to an existing framework?**
A bespoke taxonomy fits the curriculum better; an established one (NBA graduate
attributes, O*NET) is comparable across institutes and would matter if the buddy
ever spans more than one.
*Assumed:* bespoke, with `origin=author_inferred` on every node so the taxonomy
is clearly separable from retrieved data and can be re-mapped later.

**2. For courses whose prerequisites are not stated in any public document — leave
null, or infer from semester ordering and mark the inference?**
Null is honest; inferred is more useful to a planner.
*Assumed:* null. Inferring would mean a `prerequisite_edge` with no real source,
and the whole dataset's credibility rests on every edge being traceable. The
schema could carry inferred edges safely via `kind=recommended` plus a
`source_type` of its own if you would rather have them.

**3. Does "at least 15 courses" mean 15 from the programme's own core, or may
electives the programme permits from other departments count?**
*Assumed:* the programme's own course list, including electives it offers.
Cross-department electives a Mechanical student may take are in scope but were
not needed to clear the minimum.

**4. Part C says the pipeline may run on a small sample. If the full dataset is
small enough to run end to end, is a full run preferred, or do you specifically
want to see the sampling mechanism?**
*Assumed:* both are provided — `make pipeline` runs everything, `--sample N` caps
each entity, and a labelled fixture set demonstrates all five stages.

**5. For the quality report, do you want field-fill percentages per entity, or per
individual field?**
*Assumed:* per field, grouped into fully / partially / never populated, since the
useful signal is *which* fields are thin.

**6. Would you rather the validator treat a missing `objectives` field as an error
or a warning?**
It is currently a warning. Making it an error would abort runs over genuinely
incomplete public data, which pushes whoever is fixing it toward writing
plausible objectives — the exact failure mode this assignment tests for. Flagged
because it is a judgement about where to put the pressure, and you may disagree.
