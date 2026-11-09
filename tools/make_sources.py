#!/usr/bin/env python3
"""
Generates docs/SOURCES.md from the raw CSVs, so the source list cannot drift
away from the data. Hand-written sections (institute documents, licence
verification, robots.txt findings) live in docs/SOURCES_preamble.md and are
prepended verbatim.
"""
import csv, os, collections

def read(p):
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))

def main():
    res = read("data/raw/resources/resources.csv")
    courses = read("data/raw/curriculum/courses.csv")
    rules = read("data/raw/rules/academic_rules.csv")

    L = []
    A = L.append
    pre = "docs/SOURCES_preamble.md"
    if os.path.exists(pre):
        A(open(pre, encoding="utf-8").read().rstrip())
        A("")

    A("## Institute sources (course catalogue and academic rules)\n")
    if not courses and not rules:
        A("> **Status: not yet collected.** See the *Known gaps* section of the README. "
          "The institute's `robots.txt` disallows automated retrieval, so these records "
          "must be entered from documents opened by a human in a browser. No course or "
          "rule records have been fabricated to fill the gap.\n")
    else:
        seen = {}
        for r in courses + rules:
            u = (r.get("source_url") or "").strip()
            if u:
                seen.setdefault(u, {"n": 0, "date": r.get("retrieved_on", ""),
                                    "type": r.get("source_type", "")})
                seen[u]["n"] += 1
        A("| Source URL | Retrieved | source_type | Records |")
        A("|---|---|---|---:|")
        for u, m in sorted(seen.items()):
            A(f"| {u} | {m['date']} | `{m['type']}` | {m['n']} |")
        A("")

    A("## Open learning resources\n")
    A(f"{len(res)} resources. Every URL below was returned by a retrieval against the "
      "provider on the retrieval date shown; none were recalled from memory or "
      "constructed by editing another URL.\n")
    by_prov = collections.defaultdict(list)
    for r in res:
        by_prov[r["provider"]].append(r)
    for prov in sorted(by_prov):
        rows = by_prov[prov]
        lic = rows[0]
        licence = lic["licence_name"] + (f" {lic['licence_version']}" if lic["licence_version"] else " (version not stated by provider)")
        A(f"### {prov} — {len(rows)} resources\n")
        A(f"Licence applied to all {prov} rows: **{licence}**"
          + (f" ([deed]({lic['licence_url']}))" if lic["licence_url"] else "")
          + f", verified {lic['licence_verified_on']}.\n")
        A("| ID | Title | Tier | Duration | Retrieved | URL |")
        A("|---|---|---|---|---|---|")
        for r in sorted(rows, key=lambda x: x["id"]):
            tier = "page read" if "tier=page_read" in r["source_note"] else "listing only"
            dur = (f"{r['duration_value']} {r['duration_unit']}".strip()
                   if r["duration_value"] else "not stated")
            A(f"| `{r['id']}` | {r['title']} | {tier} | {dur} | {r['retrieved_on']} | {r['url']} |")
        A("")

    A("## Author-defined content (no source URL, by design)\n")
    A("- `data/raw/curriculum/skills.csv` — the skill taxonomy. Every row carries "
      "`origin=author_inferred`. These nodes are the dataset author's organising "
      "structure, not quotations from any institute or provider document. The validator "
      "exempts `author_inferred` skills from the provenance requirement so that this "
      "stays visible rather than being hidden behind a placeholder citation.")
    A("- `data/raw/resources/resource_skills.csv` and "
      "`data/raw/curriculum/course_skills.csv` — mappings. The endpoints are real; the "
      "*depth* and *level* judgements are the author's, and each row's `source_note` "
      "says so. Where a judgement was made from a specific syllabus phrase, that phrase "
      "is stored in the link's `evidence` field.\n")

    open("SOURCES.md", "w", encoding="utf-8").write("\n".join(L))
    print(f"wrote SOURCES.md ({len(chr(10).join(L)):,} chars)")

if __name__ == "__main__":
    main()
