import sys
import time
import random
import psycopg2
from datetime import datetime

cfg = {('TEST_JOB_001', 'run_time'): random.randint(3, 10), ('TEST_JOB_001', 'data_num'): random.randint(1000, 2000), ('TEST_JOB_001', 'exit_code'): 0,
       ('TEST_JOB_002', 'run_time'): random.randint(3, 10), ('TEST_JOB_002', 'data_num'): random.randint(2000, 3000), ('TEST_JOB_002', 'exit_code'): 0,
       ('TEST_JOB_003', 'run_time'): random.randint(3, 10), ('TEST_JOB_003', 'data_num'): random.randint(3000, 4000), ('TEST_JOB_003', 'exit_code'): 0,
       ('TEST_JOB_004', 'run_time'): random.randint(3, 10), ('TEST_JOB_004', 'data_num'): random.randint(4000, 5000), ('TEST_JOB_004', 'exit_code'): 0,
       ('TEST_JOB_005', 'run_time'): random.randint(3, 10), ('TEST_JOB_005', 'data_num'): random.randint(5000, 6000), ('TEST_JOB_005', 'exit_code'): 0,
       ('TEST_JOB_006', 'run_time'): random.randint(3, 10), ('TEST_JOB_006', 'data_num'): random.randint(6000, 7000), ('TEST_JOB_006', 'exit_code'): 0,
       ('TEST_JOB_007', 'run_time'): random.randint(3, 10), ('TEST_JOB_007', 'data_num'): random.randint(7000, 8000), ('TEST_JOB_007', 'exit_code'): 0,
       ('TEST_JOB_008', 'run_time'): random.randint(3, 10), ('TEST_JOB_008', 'data_num'): random.randint(8000, 9000), ('TEST_JOB_008', 'exit_code'): 0,
       ('TEST_JOB_009', 'run_time'): random.randint(3, 10), ('TEST_JOB_009', 'data_num'): random.randint(9000, 10000), ('TEST_JOB_009', 'exit_code'): 0,
       ('TEST_JOB_010', 'run_time'): random.randint(3, 10), ('TEST_JOB_010', 'data_num'): random.randint(0, 1000), ('TEST_JOB_010', 'exit_code'): 0,
       ('Job1', 'run_time'): 3, ('Job1', 'data_num'): random.randint(1000, 2000), ('Job1', 'exit_code'): 0,
       ('Job2', 'run_time'): 4, ('Job2', 'data_num'): random.randint(1000, 2000), ('Job2', 'exit_code'): 0,
       ('Job3', 'run_time'): 2, ('Job3', 'data_num'): random.randint(1000, 2000), ('Job3', 'exit_code'): 0,
       ('Job4', 'run_time'): 3, ('Job4', 'data_num'): random.randint(1000, 2000), ('Job4', 'exit_code'): 0,
       ('Job7', 'run_time'): random.randint(3, 10), ('Job7', 'data_num'): random.randint(1000, 2000), ('Job7', 'exit_code'): 1}
default_run_time = random.randint(3, 6) #3
default_data_num = random.randint(100, 10000) #1000000
default_exit_code = 0

if __name__ == '__main__':
  #print('parameter count：' + str(len(sys.argv)))
  conn = psycopg2.connect(database='mydb', user="postgres", password="1qaz2wsx#EDC", host="127.0.0.1", port="5432")
  cursor = conn.cursor()
  job_name = sys.argv[1]
  plan_dt = f'{sys.argv[2]} {sys.argv[3]}'
  status = 'running'
  act_sdt = f'{datetime.now().strftime("%Y%m%d %H%M%S")}'
  sql = f"insert into ctrl.job_exec_log values ('{job_name}', '{plan_dt}'::timestamp, '{status}', '{act_sdt}'::timestamp, null, null)"
  cursor.execute(sql)
  conn.commit()

  run_time = cfg[(sys.argv[1], 'run_time')] if (sys.argv[1], 'run_time') in cfg else default_run_time
  data_num = cfg[(sys.argv[1], 'data_num')] if (sys.argv[1], 'data_num') in cfg else default_data_num
  exit_code = cfg[(sys.argv[1], 'exit_code')] if (sys.argv[1], 'exit_code') in cfg else default_exit_code
  #print(f'run_time: {run_time}')
  #print(f'data_num: {data_num}')
  #print(f'exit_code: {exit_code}')
  time.sleep(run_time)
  #print('---------- job finish ----------')

  if exit_code == 0:
    status = 'success'    
  else:
    status = 'failure'
    data_num = 0

  act_edt = f'{datetime.now().strftime("%Y%m%d %H%M%S")}'
  sql = f"update ctrl.job_exec_log set status = '{status}', act_edt = '{act_edt}'::timestamp, data_num = {data_num} where job_name = '{job_name}' and plan_dt = '{plan_dt}'::timestamp and act_sdt = '{act_sdt}'::timestamp"
  
  cursor.execute(sql)
  conn.commit()
  conn.close()

  sys.exit(exit_code)
