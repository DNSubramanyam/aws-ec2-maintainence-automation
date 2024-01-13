#!/bin/bash
if ! [ -f /tmp/atom-status ]
then 
    touch /tmp/atom-status
fi
case $1 in
    start) sleep 5;echo "atom is running."|tee >  /tmp/atom-status;;
    stop) sleep 5;echo "atom is stopped."|tee > /tmp/atom-status;;
    status) echo $(cat /tmp/atom-status);;
    *) echo "input invalid";
esac