#!/usr/bin/env python3
"""
Writes NPTEL course durations into data/raw/resources/resources.csv.

Every value below was read from the course's own SWAYAM/NPTEL preview page on
2026-11-10, rendered in a real browser (the pages are client-side rendered, so
the plain fetch used on 2026-11-09 returned an empty shell and these fields were
correctly left null then).

Only duration_value, duration_unit and source_note are touched. Verification
state is never modified -- a record verified by a human stays verified, and the
note records what the page stated so a reviewer can re-check it.

Four courses (RES-NPT-027..030) are deliberately absent: their preview pages
have a Summary button that does not populate, so no duration is published and
theirs stay null.
"""
import csv, os, sys

RETRIEVED = "2026-11-10"

# id: (weeks, credit_points, level, course_type)
D = {
    "RES-NPT-010": (12, "3",  "Undergraduate/Postgraduate", "Elective"),
    "RES-NPT-011": (12, "3",  "Undergraduate",              "Core"),
    "RES-NPT-012": (12, "3",  "Undergraduate/Postgraduate", "Core"),
    "RES-NPT-013": (12, "3",  "Undergraduate/Postgraduate", "Elective"),
    "RES-NPT-014": (12, "3",  "Undergraduate",              "Core"),
    "RES-NPT-015": (4,  "1",  "Undergraduate",              "Elective"),
    "RES-NPT-016": (12, "3",  "Undergraduate/Postgraduate", "Elective"),
    "RES-NPT-017": (8,  "2",  "Undergraduate",              "Elective"),
    "RES-NPT-018": (12, "3",  "Undergraduate/Postgraduate", "Core"),
    "RES-NPT-019": (12, "3",  "Undergraduate",              "Core"),
    "RES-NPT-020": (12, "4",  "Undergraduate/Postgraduate", "Core"),
    "RES-NPT-021": (4,  "2",  "Undergraduate",              "Core"),
    "RES-NPT-022": (12, "3",  "Undergraduate",              "Core"),
    "RES-NPT-023": (12, "3",  "Undergraduate/Postgraduate", "Elective"),
    "RES-NPT-024": (8,  "2",  "Undergraduate",              "Elective"),
    "RES-NPT-025": (12, "3",  "Postgraduate",               "Elective"),
    "RES-NPT-026": (12, "3",  "Undergraduate",              "Core"),
    "RES-NPT-031": (12, "4",  "Undergraduate",              "Core"),
}

# Courses whose Summary panel exists but never populates -> no published duration.
NO_SUMMARY = {
    "RES-NPT-027": "noc21_me76",
    "RES-NPT-028": "noc20_me57",
    "RES-NPT-029": "noc20_me03",
    "RES-NPT-030": "noc25_me177",
}

# Extra fields read off the rendered page for one record.
EXTRA = {
    "RES-NPT-010": {"instructor": "Prof. Janakranjan Ramkumar, Prof. Amandeep Singh Oberoi",
                    "host_institute": "IIT Kanpur"},
}

PATH = os.path.join("data", "raw", "resources", "resources.csv")


def main():
    if not os.path.exists(PATH):
        sys.exit(f"{PATH} not found - run this from the repo root")
    with open(PATH, newline="", encoding="utf-8-sig") as fh:
        rdr = csv.DictReader(fh)
        rows, header = list(rdr), rdr.fieldnames

    touched = noted = 0
    for r in rows:
        rid = r["id"]
        if rid in D:
            weeks, credits, level, ctype = D[rid]
            r["duration_value"] = str(weeks)
            r["duration_unit"] = "weeks"
            note = r.get("source_note", "")
            note = note.replace("tier=listing_only", "tier=page_read")
            note = note.replace(
                "; title/URL from provider listing, resource page not opened, "
                "duration left null", "")
            note = (note + f" | page rendered in a browser and read on {RETRIEVED}: "
                           f"provider states Duration {weeks} Weeks, Credit Points "
                           f"{credits}, Course Level {level}, Course Type {ctype}").strip(" |")
            r["source_note"] = note
            for k, v in EXTRA.get(rid, {}).items():
                if not (r.get(k) or "").strip():
                    r[k] = v
            touched += 1
        elif rid in NO_SUMMARY:
            r["source_note"] = (r.get("source_note", "") +
                                f" | page rendered in a browser on {RETRIEVED}: the "
                                f"Summary panel does not populate for this course, so the "
                                f"provider publishes no duration. Left null rather than "
                                f"guessed.").strip(" |")
            noted += 1

    with open(PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    filled = sum(1 for r in rows if (r.get("duration_value") or "").strip())
    print(f"durations written: {touched}")
    print(f"no-duration notes added: {noted}")
    print(f"duration coverage now: {filled}/{len(rows)} "
          f"({100.0*filled/len(rows):.1f}%)  (was 7/56 = 12.5%)")
    ver = sum(1 for r in rows if r.get("verification_status") == "human_verified")
    print(f"human_verified resources preserved: {ver}")


if __name__ == "__main__":
    main()
