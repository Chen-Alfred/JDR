import time
import subprocess
import logging
from queue import *
from PyQt6.QtCore import *
from jdr_item import *
from jdr_util import *
logging.basicConfig(format="%(message)s", level=logging.INFO)
class JDRThread(QRunnable):
  def __init__(self, window):
    super().__init__()
    self.win = window
    self.change_node_color_signal = SignalObj()
    self.write_log_signal = SignalObj()

  def run(self):
    status_set = set()      # status of items
    dependency_set = set()  # dependency job list
    waiting_buff = list()
    while True:
      time.sleep(1)
      if self.win.sys_close == True:
        break
      try:
        waiting_buff.clear()
        # run jobs in waiting queue
        while not self.win.waiting_queue.empty():
          event = self.win.waiting_queue.get(False)
          item_name = event[0]
          type = event[1]
          cmd = self.win.item_cfg[item_name, 'item_cmd']
          plan_dt = QDateTime.fromString(self.win.item_cfg[item_name, 'item_plan_dt'], 'yyyyMMdd hhmmss')
          curr_dt = QDateTime().currentDateTime()
          if not self.win.run_on_time or curr_dt >= plan_dt:
            p = subprocess.Popen(cmd.split(' '), shell = True)
            self.write_log_signal.write_log_signal.emit(self.win, f'[Info]: JDRThread.run(): Run item: {item_name}, cmd = {cmd}', 1)
          else:
            waiting_buff.append(event)
            
        for event in waiting_buff:
          self.win.waiting_queue.put(event)

        # update jobs status
        if self.win.information['num_waiting_items'] <= 0 and self.win.information['num_running_items'] <= 0:
          status_set.clear()
          dependency_set.clear()
        else:
          item_list = list(set([key[0] for key in self.win.item_cfg.keys() if key[1] == 'item_not' and self.win.item_cfg[key] != 'Y']))
          JDRUtil.get_exec_cfg_by_key(self.win, item_list)
          ctrl_list = list(set(key[0] for key in self.win.exec_cfg))
          for item in item_list:
            if item in ctrl_list and self.win.item_cfg[item, 'item_status'] != self.win.exec_cfg[item, 'status']:
              act_sdt = QDateTime.fromString(self.win.exec_cfg[item, 'act_sdt'], 'yyyy-MM-dd hh:mm:ss')
              proc_dt = QDateTime.fromString(self.win.exec_cfg[item, 'proc_dt'], 'yyyy-MM-dd hh:mm:ss')
              if act_sdt >= proc_dt:
                if (item, self.win.exec_cfg[item, 'status']) not in status_set:
                  status_set.add((item, self.win.exec_cfg[item, 'status']))
                  self.win.information[f'num_{self.win.item_cfg[item, "item_status"]}_items'] -= 1
                  self.win.information[f'num_{self.win.exec_cfg[item, "status"]}_items'] += 1
                  self.win.item_cfg[item, 'org_status'] = self.win.item_cfg[item, 'item_status']  # backup the last status
                  self.win.item_cfg[item, 'item_status'] = self.win.exec_cfg[item, 'status']
                  self.change_node_color_signal.change_node_color_signal.emit(item)

                if type == 'dependency' and self.win.exec_cfg[item, 'status'] == 'success' and self.win.keep_running == True:
                  out_num = len(self.win.graph.out_edges(item))
                  for n in range(out_num):
                    run_flag = 1
                    out_item = list(self.win.graph.out_edges(item))[n][1]
                    in_num = len(self.win.graph.in_edges(out_item))
                    for m in range(in_num):
                      in_item = list(self.win.graph.in_edges(out_item))[m][0]
                      if self.win.item_cfg[in_item, 'item_status'] not in ['undefine', 'notjob']:
                        if self.win.exec_cfg[in_item, 'status'] not in ['success', 'undefine', 'notjob'] or self.win.item_cfg[out_item, 'item_status'] == 'running':
                          run_flag = 0
                    if run_flag == 1 and out_item not in dependency_set:
                      dependency_set.add(out_item)
                      self.win.exec_cfg[out_item, 'status'] = 'waiting'
                      self.win.exec_cfg[out_item, 'proc_dt'] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' # to compare with ctrl.act_sdt
                      self.win.exec_cfg[out_item, 'type'] = 'dependency'
                      self.win.information[f'num_{self.win.item_cfg[out_item, "item_status"]}_items'] -= 1
                      self.win.information['num_waiting_items'] += 1
                      self.win.item_cfg[out_item, 'org_status'] = self.win.item_cfg[out_item, 'item_status']  # backup the last status
                      self.win.item_cfg[out_item, 'item_status'] = 'waiting'
                      self.change_node_color_signal.change_node_color_signal.emit(out_item)
                      self.win.waiting_queue.put((out_item, 'dependency'))
      except Empty:
        self.write_log_signal.write_log_signal.emit(self.win, 'JDRThread.run warning: queue empty', 0)
        self.run()
