#!/bin/bash

# pip install jsbeautifier

timeout=400
step=1
step_nano=0
# step_nano=100000000

mkdir data plots
# get monitoring data
# energy data, timestamps, load average, system stat (cpu util etc.)
/home/tstrempel/git/scaphandre-custom/target/release/scaphandre --no-header json --timeout $timeout --step $step --step_nano $step_nano --max-top-consumers=200 > data/energy_data.json
echo $step > data/step.txt

# wait until all is done
sleep $timeout
sleep 1

# process monitoring data
js-beautify data/energy_data.json > data/energy_data_beautified.json
python evaluation.py data/energy_data_beautified.json plots 1.0
