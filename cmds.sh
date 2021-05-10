#!/bin/bash

# get monitoring data
( /home/tstrempel/git/scaphandre/target/release/scaphandre --no-header json -t 10 > energy_data.json ; for i in {1..10}; do cat /proc/loadavg ; sleep 1; done  | awk -e '{print $1}' > load_average.txt ) | parallel

# get socket consumption
jq '.sockets[] | .consumption' energy_data.json

# 1 min load average
cat /proc/loadavg | awk -e '{print $1}' > load_average.txt
