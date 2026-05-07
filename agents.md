# Agent Notes

## Background

This repo contains `DrivAerStar_Maker/`, a production pipeline for turning DrivAer STL geometry into Star-CCM+ CFD cases, and `DrivAerStar_Benchmarking/`, which is unrelated to the current setup work.

The current work should happen in `DrivAerStar_Maker_Custom/` unless the user explicitly asks to change the original `DrivAerStar_Maker/`.

User goals:

1. First replicate the Maker pipeline for a few cases only, initially with simple `car_width` and `car_len` changes.
2. Then extend the workflow to yawed vehicle geometries in a straight rectangular domain.
3. Use a simplified external-aero geometry: smooth underbody, closed wheels, no engine internal flow, no exhaust structures.

Do not run Star-CCM+, Slurm jobs, Blender batch jobs, or bulk generation unless explicitly asked.

## Prepared Geometry

Use this prepared input tree:

```text
D:\DrivAer\DrivAer_STLs\
```

It already contains one ready folder per body style:

```text
D:\DrivAer\DrivAer_STLs\Estate\body\
D:\DrivAer\DrivAer_STLs\Fastback\body\
D:\DrivAer\DrivAer_STLs\Notchback\body\
```

Each body folder contains six STLs:

```text
part_01_Body.stl
part_02_UB_Smooth.stl
part_03_Estate.stl | part_03_Fastback.stl | part_03_Notchback.stl
part_05_Wheels_Front_Closed.stl
part_06_Wheels_Rear_Closed.stl
part_07_Mirror.stl
```

Important: `make.blender.py` imports every `.stl` in its `stl_dir`. Keep each style folder limited to the intended sections. Do not mix multiple `part_03_*back.stl` files in one folder.

Reference-only original downloaded STL source:

```text
D:\Stanford - GI Research\DrivAer\STL_complete\STL_complete_NewPID
```

Do not use that full folder directly as Blender input; it includes alternate variants and files intentionally excluded from the custom simplified workflow.

## Maker Pipeline

`1.code_make_stls_by_blender/`

- Uses Blender lattice/free-form deformation to morph the STL sections.
- For multi-style runs, update `stl_dir`, `export_dir`, and `input_params` together.
- Example mapping: Notchback uses `...\Notchback\body`, `stl_N`, and `lhs_parameters_Notch_v3.csv`; Estate uses `...\Estate\body`, `stl_E`, and `lhs_parameters_Estate_v3.csv`.
- For the first dry run, use only a few parameter rows and vary width/length.

`2.code_Wheel_Alignment/`

- Original purpose: reposition/scale wheels after body morphing and write `floor.txt`.
- `floor.txt` is later used by the Star-CCM+ macro to set the moving-ground height.
- Custom geometry uses closed-wheel filenames. If this stage is retained, update it to read/write `part_05_Wheels_Front_Closed.stl` and `part_06_Wheels_Rear_Closed.stl`, or establish a consistent normalized output name used by the Java macros.
- Check the original bug: rear wheels were loaded from the front-wheel source in places.

`3.make_java_code_E/`

- Generates or contains Star-CCM+ Java macros.
- `stl_2_dbs`: imports STL wheel/porous parts and exports `.dbs`.
- `baomian`: surface-wraps body sections into `body.dbs` (`baomian` roughly means wrapped surface).
- `KwWakeRefine0521`: builds the domain, subtracts vehicle geometry, creates regions, meshes, sets physics/BCs, reports, runs, and exports `.case`.
- This is the main area requiring edits for simplified geometry and yaw.

`4.run/`

- Shows the intended Star-CCM+ macro order: `stl_2_dbs.java`, `baomian.java`, then `KwWakeRefine0521.java`.
- Not needed if only preparing STL folders and Java macros.
- Creating `.dbs`, `.sim`, or `.case` requires running Star-CCM+.

`5.case_to_vtk/` and `6.vtk_to_force_coefficient/`

- Not needed until Star-CCM+ has run and exported Ensight `.case` files.

## Simplified Geometry Implications

The original Java macros assume the full engine-flow setup, including:

```text
part_01_Body_Open_EngineBayFlow
part_02_UB_EngineBayFlow
part_04_ExhaustSystem_EngineBayFlow
part_08_EngineBayTrim_EngineBayFlow
part_09_EngineAndGearbox_EngineBayFlow
part_10_FrontGrills_EngineBayFlow
part_11B_PressureLoss_Porosity_EngineBayFlow
Porosity_EngineBayFlow region/interface
```

The custom prepared geometry does not include those internal-flow/exhaust/porous structures and uses names like `part_01_Body`, `part_02_UB_Smooth`, and closed-wheel filenames. Therefore, the Java macros must be simplified or the generated STLs must be renamed consistently. Prefer simplifying the Java macros so the case setup matches the actual external-aero geometry.

Remove or update references to missing parts in:

- STL import lists
- surface wrapping
- domain subtraction
- boundary lookups
- force/frontal-area reports
- Ensight case export boundary lists
- ParaView block selectors later, if converting to VTK

## Contact Patch And Wheels

There is no explicit named contact-patch treatment in the current repo.

The original workflow computes the lowest wheel z, writes `floor.txt`, then `KwWakeRefine0521.java` reads it, converts mm to m, and adds `0.02`. The domain bottom is placed at that raised floor, and the wheels are subtracted from the domain, so the floor clips/intersects the tire and effectively creates the contact patch.

The wheels are not stitched to the body or axle. They are separate geometry parts and become separate rotating wall boundaries.

## Yaw Extension

Preferred yaw order:

1. Generate morphed geometry.
2. Align/scale wheels and write `floor.txt`.
3. Rotate all vehicle-related STL parts together about a consistent vehicle reference point.
4. Run/prepare DBS and body wrapping on the yawed STLs.
5. Update Star-CCM+ BCs and reports for yaw.

For a straight rectangular domain:

- Keep the outer block aligned with global axes.
- Keep inlet/outlet and moving ground aligned with global streamwise flow unless the user chooses a different wind-tunnel convention.
- Rotate wheel local rotation axes and wheel coordinate-system origins with the vehicle.
- Decide whether reports are in global wind axes or vehicle body axes; make this explicit.

Known original hardcodes to fix before yaw or non-Estate styles:

- Wheel rotation axis is hardcoded as `(0, -1, 0)`.
- Front/rear wheel coordinate-system origins are hardcoded.
- Some macro sections hardcode `body.part_03_Estate.Surface`; use the selected `back` style or the actual custom part name.

## Safe Working Rules

- Keep dry runs small: one body style and a few cases.
- Preserve original `DrivAerStar_Maker/`; edit `DrivAerStar_Maker_Custom/`.
- Do not submit Slurm jobs or run Star-CCM+ without explicit approval.
- Do not assume original boundary names still exist after switching to the simplified geometry.
