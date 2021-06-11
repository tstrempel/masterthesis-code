import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import jq
import os
import sys
from scipy import stats

from plotnine import ggplot, aes, geom_line

# read in JSON as text as python json can't parse multiple JSON objects at a time
def read_in_scaphandre_json_file(file):
    with open(file) as json_file:
        data = json_file.read()
    return data
    
def read_in_system_csv(file):
    return pd.read_csv(file)

def process_socket_energy_data(data):
    energy_data = pd.DataFrame(columns = ['timestamp', 'consumption', 'core', 'uncore', 'dram', 'average_load', 'cpu_load'])
    # iterate over JSON objects to fill the dataframe
    iterator = iter(jq.compile(".host").input(text=data))
    power_iterator = iter(jq.compile(".sockets[]").input(text=data))

    # TODO: rewrite for usage with multi-socket systems
    for item,power_item in zip(iterator, power_iterator):
        new_row = {'timestamp': item['timestamp'], 'consumption': item['consumption'], 'core': power_item['domains'][0]['consumption'], 'uncore': power_item['domains'][1]['consumption'], 'dram': power_item['domains'][2]['consumption'], 'average_load': item['average_load'], 'cpu_load': item['cpu_load']}
        energy_data = energy_data.append(new_row, ignore_index=True)
    
    energy_data['timestamp'] = energy_data['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
    energy_data['consumption'] = energy_data['consumption'].apply(lambda x: x/1000000.0)
    energy_data['core'] = energy_data['core'].apply(lambda x: x/1000000.0)
    energy_data['uncore'] = energy_data['uncore'].apply(lambda x: x/1000000.0)
    # energy_data['dram'] = energy_data['consumption'] - energy_data['core'] - energy_data['uncore']  # dram bug fix by calculating it
    energy_data['dram'] = energy_data['dram'].apply(lambda x: x/1000000.0)

    # energy_data['consumption'] = energy_data['consumption'].rolling(7).mean()
    # energy_data['consumption'] = energy_data['consumption'].iloc[::7, :]

    return energy_data

def process_system_metrics(system_data):
    system_data['timestamp'] = system_data['timestamp'].apply(lambda x: x / 1000.0)
    system_data['timestamp'] = system_data['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
    system_data['socket_idle'] = system_data['socket_idle'].apply(lambda x: 1 - (x / 100))
    return system_data

def process_app_metrics(data):
    app_set = set()
    apps = iter(jq.compile(".consumers[].exe").input(text=data))
    for item in apps:
        if item not in app_set and not item == "":
            app_set.add(item)

    apps = dict()
    consumption_per_app = pd.DataFrame(columns=['app_name', 'consumption'])
    for app in app_set:
        df_tmp = pd.DataFrame(columns = ['timestamp', 'consumption'])
        for app_result in iter(jq.compile('select(.consumers[].exe=="' + app + '")').input(text=data)):
            res = next((sub for sub in app_result['consumers'] if sub['exe'] == app), None)
            new_row = {'timestamp': app_result['host']['timestamp'], 'consumption': res['consumption']}
            df_tmp = df_tmp.append(new_row, ignore_index=True)
        df_tmp.drop_duplicates(keep='first', inplace=True)
        df_tmp['timestamp'] = df_tmp['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
        df_tmp['consumption'] = df_tmp['consumption'].apply(lambda x: x/1000000.0)
        # df_tmp = df_tmp.sort_values('timestamp', ascending=True)
        df_tmp = df_tmp.reset_index(drop=True)

        app_name = os.path.basename(os.path.normpath(app))
        apps[app_name] = df_tmp
        consumption_per_app = consumption_per_app.append({'app_name': app_name, 'consumption': sum(df_tmp['consumption'])}, ignore_index=True)

    consumption_per_app = consumption_per_app.sort_values('consumption', ascending=False)
    consumption_per_app = consumption_per_app.reset_index(drop=True)
    return apps, consumption_per_app

def plot_biggest_consumers():
    return None

def compute_energy_consumption(data):
    return sum(data['consumption'] * 1.0)

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
    print(consumption_per_app.iloc[i]['app_name'])
    print(apps[consumption_per_app.iloc[i]['app_name']])
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
plt.ylim(0, 16)
plt.axhline(y=15, color='r', linestyle='-', label='TDP of 15W')
plt.legend()
plt.grid()

plt.show()
