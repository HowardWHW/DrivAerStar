from pathlib import Path

import pandas as pd


BACK = "Notchback"
CASE_ROOT = Path(r"D:/DrivAer/stl_N")
PARAMS_CSV = Path(__file__).resolve().parents[1] / "1.code_make_stls_by_blender" / "lhs_parameters_Notch_v3.csv"
TEMPLATE_FILES = [
    "baomian.java",
    "KwWakeRefine0521.java",
    "stl_2_dbs.template.java",
]


def render_template(template_content, case_dir, case_id):
    return (
        template_content
        .replace("<<<dir>>>", case_dir.as_posix())
        .replace("<<<id>>>", case_id)
        .replace("<<<back>>>", BACK)
    )


def main():
    params = pd.read_csv(PARAMS_CSV)
    case_count = len(params)

    script_dir = Path(__file__).resolve().parent
    CASE_ROOT.mkdir(parents=True, exist_ok=True)

    for template_name in TEMPLATE_FILES:
        template_path = script_dir / template_name
        if not template_path.exists():
            print(f"file {template_path} not exists")
            continue

        template_content = template_path.read_text(encoding="utf-8")
        output_name = Path(template_name).name.replace(".template", "")

        for index in range(case_count):
            case_id = f"{index:05d}"
            case_dir = CASE_ROOT / case_id
            case_dir.mkdir(parents=True, exist_ok=True)
            new_content = render_template(template_content, case_dir, case_id)
            new_file_path = case_dir / output_name
            new_file_path.write_text(new_content, encoding="utf-8")
            print(f"write {new_file_path}")


if __name__ == "__main__":
    main()
