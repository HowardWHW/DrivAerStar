import argparse
import json
from pathlib import Path


BACK = "Notchback"
DEFAULT_CASE_ROOT = Path(r"D:/DrivAer/stl_N_yaw")

PARENT_TEMPLATE_FILES = [
    "../baomian.java",
    "../stl_2_dbs.template.java",
]
YAW_TEMPLATE_FILES = [
    "KwWakeRefine0521_yaw.java",
]
STALE_MACRO_FILES = [
    "KwWakeRefine0521.java",
    "SetYawWheelRotation.java",
]


def format_float(value):
    return f"{float(value):.12g}"


def load_metadata(case_dir):
    metadata_path = case_dir / "yaw_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"missing {metadata_path}")
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def yaw_replacements(metadata):
    front = [value / 1000.0 for value in metadata["front_wheel_origin_mm"]]
    rear = [value / 1000.0 for value in metadata["rear_wheel_origin_mm"]]
    axis = metadata["wheel_axis"]
    return {
        "<<<yaw_deg>>>": format_float(metadata["yaw_deg"]),
        "<<<yaw_rad>>>": format_float(metadata["yaw_rad"]),
        "<<<yaw_reference_x_m>>>": format_float(metadata["rotation_reference_mm"][0] / 1000.0),
        "<<<yaw_reference_y_m>>>": format_float(metadata["rotation_reference_mm"][1] / 1000.0),
        "<<<yaw_reference_z_m>>>": format_float(metadata["rotation_reference_mm"][2] / 1000.0),
        "<<<front_origin_x_m>>>": format_float(front[0]),
        "<<<front_origin_y_m>>>": format_float(front[1]),
        "<<<front_origin_z_m>>>": format_float(front[2]),
        "<<<rear_origin_x_m>>>": format_float(rear[0]),
        "<<<rear_origin_y_m>>>": format_float(rear[1]),
        "<<<rear_origin_z_m>>>": format_float(rear[2]),
        "<<<axis_x>>>": format_float(axis[0]),
        "<<<axis_y>>>": format_float(axis[1]),
        "<<<axis_z>>>": format_float(axis[2]),
    }


def render_template(template_content, case_dir, case_id, metadata):
    replacements = {
        "<<<dir>>>": case_dir.as_posix(),
        "<<<id>>>": case_id,
        "<<<back>>>": BACK,
    }
    replacements.update(yaw_replacements(metadata))

    rendered = template_content
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    return rendered


def template_output_name(template_path):
    return template_path.name.replace(".template", "")


def case_dirs(case_root):
    return sorted(path.parent for path in case_root.glob("*/*/yaw_metadata.json"))


def render_templates(case_root, template_paths):
    for case_dir in case_dirs(case_root):
        metadata = load_metadata(case_dir)
        case_id = case_dir.name
        for stale_name in STALE_MACRO_FILES:
            stale_path = case_dir / stale_name
            if stale_path.exists():
                stale_path.unlink()
        for template_path in template_paths:
            template_content = template_path.read_text(encoding="utf-8")
            rendered = render_template(template_content, case_dir, case_id, metadata)
            output_path = case_dir / template_output_name(template_path)
            output_path.write_text(rendered, encoding="utf-8")
            print(f"write {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Render yaw-specific Java macros from yaw metadata.")
    parser.add_argument("--case-root", type=Path, default=DEFAULT_CASE_ROOT)
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    template_paths = [script_dir / rel_path for rel_path in PARENT_TEMPLATE_FILES + YAW_TEMPLATE_FILES]
    for template_path in template_paths:
        if not template_path.exists():
            raise FileNotFoundError(f"missing template {template_path}")

    render_templates(args.case_root, template_paths)


if __name__ == "__main__":
    main()
