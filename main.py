import pandas as pd
import matplotlib.pyplot as plt
import json
import re
import os
import perf_test_result_analysis as perf

log_file_dir = "./log"
log_raw_dir = log_file_dir + "/experiment"
log_temp_dir = log_file_dir + "/temp"

result_dir="./result"
pattern = r'Array\d+m'

dirs = [log_file_dir,log_raw_dir,log_temp_dir,result_dir]
perf.check_dependency_dir(dirs)

# proecessing raw data 
perf.proecess_raw_log_file(log_raw_dir,log_temp_dir)

csv_files = [f for f in os.listdir(log_temp_dir) if f.endswith('.csv')]

for i in range(0,len(csv_files)) : 
  rmw = csv_files[i].split("_pub")[0]
  data_size = re.search(pattern, csv_files[i]).group()
  prefix_path = result_dir + f"/{rmw}/{data_size}"
  if not os.path.exists(prefix_path):
    os.makedirs(prefix_path)

  df = perf.load_data_to_dataframe(log_temp_dir, csv_files[i])
  ax = perf.draw_recv_sent_data(df)
  plt.savefig(prefix_path+"/histogram.png")
  plt.close()
  ax = perf.draw_CPU_usage(df)
  plt.savefig(prefix_path+"/cpu_usage.png")
  plt.close()
  ax = perf.draw_troughput(df)
  plt.savefig(prefix_path + '/throughput.png')
  plt.close()
  ax = perf.draw_latency_and_memory(df)
  plt.savefig(prefix_path+"/latency_memory.png")
  plt.close()
  json_data = perf.anlasis_benchmark_to_json(df)
  with open(prefix_path+'/benchmark.json','w') as file:
    json.dump(json_data,file,indent=2)