# Part D — Data quality report

Generated from `data/processed/run_manifest.json` and `validation_report.json`. Run of 2026-11-09; programme: B.Tech Mechanical Engineering; elapsed 0.03s.

## 1. Volumes

| Entity | Records exported |
|---|---:|
| course | 41 |
| prerequisite_edge | 6 |
| skill | 60 |
| course_skill_link | 66 |
| academic_rule | 35 |
| resource | 56 |
| resource_skill_link | 109 |
| **chunks** | **223** |

## 2. Field completeness

### `course`

`n = 41`

- **100% filled (11):** `code`, `course_type`, `dept`, `mode`, `programme`, `retrieved_on`, `source_note`, `source_type`, `source_url`, `title`, `verification_status`
- **Partially filled:** `credits` 95.1%, `credit_structure` 95.1%, `semester_offered` 85.4%, `syllabus_text` 53.7%, `overlap_with` 24.4%
- **0% filled (4):** `credits_raw`, `objectives`, `verified_by`, `verified_on`

### `resource`

`n = 56`

- **100% filled (12):** `fmt`, `id`, `licence_name`, `licence_verified_on`, `provider`, `retrieved_on`, `source_note`, `source_type`, `source_url`, `title`, `url`, `verification_status`
- **Partially filled:** `host_institute` 53.6%, `licence_version` 35.7%, `licence_url` 35.7%, `instructor` 16.1%, `description` 16.1%, `duration_value` 12.5%, `duration_unit` 12.5%
- **0% filled (2):** `verified_by`, `verified_on`

### `academic_rule`

`n = 35`

- **100% filled (10):** `applies_to`, `category`, `clause_ref`, `id`, `retrieved_on`, `source_note`, `source_type`, `source_url`, `text`, `verification_status`
- **Partially filled:** `numeric_limit` 74.3%, `unit` 74.3%
- **0% filled (2):** `verified_by`, `verified_on`

### `skill`

`n = 60`

- **100% filled (6):** `id`, `name`, `origin`, `source_note`, `source_type`, `verification_status`
- **Partially filled:** `level` 98.3%, `parent_skill` 98.3%
- **0% filled (4):** `retrieved_on`, `source_url`, `verified_by`, `verified_on`

### `prerequisite_edge`

`n = 6`

- **100% filled (8):** `course`, `kind`, `requires`, `retrieved_on`, `source_note`, `source_type`, `source_url`, `verification_status`
- **0% filled (2):** `verified_by`, `verified_on`

### `course_skill_link`

`n = 66`

- **100% filled (9):** `course`, `depth`, `evidence`, `retrieved_on`, `skill`, `source_note`, `source_type`, `source_url`, `verification_status`
- **0% filled (2):** `verified_by`, `verified_on`

### `resource_skill_link`

`n = 109`

- **100% filled (8):** `level`, `resource`, `retrieved_on`, `skill`, `source_note`, `source_type`, `source_url`, `verification_status`
- **0% filled (2):** `verified_by`, `verified_on`


## 3. Checks the validator runs, and what they caught

18 checks ran. Result: **0 error(s), 17 warning(s)**.

| Check | Severity | Hits |
|---|---|---:|
| `brief_minimums` | — | 0 |
| `course_code_shape` | — | 0 |
| `credits_match_ltp` | — | 0 |
| `credits_numeric` | WARN | 2 |
| `duplicate_course_code` | — | 0 |
| `duplicate_resource_url` | — | 0 |
| `enum_values` | — | 0 |
| `illustrative_rows_flagged` | — | 0 |
| `link_targets_exist` | — | 0 |
| `orphan_course_no_skill` | WARN | 15 |
| `prereq_no_cycle` | — | 0 |
| `prereq_target_exists` | — | 0 |
| `provenance_complete` | — | 0 |
| `resource_licence_recorded` | — | 0 |
| `rule_quotable` | — | 0 |
| `semester_range` | — | 0 |
| `skill_parent_exists` | — | 0 |
| `skill_taxonomy_no_cycle` | — | 0 |

**Warnings (reported, do not block):**

- `credits_numeric` — course `NCN100`: no credits: expected for a non-graded course, which carries units rather than credits
- `credits_numeric` — course `LAN103`: no credits: expected for a non-graded course, which carries units rather than credits
- `orphan_course_no_skill` — course `MAL100`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `CYL100`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `PHL101`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `CYL101`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `CYP102`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `PHP102`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `EEL101`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `MAL101`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `ECL101`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `BML101`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `LAL100`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `LAL101`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `UGQ301`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `NCN100`: no course_skill_link; course contributes nothing to gap analysis
- `orphan_course_no_skill` — course `LAN103`: no course_skill_link; course contributes nothing to gap analysis

## 4. Chunk profile

- 223 chunks; token **estimate** (characters ÷ 4, no tokenizer and no model call): min 24, median 68, max 286, total 19,289
- By type: `course_card`=41, `resource_desc`=56, `rule`=35, `skill_node`=60, `syllabus`=31
- By source type: `manual`=167, `open-licence`=56
- By verification status: `unverified`=223
- Academic rules are never split across chunks, so every constraint stays quotable in full. Course syllabi are split on sentence boundaries with a ~150-character overlap.

## 5. What the parser reported

- MEP376->ME334: remapped to MEL334 per corrections.csv
- MEL414->MEL111: DROPPED per corrections.csv — MEL111 appears nowhere in the Courses of Study except as this course's prerequisite and overlap. No candidate course can be identified without guessing, so the edge is omitted rather than remapped. The printed value is preserved in prerequisites.csv source_note and reported in DATA_QUALITY.md.

## 6. Corrections applied to source defects

Source documents contain real errors. Each is transcribed AS PRINTED and repaired here, with a reason, so the defect stays visible in the data. Full write-up in `SOURCE_DEFECTS.md`.

| Record | Action | Reason |
|---|---|---|
| `MEP376 -> ME334` | remap to `MEL334` | ME334 is not a course code in the Courses of Study. The only course whose code differs by the missing 'L' is MEL334 Theory of Mechanisms and Machines, whose vibration and dynamics content matches this lab's experiments. Treated as a typographical omission of the 'L' in the published document. |
| `MEL414 -> MEL111` | drop | MEL111 appears nowhere in the Courses of Study except as this course's prerequisite and overlap. No candidate course can be identified without guessing, so the edge is omitted rather than remapped. The printed value is preserved in prerequisites.csv source_note and reported in DATA_QUALITY.md. |

## 7. Independent cross-check of the hand transcription

The curriculum was transcribed by hand, so `tools/crosscheck_pdf.py` re-reads the source PDF with pdfplumber and diffs every four-part L-T-P-C value it can extract against `courses.csv`. It writes nothing to the dataset.

- **33 courses verified against the PDF, 0 disagreements.**
- Full output: `PDF_CROSSCHECK.md`. Re-run with `python tools/crosscheck_pdf.py`.

## 8. How a teammate verifies a sample

Every record carries `source_url`, `retrieved_on`, `source_type` and `verification_status`. To verify a sample:

1. `shuf -n 10 data/processed/resource.csv` (or open the CSV and pick rows at random).
2. Open each row's `source_url`. Confirm the `title`, `provider`, `host_institute` and `instructor` against what the page states.
3. Check `source_note`: rows marked `tier=page_read` should match the linked document in detail; rows marked `tier=listing_only` are only guaranteed to have a correct title/URL pair, and their `duration_value` is deliberately null.
4. Set `verification_status=human_verified`, `verified_on` and `verified_by` on rows that check out; set `disputed` and add a `source_note` on rows that do not.
5. Re-run `python run_pipeline.py`. The validator warns on any row marked `human_verified` without a `verified_on` date, so the audit trail cannot be half-filled.

The same procedure applies to `course.csv` once the institute curriculum document has been parsed; its `source_url` points at the published Courses-of-Study page for the programme.
