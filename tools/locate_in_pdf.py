#!/usr/bin/env python3
"""
Adds a precise `source_locator` to every course, and cross-checks titles.

Why: `source_url` points at the institute's Courses-of-Study page. That is the
honest origin of the document, but it is useless for checking one record -- a
reviewer gets a 208-page PDF and no idea where to look. Provenance that cannot
be acted on is not really traceability.

So each course gets, e.g.:
  source_locator = "Courses_Of_Study.pdf p.32 (structure table), p.117 (description)"

Page detection:
  * structure pages  -- the page carrying the "BTech in Mechanical Engineering"
    heading plus four-part L-T-P-C values, and the two pages after it. Same
    rule as crosscheck_pdf.py, so the two tools cannot disagree.
  * description page -- a page where the code is followed, within 400 characters,
    by "Credits" and "Prerequisite(s)". That combination only occurs in the
    course-description section, never in a structure table.

Titles are compared only against the description page, where the title is
followed by a line break rather than by an L-T-P-C cell -- comparing against the
structure table produced false differences like "Mathematics-I 3-1-0-4".

    python tools/locate_in_pdf.py --dry-run
    python tools/locate_in_pdf.py
"""
import argparse, csv, os, re, sys

PDF = os.path.join("data", "raw", "curriculum", "Courses_Of_Study.pdf")
CSV = os.path.join("data", "raw", "curriculum", "courses.csv")
HEADING = "BTech in Mechanical Engineering"
LTPC = re.compile(r"\d+(?:\.\d+)?-\d+(?:\.\d+)?-\d+(?:\.\d+)?-\d+(?:\.\d+)?")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pdf", default=PDF)
    ap.add_argument("--csv", default=CSV)
    a = ap.parse_args()

    try:
        import pdfplumber
    except ImportError:
        sys.exit("pip install pdfplumber")

    with open(a.csv, newline="", encoding="utf-8-sig") as fh:
        rdr = csv.DictReader(fh)
        rows, header = list(rdr), list(rdr.fieldnames)
    codes = [r["code"] for r in rows]

    pages = {}
    with pdfplumber.open(a.pdf) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            pages[i] = page.extract_text() or ""

    # --- structure pages: same rule as crosscheck_pdf.py ---------------------
    struct = []
    for i in sorted(pages):
        if HEADING.lower() in pages[i].lower() and LTPC.search(pages[i]):
            struct = [p for p in (i, i + 1, i + 2) if p in pages]
            break

    # --- description pages ---------------------------------------------------
    # A code can appear with "Credits" and "Prerequisite" on more than one page:
    # the real catalogue entry, and any worked example quoting a course. Collect
    # all candidates and prefer the one with the most following text, since a real
    # description runs for paragraphs and an example runs for a few lines.
    cand = {c: [] for c in codes}
    for i in sorted(pages):
        text = pages[i]
        for c in codes:
            m = re.search(rf"\b{re.escape(c)}\b", text)
            if not m:
                continue
            window = text[m.end(): m.end() + 400]
            if "Credits" in window and re.search(r"Pre-?requisite", window):
                cand[c].append((i, len(text) - m.end(), m.end()))

    desc, desc_title, extra = {}, {}, {}
    for c, hits in cand.items():
        if not hits:
            continue
        hits.sort(key=lambda h: -h[1])          # most following text first
        best_page, _, offset = hits[0]
        desc[c] = best_page
        others = sorted(h[0] for h in hits[1:])
        if others:
            extra[c] = others
        text = pages[best_page]
        tm = re.match(r"[ \t]*(.+)", text[offset:])
        if tm:
            t = tm.group(1).strip()
            t = LTPC.sub("", t)
            t = re.sub(r"\d+(\.\d+)?\s*Credits.*$", "", t).strip(" -–—|")
            if 3 <= len(t) <= 120:
                desc_title[c] = t

    located, missing, diffs = 0, [], []
    for r in rows:
        c = r["code"]
        parts = []
        if struct:
            parts.append(f"p.{struct[0]} (programme structure table)")
        if c in desc:
            parts.append(f"p.{desc[c]} (course description)")
        if c in extra:
            parts.append("also quoted on p." + ",".join(str(x) for x in extra[c]))
        if not parts:
            missing.append(c)
            continue
        r["source_locator"] = "Courses_Of_Study.pdf " + ", ".join(parts)
        located += 1
        if c in desc_title and norm(desc_title[c]) != norm(r["title"]):
            diffs.append((c, desc[c], r["title"], desc_title[c]))

    print(f"structure-table pages: {struct}")
    print(f"description pages found for {len(desc)}/{len(codes)} courses")
    if extra:
        print("codes appearing on more than one description-like page "
              "(the longest was chosen):")
        for c, others in sorted(extra.items()):
            print(f"  {c}: chose p.{desc[c]}, also on p." +
                  ",".join(str(x) for x in others))
    print(f"source_locator set on {located}/{len(rows)}")
    if missing:
        print(f"no locator (code not found with a description): {', '.join(missing)}")
    print()
    if diffs:
        print(f"TITLE DIFFERENCES ({len(diffs)}):")
        for c, pg, ours, printed in diffs:
            print(f"  {c} (p.{pg})\n     csv: {ours}\n     pdf: {printed}")
    else:
        print("No title differences on any description page.")

    if a.dry_run:
        print("\n--dry-run: nothing written.")
        return
    if "source_locator" not in header:
        header.insert(header.index("source_url"), "source_locator")
    with open(a.csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"\nwrote source_locator into {a.csv}")


if __name__ == "__main__":
    main()
