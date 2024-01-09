#path=""
log_file_path='/var/log/maintenance_script.log'
script_file_path='/tmp/atom'
initial_status=`sh $script_file_path status|awk '{print $3}'`
if [ ${initial_status::-1} == "running" ]
then
    echo "`date -u`[INFO] `sh atom stop`" >> $log_file_path 2>&1
    rc=$?
    if [ ${rc} -eq 0 ]
    then
        sh $script_file_path status|awk '{print $3}'|sed 's/.$//'
    else
        echo "failed"
    fi
else
    echo "${initial_status::-1}"
fi
