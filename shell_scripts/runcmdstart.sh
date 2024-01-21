script_file_path=/app/dellboomi/Boomi_Atmosphere/Atom/Atom_DV_G1_A1_01/bin/atom
initial_status=`sh $script_file_path status|awk '{print $3}'|sed 's/.$//'`
if [ "$initial_status" = "offline" ]
then
    sh $script_file_path start > /dev/null 2>&1
    if [ `sh $script_file_path status|awk '{print $3}'|sed 's/.$//'` = "running" ]
    then
        echo "running"
    else
        echo "failed"
    fi
else
    echo "$initial_status"
fi
