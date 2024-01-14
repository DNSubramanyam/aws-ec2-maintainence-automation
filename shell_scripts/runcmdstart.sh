script_file_path=/tmp/atom
initial_status=`sh $script_file_path status|awk '{print $3}'|sed 's/.$//'`
if [ "$initial_status" = "offline" ]
then
    sh $script_file_path start > /dev/null 2>&1
    if [ `sh atom status|awk '{print $3}'|sed 's/.$//'` = "running" ]
    then
        echo "running"
    else
        echo "failed"
    fi
else
    echo "$initial_status"
fi
