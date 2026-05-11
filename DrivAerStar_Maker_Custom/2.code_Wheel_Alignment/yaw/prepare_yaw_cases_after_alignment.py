import argparse
import csv
import json
import math
import shutil
from pathlib import Path

import numpy as np


VEHICLE_STLS = [
    "part_01_Body.stl",
    "part_02_UB_Smooth.stl",
    "part_03_Notchback.stl",
    "part_05_Wheels_Front_Closed.stl",
    "part_06_Wheels_Rear_Closed.stl",
    "part_07_Mirror.stl",
]

FRONT_WHEEL = "part_05_Wheels_Front_Closed.stl"
REAR_WHEEL = "part_06_Wheels_Rear_Closed.stl"
REQUIRED_NON_STL_FILES = [
    "floor.txt",
]


def read_mesh(path):
    import pyvista as pv

    return pv.read(path)


def read_yaw_cases(path):
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            yield float(row["yaw_deg"])


def yaw_folder_name(yaw_deg):
    sign = "pos" if yaw_deg >= 0.0 else "neg"
    magnitude = abs(yaw_deg)
    return f"yaw_{sign}{magnitude:05.1f}".replace(".", "p")


def source_case_dirs(source_root, requested_case_ids):
    if requested_case_ids:
        return [source_root / case_id for case_id in requested_case_ids]
    return sorted(path for path in source_root.iterdir() if path.is_dir() and path.name.isdigit())


def combined_bounds(case_dir):
    mins = []
    maxs = []
    for name in VEHICLE_STLS:
        mesh = read_mesh(case_dir / name)
        bounds = np.array(mesh.bounds, dtype=float)
        mins.append([bounds[0], bounds[2], bounds[4]])
        maxs.append([bounds[1], bounds[3], bounds[5]])
    return np.min(mins, axis=0), np.max(maxs, axis=0)


def rotation_matrix_z(yaw_rad):
    cos_yaw = math.cos(yaw_rad)
    sin_yaw = math.sin(yaw_rad)
    return np.array(
        [
            [cos_yaw, -sin_yaw, 0.0],
            [sin_yaw, cos_yaw, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def rotate_points(points, rotation, reference):
    shifted = points - reference
    return shifted @ rotation.T + reference


def wheel_origin(mesh):
    bounds = np.array(mesh.bounds, dtype=float)
    return [
        float((bounds[0] + bounds[1]) / 2.0),
        float((bounds[2] + bounds[3]) / 2.0),
        float((bounds[4] + bounds[5]) / 2.0),
    ]


def reset_output_case(output_case):
    if not output_case.exists():
        output_case.mkdir(parents=True)
        return

    for path in output_case.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def copy_required_case_files(source_case, output_case):
    for name in REQUIRED_NON_STL_FILES:
        source_path = source_case / name
        if not source_path.exists():
            raise FileNotFoundError(f"missing required case file: {source_path}")
        shutil.copy2(source_path, output_case / name)


def prepare_yaw_case(source_root, output_root, case_id, yaw_deg):
    source_case = source_root / case_id
    output_case = output_root / case_id / yaw_folder_name(yaw_deg)
    reset_output_case(output_case)

    missing = [name for name in VEHICLE_STLS if not (source_case / name).exists()]
    if missing:
        raise FileNotFoundError(f"{case_id} missing STL files: {missing}")

    mins, maxs = combined_bounds(source_case)
    reference = np.array(
        [
            (mins[0] + maxs[0]) / 2.0,
            (mins[1] + maxs[1]) / 2.0,
            0.0,
        ],
        dtype=float,
    )
    yaw_rad = math.radians(yaw_deg)
    rotation = rotation_matrix_z(yaw_rad)

    for name in VEHICLE_STLS:
        shutil.copy2(source_case / name, output_case / name)

    copy_required_case_files(source_case, output_case)

    original_front = read_mesh(source_case / FRONT_WHEEL)
    original_floor_z = float(original_front.points[:, 2].min())
    copied_front = read_mesh(output_case / FRONT_WHEEL)
    copied_floor_z = float(copied_front.points[:, 2].min())
    if abs(original_floor_z - copied_floor_z) > 1.0e-6:
        raise RuntimeError(f"{case_id} copied wheel z min changed unexpectedly")

    axis = rotation @ np.array([0.0, -1.0, 0.0], dtype=float)
    front_origin = wheel_origin(read_mesh(source_case / FRONT_WHEEL))
    rear_origin = wheel_origin(read_mesh(source_case / REAR_WHEEL))
    yawed_front_origin = rotate_points(np.array([front_origin], dtype=float), rotation, reference)[0]
    yawed_rear_origin = rotate_points(np.array([rear_origin], dtype=float), rotation, reference)[0]
    metadata = {
        "case_id": case_id,
        "yaw_case_id": yaw_folder_name(yaw_deg),
        "yaw_deg": yaw_deg,
        "yaw_rad": yaw_rad,
        "rotation_reference_mm": [float(reference[0]), float(reference[1]), float(reference[2])],
        "wheel_axis": [float(axis[0]), float(axis[1]), float(axis[2])],
        "front_wheel_origin_mm": [float(value) for value in yawed_front_origin],
        "rear_wheel_origin_mm": [float(value) for value in yawed_rear_origin],
        "source_case": source_case.as_posix(),
    }
    (output_case / "yaw_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Prepare yawed DrivAer case folders after wheel alignment.")
    parser.add_argument("--source-root", type=Path, default=Path(r"D:/DrivAer/stl_N"))
    parser.add_argument("--output-root", type=Path, default=Path(r"D:/DrivAer/stl_N_yaw"))
    parser.add_argument(
        "--yaw-cases",
        type=Path,
        default=Path(__file__).with_name("yaw_cases_Notch_goal2.csv"),
    )
    parser.add_argument(
        "--case-ids",
        nargs="*",
        help="Optional base geometry case IDs such as 00000 00001. Defaults to all numeric source folders.",
    )
    args = parser.parse_args()

    yaw_angles = list(read_yaw_cases(args.yaw_cases))
    for source_case in source_case_dirs(args.source_root, args.case_ids):
        if not source_case.exists():
            raise FileNotFoundError(f"source case not found: {source_case}")
        for yaw_deg in yaw_angles:
            prepare_yaw_case(args.source_root, args.output_root, source_case.name, yaw_deg)
            print(
                f"prepared {source_case.name}: yaw={yaw_deg} deg "
                f"-> {args.output_root / source_case.name / yaw_folder_name(yaw_deg)}"
            )


if __name__ == "__main__":
    main()
