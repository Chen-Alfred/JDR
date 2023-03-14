import re
from functools import partial
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from jdr_item_report import *
from jdr_util import *

class SignalObj(QObject):
  change_node_color_signal = pyqtSignal(str)
  write_log_signal = pyqtSignal(QObject, str, int)

class JDRItem(QGraphicsSvgItem):
  def __init__(self, window, renderer, id, title):
    super().__init__()
    self.win = window
    self.renderer = renderer
    self.id = id
    self.title = title
    self.change_node_color_signal = SignalObj()
    self.setSharedRenderer(renderer)
    self.setElementId(id)
    if self.id.find('node') != -1:
      if self.win.item_cfg[self.title, 'item_status'] == 'undefine':
        self.init_node_color(JDRUtil.COLOR_UNDEFINE)
      elif self.win.item_cfg[self.title, 'item_status'] == 'notjob':
        self.init_node_color(JDRUtil.COLOR_NOTJOB)
      else:
        self.init_node_color(JDRUtil.COLOR_INITIAL)
    bounds = renderer.boundsOnElement(id)
    self.setPos(bounds.topLeft())

  def contextMenuEvent(self, event: 'QGraphicsSceneContextMenuEvent'):
    if self.id.find('node') != -1 and self.win.item_cfg[self.title, 'item_status'] not in ['undefine', 'notjob']:
      menu = QMenu(self.win)

      self.win.act_single = menu.addAction("Run &Single Item")
      self.win.act_single.triggered.connect(self.run_single_item)
      if self.win.item_cfg[self.title, 'item_status'] in ['waiting', 'running']:
        self.win.act_single.setEnabled(False)
      else:
        self.win.act_single.setEnabled(True)

      self.win.act_depend = menu.addAction("Run &Dependency Item")
      self.win.act_depend.triggered.connect(self.run_dependency_item)
      if self.win.item_cfg[self.title, 'item_status'] in ['waiting', 'running']:
        self.win.act_depend.setEnabled(False)
      else:
        self.win.act_depend.setEnabled(True)

      menu.addSeparator()

      self.win.act_report = menu.addAction("Show &Report")
      self.win.act_report.triggered.connect(partial(self.show_report, self.title))

      menu.addSeparator()

      self.win.act_note1 = menu.addAction("Item Name: " + self.win.item_cfg[self.title, 'item_name'])
      self.win.act_note1.setEnabled(False)
      self.win.act_note2 = menu.addAction("Item Time: " + self.win.item_cfg[self.title, 'item_plan_dt_fmt'])
      self.win.act_note2.setEnabled(False)
      self.win.act_note3 = menu.addAction("Status: " + self.win.item_cfg[self.title, 'item_status'])
      self.win.act_note3.setEnabled(False)

      if self.win.has_cycles == True or self.win.no_freq == True or self.win.err_freq == True or self.win.no_cmd == True or self.win.no_conn == True:
        self.win.act_single.setEnabled(False)
        self.win.act_depend.setEnabled(False)
        self.win.act_report.setEnabled(False)

      menu.exec(event.screenPos())

  
  def run_single_item(self):
    try:
      if self.win.item_cfg[self.title, 'item_status'] not in ['waiting', 'running']:
        JDRUtil.set_run_on_time(self.win.setup_widget3_execute_runontime_check.isChecked())
        self.win.run_on_time = JDRUtil.RUN_ON_TIME
        self.win.exec_cfg[self.title, 'status'] = 'waiting'
        self.win.exec_cfg[self.title, 'proc_dt'] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' # to compare with ctrl.act_sdt
        self.win.exec_cfg[self.title, 'type'] = 'single'
        self.win.information[f'num_{self.win.item_cfg[self.title, "item_status"]}_items'] -= 1
        self.win.information['num_waiting_items'] += 1
        self.win.item_cfg[self.title, 'org_status'] = self.win.item_cfg[self.title, 'item_status']  # backup the last status
        self.win.item_cfg[self.title, 'item_status'] = 'waiting'
        self.change_node_color_signal.change_node_color_signal.emit(self.title)
        self.win.waiting_queue.put((self.title, 'single'))
        JDRUtil.write_log(self.win, f'[Info]: JDRItem.run_single_item(): {self.title} is waiting to run.', 1)
    except Exception as e:
      JDRUtil.write_log(self.win, f'[Error]: JDRItem.run_single_item(): item: {self.title}\nerror message: {str(e)}', 2)

  def run_dependency_item(self):
    try:
      if self.win.item_cfg[self.title, 'item_status'] not in ['waiting', 'running']:
        JDRUtil.set_run_on_time(self.win.setup_widget3_execute_runontime_check.isChecked())
        self.win.run_on_time = JDRUtil.RUN_ON_TIME
        self.win.keep_running = True
        self.win.exec_cfg[self.title, 'status'] = 'waiting'
        self.win.exec_cfg[self.title, 'proc_dt'] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' # to compare with ctrl.act_sdt
        self.win.exec_cfg[self.title, 'type'] = 'dependency'
        self.win.information[f'num_{self.win.item_cfg[self.title, "item_status"]}_items'] -= 1
        self.win.information['num_waiting_items'] += 1
        self.win.item_cfg[self.title, 'org_status'] = self.win.item_cfg[self.title, 'item_status']  # backup the last status
        self.win.item_cfg[self.title, 'item_status'] = 'waiting'
        self.change_node_color_signal.change_node_color_signal.emit(self.title)
        self.win.waiting_queue.put((self.title, 'dependency'))
        JDRUtil.write_log(self.win, f'[Info]: JDRItem.run_dependency_item(): {self.title} is waiting to run.', 1)
    except Exception as e:
      JDRUtil.write_log(self.win, f'[Error]: JDRItem.run_dependency_item() item: {self.title}\nerror message: {str(e)}', 2)

  def init_node_color(self, color):
    if self.id.find('node') != -1:
      self.win.svg = re.sub('<title>' + self.title + '</title>\n<polygon fill="[#enoA-F0-9]*"', '<title>' + self.title + '</title>\n<polygon fill="' + color + '"', self.win.svg)
      self.renderer.load(bytes(self.win.svg, encoding='utf-8'))
      self.update()
      if self.id.find('node') != -1:
        btn = self.win.item_cfg[self.title, 'button']
        btn.setStyleSheet('background-color: ' + color)

  def show_report(self, item_name):
    if not self.win.item_report.__contains__(item_name):
      report = JDRItemReport(self.win, item_name)
      self.win.item_report[item_name] = report
      JDRUtil.write_log(self.win, f'[Info]: JDRItem.show_report(): open item report: {item_name}', 0)
    else:
      self.win.item_report[f'{item_name}'].activateWindow()
