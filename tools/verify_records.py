#!/usr/bin/env python3
"""
Walk a sample of records, show each one's fields and its source URL, and record
what a human actually found. Writes the real verification state back to the raw
CSV: verification_status, verified_on (today), verified_by (you).

This exists so that verification is cheap enough to be true. Marking records
verified without opening their sources would defeat the whole dataset -- Part D
invites a reviewer to spot-check records against their sources, and that only
works if the flag means what it says.

    python tools/verify_records.py --by "Garvit Sharma" -n 10
    python tools/verify_records.py --by "Garvit Sharma" --entity course -n 5
    python tools/verify_records.py --status            # just show the counts

Per record: [y] matches the source  [n] does not  [s] skip  [q] save and quit
A 'n' prompts for a note, which is appended to the record's source_note.
"""
import argparse, csv, datetime, os, random, sys, webbrowser

FILES = {
    "course":              ("data/raw/curriculum/courses.csv", "code",
                            ["code","title","dept","credits","semester_offered","course_type"]),
    "prerequisite_edge":   ("data/raw/curriculum/prerequisites.csv", None,
                            ["course","requires","kind"]),
    "academic_rule":       ("data/raw/rules/academic_rules.csv", "id",
                            ["id","category","numeric_limit","unit","clause_ref","text"]),
    "resource":            ("data/raw/resources/resources.csv", "id",
                            ["id","title","provider","instructor","host_institute",
                             "licence_name","duration_value","duration_unit"]),
    "course_skill_link":   ("data/raw/curriculum/course_skills.csv", None,
                            ["course","skill","depth","evidence"]),
    "resource_skill_link": ("data/raw/resources/resource_skills.csv", None,
                            ["resource","skill","level"]),
}


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        r = csv.DictReader(fh)
        return list(r), r.fieldnames


def save(path, rows, header):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def show_status():
    print(f"{'entity':22s} {'total':>6s} {'verified':>9s} {'disputed':>9s} {'unverified':>11s}")
    print("-" * 62)
    gt = gv = gd = 0
    for ent, (path, _k, _f) in FILES.items():
        if not os.path.exists(path):
            continue
        rows, _ = load(path)
        v = sum(1 for r in rows if r.get("verification_status") == "human_verified")
        d = sum(1 for r in rows if r.get("verification_status") == "disputed")
        print(f"{ent:22s} {len(rows):6d} {v:9d} {d:9d} {len(rows)-v-d:11d}")
        gt += len(rows); gv += v; gd += d
    print("-" * 62)
    pct = (100.0 * gv / gt) if gt else 0
    print(f"{'TOTAL':22s} {gt:6d} {gv:9d} {gd:9d} {gt-gv-gd:11d}   ({pct:.1f}% verified)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--by", help="your name, written into verified_by")
    ap.add_argument("--entity", choices=sorted(FILES), help="limit to one entity")
    ap.add_argument("-n", type=int, default=10, help="how many records to review")
    ap.add_argument("--seed", type=int, default=None, help="make the sample reproducible")
    ap.add_argument("--status", action="store_true", help="show counts and exit")
    ap.add_argument("--open", action="store_true", help="open each source URL in a browser")
    a = ap.parse_args()

    if a.status or not a.by:
        show_status()
        if not a.by:
            print("\nTo start reviewing:  python tools/verify_records.py --by \"Your Name\" -n 10")
        return 0

    today = datetime.date.today().isoformat()
    rng = random.Random(a.seed)
    ents = [a.entity] if a.entity else sorted(FILES)

    pool = []
    for ent in ents:
        path, _key, fields = FILES[ent]
        if not os.path.exists(path):
            continue
        rows, header = load(path)
        for i, r in enumerate(rows):
            if r.get("verification_status") in ("human_verified", "disputed"):
                continue
            pool.append((ent, path, header, fields, i))
    if not pool:
        print("Nothing left unverified in the selected scope.")
        return 0

    rng.shuffle(pool)
    picked = pool[:a.n]
    # group by file so each file is loaded and written once
    by_file, cache = {}, {}
    for ent, path, header, fields, i in picked:
        by_file.setdefault(path, (ent, header, fields, []))[3].append(i)
        if path not in cache:
            cache[path] = load(path)[0]

    print(f"Reviewing {len(picked)} record(s). Open each source URL and compare.\n"
          f"[y] matches  [n] does not match  [s] skip  [q] save and quit\n")

    done = quit_now = 0
    for path, (ent, header, fields, idxs) in by_file.items():
        rows = cache[path]
        for i in idxs:
            r = rows[i]
            print("=" * 72)
            print(f"{ent}   ({path})")
            for f in fields:
                val = (r.get(f) or "")
                if len(val) > 300:
                    val = val[:300] + " …"
                print(f"  {f:18s} {val}")
            print(f"  {'SOURCE':18s} {r.get('source_url','')}")
            if (r.get("source_locator") or "").strip():
                print(f"  {'FIND IT AT':18s} {r['source_locator']}")
            print(f"  {'retrieved_on':18s} {r.get('retrieved_on','')}")
            if r.get("source_note"):
                note = r["source_note"]
                print(f"  {'source_note':18s} {note[:280]}{' …' if len(note) > 280 else ''}")
            if a.open and r.get("source_url", "").startswith("http"):
                webbrowser.open(r["source_url"])
            try:
                ans = input("\n  matches the source? [y/n/s/q] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n  interrupted"); ans = "q"
            if ans == "q":
                quit_now = 1; break
            if ans == "s" or ans not in ("y", "n"):
                print("  skipped\n"); continue
            if ans == "y":
                r["verification_status"] = "human_verified"
            else:
                r["verification_status"] = "disputed"
                try:
                    why = input("  what is wrong with it? ").strip()
                except (EOFError, KeyboardInterrupt):
                    why = ""
                if why:
                    r["source_note"] = ((r.get("source_note") or "") +
                                        f" | DISPUTED {today} by {a.by}: {why}").strip(" |")
            r["verified_on"] = today
            r["verified_by"] = a.by
            done += 1
            print(f"  recorded: {r['verification_status']}\n")
        save(path, rows, header)
        if quit_now:
            break

    print(f"\n{done} record(s) recorded. Raw CSVs updated.")
    print("Now re-run the pipeline so the reports pick it up:")
    print("  python run_pipeline.py && python tools/make_quality_report.py --out data/processed\n")
    show_status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
