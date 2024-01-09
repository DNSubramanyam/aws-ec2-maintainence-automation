#!/bin/bash
if ! [ -f /tmp/atom-status ]
then 
    touch /tmp/atom-status
fi
case $1 in
    start) echo "atom is running.";sleep 5;echo "atom is running." >  /tmp/atom-status;;
    stop) echo "atom is stopped.";sleep 5 ;echo "atom is stopped." > /tmp/atom-status;;
    status) echo $(cat /tmp/atom-status);;
    *) echo "input invalid";
esac