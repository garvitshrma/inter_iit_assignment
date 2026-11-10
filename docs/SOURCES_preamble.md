# SOURCES

Every record carries `source_url`, `retrieved_on` and `source_type`. This file is
the human-readable index. It is **generated** by `tools/make_sources.py` from the
raw CSVs, so it can't drift from the data.

`source_type`: `official` (institute publication), `open-licence` (openly
licensed third-party content), `manual` (typed in by a human from a document they
opened), `illustrative` (placeholder, withheld from export by default).

## robots.txt

Checked before any retrieval, because the brief requires scraping to be polite
and legal.

| Domain | Finding | What we did |
|---|---|---|
| `www.iitbhilai.ac.in` | **Automated retrieval disallowed.** Every page refused with `robots_disallowed`. | Didn't scrape it. A human downloaded the two PDFs in a browser and the records were transcribed by hand, with the published page as `source_url`. |
| `archive.nptel.ac.in` | Allowed; static HTML and PDFs. | Primary NPTEL source. Syllabus PDFs parse and state title, coordinators, institute and duration. |
| `onlinecourses.nptel.ac.in` | Allowed, but pages render in JavaScript. | A plain fetch returns an empty shell, so on 2026-11-09 these rows were recorded as `tier=listing_only` with duration left empty. On 2026-11-10 the pages were opened in a real browser, which runs their JavaScript, and 18 were promoted to `tier=page_read` with the duration, credit points, level and course type the provider states. Four still have no published duration: their Summary panel never populates. |
| `ocw.mit.edu` | Allowed; terms page readable. | Licence verified directly. Course listings are JS-rendered, so title/URL pairs came from the provider's indexed listings. |
| `swayam.gov.in` | Not used. | Licence couldn't be verified, and an unverifiable licence is worse than a smaller dataset. |

Retrieval totalled a few dozen requests over a working session, so no rate
limiting was needed.

## Licences

Read from each provider's own terms page, not assumed.

| Provider | Licence | Verified at | Note |
|---|---|---|---|
| MIT OpenCourseWare | CC BY-NC-SA 4.0 | <https://ocw.mit.edu/pages/privacy-and-terms-of-use/> | Version stated, deed linked. |
| NPTEL | "CC BY-NC-SA" | Footer of <https://nptel.ac.in/> | **No version stated, no deed linked.** `licence_version` left empty; writing "4.0" would be a fabrication. |

Both are NonCommercial and ShareAlike. Anything built on this data has to respect
both terms.
