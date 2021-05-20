#!/bin/bash

# pip install jsbeautifier
# get monitoring data
# ( /home/tstrempel/git/scaphandre/target/release/scaphandre --no-header json -t 10 > energy_data.json ; for i in {1..10}; do date +"%T.%3N"; cat /proc/loadavg ; sleep 1; done > load_average.txt ) | parallel

timeout=20
step=1
scaphandre_step=200000000

# get monitoring data
# energy data, timestamps, load average, system stat (cpu util etc.)
/home/tstrempel/git/scaphandre/target/release/scaphandre --no-header json -t $timeout -s 0 -n $scaphandre_step > data/energy_data.json &
for ((i=1; i<=$timeout; i++)); do date +"+%s%3N"; sleep $step; done > data/time.txt &
for ((i=1; i<=$timeout; i++)); do cat /proc/loadavg; sleep $step; done > data/load_average.txt &
# vmstat $step $timeout > data/sys.txt &
mpstat $step $timeout > data/sys.txt &

sleep $timeout
sleep 1

# process monitoring data

awk -e '{print $1}' < data/load_average.txt > data/load_average2.txt
sed -e '1,3d' < data/sys.txt | sed -e '$ d' | awk -e '{print $13}' > data/sys2.txt
echo "timestamp,socket_idle,load_average" > data/system_data.csv
paste -d ',' data/time.txt data/sys2.txt data/load_average2.txt >> data/system_data.csv

# rm data/time.txt data/energy_data.txt data/sys.txt data/sys2.txt data/load_average.txt data/load_average2.txt

js-beautify data/energy_data.json > data/energy_data_beautified.json
python evaluation.py
