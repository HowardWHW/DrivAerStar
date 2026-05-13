base_case_path="${BASE_CASE_PATH:-/public/home/your_path/work/starccm/DrivAerStar_12000/stl_F}"
vtk_root="${VTK_ROOT:-/work1/your_path/starccm/DrivAerStar_12000/vtk_F}"
pvpython_path="${PVPYTHON_PATH:-/public/home/your_path/pkg/ParaView-5.13.3-MPI-Linux-Python3.10-x86_64/bin/pvpython}"
style="${STYLE:-F}"
case_file_name="${CASE_FILE_NAME:-KwWakeRefine0503.case}"
case_id_filter="${CASE_ID_FILTER:-}"
max_jobs="${MAX_JOBS:-30}"

script_dir="$(cd "$(dirname "$0")" && pwd)"

case "$style" in
    F|f) pv_script="2F.pv.py" ;;
    E|e) pv_script="2E.pv.py" ;;
    N|n) pv_script="2N.pv.py" ;;
    *)
        echo "Unknown STYLE: $style (use F/E/N)"
        exit 1
        ;;
esac

pv_script_path="${PV_SCRIPT:-$script_dir/$pv_script}"
mkdir -p "$vtk_root"

for dir in "$base_case_path"/*/; do
    folder_name=$(basename "$dir")
    if [ -n "$case_id_filter" ] && [ "$folder_name" != "$case_id_filter" ]; then
        continue
    fi
    case_dir="$base_case_path/$folder_name/case/"
    case_file_path="$case_dir/$case_file_name"
    if [ ! -f "$case_file_path" ]; then
        case_file_path="$case_dir/${style}_${folder_name}.case"
    fi
    
    vtk_case_dir="$vtk_root/$folder_name"
    vtk_file_path="$vtk_case_dir/$folder_name.vtk"

    if [ -f "$vtk_file_path" ]; then
        echo " $vtk_file_path skip"
        continue
    fi

    if [ ! -d "$case_dir" ]; then
        echo "case  $case_dir  skip"
        continue
    fi

    
    
    mkdir -p "$vtk_case_dir"
    (
        echo "run $pvpython_path $pv_script_path $case_file_path $vtk_file_path"
        "$pvpython_path" "$pv_script_path" "$case_file_path" "$vtk_file_path"
        exit_status=$?
        if [ $exit_status -ne 0 ]; then
            echo "run $pvpython_path $pv_script_path $case_file_path $vtk_file_path error exit_status: $exit_status"
        else
            echo "run $pvpython_path $pv_script_path $case_file_path $vtk_file_path win"
        fi
    ) &

    while [ $(jobs -r | wc -l) -ge $max_jobs ]; do
        current_jobs=$(jobs -r | wc -l)
        echo "running: $current_jobs ..."
        sleep 1
    done
done


wait