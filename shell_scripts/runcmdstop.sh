script_file_path=/tmp/atom
initial_status=`sh $script_file_path status|awk '{print $3}'|sed 's/.$//'`
if [ "$initial_status" = "running" ]
then
    sh $script_file_path stop > /dev/null 2>&1
    if [ `sh atom status|awk '{print $3}'|sed 's/.$//'` = "offline" ]
    then
        echo "offline"
    else
        echo "failed"
    fi
else
    echo "$initial_status"
fi
