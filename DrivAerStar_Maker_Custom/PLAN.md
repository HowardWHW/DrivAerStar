# Plan: Goal 1 Replication, Then Goal 2 Yaw Extension

## Summary

Build the custom pipeline in `DrivAerStar_Maker_Custom/` only. First, make a tiny Notchback dry-run path that morphs only `car_width` and `car_len` for a few cases. Then extend that path for yaw by rotating the aligned STL model before Star-CCM+ import, and by updating wheel rotation axes/origins in the Star-CCM+ macro so rotating-wall boundary conditions match the yawed vehicle.

No Star-CCM+, Slurm jobs, Blender batch jobs, or bulk generation should be run as part of implementation unless explicitly requested later.

## Goal 1: Small Notchback Replication

1. Update `1.code_make_stls_by_blender/doe.py`.
   - Generate a small Notchback CSV, not 8000 rows.
   - Use the existing 20-column header so downstream scripts remain compatible.
   - Keep all parameters neutral except:
     - `car_size = 1.0`
     - `tires_diameter = 0.0`
     - `tires_width = 0.0`
     - vary only `car_width` and `car_len`
   - Use deterministic rows rather than random sampling, for example:
     - baseline: `car_width=0.0`, `car_len=0.0`
     - width-only: `car_width=0.05`, `car_len=0.0`
     - length-only: `car_width=0.0`, `car_len=0.05`
     - combined: `car_width=0.05`, `car_len=0.05`
   - Write to `lhs_parameters_Notch_v3.csv`.

2. Update `1.code_make_stls_by_blender/make.blender.py`.
   - Point `stl_dir` to `D:\DrivAer\DrivAer_STLs\Notchback\body`.
   - Point `export_dir` to a small dry-run output folder, e.g. `D:\DrivAer\stl_N`.
   - Load `lhs_parameters_Notch_v3.csv` from the script directory or an explicit path.
   - Remove or disable the one-off deformation calls before `FFD(...)`; the loop should only export the parameter rows from the CSV.
   - Keep `FFD(params, names)` compatible with the 20-column CSV, but for goal 1 only `car_size`, `car_width`, and `car_len` should have non-neutral values.
   - Preserve output structure: `export_dir\00000\part_01_Body.stl`, `part_02_UB_Smooth.stl`, `part_03_Notchback.stl`, closed wheels, and mirror.

3. Update wheel alignment for the custom Notchback path.
   - Either create/standardize a Notchback custom alignment script or refactor the existing style-specific scripts with explicit config.
   - Use custom simplified filenames:
     - body/underbody reference: `part_02_UB_Smooth.stl`
     - front wheels: `part_05_Wheels_Front_Closed.stl`
     - rear wheels: `part_06_Wheels_Rear_Closed.stl`
   - Fix the known rear-wheel bug: rear wheels must be loaded from the rear-wheel source, not the front-wheel source.
   - Process only the generated small ID range, not `range(0, 8000)`.
   - Continue writing `floor.txt` per case after wheel positioning.

4. Update Java macro generation for the small Notchback path.
   - Set `back = "Notchback"`.
   - Set the root case/STL directory to the small Notchback output folder.
   - Generate macros only for the small dry-run ID range.
   - Simplify templates for external-aero geometry:
     - remove porosity/engine/exhaust/internal-flow DBS imports and region references
     - surface-wrap only body, smooth underbody, selected back, and mirror
     - import/export DBS only for front/rear closed wheels and wrapped body
     - use boundary names matching `part_01_Body`, `part_02_UB_Smooth`, `part_03_Notchback`, `part_07_Mirror`, `Wheels_Front`, and `Wheels_Rear`
   - Keep domain creation straight and global-axis aligned.

## Goal 2: Accurate Yaw Extension

1. Add yaw metadata to the parameter flow.
   - Extend the DOE with a `yaw_deg` column only after goal 1 works.
   - Default `yaw_deg = 0.0` for non-yaw cases.
   - For first yaw validation, use a tiny set such as `0`, `5`, and `-5` degrees with otherwise neutral geometry.

2. Add a post-wheel-alignment yaw case preparation step.
   - Create `2.code_Wheel_Alignment/yaw/prepare_yaw_cases_after_alignment.py` to run after wheel alignment and before Java macro generation.
   - Copy every aligned vehicle STL into each nested yaw case folder:
     - `part_01_Body.stl`
     - `part_02_UB_Smooth.stl`
     - `part_03_Notchback.stl`
     - `part_05_Wheels_Front_Closed.stl`
     - `part_06_Wheels_Rear_Closed.stl`
     - `part_07_Mirror.stl`
   - Write `yaw_metadata.json` containing yaw angle, rotation reference, rotated front/rear wheel origins, and rotated wheel axis.
   - Apply the actual vehicle yaw inside `KwWakeRefine0521_yaw.java` immediately after `execute_input(dir)` and before domain creation.
   - Rotate about global Z using a single documented vehicle reference point. Default reference: the midpoint of the case’s combined vehicle STL bounding box in X/Y, with Z unchanged.
   - Keep the rectangular domain unrotated in Star-CCM+.
   - Preserve `floor.txt`; yaw about Z should not change Z values.

3. Carry yaw data into Java macro generation.
   - Add template placeholders for:
     - `<<<yaw_deg>>>`
     - `<<<yaw_rad>>>`
     - rotated front wheel origin
     - rotated rear wheel origin
     - rotated wheel axis vector
   - Compute these values during yaw case preparation from the same yaw angle and reference point used by the Java yaw rotation.
   - Generate per-case `KwWakeRefine0521_yaw.java` macros with the yaw-specific wheel metadata.

4. Update wheel rotating-wall boundary conditions in `KwWakeRefine0521`.
   - Keep inlet, outlet, moving ground, and domain boxes aligned with global flow axes.
   - Replace hardcoded wheel axis `(0, -1, 0)` with the yaw-rotated vehicle lateral axis.
   - Replace hardcoded front/rear coordinate-system origins with yaw-rotated front/rear wheel-center origins.
   - Apply the same angular speed magnitude as before unless a later validation shows the `wallRelativeRotation = - inlet_velocity/3.6/floor` formula needs replacement with wheel radius from geometry.
   - Keep force and coefficient reports in global wind axes for the first yaw implementation.

## Test Plan

- Static checks:
  - Confirm DOE CSV has the expected header and only a few rows.
  - Confirm `make.blender.py` imports from `D:\DrivAer\DrivAer_STLs\Notchback\body`.
  - Confirm no custom Java template references missing engine-flow, exhaust, porosity, or open-wheel filenames.
  - Confirm generated scripts target only the small ID range.

- Geometry checks without Star-CCM+:
  - For goal 1, inspect generated STL folders for the six expected simplified files.
  - Compare bounding boxes across baseline, width-only, length-only, and combined cases.
  - After wheel alignment, confirm front/rear closed-wheel files exist and `floor.txt` exists.
  - For yaw, confirm XY coordinates rotate by the requested angle, Z bounds and `floor.txt` remain unchanged, and all vehicle parts share the same rotation reference.

- Java-generation checks:
  - Generate macros for only the dry-run IDs.
  - Search generated Java for forbidden old names: `EngineBayFlow`, `Porosity`, `ExhaustSystem`, `FrontGrills`, `EngineAndGearbox`, `Body_Open`, `UB_Engine`.
  - Search generated yaw Java to confirm wheel axes and origins are not hardcoded to `(0, -1, 0)` and fixed old origins.

## Assumptions

- First body style is Notchback.
- Goal 1 should prioritize a small deterministic replication path over preserving bulk 8000-case behavior.
- Reports for yaw remain in global wind axes.
- The straight rectangular domain remains global-axis aligned.
- `floor.txt` remains valid after yaw because the yaw rotation is about global Z.
- Implementation will not modify `DrivAerStar_Maker/`.
