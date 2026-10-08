# Transcription guide for validation-case geometry

The geometry of each validation case is transcribed from its primary report,
verbatim, so that every number can be traced to a printed page and checked
again. Interpretation (unit conversion, mapping to the design contract) is a
later, separate step done by code; transcription never converts or "fixes"
anything.

## Where things go

`validation/cases/<case_id>/` with:

- `source.json`: one entry per transcribed table or figure:
  `{"file": "<csv name>", "report": "NASA TP-1659", "ntrs_id": "19800012840",
  "pdf_page": 24, "printed_page": "22", "title": "<table title verbatim>",
  "dpi": 200, "notes": "..."}`, plus `"citation"` entries for every report used.
- `<report>_<table>_<part>.csv`, e.g. `TP1659_tableIII_rotor37.csv`: one CSV
  per printed table (or per row of a multi-row table).
- `scalars.json`: single values that live in text, not tables (blade counts,
  clearances, design speed, mass flow, pressure ratio, profile types,
  meanline definitions), each as `{"value": ..., "unit": "...",
  "quote": "<the sentence or cell verbatim>", "report": "...",
  "pdf_page": N}`.
- `notes.md`: anything a later reader must know (missing items, ambiguities,
  conventions stated in the report such as angle sign, what "ZI" is measured
  from, whether sections are on cones, cylinders or planes).

## CSV rules

1. Row 1: column headings exactly as printed (keep the report's symbols, e.g.
   `KIC`, `RI`, `SETTING ANGLE`). Row 2: units exactly as printed (`CM`,
   `DEG`, blank if none). Then one line per printed row, first column the row
   label as printed (`TIP`, `5`, `HUB`, `1`, ...).
2. Copy every number exactly as printed: same digits, decimals, signs,
   leading zeros dropped or kept as printed. Do not round, convert, average
   or interpolate. Do not drop rows or columns.
3. A cell you cannot read with certainty: write your best reading followed by
   `?` (e.g. `12.34?`) and explain in `notes`. A blank printed cell stays
   empty. Never invent a value.
4. Read every number from a rendered page image (`pdftoppm -r 200 -f N -l N
   -png`, crop with Python/PIL and zoom when digits are small). The pdftotext
   layer is useful to find pages and as a cross-check, but it is not the
   source: OCR swaps digits.
5. After finishing a table, re-read it from the image once more, cell by
   cell, and correct it. Note in `source.json` that this second read was done.
6. Figures with tabulated values (e.g. a flowpath coordinate box) are
   transcribed the same way. Figures without numbers are not digitized in
   this step; list them in `notes.md` as "figure only".

## What to capture for a blade row (if printed anywhere)

Blade count; tip/hub clearance (cold and running, with conditions); profile
type and its definition (MCA, DCA, NACA 65 designation, C.4, meanline
modifications, transition point, max-thickness location, edge radii); per
section: radius at LE and TE, axial positions of LE/TE (and what they are
measured from), metal angles at LE/TE (and transition point), camber,
stagger/setting angle, chord, solidity, max thickness, t/c, edge
thicknesses or radii; flowpath coordinates; positions of measurement
stations; design-point overall parameters (speed, mass flow, pressure ratio,
efficiency, tip speed). Also record the report's angle convention and the
direction the angles are measured from.

## Do not

- Do not edit anything outside your case folders. Do not run git.
- Do not use values from memory, other papers or CFD descriptions unless the
  task says so; if you add a value from another report, it gets its own
  `source.json` entry.
