# SOURCES

Every record in this dataset carries `source_url`, `retrieved_on` and
`source_type`. This file is the human-readable index of those sources. It is
**generated** by `tools/make_sources.py` from the raw CSVs, so it cannot drift
away from the data.

`source_type` values: `official` (institute publication), `open-licence`
(openly licensed third-party content), `manual` (typed in by a human from a
document they opened), `illustrative` (placeholder written to exercise the
pipeline — withheld from export unless `--allow-illustrative` is passed).

## robots.txt and polite retrieval

Checked before any retrieval, because the brief requires scraping to be polite
and legal.

| Domain | Finding | Consequence for this dataset |
|---|---|---|
| `www.iitbhilai.ac.in` | **Automated retrieval disallowed.** The fetch layer refused `/robots.txt` and every page under the domain with `robots_disallowed`. | No scraping of the institute site. Course and rule records must be entered by a human from documents opened in a browser, with `source_type=manual` and the published page recorded as `source_url`. |
| `archive.nptel.ac.in` | Retrieval permitted; static HTML and PDFs. | Used as the primary NPTEL source. Syllabus PDFs parse cleanly and state title, coordinators, institute and duration. |
| `onlinecourses.nptel.ac.in` | Retrieval permitted, but pages are client-side rendered. | Most course pages return a `Loading...` shell with no metadata. Only `noc25_me78` returned content. These rows are therefore recorded as `tier=listing_only` with `duration_value` left null. |
| `ocw.mit.edu` | Retrieval permitted; terms page readable. | Licence verified directly. Course search results are JS-rendered, so course URL/title pairs were taken from the provider's own indexed listings. |
| `swayam.gov.in` | Not used. | Its licence could not be verified within the time window. An unverifiable licence is worse than a smaller dataset, so SWAYAM is excluded entirely rather than guessed at. |

No rate limiting was required: retrieval totalled a few dozen requests spread
over the working session, well below any crawl-delay concern.

## Licence verification

Licences were read from each provider's own terms page, not assumed.

| Provider | Stated licence | Where verified | Note |
|---|---|---|---|
| MIT OpenCourseWare | Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) | <https://ocw.mit.edu/pages/privacy-and-terms-of-use/> | Version explicit; deed linked from the page. |
| NPTEL | "Creative Commons Attribution-NonCommercial-ShareAlike CC BY-NC-SA" | Footer of <https://nptel.ac.in/> | **No version is stated and no deed is linked.** `licence_version` is therefore left blank. Recording "4.0" would be a fabrication. |

Both licences are NonCommercial and ShareAlike. Any downstream product built on
this data must respect both terms — relevant if the eventual learning buddy is
ever commercial.
