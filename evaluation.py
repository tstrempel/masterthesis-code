import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import jq
import os

# read in JSON as text as python json can't parse multiple JSON objects at a time
with open('data/energy_data_beautified.json') as json_file:
    data = json_file.read()

energy_data = pd.DataFrame(columns = ['timestamp', 'socket_power', 'core', 'uncore', 'dram'])
# iterate over JSON objects to fill the dataframe
iterator = iter(jq.compile(".host").input(text=data))
power_iterator = iter(jq.compile(".sockets[]").input(text=data))

# TODO: rewrite for usage with multi-socket systems
for item,power_item in zip(iterator, power_iterator):
    new_row = {'timestamp': item['timestamp'], 'socket_power': item['consumption'], 'core': power_item['domains'][0]['consumption'], 'uncore': power_item['domains'][1]['consumption'], 'dram': power_item['domains'][2]['consumption']}
    energy_data = energy_data.append(new_row, ignore_index=True)

df_app = pd.DataFrame(columns = ['timestamp', 'consumption'])
app_iterator = iter(jq.compile('select(.consumers[].exe=="/usr/share/code/code")').input(text=data))
for item in app_iterator:
    # print(item['host']['timestamp'])
    # print(item['consumers'][0])
    res = next((sub for sub in item['consumers'] if sub['exe'] == '/usr/share/code/code'), None)
    new_row = {'timestamp': item['host']['timestamp'], 'consumption': res['consumption']}
    df_app = df_app.append(new_row, ignore_index=True)

df_app.drop_duplicates(keep='first', inplace=True)
df_app['timestamp'] = df_app['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
df_app['consumption'] = df_app['consumption'].apply(lambda x: x/1000000.0)
print(df_app)


energy_data['timestamp'] = energy_data['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
energy_data['socket_power'] = energy_data['socket_power'].apply(lambda x: x/1000000.0)
energy_data['core'] = energy_data['core'].apply(lambda x: x/1000000.0)
energy_data['uncore'] = energy_data['uncore'].apply(lambda x: x/1000000.0)
# energy_data['dram'] = energy_data['socket_power'] - energy_data['core'] - energy_data['uncore']  # dram bug fix by calculating it
energy_data['dram'] = energy_data['dram'].apply(lambda x: x/1000000.0)

print(len(energy_data))

plt.figure("Energy data")
plt.plot(energy_data['timestamp'], energy_data['socket_power'], label="Socket power consumption")
plt.plot(energy_data['timestamp'], energy_data['core'], label="Core power consumption")
plt.plot(energy_data['timestamp'], energy_data['uncore'], label="Uncore power consumption")
plt.plot(energy_data['timestamp'], energy_data['dram'], label="DRAM power consumption")

plt.xlabel("Timestamp")
plt.ylabel("Power consumption in Watt")
locs, labels = plt.xticks()
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
plt.legend()
plt.grid()

plt.figure("App data")
plt.plot(energy_data['timestamp'], energy_data['socket_power'], label="Socket power consumption")
plt.plot(df_app['timestamp'], df_app['consumption'], label="VS Code power consumption")
plt.legend()
plt.grid()


system_data = pd.read_csv("data/system_data.csv")
system_data['timestamp'] = system_data['timestamp'].apply(lambda x: x / 1000.0)
system_data['timestamp'] = system_data['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
system_data['socket_idle'] = system_data['socket_idle'].apply(lambda x: 1 - (x / 100))

plt.figure("System data")
plt.plot(system_data['timestamp'], system_data['socket_idle'], label="Non Idle")
plt.plot(system_data['timestamp'], system_data['load_average'], label="Load Average")
plt.legend()
plt.grid()

# plt.show()

app_set = set()
apps = iter(jq.compile(".consumers[].exe").input(text=data))
for item in apps:
    if item not in app_set and not item == "":
        # app_set.add(os.path.basename(os.path.normpath(item)))
        app_set.add(item)

print(app_set)


#app_dict = dict()
#for app in app_set:
#    df_tmp = pd.DataFrame(columns = ['timestamp', 'consumption'])
#    for app_result in iter(jq.compile('select(.consumers[].exe=="' + app + '")').input(text=data)):
#        res = next((sub for sub in app_result['consumers'] if sub['exe'] == app), None)
#        new_row = {'timestamp': app_result['host']['timestamp'], 'consumption': res['consumption']}
#        df_tmp = df_tmp.append(new_row, ignore_index=True)
#    df_tmp.drop_duplicates(keep='first', inplace=True)
#    app_dict[os.path.basename(os.path.normpath(app))] = df_tmp

#print(app_dict)