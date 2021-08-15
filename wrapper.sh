#!/bin/bash

function run_pipeline {
    # arg1: output dir
    # arg2: sorting algorithm
    # arg3: array size
    mkdir "$1"
    scaphandre --no-header json --timeout 86400 --step 1 --step_nano 0 --max-top-consumers=200 > "$1/energy_data.json" &
    processid_scaphandre=$!
    sleep 5
    sorting "$2" "$3" &
    processid_sorting=$!
    
    while [ -d "/proc/$processid_sorting" ]; do sleep 1; done
    sleep 5
    kill $processid_scaphandre

    nice js-beautify "$1/energy_data.json" > "$1/energy_data_beautified.json"
    python evaluation.py "$1/energy_data_beautified.json" "$1" 1.0 15 4
}

mkdir selection_sort_50000
# timeout is set to one day (in seconds)
scaphandre --no-header json --timeout 86400 --step 1 --step_nano 0 --max-top-consumers=200 > energy_data.json &
processid_scaphandre=$!

sleep 5

sorting 0 50000 &
processid_sorting=$!

while [ -d "/proc/$processid_sorting" ]; do sleep 1; done
sleep 5
kill $processid_scaphandre
