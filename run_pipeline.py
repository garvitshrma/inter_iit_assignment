#!/usr/bin/env python3
"""
One-command pipeline: raw files -> validated, chunked, metadata-rich outputs.

    python run_pipeline.py                      # full run over data/raw
    python run_pipeline.py --sample 5           # small-sample run (Part C)
    python run_pipeline.py --allow-illustrative # permit placeholder rows into export
    python run_pipeline.py --raw data/fixtures/broken   # prove the validator fires

Stages: ingest -> parse/normalise -> validate -> chunk -> export.
It stops before embedding, by design. Nothing here calls an embedding or LLM API.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import loaders
from pipeline.chunk import chunk_dataset
from pipeline.export import export
from pipeline.validate import Validator, ERROR

C = {"hdr": "\033[1;36m", "ok": "\033[0;32m", "warn": "\033[0;33m",
     "err": "\033[0;31m", "dim": "\033[2m", "off": "\033[0m"}
if not sys.stdout.isatty():
    C = {k: "" for k in C}


def banner(n, title):
    print(f"\n{C['hdr']}[stage {n}] {title}{C['off']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", default="data/raw", help="raw input directory")
    ap.add_argument("--out", default="data/processed", help="output directory")
    ap.add_argument("--sample", type=int, default=0,
                    help="cap each entity at N records (small-sample run)")
    ap.add_argument("--allow-illustrative", action="store_true",
                    help="allow source_type=illustrative rows into the export")
    ap.add_argument("--ignore-errors", action="store_true",
                    help="export even when validation errors are present (not for submission)")
    ap.add_argument("--programme", default="B.Tech Mechanical Engineering")
    args = ap.parse_args()

    t0 = time.time()
    today = dt.date.today().isoformat()
    print(f"{C['dim']}run started {dt.datetime.now().isoformat(timespec='seconds')} "
          f"| programme: {args.programme}{C['off']}")

    # ---------------------------------------------------- stage 1: ingest
    banner(1, "ingest — raw files are read, never written")
    if not os.path.isdir(args.raw):
        print(f"{C['err']}raw directory {args.raw} does not exist{C['off']}")
        return 2
    inventory = []
    for root, _dirs, files in os.walk(args.raw):
        for f in sorted(files):
            p = os.path.join(root, f)
            inventory.append((os.path.relpath(p, args.raw), os.path.getsize(p)))
    for rel, size in inventory:
        print(f"  {C['dim']}·{C['off']} {rel} ({size:,} bytes)")
    if not inventory:
        print(f"  {C['warn']}no raw files found{C['off']}")

    # Any institute PDF present is parsed as an additional official source.
    pdf_courses = []
    cur_dir = os.path.join(args.raw, "curriculum")
    manifest_path = os.path.join(cur_dir, "pdf_sources.json")
    pdf_manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as fh:
            pdf_manifest = json.load(fh)
    if os.path.isdir(cur_dir):
        for f in sorted(os.listdir(cur_dir)):
            if f.lower().endswith(".pdf"):
                meta = pdf_manifest.get(f, {})
                if not meta.get("source_url"):
                    print(f"  {C['warn']}{f}: no entry in pdf_sources.json — "
                          f"parsed rows would have no source_url, so it is skipped{C['off']}")
                    continue
                pdf_courses += loaders.parse_curriculum_pdf(
                    os.path.join(cur_dir, f), args.programme,
                    meta["source_url"], meta.get("retrieved_on", today))

    # -------------------------------------------- stage 2: parse / normalise
    banner(2, "parse & normalise — canonical codes, credits, semesters")
    data = loaders.load_dataset(args.raw)
    if pdf_courses:
        known = {c.code for c in data["course"]}
        added = [c for c in pdf_courses if c.code not in known]
        data["course"].extend(added)
        print(f"  {len(added)} course(s) added from PDF extraction "
              f"({len(pdf_courses) - len(added)} already present in CSV)")
    if args.sample:
        for k in data:
            data[k] = data[k][:args.sample]
        print(f"  {C['warn']}sample mode: each entity capped at {args.sample}{C['off']}")
    for k, v in data.items():
        print(f"  {k:22s} {len(v):4d}")
    for n in loaders.PARSE_NOTES:
        print(f"  {C['dim']}note:{C['off']} {n}")

    # ------------------------------------------------------ stage 3: validate
    banner(3, "validate — fails loudly")
    enforce = (not args.sample) and os.path.normpath(args.raw) == os.path.normpath("data/raw")
    if not enforce:
        print(f"  {C['dim']}coverage minimums not enforced (fixture or sample run){C['off']}")
    v = Validator(data, today=today, enforce_minimums=enforce)
    findings = v.run()
    print(f"  {len(v.checks_run)} checks run: {', '.join(sorted(set(v.checks_run)))}")
    for f in v.errors:
        print(f"  {C['err']}ERROR{C['off']} [{f.check}] {f.entity} {f.record_id}: {f.message}")
    for f in v.warnings:
        print(f"  {C['warn']}WARN {C['off']} [{f.check}] {f.entity} {f.record_id}: {f.message}")
    if not findings:
        print(f"  {C['ok']}no findings{C['off']}")
    print(f"  {len(v.errors)} error(s), {len(v.warnings)} warning(s)")

    if v.errors and not args.ignore_errors:
        print(f"\n{C['err']}pipeline aborted: {len(v.errors)} validation error(s). "
              f"Nothing was exported.{C['off']}")
        print(f"{C['dim']}Fix the raw data, or re-run with --ignore-errors to inspect "
              f"the downstream stages anyway.{C['off']}")
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "validation_report.json"), "w", encoding="utf-8") as fh:
            json.dump([f.as_row() for f in findings], fh, indent=2)
        return 1

    # --------------------------------------------------------- stage 4: chunk
    banner(4, "chunk — retrieval-sized, parent-linked, filterable")
    chunks = chunk_dataset(data)
    print(f"  {len(chunks)} chunks")
    if chunks:
        sizes = sorted(c.token_estimate for c in chunks)
        print(f"  token estimate: min {sizes[0]}, median {sizes[len(sizes)//2]}, max {sizes[-1]}")

    # -------------------------------------------------------- stage 5: export
    banner(5, "export — seed data + chunks.jsonl (stops before embedding)")
    if os.path.isdir(args.out):
        shutil.rmtree(args.out)
    summary = export(data, chunks, findings, args.out,
                     allow_illustrative=args.allow_illustrative)
    for k, n in summary["written"].items():
        print(f"  {k:28s} {n:5d}")
    if summary["illustrative_counts"] and not args.allow_illustrative:
        print(f"  {C['warn']}withheld placeholder rows "
              f"{summary['illustrative_counts']} — pass --allow-illustrative to include{C['off']}")

    summary["run"] = {"started": today, "programme": args.programme,
                      "sample": args.sample or None,
                      "allow_illustrative": args.allow_illustrative,
                      "raw_inventory": [{"file": r, "bytes": b} for r, b in inventory],
                      "checks_run": sorted(set(v.checks_run)),
                      "n_errors": len(v.errors), "n_warnings": len(v.warnings),
                      "parse_notes": loaders.PARSE_NOTES,
                      "elapsed_seconds": round(time.time() - t0, 2)}
    with open(os.path.join(args.out, "run_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)

    print(f"\n{C['ok']}done in {summary['run']['elapsed_seconds']}s{C['off']} "
          f"-> {args.out}/  (chunks.jsonl, *.csv, *.json, run_manifest.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
