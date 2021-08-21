#!/bin/bash

function run_pipeline {
    # arg1: output dir
    # arg2: sorting algorithm
    # arg3: array size
    # arg4: waiting period
    # arg5: step
    mkdir "$1"
    scaphandre --no-header json --timeout 86400 --step "$5" --step_nano 0 --max-top-consumers=150 > "$1/energy_data.json" &
    processid_scaphandre=$!
    sleep $4
    { time sorting "$2" "$3"; } 2> "$1/log.txt" &
    processid_sorting=$!
    
    while [ -d "/proc/$processid_sorting" ]; do sleep 1; done
    sleep $4
    kill $processid_scaphandre

    nice js-beautify "$1/energy_data.json" > "$1/energy_data_beautified.json"
    python evaluation.py "$1/energy_data_beautified.json" "$1" "$5" 15 4 'sorting' >> "$1/log.txt"
}

function run_time {
    { time sorting "$2" "$3"; } 2> "$1/log.txt"
}

function run_pipeline_vtune {
    # arg1: output dir
    # arg2: sorting algorithm
    # arg3: array size
    # arg4: waiting period
    # arg5: step
    mkdir "$1"
    scaphandre --no-header json --timeout 86400 --step "$5" --step_nano 0 --max-top-consumers=150 > "$1/energy_data.json" &
    processid_scaphandre=$!
    sleep $4
    { vtune -collect hotspots -knob sampling-mode=hw -knob sampling-interval=0.5 -r "$1/hs_$2_$3" sorting "$2" "$3" 2>&1 "$1/log.txt"; } > "$1/log_vtune.txt" &
    processid_sorting=$!

    while [ -d "/proc/$processid_sorting" ]; do sleep 1; done
    sleep $4
    kill $processid_scaphandre

    nice js-beautify "$1/energy_data.json" > "$1/energy_data_beautified.json"
    python evaluation.py "$1/energy_data_beautified.json" "$1" "$5" 15 4 'sorting' >> "$1/log.txt"    
}

function run_pipeline_vtune_nano {
    # arg1: output dir
    # arg2: sorting algorithm
    # arg3: array size
    # arg4: waiting period
    mkdir "$1"
    scaphandre --no-header json --timeout 86400 --step 0 --step_nano 500000000 --max-top-consumers=150 > "$1/energy_data.json" &
    processid_scaphandre=$!
    sleep $4
    { vtune -collect hotspots -knob sampling-mode=hw -knob sampling-interval=0.5 -r "$1/hs_$2_$3" sorting "$2" "$3" 2>&1 "$1/log.txt"; } > "$1/log_vtune.txt" &
    processid_sorting=$!

    while [ -d "/proc/$processid_sorting" ]; do sleep 1; done
    sleep $4
    kill $processid_scaphandre

    nice js-beautify "$1/energy_data.json" > "$1/energy_data_beautified.json"
    python evaluation.py "$1/energy_data_beautified.json" "$1" 0.5 15 4 'sorting' >> "$1/log.txt"
}


# source ~/git/scaphandre-custom/init.sh
# source /opt/intel/oneapi/setvars.sh

#mkdir selection_sort_1000 selection_sort_2000 selection_sort_4000 selection_sort_8000 selection_sort_16000 selection_sort_32000 selection_sort_64000 selection_sort_128000 selection_sort_256000
#mkdir insertion_sort_1000 insertion_sort_2000 insertion_sort_4000 insertion_sort_8000 insertion_sort_16000 insertion_sort_32000 insertion_sort_64000 insertion_sort_128009 insertion_sort_256000
#mkdir quick_sort_8000 quick_sort_16000 quick_sort_32000 quick_sort_64000 quick_sort_128000 quick_sort_256000 quick_sort_512000
#mkdir qsort_8000 qsort_16000 qsort_32000 qsort_64000 qsort_128000 qsort_256000 qsort_512000

#run_time selection_sort_1000 0 1000
#run_time selection_sort_2000 0 2000
#run_time selection_sort_4000 0 4000
#run_pipeline_vtune selection_sort_8000 0 8000 2 1
#run_pipeline_vtune selection_sort_16000 0 16000 5 1
#run_pipeline_vtune selection_sort_32000 0 32000 5 1
#run_pipeline_vtune selection_sort_64000 0 64000 5 1
run_pipeline_vtune selection_sort_128000 0 128000 5 2
# run_pipeline_vtune selection_sort_256000 0 256000 5 2

#run_time insertion_sort_1000 1 1000
#run_time insertion_sort_2000 1 2000
#run_time insertion_sort_4000 1 4000
#run_pipeline_vtune insertion_sort_8000 1 8000 2 1
#run_pipeline_vtune insertion_sort_16000 1 16000 5 1
#run_pipeline_vtune insertion_sort_32000 1 32000 5 1
#run_pipeline_vtune insertion_sort_64000 1 64000 5 1
run_pipeline_vtune insertion_sort_128000 1 128000 5 2
# run_pipeline_vtune insertion_sort_256000 1 256000 5 2
