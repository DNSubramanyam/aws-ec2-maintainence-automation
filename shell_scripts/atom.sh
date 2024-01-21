#!/bin/bash
if ! [ -f /tmp/atom-status ]
then 
    touch /tmp/atom-status
fi
case $1 in
    "start") sleep 5;echo "`date` atom is running." >> /tmp/log-atom;echo "atom is running."|tee /tmp/atom-status;;
    "stop") sleep 5;echo "`date` atom is offline." >> /tmp/log-atom;echo "atom is offline."|tee /tmp/atom-status;;
    "status") echo $(cat /tmp/atom-status);;
    *) echo "input invalid";;
esac