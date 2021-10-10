import sys
import matplotlib.pyplot as plt
from scipy import stats
from processing_functions import *
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

print("Total energy consumption of all applications:")
print(sum(consumption_per_app['consumption']))

mem_total = energy_data['mem_total'][0] * 1.0
max_dram = 2.92

print("Pearson coefficient:")
pearson = stats.pearsonr(energy_data['consumption'], energy_data['cpu_load'].apply(lambda x: x/float(threads)))
print(pearson)
print("Linregress:")
linregress = stats.linregress(energy_data['consumption'], energy_data['cpu_load'].apply(lambda x: x/float(threads)))
print(linregress)

plt.figure("Data points")
plt.title("Data points")
plt.plot(energy_data['consumption'], energy_data['cpu_load'].apply(lambda x: x/float(threads)), 'o')
plt.xlabel("Power consumption in Watt")
plt.ylabel("CPU Load")
plt.xlim(0, float(tdp)+1)
plt.ylim(0, 1)
plt.grid()
plt.savefig(output_dir + "/data_points.png")

plt.figure("Data points and linear regression")
plt.title("Data points and linear regression")
plt.plot(energy_data['consumption'], energy_data['cpu_load'].apply(lambda x: x/float(threads)), 'o', label='original data')
plt.plot(energy_data['consumption'], linregress.intercept + linregress.slope*energy_data['consumption'], 'r', label='fitted line')
plt.xlabel("Power consumption in Watt")
plt.ylabel("CPU Load")
plt.xlim(0, float(tdp)+1)
plt.ylim(0, 1)
plt.grid()
plt.savefig(output_dir + "/data_points_linregress.png")

plt.figure("Energy data")
plt.title("Energy data")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['consumption'], label="Total power consumption")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['core'], label="Core power consumption")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['uncore'], label="Uncore power consumption")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['dram'], label="DRAM power consumption")
plt.xlabel("Timestamp")
plt.ylabel("Power consumption in Watt")
plt.xticks([transform_timestamp(energy_data['timestamp'])[0], transform_timestamp(energy_data['timestamp'])[len(energy_data)-1]])
plt.ylim(0, float(tdp)+1.0)
plt.axhline(y=float(tdp), color='r', linestyle='-', label='TDP')
plt.locator_params(axis='x', nbins=10)
plt.legend()
plt.grid()
plt.savefig(output_dir + "/energy_data.png")

plt.figure("System data")
plt.title("System data")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['cpu_load'].apply(lambda x: x/float(threads)), label="CPU Load")
# scale down with TDP
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['consumption'].apply(lambda x: x/float(tdp)), label="Total power consumption")
plt.xlabel("Timestamp")
plt.ylabel("Power consumption scaled down and CPU Load")
plt.xticks([transform_timestamp(energy_data['timestamp'])[0], transform_timestamp(energy_data['timestamp'])[len(energy_data)-1]])
plt.ylim(0, 1.1)
plt.legend()
plt.grid(True)
plt.savefig(output_dir + "/system_data.png")

plt.figure("CPU Temperature over time")
plt.title("CPU Temperature over time")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['cpu_temp'], label="CPU Temperature")
plt.xlabel("Timestamp")
plt.ylabel("CPU Temperature")
plt.xticks([transform_timestamp(energy_data['timestamp'])[0], transform_timestamp(energy_data['timestamp'])[len(energy_data)-1]])
plt.ylim(0, 100)
plt.legend()
plt.grid(True)
plt.savefig(output_dir + "/temperature.png")

plt.figure("Memory usage over time")
plt.title("Memory usage over time")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['mem_free'].apply(lambda x: 1 - (x / mem_total)), label="Memory usage 1 -> 7.69 GiB")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['dram'].apply(lambda x: x / max_dram), label="DRAM power consumption 1 -> 2.92 W")
plt.xlabel("Timestamp")
plt.ylabel("Memory usage and DRAM power consumption to scale")
plt.xticks([transform_timestamp(energy_data['timestamp'])[0], transform_timestamp(energy_data['timestamp'])[len(energy_data)-1]])
plt.ylim(0, 1.1)
plt.legend()
plt.grid(True)
plt.savefig(output_dir + "/memory_usage.png")

print("Application: " + extra_app)
print(consumption_per_app.loc[consumption_per_app['app_name'] == extra_app])
print("Measurements taken of application: " + str(len(apps[extra_app])))

plt.figure("Power consumption of application " + extra_app)
plt.title("Power consumption of application " + extra_app)
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['consumption'], label="Total power consumption")
plt.plot(transform_timestamp(apps[extra_app]['timestamp']), apps[extra_app]['consumption'], label=extra_app)
plt.xlabel("Timestamp")
plt.ylabel("Power consumption in Watt")
plt.xticks([transform_timestamp(energy_data['timestamp'])[0], transform_timestamp(energy_data['timestamp'])[len(energy_data)-1]])
plt.ylim(0, float(tdp)+1.0)
plt.axhline(y=float(tdp), color='r', linestyle='-', label='TDP')
plt.legend()
plt.grid()
plt.savefig(output_dir + "/extra_app.png")

plt.figure("Most energy intensive applications")
plt.title("Most energy intensive applications")
plt.plot(transform_timestamp(energy_data['timestamp']), energy_data['consumption'], label="Total power consumption")
# add this so that every data point is already on the plot, if not it will look weird later when programs which may not have a measurement in every step are added

for i in range(0, 3):
    plt.plot( \
        transform_timestamp(apps[consumption_per_app.iloc[i]['app_name']]['timestamp']), \
        apps[consumption_per_app.iloc[i]['app_name']]['consumption'], \
        label=consumption_per_app.iloc[i]['app_name'])
plt.xlabel("Timestamp")
plt.ylabel("Power consumption in Watt")
plt.xticks([transform_timestamp(energy_data['timestamp'])[0], transform_timestamp(energy_data['timestamp'])[len(energy_data)-1]])
plt.ylim(0, float(tdp)+1.0)
plt.axhline(y=float(tdp), color='r', linestyle='-', label='TDP')
plt.legend()
plt.grid()
plt.savefig(output_dir + "/energy_intensive_apps.png")
