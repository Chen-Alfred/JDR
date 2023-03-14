import re
import sys
import logging
import pandas as pd
import networkx as nx
import xml.etree.cElementTree as et
from graphviz import Digraph
from functools import partial
from queue import *
from PyQt6.QtGui import *
from PyQt6.QtSvg import QSvgRenderer
from jdr_ui import *
from jdr_item import *
from jdr_util import *
from jdr_thread import *
from jdr_main_report import *

class MainWindow(QMainWindow, MainWindowUI):
  def __init__(self):
    super().__init__()
    self.setup_ui()
    self.init_ui()
  
  def init_ui(self):
    JDRUtil.write_log(self, 'Initialize...', 0)
    self.sys_close = False
    self.run_on_time = JDRUtil.RUN_ON_TIME
    self.keep_running = True
    self.has_cycles = False
    self.no_freq = False
    self.err_freq = False
    self.no_cmd = False
    self.no_conn = False
    self.title_col_num = 0
    self.job_cfg = {}
    self.item_cfg = {}
    self.exec_cfg = {}
    self.information = {
      'num_document_jobs': 0,
      'num_available_jobs': 0,
      'num_unavailable_jobs': 0,
      'num_not_jobs': 0,
      'num_undefine_jobs': 0,
      'num_all_items': 0,
      'num_available_items': 0,
      'num_initial_items': 0,
      'num_waiting_items': 0,
      'num_running_items': 0,
      'num_success_items': 0,
      'num_failure_items': 0
    }
    self.svg = ''
    self.graph = nx.DiGraph()
    self.waiting_queue = Queue()
    self.continue_set = set()
    self.trans = QTranslator(self)
    self.filename = None
    self.main_report = dict()
    self.item_report = dict()
    # setup window: change language
    self.setup_widget1_lang_combo.currentIndexChanged.connect(self.change_language)
    # setup window: 'Browse' button
    self.setup_widget1_input_browse_button.clicked.connect(self.get_excel_file)
    # setup window: 'Generate' button
    self.setup_widget1_input_generate_button.clicked.connect(self.generate_svg)
    # setup window: modify color for every status
    self.setup_widget1_color_initial_rect.mousePressEvent = partial(self.modify_color, self.setup_widget1_color_initial_lineedit, self.setup_widget1_color_initial_rect)
    self.setup_widget1_color_waiting_rect.mousePressEvent = partial(self.modify_color, self.setup_widget1_color_waiting_lineedit, self.setup_widget1_color_waiting_rect)
    self.setup_widget1_color_running_rect.mousePressEvent = partial(self.modify_color, self.setup_widget1_color_running_lineedit, self.setup_widget1_color_running_rect)
    self.setup_widget1_color_success_rect.mousePressEvent = partial(self.modify_color, self.setup_widget1_color_success_lineedit, self.setup_widget1_color_success_rect)
    self.setup_widget1_color_failure_rect.mousePressEvent = partial(self.modify_color, self.setup_widget1_color_failure_lineedit, self.setup_widget1_color_failure_rect)
    self.setup_widget1_color_notjob_rect.mousePressEvent = partial(self.modify_color, self.setup_widget1_color_notjob_lineedit, self.setup_widget1_color_notjob_rect)
    self.setup_widget1_color_undefine_rect.mousePressEvent = partial(self.modify_color, self.setup_widget1_color_undefine_lineedit, self.setup_widget1_color_undefine_rect)
    # setup window: 'Default Color' button
    self.setup_widget1_color_default_button.clicked.connect(self.default_color)
    # setup window: 'Test Connection...' button
    self.setup_widget2_conn_test_button.clicked.connect(partial(JDRUtil.test_conn_postgresql, self, True))
    # setup window: 'Run All Items' button
    self.setup_widget3_execute_runalljob_button.clicked.connect(self.run_all_items)
    # setup window: 'Continue All Items' button
    self.setup_widget3_execute_contalljob_button.clicked.connect(self.continue_all_items)
    # setup window: 'Stop All Items' button
    self.setup_widget3_execute_stopdepjob_button.clicked.connect(self.stop_all_items)
    # setup window: 'Show report' button
    self.setup_widget3_other_showrep_button.clicked.connect(self.show_report)
    # setup window: 'Reload From DB' button
    self.setup_widget3_other_reloaddb_button.clicked.connect(self.reload_from_db)
    # setup window: Save SVG' button
    self.setup_widget3_other_savesvg_button.clicked.connect(self.save_svg)

    JDRUtil.write_log(self, f'DEFAULT_COLOR_INITIAL = {JDRUtil.DEFAULT_COLOR_INITIAL}', 0)
    JDRUtil.write_log(self, f'DEFAULT_COLOR_WAITING = {JDRUtil.DEFAULT_COLOR_WAITING}', 0)
    JDRUtil.write_log(self, f'DEFAULT_COLOR_RUNNING = {JDRUtil.DEFAULT_COLOR_RUNNING}', 0)
    JDRUtil.write_log(self, f'DEFAULT_COLOR_SUCCESS = {JDRUtil.DEFAULT_COLOR_SUCCESS}', 0)
    JDRUtil.write_log(self, f'DEFAULT_COLOR_FAILURE = {JDRUtil.DEFAULT_COLOR_FAILURE}', 0)
    JDRUtil.write_log(self, f'DEFAULT_COLOR_NOTJOB = {JDRUtil.DEFAULT_COLOR_NOTJOB}', 0)
    JDRUtil.write_log(self, f'DEFAULT_COLOR_UNDEFINE = {JDRUtil.DEFAULT_COLOR_UNDEFINE}', 0)
    JDRUtil.write_log(self, f'DEFAULT_RUN_ON_TIME = {JDRUtil.DEFAULT_RUN_ON_TIME}', 0)

  @pyqtSlot(int)
  def change_language(self, index):
    data = self.setup_widget1_lang_combo.itemData(index)
    JDRUtil.write_log(self, f'change_language(): change to {self.setup_widget1_lang_combo.currentText()}', 0)
    if data:
      self.trans.load(data)
      QApplication.instance().installTranslator(self.trans)
    else:
      QApplication.instance().removeTranslator(self.trans)
    self.retranslate_ui()

  def get_excel_file(self):
    self.filename, _ = QFileDialog.getOpenFileName(self, "Open File", ".", "Excel Files (*.xlsx *.xls)")
    if self.filename:
      JDRUtil.write_log(self, f'get_excel_file(): select file "{self.filename}"', 0)
      self.setup_widget1_input_file_lineedit.setText(self.filename)
      file = pd.ExcelFile(self.filename)
      self.setup_widget1_input_sheet_combobox.clear()
      self.setup_widget1_input_sheet_combobox.addItems(file.sheet_names)

  def init_var(self):
    JDRUtil.set_color_initial(self.setup_widget1_color_initial_lineedit.text())
    JDRUtil.set_color_waiting(self.setup_widget1_color_waiting_lineedit.text())
    JDRUtil.set_color_running(self.setup_widget1_color_running_lineedit.text())
    JDRUtil.set_color_success(self.setup_widget1_color_success_lineedit.text())
    JDRUtil.set_color_failure(self.setup_widget1_color_failure_lineedit.text())
    JDRUtil.set_color_notjob(self.setup_widget1_color_notjob_lineedit.text())
    JDRUtil.set_color_undefine(self.setup_widget1_color_undefine_lineedit.text())
    JDRUtil.set_conn_ip(self.setup_widget2_conn_ip_lineedit.text())
    JDRUtil.set_conn_user(self.setup_widget2_conn_user_lineedit.text())
    JDRUtil.set_conn_passwd(self.setup_widget2_conn_passwd_lineedit.text())
    JDRUtil.set_conn_port(self.setup_widget2_conn_port_lineedit.text())
    JDRUtil.set_conn_db(self.setup_widget2_conn_db_lineedit.text())
    JDRUtil.set_ctrl_tablename(self.setup_widget2_ctrl_tablename_lineedit.text())
    JDRUtil.set_ctrl_jobname(self.setup_widget2_ctrl_jobname_lineedit.text())
    JDRUtil.set_ctrl_plandt(self.setup_widget2_ctrl_plandt_lineedit.text())
    JDRUtil.set_ctrl_status(self.setup_widget2_ctrl_status_lineedit.text())
    JDRUtil.set_ctrl_actsdt(self.setup_widget2_ctrl_actsdt_lineedit.text())
    JDRUtil.set_ctrl_actedt(self.setup_widget2_ctrl_actedt_lineedit.text())
    JDRUtil.set_ctrl_datanum(self.setup_widget2_ctrl_datanum_lineedit.text())
    JDRUtil.set_run_on_time(self.setup_widget3_execute_runontime_check.isChecked())

  def generate_svg(self):
    if not self.filename:
      JDRUtil.write_log(self, f'[Error]: file is not ready.', 2)
      return
    self.init_var()
    self.scene.clear()
    self.job_cfg.clear()
    self.item_cfg.clear()
    self.exec_cfg.clear()
    self.scene.setSceneRect(0, 0, 0, 0)
    self.viewer.setSceneRect(0, 0, 0, 0)
    # clear job button
    while self.job_layout.count():
      item = self.job_layout.takeAt(0)
      item.widget().deleteLater()

    self.run_on_time = JDRUtil.RUN_ON_TIME
    self.keep_running = True
    self.has_cycles = False
    self.no_freq = False
    self.err_freq = False
    self.no_cmd = False
    self.no_conn = False
    self.title_col_num = 0
    self.setup_widget3_execute_runalljob_button.setEnabled(True)
    self.setup_widget3_execute_contalljob_button.setEnabled(True)
    self.setup_widget3_execute_stopdepjob_button.setEnabled(True)
    self.setup_widget3_other_showrep_button.setEnabled(True)
    self.setup_widget3_other_reloaddb_button.setEnabled(True)
    self.information = {
      'num_document_jobs': 0,
      'num_available_jobs': 0,
      'num_unavailable_jobs': 0,
      'num_not_jobs': 0,
      'num_undefine_jobs': 0,
      'num_all_items': 0,
      'num_available_items': 0,
      'num_initial_items': 0,
      'num_waiting_items': 0,
      'num_running_items': 0,
      'num_success_items': 0,
      'num_failure_items': 0
    }
    self.svg = ''
    self.graph.clear()
    self.waiting_queue = Queue()
    self.continue_set.clear()

    sheet_name = self.setup_widget1_input_sheet_combobox.currentText()
    df = pd.read_excel(self.filename, sheet_name)
    dot = Digraph(strict = True, comment = 'Job Dependency Runner', format = 'svg', node_attr = {'shape': 'record', 'fontname': 'DFKai-SB'})
    self.information['num_document_jobs'] = len(df.axes[0])
    job_start_dt = self.setup_widget1_input_start_dateedit.dateTime().toString('yyyyMMdd')
    job_end_dt = self.setup_widget1_input_end_dateedit.dateTime().toString('yyyyMMdd')
    JDRUtil.write_log(self, f'generate_svg(): select sheet "{sheet_name}"', 0)
    JDRUtil.write_log(self, f'row_num = {len(df.axes[0])}', 0)
    JDRUtil.write_log(self, f'job_start_dt = {job_start_dt}', 0)
    JDRUtil.write_log(self, f'job_end_dt = {job_end_dt}', 0)
    JDRUtil.write_log(self, f'Environment Variable:', 0)
    JDRUtil.write_log(self, f'COLOR_INITIAL = {JDRUtil.COLOR_INITIAL}', 0)
    JDRUtil.write_log(self, f'COLOR_WAITING = {JDRUtil.COLOR_WAITING}', 0)
    JDRUtil.write_log(self, f'COLOR_RUNNING = {JDRUtil.COLOR_RUNNING}', 0)
    JDRUtil.write_log(self, f'COLOR_SUCCESS = {JDRUtil.COLOR_SUCCESS}', 0)
    JDRUtil.write_log(self, f'COLOR_FAILURE = {JDRUtil.COLOR_FAILURE}', 0)
    JDRUtil.write_log(self, f'COLOR_NOTJOB = {JDRUtil.COLOR_NOTJOB}', 0)
    JDRUtil.write_log(self, f'COLOR_UNDEFINE = {JDRUtil.COLOR_UNDEFINE}', 0)
    JDRUtil.write_log(self, f'CONN_IP = {JDRUtil.CONN_IP}', 0)
    JDRUtil.write_log(self, f'CONN_PORT = {JDRUtil.CONN_PORT}', 0)
    JDRUtil.write_log(self, f'CONN_DB = {JDRUtil.CONN_DB}', 0)
    JDRUtil.write_log(self, f'CTRL_TABLENAME = {JDRUtil.CTRL_TABLENAME}', 0)
    JDRUtil.write_log(self, f'CTRL_COL_JOBNAME = {JDRUtil.CTRL_COL_JOBNAME}', 0)
    JDRUtil.write_log(self, f'CTRL_COL_PLANDT = {JDRUtil.CTRL_COL_PLANDT}', 0)
    JDRUtil.write_log(self, f'CTRL_COL_STATUS = {JDRUtil.CTRL_COL_STATUS}', 0)
    JDRUtil.write_log(self, f'CTRL_COL_ACTSDT = {JDRUtil.CTRL_COL_ACTSDT}', 0)
    JDRUtil.write_log(self, f'CTRL_COL_ACTEDT = {JDRUtil.CTRL_COL_ACTEDT}', 0)
    JDRUtil.write_log(self, f'CTRL_COL_DATANUM = {JDRUtil.CTRL_COL_DATANUM}', 0)
    JDRUtil.write_log(self, f'RUN_ON_TIME = {JDRUtil.RUN_ON_TIME}', 0)

    # decide the candidate column name (suport English / Chinese column name)
    job_no_col_set = set(['job_no', '編號'])
    job_type_col_set = set(['job_type', '類別'])
    job_name_col_set = set(['job_name', 'JOB名稱'])
    job_freq_col_set = set(['job_freq', '執行頻率'])
    job_src_col_set = set(['job_src', 'JOB來源'])
    job_not_col_set = set(['job_not', '非JOB註記'])
    job_cmd_col_set = set(['job_cmd', '執行指令'])

    # check job_no
    col_num = len(job_no_col_set.intersection(set(df.axes[1])))
    if col_num == 1:
      job_no_col = job_no_col_set.intersection(set(df.axes[1])).pop()
      self.title_col_num += 1
    elif col_num == 0:
      JDRUtil.write_log(self, f'[Error]: this document lack column: {job_no_col_set}', 2)
    else:
      JDRUtil.write_log(self, f'[Error]: this document has redundancy column: {job_no_col_set}', 2)

    # check job_type
    col_num = len(job_type_col_set.intersection(set(df.axes[1])))
    if col_num == 1:
      job_type_col = job_type_col_set.intersection(set(df.axes[1])).pop()
      self.title_col_num += 1
    elif col_num == 0:
      JDRUtil.write_log(self, f'[Error]: this document lack column: {job_type_col_set}', 2)
    else:
      JDRUtil.write_log(self, f'[Error]: this document has redundancy column: {job_type_col_set}', 2)

    # check job_name
    col_num = len(job_name_col_set.intersection(set(df.axes[1])))
    if col_num == 1:
      job_name_col = job_name_col_set.intersection(set(df.axes[1])).pop()
      self.title_col_num += 1
    elif col_num == 0:
      JDRUtil.write_log(self, f'[Error]: this document lack column: {job_name_col_set}', 2)
    else:
      JDRUtil.write_log(self, f'[Error]: this document has redundancy column: {job_name_col_set}', 2)

    # check job_freq
    col_num = len(job_freq_col_set.intersection(set(df.axes[1])))
    if col_num == 1:
      job_freq_col = job_freq_col_set.intersection(set(df.axes[1])).pop()
      self.title_col_num += 1
    elif col_num == 0:
      JDRUtil.write_log(self, f'[Error]: this document lack column: {job_freq_col_set}', 2)
    else:
      JDRUtil.write_log(self, f'[Error]: this document has redundancy column: {job_freq_col_set}', 2)

    # check job_src
    col_num = len(job_src_col_set.intersection(set(df.axes[1])))
    if col_num == 1:
      job_src_col = job_src_col_set.intersection(set(df.axes[1])).pop()
      self.title_col_num += 1
    elif col_num == 0:
      JDRUtil.write_log(self, f'[Error]: this document lack column: {job_src_col_set}', 2)
    else:
      JDRUtil.write_log(self, f'[Error]: this document has redundancy column: {job_src_col_set}', 2)

    # check job_not
    col_num = len(job_not_col_set.intersection(set(df.axes[1])))
    if col_num == 1:
      job_not_col = job_not_col_set.intersection(set(df.axes[1])).pop()
      self.title_col_num += 1
    elif col_num == 0:
      JDRUtil.write_log(self, f'[Error]: this document lack column: {job_not_col_set}', 2)
    else:
      JDRUtil.write_log(self, f'[Error]: this document has redundancy column: {job_not_col_set}', 2)

    # check job_cmd
    col_num = len(job_cmd_col_set.intersection(set(df.axes[1])))
    if col_num == 1:
      job_cmd_col = job_cmd_col_set.intersection(set(df.axes[1])).pop()
      self.title_col_num += 1
    elif col_num == 0:
      JDRUtil.write_log(self, f'[Error]: this document lack column: {job_cmd_col_set}', 2)
    else:
      JDRUtil.write_log(self, f'[Error]: this document has redundancy column: {job_cmd_col_set}', 2)

    if self.title_col_num != 7:
      JDRUtil.write_log(self, f'[Error]: this document has error title, please check again.', 2)
      return

    JDRUtil.write_log(self, f'job_no_col = {job_no_col}', 0)
    JDRUtil.write_log(self, f'job_type_col = {job_type_col}', 0)
    JDRUtil.write_log(self, f'job_name_col = {job_name_col}', 0)
    JDRUtil.write_log(self, f'job_freq_col = {job_freq_col}', 0)
    JDRUtil.write_log(self, f'job_src_col = {job_src_col}', 0)
    JDRUtil.write_log(self, f'job_not_col = {job_not_col}', 0)
    JDRUtil.write_log(self, f'job_cmd_col = {job_cmd_col}', 0)

    for i in range(self.information['num_document_jobs']):
      job_no = str(df.at[i, job_no_col])
      job_type = str(df.at[i, job_type_col])
      job_name = str(df.at[i, job_name_col])
      if str(df.at[i, job_not_col]).upper() == 'Y':
        job_not = 'Y'
        job_freq = []
        job_src = []
      else:
        job_not = 'N'
        if pd.isna(df.at[i, job_src_col]):
          job_src = []
        else:
          job_src = str(df.at[i, job_src_col])
          job_src = job_src.replace('[','').replace(']','').splitlines()  # remove square brackets
        if pd.isna(df.at[i, job_freq_col]):
          job_freq = []
          job_src = []
          job_type = 'no_freq'
          job_not = 'Y'
          self.no_freq = True
          self.setup_widget3_execute_runalljob_button.setEnabled(False)
          self.setup_widget3_execute_contalljob_button.setEnabled(False)
          self.setup_widget3_execute_stopdepjob_button.setEnabled(False)
          self.setup_widget3_other_showrep_button.setEnabled(False)
          self.setup_widget3_other_reloaddb_button.setEnabled(False)
          JDRUtil.write_log(self, f'[Error]: job_no:{job_no}, job_name:{job_name} has no frequency.', 2)
        else:
          job_freq = str(df.at[i, job_freq_col])
          job_freq = job_freq.splitlines()
          for freq in job_freq:
            if JDRUtil.get_plan_dt_list(self, freq, job_start_dt, job_end_dt) == False:
              job_src = []
              job_type = 'err_freq'
              job_not = 'Y'
              self.err_freq = True
              self.setup_widget3_execute_runalljob_button.setEnabled(False)
              self.setup_widget3_execute_contalljob_button.setEnabled(False)
              self.setup_widget3_execute_stopdepjob_button.setEnabled(False)
              self.setup_widget3_other_showrep_button.setEnabled(False)
              self.setup_widget3_other_reloaddb_button.setEnabled(False)
              JDRUtil.write_log(self, f'[Error]: job_no:{job_no}, job_name:{job_name} freq format error: "{freq}"', 2)
          if self.err_freq == True:
            job_freq = []
        if pd.isna(df.at[i, job_cmd_col]):
          job_freq = []
          job_src = []
          job_cmd = ''
          job_type = 'no_cmd'
          job_not = 'Y'
          self.no_cmd = True
          self.setup_widget3_execute_runalljob_button.setEnabled(False)
          self.setup_widget3_execute_contalljob_button.setEnabled(False)
          self.setup_widget3_execute_stopdepjob_button.setEnabled(False)
          self.setup_widget3_other_showrep_button.setEnabled(False)
          self.setup_widget3_other_reloaddb_button.setEnabled(False)
          JDRUtil.write_log(self, f'[Error]: job_no:{job_no}, job_name:{job_name} has no command.', 2)
        else:
          job_cmd = str(df.at[i, job_cmd_col])
      self.job_cfg[job_name, 'job_no'] = job_no
      self.job_cfg[job_name, 'job_type'] = job_type
      self.job_cfg[job_name, 'job_freq'] = job_freq
      self.job_cfg[job_name, 'job_src'] = job_src
      self.job_cfg[job_name, 'job_not'] = job_not
      self.job_cfg[job_name, 'job_cmd'] = job_cmd

      if self.job_cfg[job_name, 'job_not'] == 'Y':
        self.job_cfg[job_name, 'plan_dt'] = []
        self.job_cfg[job_name, 'job_key'] = [job_name]
        self.information['num_not_jobs'] += 1
        self.information['num_all_items'] += 1
      else:
        plan_dt_dup = []
        for freq in job_freq:
          plan_dt_dup.extend(JDRUtil.get_plan_dt_list(self, freq, job_start_dt, job_end_dt))
          plan_dt = sorted(list(set(plan_dt_dup))) # remove duplicate item
          self.job_cfg[job_name, 'plan_dt'] = plan_dt
          self.job_cfg[job_name, 'job_key'] = [job_name + '.' + i for i in plan_dt] # job_name + plan_dt
        if len(plan_dt_dup) == 0:
          self.information['num_unavailable_jobs'] += 1
        else:
          self.information['num_available_jobs'] += 1

    # find undefined jobs in job_src
    job_list = list(set([i[0] for i in self.job_cfg.keys()]))
    for job_src_list in [self.job_cfg[key] for key in self.job_cfg.keys() if key[1] == 'job_src']:
      for job_src_temp in job_src_list:
        if job_src_temp not in job_list:
          self.job_cfg[job_src_temp, 'job_no'] = '--'
          self.job_cfg[job_src_temp, 'job_type'] = 'undefine'
          self.job_cfg[job_src_temp, 'job_freq'] = []
          self.job_cfg[job_src_temp, 'job_src'] = []
          self.job_cfg[job_src_temp, 'job_not'] = 'Y'
          self.job_cfg[job_src_temp, 'job_cmd'] = ''
          self.job_cfg[job_src_temp, 'plan_dt'] = []
          self.job_cfg[job_src_temp, 'job_key'] = [job_src_temp]
          JDRUtil.write_log(self, f'[Warning]: "{job_src_temp}" job is undefined in "{job_src_col}" column.', 2)
    job_list = list(set([i[0] for i in self.job_cfg.keys()]))
    self.information['num_undefine_jobs'] = len([key[0] for key in self.job_cfg.keys() if key[1] == 'job_type' and self.job_cfg[key] == 'undefine'])
    self.information['num_all_items'] += self.information['num_undefine_jobs']

    # genetate svg (for job)
    for job_name in sorted(job_list):
      item_no_seq = 1
      # genetate svg (for item)
      for job_key in self.job_cfg[job_name, 'job_key']:
        self.item_cfg[job_key, 'item_name'] = job_name
        self.item_cfg[job_key, 'item_src'] = []
        # 1. undefined type
        if self.job_cfg[job_name, 'job_type'] == 'undefine':
          self.item_cfg[job_key, 'item_plan_dt'] = ''
          self.item_cfg[job_key, 'item_plan_dt_fmt'] = ''
          self.item_cfg[job_key, 'item_no'] = '====    '
          self.item_cfg[job_key, 'item_src'] = []
          self.item_cfg[job_key, 'item_type'] = 'undefine'
          self.item_cfg[job_key, 'item_not'] = 'Y'
          self.item_cfg[job_key, 'item_cmd'] = '--'
          self.item_cfg[job_key, 'item_status'] = 'undefine'
          self.item_cfg[job_key, 'item_rownum'] = 0
          self.item_cfg[job_key, 'item_graph'] = '{{' + self.item_cfg[job_key, 'item_no'] + '|type: ' + self.item_cfg[job_key, 'item_type'] + '|status: ' + self.item_cfg[job_key, 'item_status'] + '}|' + self.item_cfg[job_key, 'item_name'] + '|actual_start_datetime: --\lactual__end__datetime: --\lactual_duration: --\l|cmd: ' + self.item_cfg[job_key, 'item_cmd'] + '\l|data_num: --\l}'
        # 1.1. no_freq type
        elif self.job_cfg[job_name, 'job_type'] == 'no_freq':
          self.item_cfg[job_key, 'item_plan_dt'] = ''
          self.item_cfg[job_key, 'item_plan_dt_fmt'] = ''
          self.item_cfg[job_key, 'item_no'] = (self.job_cfg[job_name, 'job_no'] + '    ').rjust(8)
          self.item_cfg[job_key, 'item_src'] = []
          self.item_cfg[job_key, 'item_type'] = 'no_freq'
          self.item_cfg[job_key, 'item_not'] = 'Y'
          self.item_cfg[job_key, 'item_cmd'] = '--'
          self.item_cfg[job_key, 'item_status'] = 'no_freq'
          self.item_cfg[job_key, 'item_rownum'] = 0
          self.item_cfg[job_key, 'item_graph'] = '{{' + self.item_cfg[job_key, 'item_no'] + '|type: ' + self.item_cfg[job_key, 'item_type'] + '|status: ' + self.item_cfg[job_key, 'item_status'] + '}|' + self.item_cfg[job_key, 'item_name'] + '|actual_start_datetime: --\lactual__end__datetime: --\lactual_duration: --\l|cmd: ' + self.item_cfg[job_key, 'item_cmd'] + '\l|data_num: --\l}'
        # 1.2. err_freq type
        elif self.job_cfg[job_name, 'job_type'] == 'err_freq':
          self.item_cfg[job_key, 'item_plan_dt'] = ''
          self.item_cfg[job_key, 'item_plan_dt_fmt'] = ''
          self.item_cfg[job_key, 'item_no'] = (self.job_cfg[job_name, 'job_no'] + '    ').rjust(8)
          self.item_cfg[job_key, 'item_src'] = []
          self.item_cfg[job_key, 'item_type'] = 'err_freq'
          self.item_cfg[job_key, 'item_not'] = 'Y'
          self.item_cfg[job_key, 'item_cmd'] = '--'
          self.item_cfg[job_key, 'item_status'] = 'err_freq'
          self.item_cfg[job_key, 'item_rownum'] = 0
          self.item_cfg[job_key, 'item_graph'] = '{{' + self.item_cfg[job_key, 'item_no'] + '|type: ' + self.item_cfg[job_key, 'item_type'] + '|status: ' + self.item_cfg[job_key, 'item_status'] + '}|' + self.item_cfg[job_key, 'item_name'] + '|actual_start_datetime: --\lactual__end__datetime: --\lactual_duration: --\l|cmd: ' + self.item_cfg[job_key, 'item_cmd'] + '\l|data_num: --\l}'
        # 1.3. no_cmd type
        elif self.job_cfg[job_name, 'job_type'] == 'no_cmd':
          self.item_cfg[job_key, 'item_plan_dt'] = ''
          self.item_cfg[job_key, 'item_plan_dt_fmt'] = ''
          self.item_cfg[job_key, 'item_no'] = (self.job_cfg[job_name, 'job_no'] + '    ').rjust(8)
          self.item_cfg[job_key, 'item_src'] = []
          self.item_cfg[job_key, 'item_type'] = 'no_cmd'
          self.item_cfg[job_key, 'item_not'] = 'Y'
          self.item_cfg[job_key, 'item_cmd'] = '--'
          self.item_cfg[job_key, 'item_status'] = 'no_cmd'
          self.item_cfg[job_key, 'item_rownum'] = 0
          self.item_cfg[job_key, 'item_graph'] = '{{' + self.item_cfg[job_key, 'item_no'] + '|type: ' + self.item_cfg[job_key, 'item_type'] + '|status: ' + self.item_cfg[job_key, 'item_status'] + '}|' + self.item_cfg[job_key, 'item_name'] + '|actual_start_datetime: --\lactual__end__datetime: --\lactual_duration: --\l|cmd: ' + self.item_cfg[job_key, 'item_cmd'] + '\l|data_num: --\l}'
        # 2. notjob type
        elif self.job_cfg[job_name, 'job_not'] == 'Y':
          self.item_cfg[job_key, 'item_plan_dt'] = ''
          self.item_cfg[job_key, 'item_plan_dt_fmt'] = ''
          self.item_cfg[job_key, 'item_no'] = '====    '
          self.item_cfg[job_key, 'item_src'] = []
          self.item_cfg[job_key, 'item_type'] = self.job_cfg[job_name, 'job_type']
          self.item_cfg[job_key, 'item_not'] = 'Y'
          self.item_cfg[job_key, 'item_cmd'] = '--'
          self.item_cfg[job_key, 'item_status'] = 'notjob'
          self.item_cfg[job_key, 'item_rownum'] = 0
          self.item_cfg[job_key, 'item_graph'] = '{{' + self.item_cfg[job_key, 'item_no'] + '|type: ' + self.item_cfg[job_key, 'item_type'] + '|status: ' + self.item_cfg[job_key, 'item_status'] + '}|' + self.item_cfg[job_key, 'item_name'] + '|actual_start_datetime: --\lactual__end__datetime: --\lactual_duration: --\l|cmd: ' + self.item_cfg[job_key, 'item_cmd'] + '\l|data_num: --\l}'
        # 3. other type
        else:
          self.item_cfg[job_key, 'item_plan_dt'] = job_key.split('.')[1]
          dt_temp = self.item_cfg[job_key, 'item_plan_dt']
          self.item_cfg[job_key, 'item_plan_dt_fmt'] = f'{dt_temp[0:4]}-{dt_temp[4:6]}-{dt_temp[6:8]} {dt_temp[9:11]}:{dt_temp[11:13]}:{dt_temp[13:15]}'
          # 3.1. one job for multi job_key
          if len(self.job_cfg[job_name, 'job_key']) > 1:
            self.item_cfg[job_key, 'item_no'] = (self.job_cfg[job_name, 'job_no'] + f'-{str(item_no_seq).rjust(3, "0")}').rjust(8)
            # 3.1.1. one job for multi job_key -- the first item
            if item_no_seq == 1:
              self.item_cfg[job_key, 'item_src'] = []
            # 3.1.2. one job for multi job_key -- the 2nd ~ Nth item
            else:
              self.item_cfg[job_key, 'item_src'].append(last_job_key)
              with dot.subgraph(name = f'cluster_{job_name}') as c:
                c.attr(style='filled', color='#A0A0A0')
                c.edge(last_job_key, job_key)
                c.attr(label = job_name)
                self.graph.add_edges_from([(last_job_key, job_key)])
            last_job_key = job_key
          # 3.2. one job for only one job_key
          else:
            self.item_cfg[job_key, 'item_no'] = (self.job_cfg[job_name, 'job_no'] + '    ').rjust(8)

          self.item_cfg[job_key, 'item_type'] = self.job_cfg[job_name, 'job_type']
          self.item_cfg[job_key, 'item_not'] = self.job_cfg[job_name, 'job_not']
          self.item_cfg[job_key, 'item_cmd'] = self.job_cfg[job_name, 'job_cmd'].replace('${PLANDT}', self.item_cfg[job_key, 'item_plan_dt'])
          self.item_cfg[job_key, 'item_status'] = 'initial'
          self.item_cfg[job_key, 'item_rownum'] = 0
          self.item_cfg[job_key, 'item_graph'] = '{{' + self.item_cfg[job_key, 'item_no'] + '|type: ' + self.item_cfg[job_key, 'item_type'] + '|status: ' + self.item_cfg[job_key, 'item_status'] + '}|' + self.item_cfg[job_key, 'item_name'] + '\\n' + self.item_cfg[job_key, 'item_plan_dt_fmt'] + '|actual_start_datetime: --\lactual__end__datetime: --\lactual_duration: --\l|cmd: ' + self.item_cfg[job_key, 'item_cmd'] + '\l|data_num: --\l}'
          item_no_seq += 1

          self.exec_cfg[job_key, 'status'] = 'initial'
          self.exec_cfg[job_key, 'act_sdt'] = '--'
          self.exec_cfg[job_key, 'act_edt'] = '--'
          self.exec_cfg[job_key, 'dur'] = '--'
          self.exec_cfg[job_key, 'data_num'] = '--'
          self.exec_cfg[job_key, 'proc_dt'] = '--'
          self.exec_cfg[job_key, 'type'] = '--'

        # 4. travel all job_src of all jobs
        for job_src_item in self.job_cfg[job_name, 'job_src']:
          if self.job_cfg[job_src_item, 'job_type'] == 'undefine' or self.job_cfg[job_src_item, 'job_not'] == 'Y':
            item_src = f'{job_src_item}'
            self.item_cfg[job_key, 'item_src'].append(item_src)
            dot.edge(item_src, job_key)
            self.graph.add_edges_from([(item_src, job_key)])
          else:
            closest_src_plan_dt = self.get_closest_src_plan_dt(job_key, job_src_item)
            if closest_src_plan_dt:
              item_src = f'{job_src_item}.{closest_src_plan_dt}'
              self.item_cfg[job_key, 'item_src'].append(item_src)
              dot.edge(item_src, job_key)
              self.graph.add_edges_from([(item_src, job_key)])

        # 5. generate graphviz node
        dot.node(job_key, self.item_cfg[job_key, 'item_graph'])

    # generate button of left side
    item_no_dict = {k: v for k, v in self.item_cfg.items() if k[1] == 'item_no'}
    item_list = [i[0][0] for i in sorted(item_no_dict.items(), key=lambda item: item[1])]
    for job_key in item_list:
      if self.item_cfg[job_key, 'item_status'] in ['undefine', 'notjob']:
        button_text = job_key
      else:
        item_plan_dt_fmt = self.item_cfg[job_key, 'item_plan_dt_fmt']
        button_text = f'{self.item_cfg[job_key, "item_name"]} ({item_plan_dt_fmt})'
      self.bt = QPushButton(button_text)
      self.job_layout.addRow(str(self.item_cfg[job_key, 'item_no']), self.bt)
      self.bt.clicked.connect(partial(self.move_graphic_pos, job_key))
      self.item_cfg[job_key, 'button'] = self.bt
    self.svg = dot.pipe(encoding = 'utf-8')

    renderer = QSvgRenderer()
    renderer.load(bytes(self.svg, encoding='utf-8'))
    root = et.fromstring(self.svg)
    for g in root.findall('.//{*}g'):
      id = g.get('id')
      title = g.find('.//{*}title').text
      if id != 'graph0':
        self.item = JDRItem(self, renderer, id, title)
        self.item.change_node_color_signal.change_node_color_signal.connect(self.change_node_color)
        self.scene.addItem(self.item)
        self.item_cfg[title, 'x'] = self.item.pos().x()
        self.item_cfg[title, 'y'] = self.item.pos().y()
        self.item_cfg[title, 'org_status'] = 'initial'
        self.item_cfg[title, 'id'] = id
        self.item_cfg[title, 'item'] = self.item

    screen_size = app.primaryScreen().size()
    max_screen_width = max([self.scene.width(), screen_size.width()])
    max_screen_height = max([self.scene.height(), screen_size.height()])
    self.scene.setSceneRect(0, -self.scene.height(), self.scene.width(), self.scene.height())
    self.viewer.setSceneRect(-50, -self.scene.height()-50, max_screen_width * 2, max_screen_height * 2)
    self.viewer.horizontalScrollBar().setSliderPosition(-50)
    self.viewer.verticalScrollBar().setSliderPosition(-int(self.scene.height())-50)
    self.viewer.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    # update information
    self.information['num_available_items'] = len(list(set([key[0] for key in self.item_cfg.keys() if key[1] == 'item_not' and self.item_cfg[key] != 'Y'])))
    self.information['num_all_items'] = self.information['num_available_items'] + self.information['num_not_jobs'] + self.information['num_undefine_jobs']
    self.information['num_initial_items'] = self.information['num_available_items']
    self.setup_widget4_info_jobs_document2_label.setText(str(self.information['num_document_jobs']))
    self.setup_widget4_info_jobs_available2_label.setText(str(self.information['num_available_jobs']))
    self.setup_widget4_info_jobs_unavailable2_label.setText(str(self.information['num_unavailable_jobs']))
    self.setup_widget4_info_jobs_not2_label.setText(str(self.information['num_not_jobs']))
    self.setup_widget4_info_jobs_undefine2_label.setText(str(self.information['num_undefine_jobs']))
    self.setup_widget4_info_items_all2_label.setText(str(self.information['num_all_items']))
    self.setup_widget4_info_items_available2_label.setText(str(self.information['num_available_items']))
    self.setup_widget4_info_items_initial2_label.setText(str(self.information['num_initial_items']))
    self.setup_widget4_info_items_waiting2_label.setText(str(self.information['num_waiting_items']))
    self.setup_widget4_info_items_running2_label.setText(str(self.information['num_running_items']))
    self.setup_widget4_info_items_success2_label.setText(str(self.information['num_success_items']))
    self.setup_widget4_info_items_failure2_label.setText(str(self.information['num_failure_items']))

    # update nodes color according to DB status
    if JDRUtil.test_conn_postgresql(self, False) == True:
      item_list = list(set([key[0] for key in self.item_cfg.keys() if key[1] == 'item_not' and self.item_cfg[key] != 'Y']))
      JDRUtil.get_exec_cfg_by_key(self, item_list)
      ctrl_list = list(set(key[0] for key in self.exec_cfg))
      for item in item_list:
        if item in ctrl_list:
          status = self.exec_cfg[item, 'status']
          self.item_cfg[item, 'item_status'] = status  # update item status
          self.information['num_initial_items'] -= 1
          self.information[f'num_{status}_items'] += 1
          self.change_node_color(item)
    else:
      self.no_conn = True
      self.setup_widget3_execute_runalljob_button.setEnabled(False)
      self.setup_widget3_execute_contalljob_button.setEnabled(False)
      self.setup_widget3_execute_stopdepjob_button.setEnabled(False)
      self.setup_widget3_other_showrep_button.setEnabled(False)
      self.setup_widget3_other_reloaddb_button.setEnabled(False)

    # update edges color according to execution order
    item_list = list(set([key[0] for key in self.item_cfg.keys()]))
    for item_name in item_list:
      item = self.item_cfg[item_name, 'item']
      if item.id.find('edge') != -1:
        src_item = item_name.split('->')[0]
        dst_item = item_name.split('->')[1]
        if self.item_cfg[src_item, 'item_not'] != 'Y' and self.item_cfg[dst_item, 'item_not'] != 'Y':
          if self.exec_cfg[src_item, 'status'] == 'success' and self.exec_cfg[dst_item, 'status'] == 'success':
            src_act_edt = QDateTime.fromString(self.exec_cfg[src_item, 'act_edt'], 'yyyy-MM-dd hh:mm:ss')
            dst_act_sdt = QDateTime.fromString(self.exec_cfg[dst_item, 'act_sdt'], 'yyyy-MM-dd hh:mm:ss')
            if src_act_edt > dst_act_sdt:
              self.change_edge_color(src_item, dst_item, 'red')

    # check cycles in graph
    cycles = nx.recursive_simple_cycles(self.graph)
    cycles_len = len(cycles)
    if cycles_len != 0:
      self.has_cycles = True
      self.setup_widget3_execute_runalljob_button.setEnabled(False)
      self.setup_widget3_execute_contalljob_button.setEnabled(False)
      self.setup_widget3_execute_stopdepjob_button.setEnabled(False)
      self.setup_widget3_other_showrep_button.setEnabled(False)
      self.setup_widget3_other_reloaddb_button.setEnabled(False)
      JDRUtil.write_log(self, f'[Error]: The graph has cycles:', 2)
    for i in range(cycles_len):
      cycle_len = len(cycles[i])
      for j in range(cycle_len):
        if j == 0:
          cycle_str = f'[{cycles[i][0]}]'
        else:
          cycle_str += f' -> [{cycles[i][j]}]'
      cycle_str += f' -> [{cycles[i][0]}]'
      JDRUtil.write_log(self, f'--> cycle {i+1}: {cycle_str}', 2)

  def get_closest_src_plan_dt(self, job_key, job_src_item):
    result_plan_dt_str = None
    job_plan_dt_str = job_key.split('.')[1]
    job_plan_dt_dt = QDateTime.fromString(job_plan_dt_str, 'yyyyMMdd hhmmss')
    src_plan_dt_list = self.job_cfg[job_src_item, 'plan_dt']
    for src_plan_dt_str in src_plan_dt_list:
      src_plan_dt_dt = QDateTime.fromString(src_plan_dt_str, 'yyyyMMdd hhmmss') 
      if job_plan_dt_dt >= src_plan_dt_dt:
        result_plan_dt_str = src_plan_dt_dt.toString('yyyyMMdd hhmmss')
    return result_plan_dt_str
  
  def modify_color(self, obj_ed, obj_rect, event):
    dialog = QColorDialog(self)
    color = dialog.getColor(QColor(obj_ed.text()))
    if color.isValid():
      obj_ed.setText(color.name().upper())
      obj_rect.setStyleSheet(f'background-color: {color.name().upper()}')

  def default_color(self):
    self.setup_widget1_color_initial_lineedit.setText(JDRUtil.DEFAULT_COLOR_INITIAL)
    self.setup_widget1_color_waiting_lineedit.setText(JDRUtil.DEFAULT_COLOR_WAITING)
    self.setup_widget1_color_running_lineedit.setText(JDRUtil.DEFAULT_COLOR_RUNNING)
    self.setup_widget1_color_success_lineedit.setText(JDRUtil.DEFAULT_COLOR_SUCCESS)
    self.setup_widget1_color_failure_lineedit.setText(JDRUtil.DEFAULT_COLOR_FAILURE)
    self.setup_widget1_color_notjob_lineedit.setText(JDRUtil.DEFAULT_COLOR_NOTJOB)
    self.setup_widget1_color_undefine_lineedit.setText(JDRUtil.DEFAULT_COLOR_UNDEFINE)
    self.setup_widget1_color_initial_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_INITIAL}')
    self.setup_widget1_color_waiting_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_WAITING}')
    self.setup_widget1_color_running_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_RUNNING}')
    self.setup_widget1_color_success_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_SUCCESS}')
    self.setup_widget1_color_failure_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_FAILURE}')
    self.setup_widget1_color_notjob_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_NOTJOB}')
    self.setup_widget1_color_undefine_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_UNDEFINE}')

  def change_node_color(self, item_name):
    item = self.item_cfg[item_name, 'item']
    status = self.exec_cfg[item_name, 'status']
    act_sdt = ' ' + self.exec_cfg[item_name, 'act_sdt']  # add prefix space to prevent parsing error (only integer)
    act_edt = ' ' + self.exec_cfg[item_name, 'act_edt']
    dur = ' ' + self.exec_cfg[item_name, 'dur']
    data_num = ' ' + self.exec_cfg[item_name, 'data_num']
    if status == 'initial':
      color = JDRUtil.COLOR_INITIAL
    elif status == 'notjob':
      color = JDRUtil.COLOR_NOTJOB
    elif status == 'undefine':
      color = JDRUtil.COLOR_UNDEFINE
    elif status == 'waiting':
      color = JDRUtil.COLOR_WAITING
    elif status == 'running':
      color = JDRUtil.COLOR_RUNNING
    elif status == 'success':
      color = JDRUtil.COLOR_SUCCESS
    elif status == 'failure':
      color = JDRUtil.COLOR_FAILURE

    if item.id.find('node') != -1:
      # change node color and content
      if status in ['waiting', 'running']:
        (self.svg, num) = re.subn('(<title>' + item_name + '</title>\n<polygon fill=")([#enoA-F0-9]*)(")(.{0,2000})(status: )([a-z_]*)(</text>)', '\\1' + color + '\\3\\4\\5' + status + '\\7', self.svg, 1, flags = re.DOTALL)
      else:
        (self.svg, num) = re.subn('(<title>' + item_name + '</title>\n<polygon fill=")([#enoA-F0-9]*)(")(.{0,2000})(status: )([a-z_]*)(</text>)(.{0,1000})(actual_start_datetime: )(.{0,30})(</text>)(.{0,150})(actual__end__datetime: )(.{0,30})(</text>)(.{0,150})(actual_duration: )(.{0,20})(</text>)(.{0,500})(data_num: )(.{0,20})(</text>)', '\\1' + color + '\\3\\4\\5' + status + '\\7\\8\\9' + act_sdt + '\\11\\12\\13' + act_edt + '\\15\\16\\17' + dur + '\\19\\20\\21' + data_num + '\\23', self.svg, 1, flags = re.DOTALL)
      if num != 1:
        JDRUtil.write_log(self, f'[Warning]: change_node_color(): {item_name} change to {status} (num = {num})', 2)
      item.renderer.load(bytes(self.svg, encoding='utf-8'))
      item.update()

      # change button color
      btn = self.item_cfg[item_name, 'button']
      btn.setStyleSheet('background-color: ' + color)
      # change information content
      self.setup_widget4_info_items_initial2_label.setText(str(self.information['num_initial_items']))
      self.setup_widget4_info_items_waiting2_label.setText(str(self.information['num_waiting_items']))
      self.setup_widget4_info_items_running2_label.setText(str(self.information['num_running_items']))
      self.setup_widget4_info_items_success2_label.setText(str(self.information['num_success_items']))
      self.setup_widget4_info_items_failure2_label.setText(str(self.information['num_failure_items']))

      # change edge color
      if status == 'success':
        out_num = len(self.graph.out_edges(item_name))
        for n in range(out_num):
          out_item = list(self.graph.out_edges(item_name))[n][1]
          if self.exec_cfg[out_item, 'status'] == 'success':
            src_act_edt = QDateTime.fromString(self.exec_cfg[item_name, 'act_edt'], 'yyyy-MM-dd hh:mm:ss')
            dst_act_sdt = QDateTime.fromString(self.exec_cfg[out_item, 'act_sdt'], 'yyyy-MM-dd hh:mm:ss')
            if src_act_edt > dst_act_sdt:
              self.change_edge_color(item_name, out_item, 'red')
            else:
              self.change_edge_color(item_name, out_item, 'black')
        in_num = len(self.graph.in_edges(item_name))
        for n in range(in_num):
          in_item = list(self.graph.in_edges(item_name))[n][0]
          if self.item_cfg[in_item, 'item_not'] != 'Y':
            if self.exec_cfg[in_item, 'status'] == 'success':
              src_act_edt = QDateTime.fromString(self.exec_cfg[in_item, 'act_edt'], 'yyyy-MM-dd hh:mm:ss')
              dst_act_sdt = QDateTime.fromString(self.exec_cfg[item_name, 'act_sdt'], 'yyyy-MM-dd hh:mm:ss')
              if src_act_edt > dst_act_sdt:
                self.change_edge_color(in_item, item_name, 'red')
              else:
                self.change_edge_color(in_item, item_name, 'black')

  def change_edge_color(self, src_item, dst_item, color):
    item_name = f'{src_item}->{dst_item}'
    item_name2 = f'{src_item}&#45;&gt;{dst_item}'
    item = self.item_cfg[item_name, 'item']
    if item.id.find('edge') != -1:
      (self.svg, num) = re.subn('(<title>' + item_name2 + '</title>\n<path fill="none" stroke=")([a-z]*)(")(.{0,1000})(\n<polygon fill=")([a-z]*)(" stroke=")([a-z]*)(")', '\\1' + color + '\\3\\4\\5' + color + '\\7' + color + '\\9', self.svg, 1)
      if num != 1:
        JDRUtil.write_log(self, f'[Warning]: change_edge_color(): {item_name} change to {color} (num = {num})', 2)
      item.renderer.load(bytes(self.svg, encoding='utf-8'))
      item.update()
    # change button color
    btn = self.item_cfg[dst_item, 'button']
    btn.setStyleSheet(f'color: {color}; background-color: {JDRUtil.COLOR_SUCCESS}' )

  def run_all_items(self):
    for status in [self.item_cfg[key] for key in self.item_cfg.keys() if key[1] == 'item_status']:
      if status in ['waiting', 'running']:
        JDRUtil.write_log(self, f'[Error]: run_all_items(): You can\'t use \'run_all_items\' function if any item\'s status is waiting or running.', 2)
        return
    self.init_var()
    self.run_on_time = JDRUtil.RUN_ON_TIME
    self.keep_running = True
    item_list = list(set([key[0] for key in self.item_cfg.keys() if key[1] == 'item_not' and self.item_cfg[key] != 'Y']))
    for item_name in item_list:
      item = self.item_cfg[item_name, 'item']
      if item.id.find('node') != -1:
        non_available_num = 0
        in_num = len(self.graph.in_edges(item_name))
        for n in range(in_num):
          in_item = list(self.graph.in_edges(item_name))[n][0]
          if self.item_cfg[in_item, 'item_status'] in ['undefine', 'notjob']:
            non_available_num += 1
        if in_num - non_available_num == 0:
          self.exec_cfg[item_name, 'status'] = 'waiting'
          self.exec_cfg[item_name, 'proc_dt'] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' # to compare with ctrl.act_sdt
          self.exec_cfg[item_name, 'type'] = 'dependency'
          self.information[f'num_{self.item_cfg[item_name, "item_status"]}_items'] -= 1
          self.information['num_waiting_items'] += 1
          self.item_cfg[item_name, 'org_status'] = self.item_cfg[item_name, 'item_status']  # backup the last status
          self.item_cfg[item_name, 'item_status'] = 'waiting'
          self.change_node_color(item_name)
          self.waiting_queue.put((item_name, 'dependency'))
          JDRUtil.write_log(self, f'[Info]: run_all_items(): {item_name} is waiting to run.  (in_num = {in_num}, non_available_num = {non_available_num})', 1)

  def continue_all_items(self):
    for status in [self.item_cfg[key] for key in self.item_cfg.keys() if key[1] == 'item_status']:
      if status in ['waiting', 'running']:
        JDRUtil.write_log(self, f'[Error]: continue_all_items(): You can\'t use \'continue_all_items\' function if any item\'s status is waiting or running.', 2)
        return
    self.init_var()
    self.run_on_time = JDRUtil.RUN_ON_TIME
    self.keep_running = True
    self.continue_set.clear()
    item_list = list(set([key[0] for key in self.item_cfg.keys() if key[1] == 'item_not' and self.item_cfg[key] != 'Y']))
    for item_name in item_list:
      flag = 1
      in_num = len(self.graph.in_edges(item_name))
      for n in range(in_num):
        in_item = list(self.graph.in_edges(item_name))[n][0]
        if self.check_ancestor_effective(in_item) == False:
          flag = 0
      if flag == 1:
        if self.exec_cfg[item_name, 'status'] in ['initial', 'failure']:
          self.continue_set.add(item_name)
        if self.exec_cfg[item_name, 'status'] == 'success' and self.check_ancestor_effective(item_name) == False:
          self.continue_set.add(item_name)

    for item_name in self.continue_set:
      self.exec_cfg[item_name, 'status'] = 'waiting'
      self.exec_cfg[item_name, 'proc_dt'] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' # to compare with ctrl.act_sdt
      self.exec_cfg[item_name, 'type'] = 'dependency'
      self.information[f'num_{self.item_cfg[item_name, "item_status"]}_items'] -= 1
      self.information['num_waiting_items'] += 1
      self.item_cfg[item_name, 'org_status'] = self.item_cfg[item_name, 'item_status']  # backup the last status
      self.item_cfg[item_name, 'item_status'] = 'waiting'
      self.change_node_color(item_name)
      self.waiting_queue.put((item_name, 'dependency'))
      JDRUtil.write_log(self, f'[Info]: continue_all_items(): {item_name} is waiting to run.', 1)

  def check_ancestor_effective(self, item_name):
    if self.item_cfg[item_name, 'item_status'] in ['undefine', 'notjob']:
      return True
    if self.exec_cfg[item_name, 'status'] in ['initial', 'waiting', 'running', 'failure']:
      return False
    if self.exec_cfg[item_name, 'status'] == 'success':
      result = True
      in_num = len(self.graph.in_edges(item_name))
      for n in range(in_num):
        in_item = list(self.graph.in_edges(item_name))[n][0]
        if self.item_cfg[in_item, 'item_status'] in ['undefine', 'notjob']:
          continue
        src_act_edt = QDateTime.fromString(self.exec_cfg[in_item, 'act_edt'], 'yyyy-MM-dd hh:mm:ss')
        dst_act_sdt = QDateTime.fromString(self.exec_cfg[item_name, 'act_sdt'], 'yyyy-MM-dd hh:mm:ss')
        if src_act_edt > dst_act_sdt:
          result = False
          break
        else:
          result = self.check_ancestor_effective(in_item)
          if result == False:
            break
      return result

  def stop_all_items(self):
    self.keep_running = False
    try:
      while not self.waiting_queue.empty():
        event = self.waiting_queue.get(False)
        item = event[0]
        org_status = self.item_cfg[item, 'org_status']
        self.exec_cfg[item, 'status'] = org_status
        self.item_cfg[item, 'item_status'] = org_status
        self.information['num_waiting_items'] -= 1
        self.information[f'num_{org_status}_items'] += 1
        self.change_node_color(item)
        JDRUtil.write_log(self, f'[Info]: stop_all_items(): remove item from waiting_queue: {item}', 1)
    except Empty:
        JDRUtil.write_log(self, f'[Warning]: stop_all_items() warning: queue empty.', 2)

  def show_report(self):
    if self.job_cfg:
      if not self.main_report.__contains__('main'):
        self.main_report['main'] = JDRMainReport(self)
        JDRUtil.write_log(self, f'[Info]: show_report(): open main report', 0)
      else:
        self.main_report['main'].activateWindow()

  def reload_from_db(self):
    # update nodes color according to DB status
    self.init_var()
    if JDRUtil.test_conn_postgresql(self, False) == True:
      item_list = list(set([key[0] for key in self.item_cfg.keys() if key[1] == 'item_not' and self.item_cfg[key] != 'Y']))
      JDRUtil.get_exec_cfg_by_key(self, item_list)
      ctrl_list = list(set(key[0] for key in self.exec_cfg))
      for item in item_list:
        if item in ctrl_list:
          if self.item_cfg[item, 'item_status'] != self.exec_cfg[item, 'status']:
            self.information[f'num_{self.item_cfg[item, "item_status"]}_items'] -= 1
            self.information[f'num_{self.exec_cfg[item, "status"]}_items'] += 1
            self.item_cfg[item, 'org_status'] = self.item_cfg[item, 'item_status']  # backup the last status
            self.item_cfg[item, 'item_status'] = self.exec_cfg[item, 'status']
          self.change_node_color(item)
      JDRUtil.write_log(self, f'[Info]: reload_from_db(): update all items status and color according to DB.', 0)
    else:
      self.no_conn = True
      self.setup_widget3_execute_runalljob_button.setEnabled(False)
      self.setup_widget3_execute_contalljob_button.setEnabled(False)
      self.setup_widget3_execute_stopdepjob_button.setEnabled(False)
      self.setup_widget3_other_showrep_button.setEnabled(False)
      self.setup_widget3_other_reloaddb_button.setEnabled(False)

  def save_svg(self):
    name = QFileDialog.getSaveFileName(self, 'Save File', '.', '*.svg')[0]
    if name:
      file = open(name, 'w')
      text = str(self.svg)
      file.write(text)
      file.close()
      JDRUtil.write_log(self, f'[Info]: save_svg(): save file: "{name}"', 0)

  def move_graphic_pos(self, job_key):
    self.viewer.horizontalScrollBar().setSliderPosition(int(self.item_cfg[(job_key, 'x')]))
    self.viewer.verticalScrollBar().setSliderPosition(int(self.item_cfg[(job_key, 'y')]))
    JDRUtil.write_log(self, f'[Info]: move_graphic_pos(): move to {job_key}', 0)

  def closeEvent(self, event):
    self.sys_close = True


logging.basicConfig(format = '%(message)s', level = logging.INFO)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = MainWindow()
  window.setStyleSheet(JDRUtil.STYLE_CONFIG)

  # create job thread
  pool = QThreadPool.globalInstance()
  run = JDRThread(window)
  run.change_node_color_signal.change_node_color_signal.connect(window.change_node_color)
  run.write_log_signal.write_log_signal.connect(JDRUtil.write_log)
  pool.start(run)

  window.showMaximized()
  sys.exit(app.exec())

    