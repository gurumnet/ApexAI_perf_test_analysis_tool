import pandas as pd
import matplotlib.pyplot as plt
import os
import perf_test_result_analysis as perf

log_file_dir = "./log"
log_raw_dir = log_file_dir + "/experiment"
log_temp_dir = log_file_dir + "/temp"

result_dir="./result"

dirs = [log_file_dir,log_raw_dir,log_temp_dir,result_dir]
perf.check_dependency_dir(dirs)

# proecessing raw data 
perf.proecess_raw_log_file(log_raw_dir,log_temp_dir)

csv_files = [f for f in os.listdir(log_temp_dir) if f.endswith('.csv')]

for csv_file in csv_files: 
  df = perf.load_data_to_dataframe(log_temp_dir,csv_file)
  ax = perf.draw_recv_sent_data(df)
  plt.savefig(result_dir + "/histogram.png")
  ax = perf.draw_CPU_usage(df)
  plt.savefig(result_dir + "/cpu_usage.png")
  ax = perf.draw_troughput(df)
  plt.savefig(result_dir + '/throunghput.png')
  ax = perf.draw_latency_and_memory(df)
  plt.savefig(result_dir + "/latency_memory.png")