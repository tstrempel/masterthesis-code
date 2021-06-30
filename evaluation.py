import sys
import matplotlib.pyplot as plt
from scipy import stats
from processing_functions import *


data = read_in_scaphandre_json_file(sys.argv[1])

energy_data = process_socket_energy_data(data)
print("energy data")
print(energy_data)
print(len(energy_data))

print("Total power consumption in Joule")
print(compute_energy_consumption(energy_data))

energy_data.to_csv(r'plot/energy.csv', index=False)

print("Person coefficient:")
print(stats.pearsonr(energy_data['consumption'], energy_data['cpu_load']))
print("Kolmogorov-Smirnov test:")
print(stats.kstest(energy_data['consumption'], energy_data['cpu_load']))
print("Kolmogorov-Smirnov 2-sample test:")
print(stats.ks_2samp(energy_data['consumption'], energy_data['cpu_load']))
print("Linregress:")
print(stats.linregress(energy_data['consumption'], energy_data['cpu_load']))
print("Core correlation:")
print(stats.pearsonr(energy_data['consumption'], energy_data['core']))
print("Uncore correlation")
print(stats.pearsonr(energy_data['consumption'], energy_data['uncore']))
print("DRAM correlation")
print(stats.pearsonr(energy_data['consumption'], energy_data['dram']))

plt.figure("Energy data")
plt.plot(energy_data['timestamp'], energy_data['consumption'], label="Total power consumption")
plt.plot(energy_data['timestamp'], energy_data['core'], label="Core power consumption")
plt.plot(energy_data['timestamp'], energy_data['uncore'], label="Uncore power consumption")
plt.plot(energy_data['timestamp'], energy_data['dram'], label="DRAM power consumption")
plt.xlabel("Timestamp")
plt.ylabel("Power consumption in Watt")
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
plt.ylim(0, 16)
plt.axhline(y=15, color='r', linestyle='-', label='TDP of 15W')
plt.locator_params(axis='x', nbins=10)
plt.legend()
plt.grid()


plt.figure("System data")
plt.plot(energy_data['timestamp'], energy_data['cpu_load'], label="Non Idle")
plt.plot(energy_data['timestamp'], energy_data['average_load'], label="Average Load")
plt.plot(energy_data['timestamp'], energy_data['consumption'], label="Total power consumption")
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
plt.ylim(0, 16)
plt.axhline(y=15, color='r', linestyle='-', label='TDP of 15W')
plt.legend()
plt.grid(True)

# apps store a dataframe value with all related measurements to an app 
# consumption_per_app stores the sum of all energy measurements of an app
apps, consumption_per_app = process_app_metrics(data)

plt.figure("Most energy intesive applications")
# add this so that every data point is already on the plot, if not it will look weird later when programs which may not have a measurement in every step are added
plt.plot(energy_data['timestamp'], energy_data['consumption'], label="Total power consumption")

for i in range(0, 5):
    plt.plot(apps[consumption_per_app.iloc[i]['app_name']]['timestamp'], apps[consumption_per_app.iloc[i]['app_name']]['consumption'], label=consumption_per_app.iloc[i]['app_name'])
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
plt.ylim(0, 16)
plt.axhline(y=15, color='r', linestyle='-', label='TDP of 15W')
plt.legend()
plt.grid()

# rolling average for better visualization
energy_data_rolling_avg = energy_data.rolling(10).mean()
energy_data_rolling_avg['timestamp'] = energy_data['timestamp']
energy_data_rolling_avg = energy_data_rolling_avg.dropna()
energy_data_rolling_avg = energy_data_rolling_avg.reset_index(drop=True)
print(energy_data)
print(energy_data_rolling_avg)
plt.figure("Rolling average")
plt.plot(energy_data_rolling_avg['timestamp'], energy_data_rolling_avg['consumption'], label="Total power consumption")
plt.plot(energy_data_rolling_avg['timestamp'], energy_data_rolling_avg['core'], label="Core power consumption")
plt.plot(energy_data_rolling_avg['timestamp'], energy_data_rolling_avg['uncore'], label="Uncore power consumption")
plt.plot(energy_data_rolling_avg['timestamp'], energy_data_rolling_avg['dram'], label="DRAM power consumption")
plt.xlabel("Timestamp")
plt.ylabel("Power consumption in Watt")
plt.xticks([energy_data_rolling_avg['timestamp'][0], energy_data_rolling_avg['timestamp'][len(energy_data_rolling_avg)-1]])
plt.ylim(0, 16)
plt.axhline(y=15, color='r', linestyle='-', label='TDP of 15W')
plt.legend()
plt.grid(True)

plt.show()