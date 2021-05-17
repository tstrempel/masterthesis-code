import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import jq
import json

# read in JSON as text as python json can't parse multiple JSON objects at a time
with open('data/energy_data_beautified.json') as json_file:
    data = json_file.read()

energy_data = pd.DataFrame(columns = ['timestamp', 'socket_power'])
# iterate over JSON objects to fill the dataframe
iterator = iter(jq.compile(".host").input(text=data))
power_iterator = iter(jq.compile(".sockets[]").input(text=data))

for item in iterator:
    new_row = {'timestamp': item['timestamp'], 'socket_power': item['consumption']}
    energy_data = energy_data.append(new_row, ignore_index=True)
energy_data['timestamp'] = energy_data['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
energy_data['socket_power'] = energy_data['socket_power'].apply(lambda x: x/1000000.0)

# energy_data['app_power'] = energy_data['app_power'].apply(lambda x: x/1000000.0)

print(len(energy_data))
# plt.plot(energy_data['timestamp'], energy_data['app_power'])
plt.plot(energy_data['timestamp'], energy_data['socket_power'])
plt.xlabel("Timestamp")
plt.ylabel("Socket power consumption in Watt")
locs, labels = plt.xticks()
plt.xticks([energy_data['timestamp'][1], energy_data['timestamp'][len(energy_data)-1]])
plt.show()