import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

energy_data = pd.read_csv("data/energy_data.csv")
energy_data['timestamp'] = energy_data['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
energy_data['socket_power'] = energy_data['socket_power'].apply(lambda x: x/1000000.0)
energy_data['app_power'] = energy_data['app_power'].apply(lambda x: x/1000000.0)

plt.plot(energy_data['timestamp'], energy_data['app_power'])
plt.plot(energy_data['timestamp'], energy_data['socket_power'])
plt.xlabel("Timestamp")
plt.ylabel("Socket power consumption in Watt")
locs, labels = plt.xticks()
plt.xticks([energy_data['timestamp'][1], energy_data['timestamp'][len(energy_data)-1]])
plt.show()