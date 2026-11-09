# Part C — Pipeline design

One command: `python run_pipeline.py` (or `make pipeline`). Flags: `--raw`,
`--out`, `--sample N`, `--allow-illustrative`, `--ignore-errors`.

What each stage promises, and how it's allowed to fail.

## 1. Ingest

**In:** everything in `data/raw/`. **Out:** an inventory of every file, recorded
in `run_manifest.json`.

- It never writes to `data/raw/`. A bad parse is fixed by re-running, not
  re-downloading.
- A PDF is only parsed if `pdf_sources.json` records the URL it came from.
  Otherwise it's skipped loudly, since rows from it would have no `source_url`.
- `"parse": false` marks a PDF that is *provenance* for hand-typed rows rather
  than something to auto-parse. Needed here: the institute's PDF covers every
  programme, so auto-parsing would drag other branches into a dataset that's
  supposed to cover one.

**Fails:** missing `data/raw/` exits 2. An unregistered PDF is a warning.

## 2. Parse and normalise

**In:** raw files. **Out:** typed records with canonical values.

- One form per concept. `mel 251` / `MEL-251` / `MEL251` become one course;
  `V` / `Sem 5` / `5th` become `5`. Without this the duplicate check misses
  duplicates that differ by a space.
- **It never invents a value.** Given `3-0-2` with no total it leaves `credits`
  empty, because institutes weight practicals differently and a computed number
  would be a guess. Given `2-1-0-3` it takes the 3, because the source says so.
- Unreadable values are kept, not dropped, so the validator can name them.
- Source defects are repaired only through `corrections.csv`, each with a reason,
  and the original value is written into the record's `source_note`.

**Fails:** never fatally. Problems become notes for stage 3 to judge.

## 3. Validate

**In:** the parsed dataset. **Out:** findings, and a decision on whether to
continue.

- **ERROR stops the run and exports nothing.** A half-built knowledge base that
  looks complete is worse than an empty one, because whatever reads it will state
  its contents confidently.
- **WARN reports and continues.** A prerequisite naming a missing course is an
  ERROR — it silently breaks eligibility logic. A missing `objectives` field is a
  WARN, because the institute genuinely doesn't publish one, and stopping would
  pressure someone into writing plausible objectives. That is the exact failure
  this assignment tests for.
- Findings are actionable. Cycles report the path
  (`ME107 -> ME108 -> ME109 -> ME107`), not just that one exists.
- The same code produces the enforcement and the Part D report, so the report
  can't drift from what was checked.
- Proven by `data/fixtures/broken/`, which plants one defect per check.

**Fails:** exit 1, findings printed, `validation_report.json` written.
`--ignore-errors` is for inspecting later stages and is not for submission.

## 4. Chunk

**In:** validated data. **Out:** retrieval-sized pieces with parent, type, source
and filter metadata.

Chunking is rule-driven, not uniform, because chunk boundaries decide which
questions are answerable:

- **Rules are never split.** A limit whose number landed in the next chunk can't
  be cited, and a rule that can't be cited is worse than no rule.
- **Syllabi are split** on sentence boundaries with ~150 characters of overlap,
  since a syllabus covers several topics and a question targets one.
- **Every course gets a `course_card`** restating its structured facts, because
  prerequisites appear in no sentence anywhere.
- Every chunk carries `filter_metadata` so a consumer can filter before searching.
  No amount of embedding quality stops a semester-7 elective being offered to a
  second-year student; metadata does.

**Fails:** it can't. Pure function of validated data.

## 5. Export

**In:** data, chunks, findings. **Out:** `data/processed/` — CSV and JSON per
entity, `chunks.jsonl`, `validation_report.*`, `run_manifest.json`.

- **It stops here.** No embedding, no vector store, no LLM call.
  `make verify-no-embeddings` proves it by parsing imports.
- `illustrative` rows are refused unless `--allow-illustrative` is passed, and
  then go to separate files.
- Stale outputs are cleared so an old export can't be mistaken for this one. Where
  the directory can't be deleted it overwrites in place and says which files may
  be stale, rather than crashing after the work is done.
- `run_manifest.json` records the inputs, checks run, counts and fill rates, so a
  run can be audited afterwards.

## What day two does

`chunks.jsonl` is one JSON object per line: text, `filter_metadata`, provenance.
Embed `text`, store the vector next to the metadata, and retrieve with the
metadata filter applied first.

That step is left out deliberately. The brief forbids it, and the value here is
that the data is trustworthy — which is settled before any embedding exists.
