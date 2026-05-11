# Yaw Run Path

This path is reserved for yaw-specific run scripts. Do not reuse the straight
`4.run/krun_10.slurm` path for yawed cases without adding the yaw wheel-boundary
macro into the Star-CCM+ sequence.

Expected yaw case folder root:

```text
D:/DrivAer/stl_N_yaw
```

Expected nested case folders:

```text
D:/DrivAer/stl_N_yaw/00000/yaw_neg05p0
D:/DrivAer/stl_N_yaw/00000/yaw_pos05p0
D:/DrivAer/stl_N_yaw/00001/yaw_neg05p0
```

Expected generated macros per case:

```text
stl_2_dbs.java
baomian.java
KwWakeRefine0521_yaw.java
```

`KwWakeRefine0521_yaw.java` replaces `KwWakeRefine0521.java` for yawed cases.
It keeps the full case setup in one macro and applies yaw after `execute_input()`.
It writes `star.KwWakeRefine0521_yaw.sim` and `case/KwWakeRefine0521_yaw.case`
inside the yaw subcase folder.
