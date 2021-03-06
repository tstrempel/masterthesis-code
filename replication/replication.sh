#!/bin/bash

function run_pipeline {
    # arg1: output dir
    # arg2: sorting algorithm
    # arg3: array size
    # arg4: waiting period
    # arg5: step
    # arg6: TDP
    # arg7: threads
    # arg8: application
    echo "$1"
    sleep 120
    mkdir "$1"
    scaphandre --no-header json --timeout 86400 --step "$5" --step_nano 0 --max-top-consumers=10 > "$1/energy_data.json" &
    processid_scaphandre=$!
    sleep $4
    { time $8 "$2" "$3"; } 2> "$1/log.txt" &
    processid_sorting=$!
    
    while [ -d "/proc/$processid_sorting" ]; do sleep 1; done
    sleep $4
    kill $processid_scaphandre

    nice js-beautify "$1/energy_data.json" > "$1/energy_data_beautified.json"
    python evaluation.py "$1/energy_data_beautified.json" "$1" "$5" "$6" "$7" "$8" > "$1/stats.txt"
}

function run_time {
    # arg1: output dir
    # arg2: sorting algorithm
    # arg3: array size
    # arg4: application
    echo "$1"
    sleep 10
    mkdir "$1"
    { time $4 "$2" "$3"; } 2> "$1/log.txt"
}

# $1: TDP
# $2: threads
# $3: application, either 'sorting' or 'sorting-O2'


run_time /data/selection_sort_1000 0 1000 $3
run_time /data/selection_sort_2000 0 2000 $3
run_time /data/selection_sort_4000 0 4000 $3
run_pipeline /data/selection_sort_8000 0 8000 5 1 $1 $2 $3
run_pipeline /data/selection_sort_16000 0 16000 5 1 $1 $2 $3
run_pipeline /data/selection_sort_32000 0 32000 5 1 $1 $2 $3
run_pipeline /data/selection_sort_64000 0 64000 5 1 $1 $2 $3
run_pipeline /data/selection_sort_128000 0 128000 5 2 $1 $2 $3
sleep 120
run_pipeline /data/selection_sort_256000 0 256000 5 2 $1 $2 $3
sleep 120

run_time /data/insertion_sort_1000 1 1000 $3
run_time /data/insertion_sort_2000 1 2000 $3
run_time /data/insertion_sort_4000 1 4000 $3
run_pipeline /data/insertion_sort_8000 1 8000 5 1 $1 $2 $3
run_pipeline /data/insertion_sort_16000 1 16000 5 1 $1 $2 $3
run_pipeline /data/insertion_sort_32000 1 32000 5 1 $1 $2 $3
run_pipeline /data/insertion_sort_64000 1 64000 5 1 $1 $2 $3
run_pipeline /data/insertion_sort_128000 1 128000 5 2 $1 $2 $3
sleep 120
run_pipeline /data/insertion_sort_256000 1 256000 5 2 $1 $2 $3
sleep 120

run_time /data/quick_sort_32000 2 32000 $3
run_time /data/quick_sort_64000 2 64000 $3
run_pipeline /data/quick_sort_128000 2 128000 3 1 $1 $2 $3
run_pipeline /data/quick_sort_256000 2 256000 3 1 $1 $2 $3
run_pipeline /data/quick_sort_512000 2 512000 3 1 $1 $2 $3
run_pipeline /data/quick_sort_1024000 2 1024000 5 1 $1 $2 $3
run_pipeline /data/quick_sort_2048000 2 2048000 5 1 $1 $2 $3
sleep 120

run_time /data/qsort_32000 3 32000 $3
run_time /data/qsort_64000 3 64000 $3
run_pipeline /data/qsort_128000 3 128000 3 1 $1 $2 $3
run_pipeline /data/qsort_256000 3 256000 3 1 $1 $2 $3
run_pipeline /data/qsort_512000 3 512000 3 1 $1 $2 $3
run_pipeline /data/qsort_1024000 3 1024000 5 1 $1 $2 $3
run_pipeline /data/qsort_2048000 3 2048000 5 1 $1 $2 $3
