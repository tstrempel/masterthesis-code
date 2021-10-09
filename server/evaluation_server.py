import sys
import matplotlib.pyplot as plt
from scipy import stats
from processing_functions_server import *
import statistics

# parameters: input data, output dir for plots, time measurement step, TDP, cores
# beautified json file from scaphandre
data = read_in_scaphandre_json_file(sys.argv[1])
# output dir for plots
output_dir = sys.argv[2]
# time measurement step
interval = sys.argv[3]
# TDP (thermal design power)
tdp = sys.argv[4]
# number of threads (includes physical and hyperthreading cores, so for a 2 core processor with 2 hyperthreads use 4)
threads = sys.argv[5]
# App
extra_app = sys.argv[6]

energy_data = process_socket_energy_data(data)

print("Total energy consumption in Joule:")
print(compute_energy_consumption(energy_data, interval))

print("Median energy consumption per interval:")
print(statistics.median(energy_data['consumption']))

print("Total scaphandre measurements:")
print(len(energy_data))

# apps store a dataframe value with all related measurements to an app 
# consumption_per_app stores the sum of all energy measurements of an app
apps, consumption_per_app = process_app_metrics(data, interval)

print("Application: " + extra_app)
print("Measurements taken: " + str(len(apps[extra_app])))

plt.figure("Energy data")
plt.title("Energy data")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['consumption'], label="Total power consumption")
plt.xlabel("Timestamp")
plt.ylabel("Power consumption in Watt")
plt.xticks([transform_timestamp(energy_data['timestamp'])[0], transform_timestamp(energy_data['timestamp'])[len(energy_data)-1]])
plt.ylim(0, float(tdp)+1.0)
plt.axhline(y=float(tdp), color='r', linestyle='-', label='TDP')
plt.legend()
plt.grid()
plt.savefig(output_dir + "/energy_data.png")
