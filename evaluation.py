import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import jq
import json

# read in JSON as text as python json can't parse multiple JSON objects at a time
with open('data/energy_data_beautified.json') as json_file:
    data = json_file.read()

energy_data = pd.DataFrame(columns = ['timestamp', 'socket_power', 'core', 'uncore', 'dram'])
# iterate over JSON objects to fill the dataframe
iterator = iter(jq.compile(".host").input(text=data))
power_iterator = iter(jq.compile(".sockets[]").input(text=data))

for item,power_item in zip(iterator, power_iterator):
    new_row = {'timestamp': item['timestamp'], 'socket_power': power_item['consumption'], 'core': power_item['domains'][0]['consumption'], 'uncore': power_item['domains'][1]['consumption'], 'dram': power_item['domains'][2]['consumption']}
    energy_data = energy_data.append(new_row, ignore_index=True)

energy_data['timestamp'] = energy_data['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
energy_data['socket_power'] = energy_data['socket_power'].apply(lambda x: x/1000000.0)
energy_data['core'] = energy_data['core'].apply(lambda x: x/1000000.0)
energy_data['uncore'] = energy_data['uncore'].apply(lambda x: x/1000000.0)
# energy_data['dram'] = energy_data['socket_power'] - energy_data['core'] - energy_data['uncore']  # dram bug fix by calculating it
energy_data['dram'] = energy_data['dram'].apply(lambda x: x/1000000.0)

print(len(energy_data))
plt.plot(energy_data['timestamp'], energy_data['socket_power'], label="Socket power consumption")
plt.plot(energy_data['timestamp'], energy_data['core'], label="Core power consumption")
plt.plot(energy_data['timestamp'], energy_data['uncore'], label="Uncore power consumption")
plt.plot(energy_data['timestamp'], energy_data['dram'], label="DRAM power consumption")
plt.xlabel("Timestamp")
plt.ylabel("Socket power consumption in Watt")
locs, labels = plt.xticks()
plt.xticks([energy_data['timestamp'][0], energy_data['timestamp'][len(energy_data)-1]])
plt.legend()
plt.grid()
plt.show()