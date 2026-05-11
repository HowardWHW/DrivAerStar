# Yaw-Specific Java Generation

This folder is intentionally separate from the straight-case Java generator.

Goal-2 order:

1. Generate morphed STLs with `1.code_make_stls_by_blender/make.blender.py`.
2. Align wheels with `2.code_Wheel_Alignment/parallelru_N.py`.
3. Prepare nested yaw case folders with `2.code_Wheel_Alignment/yaw/prepare_yaw_cases_after_alignment.py`.
4. Render yaw macros with `3.make_java_code_E/yaw/make_yaw.py`.

The yaw preparation utility copies the aligned straight-case inputs and writes
`yaw_metadata.json` into each nested yaw case folder, for example
`D:/DrivAer/stl_N_yaw/00000/yaw_pos05p0/`.

`make_yaw.py` discovers those metadata files recursively and generates:

- `stl_2_dbs.java`
- `baomian.java`
- `KwWakeRefine0521_yaw.java`

`KwWakeRefine0521_yaw.java` is a full-case macro based on the custom
`KwWakeRefine0521.java`. It imports the DBS parts, applies yaw immediately after
`execute_input(dir)`, then continues with domain creation, meshing, wheel rotation
BCs, reports, solve, and export in one macro.
