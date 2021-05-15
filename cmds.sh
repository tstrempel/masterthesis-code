#!/bin/bash

# get monitoring data
# ( /home/tstrempel/git/scaphandre/target/release/scaphandre --no-header json -t 10 > energy_data.json ; for i in {1..10}; do date +"%T.%3N"; cat /proc/loadavg ; sleep 1; done > load_average.txt ) | parallel

timeout=10
step=1
scaphandre_step=100000000

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
jq '.sockets[] | .consumption' data/energy_data.json > data/energy_data.txt
jq '.host.timestamp' data/energy_data.json > data/time_data.txt
jq '.consumers[] | select(.exe=="/usr/share/code/code") | .consumption' data/energy_data.json > data/app.txt
# paste -d ',' "$(jq '. | select(.consumers[].exe=="/usr/share/code/code") | .host.timestamp' data/energy_data.json)" "$(jq '.consumers[] | select(.exe=="/usr/share/code/code") | .consumption' data/energy_data.json)" > app.csv

awk -e '{print $1}' < data/load_average.txt > data/load_average2.txt
sed -e '1,3d' < data/sys.txt | sed -e '$ d' | awk -e '{print $13}' > data/sys2.txt
echo "timestamp,socket_idle,load_average" > data/system_data.csv
paste -d ',' data/time.txt data/sys2.txt data/load_average2.txt >> data/system_data.csv

# first=$(head -n 1 data/time.txt)
# for ((i=0; i<$((2 * $timeout)); i++)); do echo $(($first + i * 500)); done > data/time_data.txt
echo "timestamp,socket_power,app_power" > data/energy_data.csv
paste -d ',' data/time_data.txt data/energy_data.txt data/app.txt >> data/energy_data.csv
# rm data/time.txt data/energy_data.txt data/sys.txt data/sys2.txt data/load_average.txt data/load_average2.txt

python evaluation.py
