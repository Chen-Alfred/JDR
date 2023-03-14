import pytz
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import Slider
from matplotlib.figure import Figure
from datetime import datetime
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from jdr_util import *

class JDRMainReport(QWidget):
  def __init__(self, window):
    super().__init__()
    self.win = window
    job_start_dt_fmt = self.win.setup_widget1_input_start_dateedit.dateTime().toString('yyyy-MM-dd')
    job_end_dt_fmt = self.win.setup_widget1_input_end_dateedit.dateTime().toString('yyyy-MM-dd')
    self.setup_ui()
    self.setWindowTitle(f'Main Report ({job_start_dt_fmt} ~ {job_end_dt_fmt}) [Current Time]')
    self.setWindowModality(Qt.WindowModality.WindowModal)
    self.setStyleSheet(JDRUtil.STYLE_CONFIG)
    self.setGeometry(0, 0, 1700, 1000)
    self.show()

  def setup_ui(self):
    self.report_layout = QVBoxLayout()
    self.report_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMaximumSize)
    chart = JDRMainReport_MainChart(self.win)
    toolbar = NavigationToolbar(chart, self)
    self.report_layout.addWidget(toolbar)
    self.report_layout.addWidget(chart)
    self.report_widget = QWidget()
    self.report_widget.setLayout(self.report_layout)
    self.report_scroll = QScrollArea()
    self.report_scroll.setWidget(self.report_widget)
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.report_scroll)
    self.setLayout(self.layout)

  def closeEvent(self, event):
    JDRUtil.write_log(self.win, f'[Info]: JDRMainReport.closeEvent(): close main report', 0)
    self.win.main_report.pop('main')


class JDRMainReport_MainChart(FigureCanvas):
  def __init__(self, window, parent=None):
    self.win = window
    fig = Figure()
    fig, ax = plt.subplots(4,3)
    fig.set_figwidth(15)
    fig.set_figheight(30)

    # 1. status pie char (document_jobs)
    job_status = ['available_jobs', 'unavailable_jobs', 'not_jobs']
    job_status_val = [self.win.information['num_available_jobs'], self.win.information['num_unavailable_jobs'], self.win.information['num_not_jobs']]
    wedges, texts, autotexts = ax[0][0].pie(job_status_val, labels=job_status, autopct='')
    ax[0][0].set_title(f'Document Jobs Status (Total: {self.win.information["num_document_jobs"]})')
    plt.setp(autotexts, size=8, weight="bold")
    for i, a in enumerate(autotexts):
      if job_status_val[i] == 0:
        a.remove()
      else:
        a.set_text('{:.2f} %\n({} items)'.format(job_status_val[i]/sum(job_status_val)*100, job_status_val[i]))
    for i, a in enumerate(texts):
      if job_status_val[i] == 0:
        a.remove()
    ax[0][0].legend(wedges, job_status, title='Status', loc='lower right')

    # 2. status pie char (all_items)
    all_item_status = ['not_jobs', 'undefine_jobs', 'available_items']
    all_item_status_val = [self.win.information['num_not_jobs'], self.win.information['num_undefine_jobs'], self.win.information['num_available_items']]
    wedges, texts, autotexts = ax[0][1].pie(all_item_status_val, labels=all_item_status, autopct='')
    ax[0][1].set_title(f'All Items Status (Total: {self.win.information["num_all_items"]})')
    plt.setp(autotexts, size=8, weight="bold")
    for i, a in enumerate(autotexts):
      if all_item_status_val[i] == 0:
        a.remove()
      else:
        a.set_text('{:.2f} %\n({} items)'.format(all_item_status_val[i]/sum(all_item_status_val)*100, all_item_status_val[i]))
    for i, a in enumerate(texts):
      if all_item_status_val[i] == 0:
        a.remove()
    ax[0][1].legend(wedges, all_item_status, title='Status', loc='lower right')

    # 3. status pie char (available_items)
    avail_item_status = ['initial', 'waiting', 'running', 'success', 'failure']
    avail_item_status_val = [self.win.information['num_initial_items'], self.win.information['num_waiting_items'], self.win.information['num_running_items'], self.win.information['num_success_items'], self.win.information['num_failure_items']]
    wedges, texts, autotexts = ax[0][2].pie(avail_item_status_val, labels=avail_item_status, autopct='')
    ax[0][2].set_title(f'Available Items Status (Total: {self.win.information["num_available_items"]})')
    plt.setp(autotexts, size=8, weight="bold")
    for i, a in enumerate(autotexts):
      if avail_item_status_val[i] == 0:
        a.remove()
      else:
        a.set_text('{:.2f} %\n({} items)'.format(avail_item_status_val[i]/sum(avail_item_status_val)*100, avail_item_status_val[i]))
    for i, a in enumerate(texts):
      if avail_item_status_val[i] == 0:
        a.remove()
    for i, a in enumerate(wedges):
      v = a.get_label()
      if v == 'initial':
        color = JDRUtil.COLOR_INITIAL
      elif v == 'notjob':
        color = JDRUtil.COLOR_NOTJOB
      elif v == 'undefine':
        color = JDRUtil.COLOR_UNDEFINE
      elif v == 'waiting':
        color = JDRUtil.COLOR_WAITING
      elif v == 'running':
        color = JDRUtil.COLOR_RUNNING
      elif v == 'success':
        color = JDRUtil.COLOR_SUCCESS
      elif v == 'failure':
        color = JDRUtil.COLOR_FAILURE
      a.set_color(color)
    ax[0][2].legend(wedges, avail_item_status, title='Status', loc='lower right')

    labels = list()
    plan_dt = list()
    act_sdt = list()
    dur = list()
    data_num = list()
    item_no_dict = {k: v for k, v in self.win.item_cfg.items() if k[1] == 'item_no'}
    item_list = [i[0][0] for i in sorted(item_no_dict.items(), key=lambda item: item[1])]
    for job_key in item_list:
      if self.win.item_cfg[job_key, 'item_status'] not in ['undefine', 'notjob']:
        item_plan_dt_fmt = self.win.item_cfg[job_key, 'item_plan_dt_fmt']
        labels.append(f'[{str(self.win.item_cfg[job_key, "item_no"])}] {self.win.item_cfg[job_key, "item_name"]} ({item_plan_dt_fmt})')
        plan_dt.append(datetime.strptime(item_plan_dt_fmt, '%Y-%m-%d %H:%M:%S').replace(tzinfo=None))

        val = self.win.exec_cfg[job_key, 'act_sdt']
        if val == '--':
          act_sdt.append(datetime.strptime(item_plan_dt_fmt, '%Y-%m-%d %H:%M:%S').replace(tzinfo=None))
        else:
          act_sdt.append(datetime.strptime(val, '%Y-%m-%d %H:%M:%S').replace(tzinfo=None))
        
        val = self.win.exec_cfg[job_key, 'dur']
        if val == '--':
          dur.append(0)
        else:
          dur.append(int(val))

        val = self.win.exec_cfg[job_key, 'data_num']
        if val == '--':
          data_num.append(0)
        else:
          data_num.append(int(val))

    # 4.Plan & Start Datetime Chart
    cur_ax = plt.subplot2grid((4,3), (1, 0), rowspan=1, colspan=3)
    cur_ax.yaxis_date()
    cur_ax.yaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    cur_ax.yaxis.set_minor_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    for i in range(len(labels)):
      cur_ax.plot(labels[i], act_sdt[i], 'ro', markersize = 4)
      cur_ax.plot(labels[i], plan_dt[i], 'bo', markersize = 4)
      cur_ax.plot((labels[i], labels[i]), (plan_dt[i], act_sdt[i]), c='#FF0000', fillstyle='bottom')
    cur_ax.set_title(f'Plan & Start Datetime Chart')
    cur_ax.set_ylabel('Execution Time')
    cur_ax.legend(labels=['act_sdt', 'plan_dt'], loc='lower right')
    plt.xticks(rotation=-90, ha='right')

    # 5.Duration Chart
    cur_ax = plt.subplot2grid((4,3), (2, 0), rowspan=1, colspan=3)
    cur_ax.bar(labels, dur, label = labels, width = 0.1)
    cur_ax.set_title(f'Duration Chart')
    cur_ax.set_ylabel('Duration (sec)')
    plt.xticks(rotation=-90, ha='right')

    # 6.Data Number Chart
    cur_ax = plt.subplot2grid((4,3), (3, 0), rowspan=1, colspan=3)
    cur_ax.bar(labels, data_num, label = labels, width = 0.1)
    cur_ax.set_title(f'Data Number Chart')
    cur_ax.set_ylabel('Data Number')
    plt.xticks(rotation=-90, ha='right')
    plt.subplots_adjust(top=1, bottom=0.5)

    plt.tight_layout()
    super(JDRMainReport_MainChart, self).__init__(fig)

