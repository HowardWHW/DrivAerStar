# Yaw Case Preparation Stage

This folder is separate from the straight wheel-alignment scripts.

`prepare_yaw_cases_after_alignment.py` reads aligned straight-case folders from
`D:/DrivAer/stl_N` and writes yaw case folders under `D:/DrivAer/stl_N_yaw`.

Each base geometry gets its own yaw subcases:

```text
D:/DrivAer/stl_N_yaw/00000/yaw_neg05p0/
D:/DrivAer/stl_N_yaw/00000/yaw_neg02p5/
D:/DrivAer/stl_N_yaw/00000/yaw_pos02p5/
D:/DrivAer/stl_N_yaw/00000/yaw_pos05p0/
D:/DrivAer/stl_N_yaw/00001/yaw_neg05p0/
...
```

Folder naming uses `neg`/`pos` and replaces the decimal point with `p` so paths
are sortable and shell-safe.

It copies the straight aligned STLs into each yaw subcase:

- `part_01_Body.stl`
- `part_02_UB_Smooth.stl`
- `part_03_Notchback.stl`
- `part_05_Wheels_Front_Closed.stl`
- `part_06_Wheels_Rear_Closed.stl`
- `part_07_Mirror.stl`

Before writing a yaw subcase, the script clears that yaw subfolder so stale
macros, `.dbs`, `.sim`, logs, and `case/` outputs cannot be reused accidentally.
It then copies only the six required STLs plus `floor.txt`, and writes
`yaw_metadata.json` for Java macro generation.

The actual vehicle yaw is applied later inside `KwWakeRefine0521_yaw.java`,
immediately after `execute_input(dir)`, so the full case setup remains in one
Star-CCM+ macro.
