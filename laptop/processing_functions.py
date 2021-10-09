import os
import jq
import pandas as pd
from datetime import datetime


# read in JSON as text as python json can't parse multiple JSON objects at a time
def read_in_scaphandre_json_file(file):
    with open(file) as json_file:
        data = json_file.read()
    return data
    
def process_socket_energy_data(data):
    energy_data = pd.DataFrame(columns = ['timestamp', 'consumption', \
        'core', 'uncore', 'dram', 'average_load', 'cpu_load', 'cpu_temp', \
        'mem_total', 'mem_free'])
    # iterate over JSON objects to fill the dataframe
    iterator = iter(jq.compile(".host").input(text=data))
    power_iterator = iter(jq.compile(".sockets[]").input(text=data))

    for item,power_item in zip(iterator, power_iterator):
        # domain consumption metrics are given in dram, core, uncore order
        new_row = {'timestamp': item['timestamp'], 'consumption': item['consumption'], \
            'core': power_item['domains'][1]['consumption'], 'uncore': power_item['domains'][2]['consumption'], \
            'dram': power_item['domains'][0]['consumption'], 'average_load': item['average_load'], \
            'cpu_load': item['cpu_load'], 'cpu_temp': item['cpu_temp'], 'mem_total': item['mem_total'], 'mem_free': item['mem_free']}
        energy_data = energy_data.append(new_row, ignore_index=True)
    
    energy_data['consumption'] = energy_data['consumption'].apply(lambda x: x/1000000.0)
    energy_data['core'] = energy_data['core'].apply(lambda x: x/1000000.0)
    energy_data['uncore'] = energy_data['uncore'].apply(lambda x: x/1000000.0)
    energy_data['dram'] = energy_data['dram'].apply(lambda x: x/1000000.0)

    return energy_data

def process_system_metrics(system_data):
    system_data['timestamp'] = system_data['timestamp'].apply(lambda x: x / 1000.0)
    system_data['timestamp'] = system_data['timestamp'].apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S.%f')[:-3])
    system_data['socket_idle'] = system_data['socket_idle'].apply(lambda x: 1 - (x / 100))
    return system_data

def process_app_metrics(data, interval):
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
            # print(res)
            new_row = {'timestamp': app_result['host']['timestamp'], 'consumption': res['consumption']}
            df_tmp = df_tmp.append(new_row, ignore_index=True)
        df_tmp.drop_duplicates(keep='first', inplace=True)
        df_tmp['consumption'] = df_tmp['consumption'].apply(lambda x: x/1000000.0)
        df_tmp = df_tmp.sort_values('timestamp', ascending=True)
        df_tmp = df_tmp.reset_index(drop=True)

        app_name = os.path.basename(os.path.normpath(app))
        apps[app_name] = df_tmp
        consumption_per_app = consumption_per_app.append({'app_name': app_name, 'consumption': compute_energy_consumption(df_tmp, interval)}, ignore_index=True)

    consumption_per_app = consumption_per_app.sort_values('consumption', ascending=False)
    consumption_per_app = consumption_per_app.reset_index(drop=True)
    return apps, consumption_per_app

def compute_energy_consumption(data, interval):
    return sum(data['consumption'] * float(interval))

def transform_timestamp(df):
    return df.apply(lambda time: datetime.utcfromtimestamp(time).strftime('%H:%M:%S'))
