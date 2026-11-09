# Part D — Data quality report

Generated from `data/fixtures/sample_out/run_manifest.json` and `validation_report.json`. Run of 2026-11-09; programme: B.Tech Mechanical Engineering; elapsed 0.02s.

## 1. Volumes

| Entity | Records exported |
|---|---:|
| course | 0 |
| prerequisite_edge | 0 |
| skill | 60 |
| course_skill_link | 0 |
| academic_rule | 0 |
| resource | 56 |
| resource_skill_link | 109 |
| **chunks** | **138** |

Placeholder rows held back from the real export (`source_type=illustrative`): academic_rule=4, course=6, course_skill_link=19, prerequisite_edge=5.

## 2. Field completeness

### `course`

_no records_

### `resource`

`n = 56`

- **100% filled (12):** `fmt`, `id`, `licence_name`, `licence_verified_on`, `provider`, `retrieved_on`, `source_note`, `source_type`, `source_url`, `title`, `url`, `verification_status`
- **Partially filled:** `host_institute` 53.6%, `licence_version` 35.7%, `licence_url` 35.7%, `instructor` 16.1%, `description` 16.1%, `duration_value` 12.5%, `duration_unit` 12.5%
- **0% filled (2):** `verified_by`, `verified_on`

### `academic_rule`

_no records_

### `skill`

`n = 60`

- **100% filled (6):** `id`, `name`, `origin`, `source_note`, `source_type`, `verification_status`
- **Partially filled:** `level` 98.3%, `parent_skill` 98.3%
- **0% filled (4):** `retrieved_on`, `source_url`, `verified_by`, `verified_on`

### `prerequisite_edge`

_no records_

### `course_skill_link`

_no records_

### `resource_skill_link`

`n = 109`

- **100% filled (8):** `level`, `resource`, `retrieved_on`, `skill`, `source_note`, `source_type`, `source_url`, `verification_status`
- **0% filled (2):** `verified_by`, `verified_on`


## 3. Checks the validator runs, and what they caught

16 checks ran. Result: **0 error(s), 4 warning(s)**.

| Check | Severity | Hits |
|---|---|---:|
| `course_code_shape` | — | 0 |
| `credits_match_ltp` | — | 0 |
| `credits_numeric` | — | 0 |
| `duplicate_course_code` | — | 0 |
| `duplicate_resource_url` | — | 0 |
| `enum_values` | — | 0 |
| `illustrative_rows_flagged` | WARN | 4 |
| `link_targets_exist` | — | 0 |
| `prereq_no_cycle` | — | 0 |
| `prereq_target_exists` | — | 0 |
| `provenance_complete` | — | 0 |
| `resource_licence_recorded` | — | 0 |
| `rule_quotable` | — | 0 |
| `semester_range` | — | 0 |
| `skill_parent_exists` | — | 0 |
| `skill_taxonomy_no_cycle` | — | 0 |

**Warnings (reported, do not block):**

- `illustrative_rows_flagged` — course `6 record(s)`: source_type=illustrative: placeholders, withheld from export unless --allow-illustrative is passed [DEMO101, DEMO102, DEMO103, DEMO104, DEMO105, +1 more]
- `illustrative_rows_flagged` — prerequisite_edge `5 record(s)`: source_type=illustrative: placeholders, withheld from export unless --allow-illustrative is passed [DEMO103->DEMO101, DEMO103->DEMO102, DEMO106->DEMO104, DEMO105->DEMO104, DEMO102->DEMO101]
- `illustrative_rows_flagged` — academic_rule `4 record(s)`: source_type=illustrative: placeholders, withheld from export unless --allow-illustrative is passed [DEMO-RULE-01, DEMO-RULE-02, DEMO-RULE-03, DEMO-RULE-04]
- `illustrative_rows_flagged` — course_skill_link `19 record(s)`: source_type=illustrative: placeholders, withheld from export unless --allow-illustrative is passed [DEMO101~SK-LAWS, DEMO101~SK-PROPS, DEMO101~SK-CYCLES, DEMO102~SK-FLUIDSTAT, DEMO102~SK-VISC, +14 more]

## 4. Chunk profile

- 138 chunks; token **estimate** (characters ÷ 4, no tokenizer and no model call): min 33, median 66, max 166, total 9,789
- By type: `course_card`=6, `objectives`=6, `resource_desc`=56, `rule`=4, `skill_node`=60, `syllabus`=6
- By source type: `illustrative`=22, `manual`=60, `open-licence`=56
- By verification status: `unverified`=138
- Academic rules are never split across chunks, so every constraint stays quotable in full. Course syllabi are split on sentence boundaries with a ~150-character overlap.

## 6. How a teammate verifies a sample

Every record carries `source_url`, `retrieved_on`, `source_type` and `verification_status`. To verify a sample:

1. `shuf -n 10 data/processed/resource.csv` (or open the CSV and pick rows at random).
2. Open each row's `source_url`. Confirm the `title`, `provider`, `host_institute` and `instructor` against what the page states.
3. Check `source_note`: rows marked `tier=page_read` should match the linked document in detail; rows marked `tier=listing_only` are only guaranteed to have a correct title/URL pair, and their `duration_value` is deliberately null.
4. Set `verification_status=human_verified`, `verified_on` and `verified_by` on rows that check out; set `disputed` and add a `source_note` on rows that do not.
5. Re-run `python run_pipeline.py`. The validator warns on any row marked `human_verified` without a `verified_on` date, so the audit trail cannot be half-filled.

The same procedure applies to `course.csv` once the institute curriculum document has been parsed; its `source_url` points at the published Courses-of-Study page for the programme.
