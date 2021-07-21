import sys
import matplotlib.pyplot as plt
from scipy import stats
from processing_functions import *
import numpy as np
import statistics

data = read_in_scaphandre_json_file(sys.argv[1])
interval = sys.argv[2]

energy_data = process_socket_energy_data(data)

print("Total power consumption in Joule")
print(compute_energy_consumption(energy_data, interval))
print(compute_total_energy_consumption(energy_data))
print(energy_data)

energy_data.to_csv(r'plot/energy.csv', index=False)

print("Pearson coefficient:")
print(stats.pearsonr(energy_data['consumption'], energy_data['cpu_load']))
pearson = stats.pearsonr(energy_data['consumption'], energy_data['cpu_load'])
print("Kolmogorov-Smirnov test:")
print(stats.kstest(energy_data['consumption'], energy_data['cpu_load']))
print("Test:")
print(stats.kstest(np.random.normal(size=1000000), 'expon'))
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

print("Median")
print(statistics.median(energy_data['consumption']))

plt.figure("Histogram")
plt.hist(energy_data['consumption'])

plt.figure("data")
plt.plot(energy_data['consumption'], energy_data['cpu_load'], 'o')
# plt.show()

plt.figure("Energy data")
plt.title("Energy data")
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
plt.title("System data\n Pearson: {:.2f}".format(pearson[0]))
plt.plot(energy_data['timestamp'], energy_data['cpu_load'], label="CPU Load")
# plt.plot(energy_data['timestamp'], energy_data['average_load'], label="Average Load 1min")
# scale down with TDP
plt.plot(energy_data['timestamp'], energy_data['consumption'].apply(lambda x: x/15.0), label="Total power consumption")
plt.xlabel("Timestamp")
plt.ylabel("Power consumption scaled down and CPU Load")
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
plt.ylim(0, 1.1)
# plt.axhline(y=15, color='r', linestyle='-', label='TDP of 15W')
plt.legend()
plt.grid(True)

# apps store a dataframe value with all related measurements to an app 
# consumption_per_app stores the sum of all energy measurements of an app
apps, consumption_per_app = process_app_metrics(data, interval)

print("App")
# print(consumption_per_app.loc[consumption_per_app['app_name'] == "mprime"]['consumption'])

plt.figure("Most energy intensive applications")
plt.title("Most energy intensive applications")
# add this so that every data point is already on the plot, if not it will look weird later when programs which may not have a measurement in every step are added
plt.plot(energy_data['timestamp'], energy_data['consumption'], label="Total power consumption")

for i in range(0, 5):
    plt.plot(apps[consumption_per_app.iloc[i]['app_name']]['timestamp'], apps[consumption_per_app.iloc[i]['app_name']]['consumption'], label=consumption_per_app.iloc[i]['app_name'])
plt.xlabel("Timestamp")
plt.ylabel("Power consumption in Watt")
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
plt.ylim(0, 16)
plt.axhline(y=15, color='r', linestyle='-', label='TDP of 15W')
plt.legend()
plt.grid()

print("pi")
print(consumption_per_app.loc[consumption_per_app['app_name'] == "pi"]['consumption'])

# rolling average for better visualization
energy_data_rolling_avg = energy_data.rolling(10).mean()
energy_data_rolling_avg['timestamp'] = energy_data['timestamp']
energy_data_rolling_avg = energy_data_rolling_avg.dropna()
energy_data_rolling_avg = energy_data_rolling_avg.reset_index(drop=True)
plt.figure("Rolling average")
plt.title("Rolling average")
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