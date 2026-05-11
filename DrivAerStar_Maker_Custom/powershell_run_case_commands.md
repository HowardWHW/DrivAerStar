## Straightline: 

```
$STARCCM = "D:\Siemens\18.06.006-R8\STAR-CCM+18.06.006-R8\star\bin\starccm+.bat"
$CASE = "D:\DrivAer\stl_N\00000"
$NP = 8

Set-Location $CASE

& $STARCCM -np $NP -power -batch "$CASE\stl_2_dbs.java" 2>&1 | Tee-Object -FilePath "$CASE\2dbs.log"
& $STARCCM -np $NP -power -batch "$CASE\baomian.java" 2>&1 | Tee-Object -FilePath "$CASE\baomian.log"
& $STARCCM -np $NP -power -batch "$CASE\KwWakeRefine0521.java" 2>&1 | Tee-Object -FilePath "$CASE\KwWakeRefine0521.log"
```

## Yaw:

```
$STARCCM = "D:\Siemens\18.06.006-R8\STAR-CCM+18.06.006-R8\star\bin\starccm+.bat"
$CASE = "D:\DrivAer\stl_N_yaw\00000\yaw_neg005p0"
$NP = 8

Set-Location $CASE

& $STARCCM -locale zh -np $NP -power -batch "$CASE\stl_2_dbs.java" 2>&1 | Tee-Object -FilePath "$CASE\2dbs.log"
& $STARCCM -np $NP -power -batch "$CASE\baomian.java" 2>&1 | Tee-Object -FilePath "$CASE\baomian.log"
& $STARCCM -locale zh -np $NP -power -batch "$CASE\KwWakeRefine0521_yaw.java" 2>&1 | Tee-Object -FilePath "$CASE\KwWakeRefine0521_yaw.log"
```