script_file_path=/app/dellboomi/Boomi_Atmosphere/Atom/Atom_DV_G1_A1_01/bin/atom
initial_status=`sh $script_file_path status|awk '{print $3}'|sed 's/.$//'`
if [ "$initial_status" = "running" ]
then
    sh $script_file_path stop > /dev/null 2>&1
    if [ `sh $script_file_path status|awk '{print $3}'|sed 's/.$//'` = "offline" ]
    then
        echo "offline"
    else
        echo "failed"
    fi
else
    echo "$initial_status"
fi
