import pandas as pd
import matplotlib.pyplot as plt
import os

BYTE_TO_MBYTE = 1 / (1024*1024)
BYTE_TO_KBYTE = 1 / (1024)

def check_dependency_dir(dirs):
   for _ in dirs:
      if not os.path.exists(_):
         os.makedirs(_,exist_ok=True)
   
def proecess_raw_log_file(raw_dir, out_dir):  
  rmw_name = ""
  raw_log_files = os.listdir(raw_dir) # get files
  for log_file in raw_log_files: 
    file_path = os.path.join(raw_dir, log_file) # make relative file path
    if os.path.isfile(file_path): # check exist
      with open(file_path, 'r') as file:
          lines = file.readlines()
          start_line = 0
          for i, line in enumerate(lines):
            if 'RMW Implementation:' in line:
              rmw_name = line.split(': ')[1].strip() # 콜론(:) 뒤의 값을 추출하고 공백을 제거
            if line.strip() == '---EXPERIMENT-START---': # data section
                start_line = i + 1
                break
      # extraction data section
      temp_csv_name = f"{out_dir}/{rmw_name}_{log_file}.csv"
      precessed_line = [line.replace(',', '') for line in lines[start_line:]] # remove ','
      precessed_line = [line.replace('\t\t','\t') for line in precessed_line] # remove duplicated '\t'
      with open(temp_csv_name, 'w') as file:
        file.writelines(precessed_line)

def load_data_to_dataframe(directory, filename):
    file_path = os.path.join(directory, filename)
    dataframe = pd.read_csv(file_path, delimiter='\t')
    return dataframe

def draw_recv_sent_data(dataframe, dds_name = "DDS"):
   ax = dataframe.plot(kind='bar',y=['received','sent', 'lost'])
   plt.title('Received/Sent messages per second and Lost messages\n'
              + f'{dds_name}')
   ax.set_ylabel('Number of messages')
   return ax

def draw_latency_and_memory(dataframe, dds_name = "DDS"):
  # copy for dropping
  dataframe = dataframe.copy()
  # create data
  dataframe['maxrss (Mb)'] = dataframe['ru_maxrss'] * BYTE_TO_KBYTE # convert unit
  dataframe.drop(list(dataframe.filter(regex='ru_')),axis=1, inplace=True)
  dataframe['latency_variance (ms) * 100'] = 100.0 * dataframe['latency_variance (ms)']
  percentils_latency = dataframe['latency_mean (ms)'].describe(percentiles=[0.95])
  dataframe['latency_p95 (ms)'] = percentils_latency.iloc[5]
  # target columns
  columns = ['T_experiment',
            'latency_min (ms)',
            'latency_max (ms)',
            'latency_mean (ms)',
            'latency_p95 (ms)',
            'latency_variance (ms) * 100',
            'maxrss (Mb)']
  ax = dataframe[columns].plot(x=columns[0],secondary_y=['maxrss (Mb)'])
  plt.title("Performance Tests Latency \n"
            +f"{dds_name}")
  ax.set_ylabel('ms')
  return ax

def draw_troughput(dataframe, dds_name= "DDS"):
  dataframe['data_received Mbits/s'] = dataframe['data_received'] * BYTE_TO_MBYTE # convert unit
  percentils_data_received = dataframe['data_received Mbits/s'].describe(percentiles=[0.95])
  dataframe['data_received Mbits/s (P95)'] = percentils_data_received.iloc[5]
  ax = dataframe[['T_experiment',
                  'data_received Mbits/s',
                  'data_received Mbits/s (P95)']].plot(x='T_experiment')
  plt.title('Performance Throughput (Mbits/s) Tests\n'
            + f'{dds_name}')
  ax.set_ylabel('Mbits/s')
  return ax

def draw_CPU_usage(dataframe, dds_name= "DDS"):
  ax = dataframe[['T_experiment', 'cpu_usage (%)']].plot(x='T_experiment')
  plt.title('Performance tests CPU usage (%)\n'
            + f'{dds_name}')
  ax.set_ylabel('%')
  return ax

def anlasis_benchmark_to_json(dataframe):
    dataframe_agg = dataframe.agg(['max', 'mean', 'sum', 'median'])

    values = [
        dataframe_agg.loc['mean', 'latency_mean (ms)'],
        dataframe_agg.loc['median', 'latency_mean (ms)'],
        dataframe['latency_mean (ms)'].describe(percentiles=[0.95]).iloc[5],
        dataframe_agg.loc['max', 'ru_maxrss'],
        dataframe_agg.loc['mean', 'received'],
        dataframe_agg.loc['mean', 'sent'],
        dataframe_agg.loc['sum', 'lost'],
        dataframe_agg.loc['mean', 'cpu_usage (%)'],
        dataframe['cpu_usage (%)'].describe(percentiles=[0.95]).iloc[5],
        dataframe_agg.loc['median', 'cpu_usage (%)'],
        dataframe_agg.loc['mean', 'data_received'] * BYTE_TO_MBYTE,
        dataframe_agg.loc['median', 'data_received'] * BYTE_TO_MBYTE,
        dataframe['data_received'].describe(percentiles=[0.95]).iloc[5] * BYTE_TO_MBYTE,
    ]
    json_values = {
        'average_single_trip_time': {
            'dblValue': values[0],
            'unit': 'ms',
        },
        'throughput': {
            'dblValue': values[10],
            'unit': 'Mbit/s',
        },
        'max_resident_set_size': {
            'dblValue': values[3],
            'unit': 'MB',
        },
        'received_messages': {
            'dblValue': values[4],
        },
        'sent_messages': {
            'dblValue': values[5],
        },
        'lost_messages': {
            'intValue': values[6],
        },
        'cpu_usage': {
            'dblValue': values[8],
            'unit': 'percent',
        },
    }
    return json_values
