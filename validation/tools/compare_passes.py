"""Compare two independent transcriptions of the same tables, cell by cell.

Pass A lives in validation/cases/<case>/, pass B (a blind re-read) in
validation/pass_b/<case>/ with the same file names. Numbers are compared as
numbers ('.50' equals '0.5'); text cells as stripped text. A trailing '?'
marks doubt in either pass and is reported but not counted as a difference
when the values agree.

Usage: python compare_passes.py [case ...] > report.md
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A, B = ROOT / "cases", ROOT / "pass_b"


def _num(cell):
    s = cell.strip().rstrip("?").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        data = list(csv.reader(fh))
    header = data[0] if data else []
    body = {}
    order = []
    for line in data[2:]:
        if not line or not any(c.strip() for c in line):
            continue
        key = line[0].strip()
        while key in body:  # repeated labels: keep them apart
            key += "'"
        body[key] = line
        order.append(key)
    return header, order, body


def compare(case):
    out = []
    a_dir, b_dir = A / case, B / case
    for b_file in sorted(b_dir.glob("*.csv")):
        a_file = a_dir / b_file.name
        if not a_file.exists():
            out.append("- {}: no pass-A file".format(b_file.name))
            continue
        ha, oa, ra = _rows(a_file)
        hb, ob, rb = _rows(b_file)
        diffs, doubtful, cells = [], 0, 0
        if [h.strip() for h in ha] != [h.strip() for h in hb]:
            out.append("- {}: headings differ\n  A: {}\n  B: {}".format(b_file.name, ha, hb))
        # Rows are paired by position when both passes have the same number of rows
        # (labels repeat or are left blank in some tables), otherwise by label.
        positional = len(oa) == len(ob)
        pairs = list(zip(oa, ob)) if positional else [(k, k) for k in oa]
        start = 0 if positional else 1
        for key, key_b in pairs:
            if key_b not in rb:
                diffs.append("row {} missing in B".format(key))
                continue
            for j, col in enumerate(ha[start:], start=start):
                ca = ra[key][j].strip() if j < len(ra[key]) else ""
                cb = rb[key_b][j].strip() if j < len(rb[key_b]) else ""
                if not ca and not cb:
                    continue
                cells += 1
                na, nb = _num(ca), _num(cb)
                same = (na is not None and nb is not None and abs(na - nb) < 1e-12) or (na is None and nb is None and ca.rstrip("?") == cb.rstrip("?"))
                if ca.endswith("?") or cb.endswith("?"):
                    doubtful += 1
                if not same:
                    diffs.append("row {} col {}: A={} B={}".format(key, col, ca or "(blank)", cb or "(blank)"))
        if not positional:
            for key in ob:
                if key not in ra:
                    diffs.append("row {} only in B".format(key))
        out.append("- {}: {} cells, {} differ, {} doubtful in either pass{}".format(
            b_file.name, cells, len(diffs), doubtful, "".join("\n  - " + d for d in diffs)))
    return out


def main(argv):
    cases = argv or sorted(p.name for p in B.iterdir() if p.is_dir())
    for case in cases:
        print("## {}\n".format(case))
        print("\n".join(compare(case)))
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
