"""Consistency checks on transcribed NASA Lewis-format blade geometry tables.

The Lewis reports (TP-1337 family, TM X single stages, TP-1493, TP-2597, ...)
print blade geometry with columns RI, RO, KIC, KTC, KOC, ..., ZI, ZMC, ZTC,
ZO, AERO CHORD, SETTING ANGLE, TOTAL CAMBER, SOLIDITY. This script finds those
tables in validation/cases/*/, joins tables split into parts, and checks:

1. camber: KIC - KOC equals TOTAL CAMBER to print rounding;
2. blade count: SOLIDITY * 2 pi r_mean / AERO CHORD is one integer on every row;
3. ordering: radii fall from tip to hub, ZI < ZMC < ZO and ZI < ZTC < ZO;
4. smoothness: a cell far off the spanwise curve through its neighbours;
5. text layer: whether each printed number occurs on the PDF page's OCR text.

Nothing is changed; the result is a list of cells to look at again.
Usage: python check_lewis_geometry.py [case ...] > report.md
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

CASES = Path(__file__).resolve().parent.parent / "cases"
PDF_DIR = Path(r"C:\Users\mfati\AppData\Local\Temp\claude\d--Projeler-Suni-Muhendis-Workspace\29c41291-e624-4472-81a7-d543134c6243\scratchpad\validation")
PREFIXES = ("RADII ", "BLADE ANGLES ", "BLADE THICKNESSES ", "AXIAL DIMENSIONS ")
RENAME = {"ZIC": "ZI", "ZOC": "ZO"}


def _name(col):
    col = col.strip()
    for p in PREFIXES:
        if col.startswith(p):
            col = col[len(p):]
    return RENAME.get(col, col)


def _value(cell):
    cell = cell.strip()
    flagged = cell.endswith("?")
    cell = cell.rstrip("?").replace(",", ".")
    try:
        return float(cell), flagged
    except ValueError:
        return None, flagged


def read_table(paths):
    """Join the CSV parts of one printed table on their first column."""
    rows, order, raw = {}, [], {}
    for path in paths:
        with open(path, newline="", encoding="utf-8") as fh:
            data = list(csv.reader(fh))
        header = [_name(c) for c in data[0]]
        for line in data[2:]:
            if not line or not line[0].strip():
                continue
            label = line[0].strip()
            if label not in rows:
                rows[label], raw[label] = {}, {}
                order.append(label)
            for col, cell in zip(header[1:], line[1:]):
                rows[label][col] = _value(cell)
                raw[label][col] = (cell.strip(), path.name)
    return order, rows, raw


def geometry_tables(case_dir):
    groups = defaultdict(list)
    for path in sorted(case_dir.glob("*.csv")):
        with open(path, newline="", encoding="utf-8") as fh:
            header = next(csv.reader(fh), [])
        key = re.sub(r"_part\d+$", "", path.stem)
        groups[key].append((path, [_name(c) for c in header]))
    for key, items in groups.items():
        cols = {c for _, h in items for c in h}
        if {"KIC", "KOC", "SOLIDITY"} <= cols and ("AERO CHORD" in cols or "CHORD" in cols):
            yield key, [p for p, _ in items]


def page_text(case_dir):
    """OCR text by CSV file, from source.json (file -> pdf_page) and the .txt dumps."""
    out = {}
    src = case_dir / "source.json"
    if not src.exists():
        return out
    try:
        entries = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    if isinstance(entries, dict):
        entries = entries.get("entries") or entries.get("files") or list(entries.values())
    texts = {}
    for e in entries if isinstance(entries, list) else []:
        if not isinstance(e, dict) or "file" not in e or "pdf_page" not in e:
            continue
        report = str(e.get("report", ""))
        stem = re.sub(r"[^A-Za-z0-9]", "", report.replace("NASA", "").replace("NACA", ""))
        candidates = [p for p in PDF_DIR.glob("*.txt") if p.stem.replace("-", "").upper().startswith(stem.upper())]
        if not candidates:
            continue
        txt = texts.setdefault(candidates[0], candidates[0].read_text(encoding="utf-8", errors="replace").split("\f"))
        pages = e["pdf_page"] if isinstance(e["pdf_page"], list) else [e["pdf_page"]]
        try:
            out[e["file"]] = " ".join(txt[int(p) - 1] for p in pages if 0 < int(p) <= len(txt))
        except (ValueError, TypeError):
            continue
    return out


def _variants(s):
    s = s.rstrip("?")
    v = {s}
    if s.startswith("0."):
        v.add(s[1:])
    if s.startswith("-0."):
        v.add("-" + s[2:])
    if s.startswith("."):
        v.add("0" + s)
    return v


def check(case_dir):
    findings = []
    texts = page_text(case_dir)
    for key, paths in geometry_tables(case_dir):
        order, rows, raw = read_table(paths)
        get = lambda c: np.array([rows[l].get(c, (None, False))[0] if rows[l].get(c, (None, False))[0] is not None else np.nan for l in order])
        chord = get("AERO CHORD") if not np.all(np.isnan(get("AERO CHORD"))) else get("CHORD")
        kic, koc, cam, sol = get("KIC"), get("KOC"), get("TOTAL CAMBER"), get("SOLIDITY")
        ri, ro = get("RI"), get("RO")
        lines = ["### {} ({} rows)".format(key, len(order))]
        # 1. camber
        if not np.all(np.isnan(cam)):
            d = np.abs((kic - koc) - cam)
            for l, x in zip(order, d):
                if x > 0.025:
                    lines.append("- camber {}: KIC-KOC = {:.2f}, printed {}".format(l, float(rows[l]["KIC"][0] - rows[l]["KOC"][0]), raw[l]["TOTAL CAMBER"][0]))
        # 2. blade count
        r_mean = 0.5 * (ri + ro)
        z = sol * 2 * np.pi * r_mean / chord
        if np.any(np.isfinite(z)):
            zr = np.nanmedian(z)
            lines.append("- blade count from solidity: median {:.2f} (range {:.2f} to {:.2f})".format(zr, np.nanmin(z), np.nanmax(z)))
            for l, x in zip(order, z):
                if np.isfinite(x) and abs(x / round(zr) - 1) > 0.006:
                    lines.append("  - row {}: {:.2f}".format(l, x))
        # 3. ordering
        for name, arr in (("RI", ri), ("RO", ro)):
            if np.any(np.diff(arr[np.isfinite(arr)]) >= 0):
                lines.append("- {} not falling from tip to hub: {}".format(name, [raw[l][name][0] for l in order]))
        zi, zm, zt, zo = get("ZI"), get("ZMC"), get("ZTC"), get("ZO")
        for l, a, m, t, o in zip(order, zi, zm, zt, zo):
            if np.isfinite(a) and np.isfinite(o) and not (a <= m <= o and a <= t <= o):
                lines.append("- axial order row {}: ZI {} ZMC {} ZTC {} ZO {}".format(l, a, m, t, o))
        # 4. smoothness: residual from the quadratic through the two neighbours on each side,
        # against percent span (rows are not evenly spaced, e.g. near part-span dampers)
        span_pos = get("PERCENT SPAN")
        if np.any(~np.isfinite(span_pos)):
            span_pos = np.arange(len(order), dtype=float)
        for col in sorted({c for l in order for c in rows[l]}):
            arr = get(col)
            if np.sum(np.isfinite(arr)) < 6 or col in ("PERCENT SPAN",):
                continue
            res = np.full(arr.size, np.nan)
            for i in range(arr.size):
                idx = [j for j in range(max(0, i - 2), min(arr.size, i + 3)) if j != i and np.isfinite(arr[j])]
                if len(idx) >= 3 and np.isfinite(arr[i]):
                    p = np.polyfit(span_pos[idx], arr[idx], 2 if len(idx) >= 4 else 1)
                    res[i] = arr[i] - np.polyval(p, span_pos[i])
            scale = np.nanmedian(np.abs(res))
            span = np.nanmax(arr) - np.nanmin(arr)
            for l, x in zip(order, res):
                if np.isfinite(x) and abs(x) > max(8 * scale, 0.05 * span, 1e-9) and abs(x) > 0.02 * max(abs(np.nanmedian(arr)), 1e-6):
                    lines.append("- smoothness {} row {}: printed {} is {:+.4g} off its neighbours' curve".format(col, l, raw[l][col][0], x))
        # 5. text layer
        missing = []
        for l in order:
            for col, (cell, fname) in raw[l].items():
                text = texts.get(fname)
                if text is None or not cell or col == "PERCENT SPAN":
                    continue
                if not any(v in text for v in _variants(cell)):
                    missing.append("{}:{}={}".format(l, col, cell))
        if texts.get(paths[0].name) is not None:
            total = sum(len(raw[l]) for l in order)
            lines.append("- text layer: {} of {} cells not found{}".format(len(missing), total, (": " + ", ".join(missing[:40]) + (" ..." if len(missing) > 40 else "")) if missing else ""))
        findings.append("\n".join(lines))
    return findings


def main(argv):
    cases = [CASES / a for a in argv] if argv else sorted(p for p in CASES.iterdir() if p.is_dir())
    for case in cases:
        found = check(case)
        if found:
            print("## {}\n".format(case.name))
            print("\n\n".join(found))
            print()


if __name__ == "__main__":
    main(sys.argv[1:])
