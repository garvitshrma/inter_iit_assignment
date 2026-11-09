"""
Stage 5: export.

Writes data/processed/*.csv + *.json (future seed data) and chunks.jsonl (input
for the day-two embedding step). No embedding or LLM call happens here or
anywhere else in this pipeline.

The export gate: rows whose source_type is "illustrative" are placeholders. They
are refused unless --allow-illustrative is passed, and when allowed they are
written to a SEPARATE set of files suffixed _illustrative so they can never be
mistaken for retrieved data by whatever consumes data/processed/ next.
"""
from __future__ import annotations

import csv
import json
import os
from collections import Counter, defaultdict
from typing import Dict, List

from .models import ENTITY_CLASSES, field_names, flatten


def _write_csv(path: str, rows: List[dict], header: List[str]):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in header})


def _write_json(path: str, rows: List[dict]):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False, default=str)


def split_illustrative(dataset: Dict[str, list]):
    real, placeholder = defaultdict(list), defaultdict(list)
    for entity, rows in dataset.items():
        for r in rows:
            (placeholder if r.prov.source_type == "illustrative" else real)[entity].append(r)
    return dict(real), dict(placeholder)


def fill_rates(dataset: Dict[str, list]) -> Dict[str, dict]:
    """Percentage of non-empty values per field per entity -- feeds Part D."""
    out = {}
    for entity, rows in dataset.items():
        if entity not in ENTITY_CLASSES or not rows:
            continue
        header = field_names(ENTITY_CLASSES[entity])
        counts = Counter()
        for r in rows:
            flat = flatten(r)
            for k in header:
                v = flat.get(k)
                if v is not None and str(v).strip() != "":
                    counts[k] += 1
        n = len(rows)
        out[entity] = {"n_records": n,
                       "fields": {k: round(100.0 * counts[k] / n, 1) for k in header}}
    return out


def export(dataset: Dict[str, list], chunks: list, findings: list,
           out_dir: str, allow_illustrative: bool = False) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    real, placeholder = split_illustrative(dataset)

    written = {}
    for entity, cls in ENTITY_CLASSES.items():
        header = field_names(cls)
        rows = [flatten(r) for r in real.get(entity, [])]
        _write_csv(os.path.join(out_dir, f"{entity}.csv"), rows, header)
        _write_json(os.path.join(out_dir, f"{entity}.json"), rows)
        written[entity] = len(rows)

        ph = placeholder.get(entity, [])
        if ph and allow_illustrative:
            prows = [flatten(r) for r in ph]
            _write_csv(os.path.join(out_dir, f"{entity}_illustrative.csv"), prows, header)
            written[f"{entity}_illustrative"] = len(prows)

    # chunks.jsonl -- one JSON object per line, ready for an embedding step
    kept = 0
    with open(os.path.join(out_dir, "chunks.jsonl"), "w", encoding="utf-8") as fh:
        for ch in chunks:
            if ch.prov.source_type == "illustrative" and not allow_illustrative:
                continue
            rec = {
                "chunk_id": ch.chunk_id,
                "parent_id": ch.parent_id,
                "parent_type": ch.parent_type,
                "chunk_type": ch.chunk_type,
                "text": ch.text,
                "token_estimate": ch.token_estimate,
                "ordinal": ch.ordinal,
                "filter_metadata": ch.filter_metadata,
                "source_url": ch.prov.source_url,
                "retrieved_on": ch.prov.retrieved_on,
                "source_type": ch.prov.source_type,
                "verification_status": ch.prov.verification_status,
            }
            fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            kept += 1
    written["chunks"] = kept

    # validation report, machine-readable, generated from the validator itself
    freport = [f.as_row() for f in findings]
    _write_csv(os.path.join(out_dir, "validation_report.csv"), freport,
               ["check", "severity", "entity", "record_id", "message"])
    _write_json(os.path.join(out_dir, "validation_report.json"), freport)

    return {"written": written,
            "fill_rates": fill_rates(real),
            "illustrative_counts": {k: len(v) for k, v in placeholder.items() if v},
            "chunk_type_counts": dict(Counter(c.chunk_type for c in chunks)),
            "chunk_token_estimate_total": sum(c.token_estimate for c in chunks)}
