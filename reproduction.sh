#!/bin/bash


list = "selection_sort_8000 selection_sort_16000 selection_sort_32000 selection_sort_64000 insertion_sort_8000 insertion_sort_16000 insertion_sort_32000 insertion_sort_64000 quick_sort_128000 quick_sort_256000 quick_sort_512000 quick_sort_1024000 quick_sort_2048000 qsort_128000 qsort_256000 qsort_512000 qsort_1024000 qsort_2048000"
list2 = "selection_sort_128000 selection_sort_256000 insertion_sort_128000 insertion_sort_256000"

### laptop ###
echo "laptop"

# interval of 1s
for value in $list
do
        python laptop/evaluation.py "laptop-O0/$value/energy_data_beautified.json" "laptop-O0/$value" 1 15 4 'sorting' > "laptop-O0/$value/stats.txt"
        python laptop/evaluation.py "laptop-O2/$value/energy_data_beautified.json" "laptop-O2/$value" 1 15 4 'sorting-O2' > "laptop-O2/$value/stats.txt"
done

# interval of 2s
for value in $list2
do
        python laptop/evaluation.py "laptop-O0/$value/energy_data_beautified.json" "laptop-O0/$value" 2 15 4 'sorting' > "laptop-O0/$value/stats.txt"
        python laptop/evaluation.py "laptop-O2/$value/energy_data_beautified.json" "laptop-O2/$value" 2 15 4 'sorting-O2' > "laptop-O2/$value/stats.txt"
done

python laptop/evaluation.py laptop-idle/energy_data_beautified.json laptop-idle 1 15 4 'scaphandre' > "laptop-idle/$value/stats.txt"
python laptop/evaluation.py vpxenc/energy_data_beautified.json vpxenc  1 15 4 'vpxenc' > "vpxenc/$value/stats.txt"
python laptop/evaluation.py vpxenc-vtune/energy_data_beautified.json vpxenc-vtune  1 15 4 'vpxenc' > "vpxenc-vtune/$value/stats.txt"

# legacy evaluation.py
python legacy/evaluation_legacy.py laptop-legacy/prime-ram/energy_data_beautified.json laptop-legacy/prime-ram 1 4 > "laptop-legacy/prime-ram/stats.txt"
python legacy/evaluation_legacy.py laptop-legacy/prime95_short/energy_data_beautified.json laptop-legacy/prime95_short 1 4 > "laptop-legacy/prime95_short/stats.txt"
python legacy/evaluation_legacy.py laptop-legacy/prime95_short2/energy_data_beautified.json laptop-legacy/prime95_short2 1 4 > "laptop-legacy/prime95_short2/stats.txt"
python legacy/evaluation_legacy.py laptop-legacy/vpxenc-synchronised/energy_data_beautified.json laptop-legacy/vpxenc-synchronised 1 4 >  "laptop-legacy/vpxenc-synchronised/stats.txt"
python legacy/evaluation_legacy.py laptop-legacy/vpxenc-unsynchronised/energy_data_beautified.json laptop-legacy/unvpxenc-synchronised 1 1 >  "laptop-legacy/unvpxenc-synchronised/stats.txt"

series="01_quick_sort_128000 01_selection_sort_16000 01_selection_sort_8000 02_quick_sort_128000 02_selection_sort_16000 02_selection_sort_8000 03_quick_sort_128000 03_selection_sort_16000 03_selection_sort_8000 04_quick_sort_128000 04_selection_sort_16000 04_selection_sort_8000 05_quick_sort_128000 05_selection_sort_16000 05_selection_sort_8000 06_quick_sort_128000 06_selection_sort_16000 06_selection_sort_8000 07_quick_sort_128000 07_selection_sort_16000 07_selection_sort_8000 08_quick_sort_128000 08_selection_sort_16000 08_selection_sort_8000 09_quick_sort_128000 09_selection_sort_16000 09_selection_sort_8000 10_quick_sort_128000 10_selection_sort_16000 10_selection_sort_8000"

for value in $series
do
        python laptop/evaluation.py "laptop-series/$value/energy_data_beautified.json" "laptop-series/$value" 1 15 4 'sorting' > stats.txt
done


### server ###

# interval of 1s
for value in $list
do
        python server/evaluation_server.py "server-O0/$value/energy_data_beautified.json" "server-O0/$value" 1 270 28 'sorting' > "server-O0/$value/stats.txt"
        python server/evaluation_server.py "server-O2/$value/energy_data_beautified.json" "server-O2/$value" 1 270 28 'sorting-O2' > "server-O2/$value/stats.txt"
done

# interval of 2s
for value in $list2
do
        python server/evaluation_server.py "server-O0/$value/energy_data_beautified.json" "server-O0/$value" 2 270 28 'sorting' > "server-O0/$value/stats.txt"
        python server/evaluation_server.py "server-O2/$value/energy_data_beautified.json" "server-O2/$value" 2 270 28 'sorting-O2' > "server-O2/$value/stats.txt"
done

python server/evaluation_server.py server-idle/energy_data_beautified.json server-idle 1 270 28 'scaphandre' > "server-idle/$value/stats.txt"


### desktop ###


# interval of 1s
for value in $list
do
        python desktop/evaluation.py "desktop-O0/$value/energy_data_beautified.json" "desktop-O0/$value" 1 65 12 'sorting' > "desktop-O0/$value/stats.txt"
	python desktop/evaluation.py "desktop-O2/$value/energy_data_beautified.json" "desktop-O2/$value" 1 65 12 'sorting-O2' > "desktop-O2/$value/stats.txt"
done

# interval of 2s
for value in $list2
do
        python desktop/evaluation.py "desktop-O0/$value/energy_data_beautified.json" "desktop-O0/$value" 2 65 12 'sorting' > "desktop-O0/$value/stats.txt"
	python desktop/evaluation.py "desktop-O2/$value/energy_data_beautified.json" "desktop-O2/$value" 2 65 12 'sorting-O2' > "desktop-O2/$value/stats.txt"
done

python desktop/evaluation.py desktop-idle/energy_data_beautified.json desktop_idle 1 65 12 'scaphandre' > "desktop-idle/$value/stats.txt"

