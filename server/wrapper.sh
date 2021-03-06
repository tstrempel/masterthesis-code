#!/bin/bash

function run_pipeline {
    # arg1: output dir
    # arg2: sorting algorithm
    # arg3: array size
    # arg4: waiting period
    # arg5: step
    sleep 120
    mkdir "$1"
    scaphandre --no-header json --timeout 86400 --step "$5" --step_nano 0 --max-top-consumers=10 > "$1/energy_data.json" &
    processid_scaphandre=$!
    sleep $4
    { time sorting "$2" "$3"; } 2> "$1/log_time.txt" &
    processid_sorting=$!
    
    while [ -d "/proc/$processid_sorting" ]; do sleep 1; done
    sleep $4
    kill $processid_scaphandre

    nice js-beautify "$1/energy_data.json" > "$1/energy_data_beautified.json"
    python evaluation_server.py "$1/energy_data_beautified.json" "$1" "$5" 270 28 'sorting' >> "$1/log.txt"
}

function run_time {
    sleep 10
    mkdir "$1"
    { time sorting "$2" "$3"; } 2> "$1/log.txt"
}

function run_pipeline_vtune {
    # arg1: output dir
    # arg2: sorting algorithm
    # arg3: array size
    # arg4: waiting period
    # arg5: step
    sleep 120
    mkdir "$1"
    scaphandre --no-header json --timeout 86400 --step "$5" --step_nano 0 --max-top-consumers=200 > "$1/energy_data.json" &
    processid_scaphandre=$!
    sleep $4
    { vtune -collect hotspots -knob sampling-mode=hw -knob sampling-interval=0.5 -r "$1/hs_$2_$3" sorting "$2" "$3" 2>&1 "$1/log.txt"; } > "$1/log_vtune.txt" &
    processid_sorting=$!

    while [ -d "/proc/$processid_sorting" ]; do sleep 1; done
    sleep $4
    kill $processid_scaphandre

    nice js-beautify "$1/energy_data.json" > "$1/energy_data_beautified.json"
    # python evaluation.py "$1/energy_data_beautified.json" "$1" "$5" 15 4 'sorting' >> "$1/log.txt"    
}

function idle {
    # arg1: output dir
    # arg2: sorting algorithm
    # arg3: array size
    # arg4: waiting period
    # arg5: step
    sleep 10
    scaphandre --no-header json --timeout 600 --step "$5" --step_nano 0 --max-top-consumers=10 > "$1/energy_data.json" &
    nice js-beautify "$1/energy_data.json" > "$1/energy_data_beautified.json"

    python evaluation.py "$1/energy_data_beautified.json" "$1" "$5" 15 4 'sorting' >> "$1/log.txt"
}

# source ~/git/scaphandre-custom/init.sh
# source /opt/intel/oneapi/setvars.sh

run_time selection_sort_1000 0 1000
run_time selection_sort_2000 0 2000
run_time selection_sort_4000 0 4000
run_pipeline selection_sort_8000 0 8000 5 1
run_pipeline selection_sort_16000 0 16000 5 1
run_pipeline selection_sort_32000 0 32000 5 1
run_pipeline selection_sort_64000 0 64000 5 1
run_pipeline selection_sort_128000 0 128000 5 2
sleep 120
run_pipeline selection_sort_256000 0 256000 5 2
sleep 120

run_time insertion_sort_1000 1 1000
run_time insertion_sort_2000 1 2000
run_time insertion_sort_4000 1 4000
run_pipeline insertion_sort_8000 1 8000 5 1
run_pipeline insertion_sort_16000 1 16000 5 1
run_pipeline insertion_sort_32000 1 32000 5 1
run_pipeline insertion_sort_64000 1 64000 5 1
run_pipeline insertion_sort_128000 1 128000 5 2
sleep 120
run_pipeline insertion_sort_256000 1 256000 5 2
sleep 120

run_time quick_sort_32000 2 32000
run_time quick_sort_64000 2 64000
run_pipeline quick_sort_128000 2 128000 3 1
run_pipeline quick_sort_256000 2 256000 3 1
run_pipeline quick_sort_512000 2 512000 3 1
run_pipeline quick_sort_1024000 2 1024000 5 1
run_pipeline quick_sort_2048000 2 2048000 5 1
sleep 120

run_time qsort_32000 3 32000 
run_time qsort_64000 3 64000
run_pipeline qsort_128000 3 128000 3 1
run_pipeline qsort_256000 3 256000 3 1
run_pipeline qsort_512000 3 512000 3 1
run_pipeline qsort_1024000 3 1024000 5 1
run_pipeline qsort_2048000 3 2048000 5 1
