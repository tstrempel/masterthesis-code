import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import jq
import os
import sys

from plotnine import ggplot, aes, geom_line

# read in JSON as text as python json can't parse multiple JSON objects at a time
def read_in_scaphandre_json_file(file):
    with open(file) as json_file:
        data = json_file.read()
    return data
    
def read_in_system_csv(file):
    return pd.read_csv(file)

def process_socket_energy_data(data):
    energy_data = pd.DataFrame(columns = ['timestamp', 'socket_power', 'core', 'uncore', 'dram'])
    # iterate over JSON objects to fill the dataframe
    iterator = iter(jq.compile(".host").input(text=data))
    power_iterator = iter(jq.compile(".sockets[]").input(text=data))

    # TODO: rewrite for usage with multi-socket systems
    for item,power_item in zip(iterator, power_iterator):
        new_row = {'timestamp': item['timestamp'], 'socket_power': item['consumption'], 'core': power_item['domains'][0]['consumption'], 'uncore': power_item['domains'][1]['consumption'], 'dram': power_item['domains'][2]['consumption']}
        energy_data = energy_data.append(new_row, ignore_index=True)
    
    energy_data['timestamp'] = energy_data['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
    energy_data['socket_power'] = energy_data['socket_power'].apply(lambda x: x/1000000.0)
    energy_data['core'] = energy_data['core'].apply(lambda x: x/1000000.0)
    energy_data['uncore'] = energy_data['uncore'].apply(lambda x: x/1000000.0)
    # energy_data['dram'] = energy_data['socket_power'] - energy_data['core'] - energy_data['uncore']  # dram bug fix by calculating it
    energy_data['dram'] = energy_data['dram'].apply(lambda x: x/1000000.0)

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

    app_dict = dict()
    df_app_power = pd.DataFrame(columns=['app_name', 'consumption'])
    for app in app_set:
        df_tmp = pd.DataFrame(columns = ['timestamp', 'consumption'])
        for app_result in iter(jq.compile('select(.consumers[].exe=="' + app + '")').input(text=data)):
            res = next((sub for sub in app_result['consumers'] if sub['exe'] == app), None)
            new_row = {'timestamp': app_result['host']['timestamp'], 'consumption': res['consumption']}
            df_tmp = df_tmp.append(new_row, ignore_index=True)
        df_tmp.drop_duplicates(keep='first', inplace=True)
        df_tmp['timestamp'] = df_tmp['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
        df_tmp['consumption'] = df_tmp['consumption'].apply(lambda x: x/1000000.0)

        app_name = os.path.basename(os.path.normpath(app))
        app_dict[app_name] = df_tmp
        df_app_power = df_app_power.append({'app_name': app_name, 'consumption': sum(df_tmp['consumption'])}, ignore_index=True)

    df_app_power = df_app_power.sort_values('consumption', ascending=False)
    df_app_power = df_app_power.reset_index(drop=True)
    return app_dict, df_app_power

def plot_biggest_consumers():
    return None

data = read_in_scaphandre_json_file(sys.argv[1])
system_data = read_in_system_csv(sys.argv[2])

energy_data = process_socket_energy_data(data)
system_data = process_system_metrics(system_data)
print("energy data")
print(energy_data)
print("system data")
print(system_data)

energy_data.to_csv(r'plot/energy.csv', index=False)
system_data.to_csv(r'plot/system.csv', index=False)


# fig, ax = plt.subplots()
plt.figure("Energy data")
plt.plot(energy_data['timestamp'], energy_data['socket_power'], label="Socket power consumption")
plt.plot(energy_data['timestamp'], energy_data['core'], label="Core power consumption")
plt.plot(energy_data['timestamp'], energy_data['uncore'], label="Uncore power consumption")
plt.plot(energy_data['timestamp'], energy_data['dram'], label="DRAM power consumption")
plt.xlabel("Timestamp")
plt.ylabel("Power consumption in Watt")
# locs, labels = plt.xticks()
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
# plt.gca().xaxis.locator_params(nbins=10)
plt.locator_params(axis='x', nbins=10)
plt.legend()
plt.grid()


plt.figure("System data")
plt.plot(system_data['timestamp'], system_data['socket_idle'], label="Non Idle")
plt.plot(system_data['timestamp'], system_data['load_average'], label="Load Average")
plt.plot(energy_data['timestamp'], energy_data['socket_power'], label="Socket power consumption")
# plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data-1)], system_data['timestamp'][0], system_data['timestamp'][len(system_data)-1]])
plt.xticks([energy_data['timestamp'][0], system_data['timestamp'][0]])
plt.legend()
plt.grid(True)

app_dict, df_app_power = process_app_metrics(data)

plt.figure("Most energy intesive applications")

for i in range(1, 5):
    plt.plot(app_dict[df_app_power.iloc[i]['app_name']]['timestamp'], app_dict[df_app_power.iloc[i]['app_name']]['consumption'], label=df_app_power.iloc[i]['app_name'])
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
plt.legend()
plt.grid()



# plt.show()


p = (ggplot() + 
  geom_line(aes(x='timestamp', y='socket_power', group=1), data=energy_data, color='green') +
  geom_line(aes(x='timestamp', y='socket_idle', group=1), data=system_data, color='blue'))

fig = p.draw()
fig.show

plt.show()



fig, ax1 = plt.subplots()
color = 'tab:red'
ax1.plot(system_data['timestamp'], system_data['socket_idle'], color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('sin', color=color)  # we already handled the x-label with ax1
ax2.plot(energy_data['timestamp'], energy_data['socket_power'], color=color)
ax2.tick_params(axis='y', labelcolor=color)
fig.tight_layout() 
plt.show()