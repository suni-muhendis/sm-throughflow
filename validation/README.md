# Validation cases

Geometry of open axial-compressor test cases, transcribed verbatim from their
primary reports (NASA, NACA, GE, P&W) for validating the throughflow simulator.
Nothing here is converted or corrected: each number is as printed, with its
source page, and every doubtful reading is marked with a trailing `?`.

- `TRANSCRIPTION_GUIDE.md`: the rules every transcription followed.
- `cases/<case>/`: one folder per case with the CSV tables, `source.json`
  (report, NTRS id, PDF page and title of every table), `scalars.json`
  (values quoted from the text) and `notes.md` (conventions, gaps, print
  errors found in the reports, and how uncertain cells were resolved).
- `pass_b/<case>/`: independent blind re-readings of the tables without strong
  internal checks (NACA, GE LSRC, UTRC, LSAC, P&W exit-stage geometry).
- `tools/check_lewis_geometry.py`: consistency checks on the NASA Lewis-format
  geometry tables (camber, blade count from solidity, ordering, smoothness,
  text layer). `tools/compare_passes.py`: cell-by-cell comparison of the two
  readings.
- `reports/`: the outputs of those two tools.

Result of the checks: all 47 Lewis-format geometry tables give an integer
blade count to within 0.03 on every row and satisfy KIC - KOC = camber; the
blind re-readings agree with the first reading in every numeric cell except 11
(2 P&W cells already marked doubtful, 9 UTRC dot-matrix cells resolved or
marked in `cases/utrc_isolated_rotor/notes.md`).

The source PDFs are public NASA/NACA reports and are not stored here; each
`source.json` gives the NTRS id.
