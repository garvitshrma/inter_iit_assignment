#!/usr/bin/env python3
"""
Inspect chunks.jsonl by keyword and metadata filters. NO embeddings, NO model.

This exists to show what the dataset can support, and to make the chunk
metadata inspectable by hand. It is plain substring matching plus filtering on
filter_metadata -- deliberately dumb, because the retrieval step is day two's
job and the brief forbids starting it.

    python tools/query_demo.py --out data/processed "prerequisite"
    python tools/query_demo.py --type rule --out data/processed "credit"
    python tools/query_demo.py --skill SK-CASTING --out data/processed
    python tools/query_demo.py --semester 5 --type course_card --out data/processed
"""
import argparse, json, os, re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="*", help="substring(s), all must appear (case-insensitive)")
    ap.add_argument("--out", default="data/processed")
    ap.add_argument("--type", help="chunk_type filter, e.g. course_card, rule, resource_desc")
    ap.add_argument("--skill", help="only chunks whose filter_metadata.skill_ids contains this")
    ap.add_argument("--semester", type=int, help="filter_metadata.semester_offered")
    ap.add_argument("--provider", help="filter_metadata.provider, e.g. NPTEL")
    ap.add_argument("-n", type=int, default=5, help="max results")
    ap.add_argument("--full", action="store_true", help="print full text, not a snippet")
    a = ap.parse_args()

    path = os.path.join(a.out, "chunks.jsonl")
    if not os.path.exists(path):
        raise SystemExit(f"{path} not found — run the pipeline first.")
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]

    hits = []
    for r in rows:
        md = r.get("filter_metadata") or {}
        if a.type and r["chunk_type"] != a.type:
            continue
        if a.skill and a.skill not in (md.get("skill_ids") or []):
            continue
        if a.semester is not None and md.get("semester_offered") != a.semester:
            continue
        if a.provider and (md.get("provider") or "").lower() != a.provider.lower():
            continue
        if a.query and not all(q.lower() in r["text"].lower() for q in a.query):
            continue
        hits.append(r)

    filters = [f"type={a.type}" if a.type else None, f"skill={a.skill}" if a.skill else None,
               f"semester={a.semester}" if a.semester is not None else None,
               f"provider={a.provider}" if a.provider else None,
               f"text~{' + '.join(a.query)}" if a.query else None]
    print(f"{len(hits)} of {len(rows)} chunks match ["
          f"{', '.join(f for f in filters if f) or 'no filter'}]\n")

    for r in hits[:a.n]:
        print(f"── {r['chunk_id']}")
        print(f"   parent: {r['parent_type']}/{r['parent_id']}   type: {r['chunk_type']}"
              f"   ~{r['token_estimate']} tok   source_type: {r['source_type']}")
        txt = r["text"] if a.full else (r["text"][:300] + ("…" if len(r["text"]) > 300 else ""))
        print("   " + re.sub(r"\n", "\n   ", txt))
        print(f"   source: {r['source_url']}  (retrieved {r['retrieved_on']}, "
              f"{r['verification_status']})\n")
    if len(hits) > a.n:
        print(f"…{len(hits) - a.n} more (raise -n)")

if __name__ == "__main__":
    main()
