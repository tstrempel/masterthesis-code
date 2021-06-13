#!/bin/bash

# pip install jsbeautifier

timeout=30
step=1
# scaphandre_step=500000000

# get monitoring data
# energy data, timestamps, load average, system stat (cpu util etc.)
/home/tstrempel/git/scaphandre-custom/target/release/scaphandre --no-header json -t $timeout -s $step > data/energy_data.json &
echo $step > data/step.txt

# wait until all is done
sleep $timeout
sleep 1

# process monitoring data
js-beautify data/energy_data.json > data/energy_data_beautified.json
python evaluation.py data/energy_data_beautified.json
