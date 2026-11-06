"""Check the conditional momentum march against the Liu planar wakes."""
import argparse
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import re
from zipfile import ZipFile

import numpy as np

from validation.campaign import create_campaign, write_json_new
from validation.probe_compressible_diffusion import BASELINE
from validation.verify_family_source_v14 import verify
from validation.wake_junction_reference import march_momentum


SOURCE = "https://www.nasa.gov/wp-content/uploads/2025/10/symmetricwake-uvcorrected.zip"
SHA256 = "10627a194ae18bc5709430da64a3399eb19f2e68c4319bdb708fd2b2f0294905"
STATION = re.compile(r"-(\d+)(in|mm)\.txt$", re.IGNORECASE)
CASES = {"Zero": 9, "AP1": 10, "FP1": 11, "FP2": 11}


def _read_profile(raw):
    # The data files have one header row and some rows omit stresses.
    positions, speed = np.loadtxt(BytesIO(raw), skiprows=1, usecols=(0, 1)).T
    y, inverse, counts = np.unique(positions / 1000, return_inverse=True, return_counts=True)
    u = np.bincount(inverse, weights=speed) / counts
    if len(y) < 17 or not np.all(np.isfinite((y, u))) or np.any(u <= 0):
        raise ValueError("the traverse must have finite positions and positive speeds")
    return y, u, int(len(positions) - len(y))


def evaluate(raw):
    if sha256(raw).hexdigest() != SHA256:
        raise ValueError("unexpected planar wake archive")
    result = {}
    with ZipFile(BytesIO(raw)) as archive:
        for case, station_count in CASES.items():
            profiles = []
            for member in archive.namelist():
                match = STATION.search(member)
                if match and f"/{case}/" in member:
                    distance, units = match.groups()
                    x = int(distance) * {"in": .0254, "mm": .001}[units.lower()]
                    profiles.append((x, member, _read_profile(archive.read(member))))
            if len(profiles) != station_count:
                raise ValueError(f"unexpected station count for {case}")
            profiles.sort()
            result[case] = {}
            for tail_points in (3, 5, 8):
                stations = []
                for x, member, (y, u, duplicates) in profiles:
                    edge = (u[:tail_points].mean() + u[-tail_points:].mean()) / 2
                    q = u / edge
                    theta = np.trapezoid(q * (1 - q), y)
                    shape = np.trapezoid(1 - q, y) / theta
                    stations.append(dict(member=member, x_m=x, edge_m_s=float(edge),
                                         theta_m=float(theta), shape=float(shape),
                                         averaged_repeated_y_samples=duplicates))
                x, edge, theta, shape = (
                    np.array([row[key] for row in stations])
                    for key in ("x_m", "edge_m_s", "theta_m", "shape")
                )
                predicted = march_momentum(x, edge, shape, theta[0])
                errors = predicted / theta - 1
                for row, value in zip(stations, predicted):
                    row["marched_theta_m"] = float(value)
                result[case][str(tail_points)] = dict(
                    stations=stations, final_relative_error=float(errors[-1]),
                    max_absolute_relative_error=float(np.max(np.abs(errors))),
                )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    raw = args.archive.read_bytes()
    identity = verify(BASELINE)
    result = evaluate(raw)
    if evaluate(raw) != result:
        raise RuntimeError("the repeated wake reductions differ")
    output = create_campaign(
        purpose="liu_planar_wake_momentum_compatibility",
        selection=dict(research_only=True, training_label_qualified=False,
                       source=SOURCE, archive_sha256=SHA256),
    )
    with (output / "symmetricwake-uvcorrected.zip").open("xb") as stream:
        stream.write(raw)
    write_json_new(output / "analysis.json", dict(source=identity, result=result))
    print(output, flush=True)


if __name__ == "__main__":
    main()
