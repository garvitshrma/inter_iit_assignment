#!/usr/bin/env python3
"""
Generates docs/DATA_QUALITY.md (Part D) from a run's artefacts.

The report is generated, not hand-written, so the numbers in it cannot drift
away from what the pipeline actually produced. Run the pipeline first, then this.

    python run_pipeline.py --raw <dir> --out <dir> [--allow-illustrative]
    python tools/make_quality_report.py --out <dir>
"""
import argparse, json, os, collections

def pct_table(fill, entity):
    if entity not in fill:
        return "_no records_\n"
    f = fill[entity]["fields"]
    n = fill[entity]["n_records"]
    full  = sorted([k for k, v in f.items() if v == 100.0])
    part  = sorted([(k, v) for k, v in f.items() if 0 < v < 100], key=lambda x: -x[1])
    empty = sorted([k for k, v in f.items() if v == 0.0])
    out = [f"`n = {n}`\n"]
    if full:
        out.append(f"- **100% filled ({len(full)}):** {', '.join('`%s`' % x for x in full)}")
    if part:
        out.append("- **Partially filled:** " + ", ".join(f"`{k}` {v}%" for k, v in part))
    if empty:
        out.append(f"- **0% filled ({len(empty)}):** {', '.join('`%s`' % x for x in empty)}")
    return "\n".join(out) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/processed")
    ap.add_argument("--report", default="docs/DATA_QUALITY.md")
    a = ap.parse_args()

    man = json.load(open(os.path.join(a.out, "run_manifest.json"), encoding="utf-8"))
    findings = json.load(open(os.path.join(a.out, "validation_report.json"), encoding="utf-8"))
    chunks_path = os.path.join(a.out, "chunks.jsonl")
    chunks = [json.loads(l) for l in open(chunks_path, encoding="utf-8")] if os.path.exists(chunks_path) else []

    w, fill, run = man["written"], man["fill_rates"], man["run"]
    by_check = collections.Counter((f["check"], f["severity"]) for f in findings)
    errs = [f for f in findings if f["severity"] == "ERROR"]
    warns = [f for f in findings if f["severity"] == "WARN"]
    toks = [c["token_estimate"] for c in chunks]
    ctypes = collections.Counter(c["chunk_type"] for c in chunks)
    stypes = collections.Counter(c["source_type"] for c in chunks)
    verif = collections.Counter(c["verification_status"] for c in chunks)

    L = []
    A = L.append
    A("# Part D — Data quality report\n")
    A(f"Generated from `{a.out}/run_manifest.json` and `validation_report.json`. "
      f"Run of {run['started']}; programme: {run['programme']}; "
      f"elapsed {run['elapsed_seconds']}s.\n")

    A("## 1. Volumes\n")
    A("| Entity | Records exported |")
    A("|---|---:|")
    for k in ("course", "prerequisite_edge", "skill", "course_skill_link",
              "academic_rule", "resource", "resource_skill_link"):
        A(f"| {k} | {w.get(k, 0)} |")
    A(f"| **chunks** | **{w.get('chunks', 0)}** |")
    ill = man.get("illustrative_counts") or {}
    if ill:
        A("")
        A("Placeholder rows held back from the real export "
          f"(`source_type=illustrative`): {', '.join(f'{k}={v}' for k, v in sorted(ill.items()))}.")
    A("")

    A("## 2. Field completeness\n")
    for e in ("course", "resource", "academic_rule", "skill",
              "prerequisite_edge", "course_skill_link", "resource_skill_link"):
        A(f"### `{e}`\n")
        A(pct_table(fill, e))
    A("")

    A("## 3. Checks the validator runs, and what they caught\n")
    A(f"{len(run['checks_run'])} checks ran. "
      f"Result: **{run['n_errors']} error(s), {run['n_warnings']} warning(s)**.\n")
    A("| Check | Severity | Hits |")
    A("|---|---|---:|")
    for chk in run["checks_run"]:
        e_hits, w_hits = by_check.get((chk, "ERROR"), 0), by_check.get((chk, "WARN"), 0)
        sev = "ERROR" if e_hits else ("WARN" if w_hits else "—")
        A(f"| `{chk}` | {sev} | {e_hits + w_hits} |")
    A("")
    if errs:
        A("**Errors (these abort the run; nothing is exported):**\n")
        for f in errs[:25]:
            A(f"- `{f['check']}` — {f['entity']} `{f['record_id']}`: {f['message']}")
        if len(errs) > 25:
            A(f"- _…and {len(errs)-25} more; see `validation_report.csv`_")
        A("")
    if warns:
        A("**Warnings (reported, do not block):**\n")
        for f in warns[:20]:
            A(f"- `{f['check']}` — {f['entity']} `{f['record_id']}`: {f['message']}")
        if len(warns) > 20:
            A(f"- _…and {len(warns)-20} more_")
        A("")

    A("## 4. Chunk profile\n")
    if toks:
        toks_s = sorted(toks)
        A(f"- {len(toks)} chunks; token **estimate** (characters ÷ 4, no tokenizer "
          f"and no model call): min {toks_s[0]}, median {toks_s[len(toks_s)//2]}, "
          f"max {toks_s[-1]}, total {sum(toks):,}")
        A("- By type: " + ", ".join(f"`{k}`={v}" for k, v in sorted(ctypes.items())))
        A("- By source type: " + ", ".join(f"`{k}`={v}" for k, v in sorted(stypes.items())))
        A("- By verification status: " + ", ".join(f"`{k}`={v}" for k, v in sorted(verif.items())))
        A("- Academic rules are never split across chunks, so every constraint stays "
          "quotable in full. Course syllabi are split on sentence boundaries with a "
          "~150-character overlap.")
    else:
        A("_No chunks were exported in this run._")
    A("")

    if run.get("parse_notes"):
        A("## 5. What the parser reported\n")
        for n in run["parse_notes"]:
            A(f"- {n}")
        A("")

    # corrections + independent cross-check
    import csv as _csv
    corr_path = "data/raw/curriculum/corrections.csv"
    if os.path.exists(corr_path):
        with open(corr_path, newline="", encoding="utf-8-sig") as fh:
            corr = list(_csv.DictReader(fh))
        if corr:
            A("## 6. Corrections applied to source defects\n")
            A("Source documents contain real errors. Each is transcribed AS PRINTED and "
              "repaired here, with a reason, so the defect stays visible in the data. "
              "Full write-up in `SOURCE_DEFECTS.md`.\n")
            A("| Record | Action | Reason |")
            A("|---|---|---|")
            for c in corr:
                rec = f"{c.get('match_course','')} -> {c.get('match_requires','')}"
                act = c.get("action", "")
                if act == "remap":
                    act = f"remap to `{c.get('new_value','')}`"
                A(f"| `{rec}` | {act} | {c.get('reason','')} |")
            A("")

    xc = "docs/PDF_CROSSCHECK.md"
    if os.path.exists(xc):
        head = open(xc, encoding="utf-8").read()
        import re as _re
        m = _re.search(r"\| L-T-P-C agrees with the PDF \| (\d+) \|", head)
        d = _re.search(r"\| L-T-P-C disagrees \| (\d+) \|", head)
        A("## 7. Independent cross-check of the hand transcription\n")
        A("The curriculum was transcribed by hand, so `tools/crosscheck_pdf.py` re-reads "
          "the source PDF with pdfplumber and diffs every four-part L-T-P-C value it can "
          "extract against `courses.csv`. It writes nothing to the dataset.\n")
        if m and d:
            A(f"- **{m.group(1)} courses verified against the PDF, "
              f"{d.group(1)} disagreements.**")
        A("- Full output: `PDF_CROSSCHECK.md`. Re-run with `python tools/crosscheck_pdf.py`.")
        A("")

    A("## 8. How a teammate verifies a sample\n")
    A("Every record carries `source_url`, `retrieved_on`, `source_type` and "
      "`verification_status`. To verify a sample:\n")
    A("1. `shuf -n 10 data/processed/resource.csv` (or open the CSV and pick rows at random).")
    A("2. Open each row's `source_url`. Confirm the `title`, `provider`, "
      "`host_institute` and `instructor` against what the page states.")
    A("3. Check `source_note`: rows marked `tier=page_read` should match the linked "
      "document in detail; rows marked `tier=listing_only` are only guaranteed to have "
      "a correct title/URL pair, and their `duration_value` is deliberately null.")
    A("4. Set `verification_status=human_verified`, `verified_on` and `verified_by` on "
      "rows that check out; set `disputed` and add a `source_note` on rows that do not.")
    A("5. Re-run `python run_pipeline.py`. The validator warns on any row marked "
      "`human_verified` without a `verified_on` date, so the audit trail cannot be "
      "half-filled.\n")
    A("The same procedure applies to `course.csv` once the institute curriculum "
      "document has been parsed; its `source_url` points at the published "
      "Courses-of-Study page for the programme.\n")

    os.makedirs(os.path.dirname(a.report), exist_ok=True)
    open(a.report, "w", encoding="utf-8").write("\n".join(L))
    print(f"wrote {a.report} ({len(chr(10).join(L)):,} chars)")

if __name__ == "__main__":
    main()
