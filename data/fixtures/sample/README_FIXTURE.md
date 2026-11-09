# Sample fixture — ILLUSTRATIVE DATA ONLY

Every course, prerequisite edge, course-skill link and academic rule in this
directory was **written by the dataset author** to exercise the pipeline. None of
it is IIT Bhilai data. Each row carries `source_type=illustrative`, which means
the exporter refuses to write it to `data/processed/` unless
`--allow-illustrative` is passed explicitly.

The `skills.csv`, `resources.csv` and `resource_skills.csv` in this directory are
copies of the real files from `data/raw/` — those resources were genuinely
retrieved from NPTEL and MIT OpenCourseWare on 2026-11-09.

Purpose: Part C of the brief permits demonstrating the pipeline on a small
sample. This fixture is that sample, and it is kept separate from `data/raw/`
so that placeholder course rows can never be mistaken for retrieved ones.
