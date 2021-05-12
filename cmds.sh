#!/bin/bash

# get monitoring data
# ( /home/tstrempel/git/scaphandre/target/release/scaphandre --no-header json -t 10 > energy_data.json ; for i in {1..10}; do date +"%T.%3N"; cat /proc/loadavg ; sleep 1; done > load_average.txt ) | parallel

timeout=100
step=1

# get monitoring data
# energy data, timestamps, load average, system stat (cpu util etc.)
/home/tstrempel/git/scaphandre/target/release/scaphandre --no-header json -t $timeout -s $step > data/energy_data.json &
for ((i=1; i<=$timeout; i++)); do date +"+%s%3N"; sleep $step; done > data/time.txt &
for ((i=1; i<=$timeout; i++)); do cat /proc/loadavg; sleep $step; done > data/load_average.txt &
# vmstat $step $timeout > data/sys.txt &
mpstat $step $timeout > data/sys.txt &

sleep $timeout
sleep 1

# process monitoring data
jq '.sockets[] | .consumption' data/energy_data.json > data/energy_data.txt
awk -e '{print $1}' < data/load_average.txt > data/load_average2.txt
sed -e '1,3d' < data/sys.txt | sed -e '$ d' | awk -e '{print $13}' > data/sys2.txt

paste -d ',' data/time.txt data/energy_data.txt data/sys2.txt data/load_average2.txt > data/all.csv
rm data/time.txt data/energy_data.txt data/sys.txt data/sys2.txt data/load_average.txt data/load_average2.txt

# 1 min load average
# cat /proc/loadavg | awk -e '{print $1}' > load_average.txt
