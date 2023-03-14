import networkx as nx
import xml.etree.cElementTree as et
import matplotlib
import matplotlib.dates
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from graphviz import Digraph
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from jdr_util import *

class JDRItemReport(QWidget):
  def __init__(self, window, item_name):
    super().__init__()
    self.setup_ui()
    self.win = window
    self.item_name = item_name
    self.job_name = item_name.split('.')[0]
    self.plan_dt = item_name.split('.')[1]
    self.plan_dt_fmt = f'{self.plan_dt[0:4]}-{self.plan_dt[4:6]}-{self.plan_dt[6:8]} {self.plan_dt[9:11]}:{self.plan_dt[11:13]}:{self.plan_dt[13:15]}'
    self.svg = ''
    self.setWindowTitle(f'{self.job_name} ({self.plan_dt_fmt})')
    self.setWindowModality(Qt.WindowModality.WindowModal)
    self.setStyleSheet(JDRUtil.STYLE_CONFIG)
    self.setGeometry(0, 0, 1000, 1000)
    self.show()
    self.create_related_items()

    chart1 = JDRItemReport_StatusPie(self.win, self.item_name, width=5, height=4, dpi=100)
    toolbar1 = NavigationToolbar(chart1, self)
    self.report_layout2.addWidget(chart1, 0, 0)
    self.report_layout2.addWidget(toolbar1, 1, 0)

    chart2 = JDRItemReport_StartDTChart(self.win, self.item_name, width=5, height=4, dpi=100)
    toolbar2 = NavigationToolbar(chart2, self)
    self.report_layout2.addWidget(chart2, 0, 1)
    self.report_layout2.addWidget(toolbar2, 1, 1)
    
    chart3 = JDRItemReport_DurationChart(self.win, self.item_name, width=5, height=4, dpi=100)
    toolbar3 = NavigationToolbar(chart3, self)
    self.report_layout2.addWidget(chart3, 2, 0)
    self.report_layout2.addWidget(toolbar3, 3, 0)

    chart4 = JDRItemReport_DataNumberChart(self.win, self.item_name, width=5, height=4, dpi=100)
    toolbar4 = NavigationToolbar(chart4, self)
    self.report_layout2.addWidget(chart4, 2, 1)
    self.report_layout2.addWidget(toolbar4, 3, 1)

  def setup_ui(self):
    self.layout = QVBoxLayout()
    self.report_widget = QTabWidget()
    self.report_widget1 = QWidget()
    self.report_widget2 = QWidget()
    self.report_widget.addTab(self.report_widget1, 'Related Items')   # translate: Related Items
    self.report_widget.addTab(self.report_widget2, 'Execution Info')  # translate: Execution Info
    self.report_layout1 = QVBoxLayout()
    self.report_layout2 = QGridLayout()
    self.report_layout2.setSizeConstraint(QGridLayout.SizeConstraint.SetFixedSize)
    self.report_widget1.setLayout(self.report_layout1)
    self.report_widget2.setLayout(self.report_layout2)
    self.layout.addWidget(self.report_widget)
    self.setLayout(self.layout)
    self.init_setup_report1()

  def init_setup_report1(self):
    self.viewer = QGraphicsView(self)
    self.scene = QGraphicsScene(self)
    self.scene.clear()
    self.viewer.setScene(self.scene)
    self.viewer.resetTransform()
    self.report_layout1.addWidget(self.viewer)
    self.report_relateditem_button = QPushButton('🖫 　Save SVG')
    self.report_relateditem_button.clicked.connect(self.save_related_items)
    self.report_layout1.addWidget(self.report_relateditem_button)

  def closeEvent(self, event):
    JDRUtil.write_log(self.win, f'[Info]: JDRItemReport.closeEvent(): close item report: {self.item_name}', 0)
    self.win.item_report.pop(self.item_name)

  def create_related_items(self):
    item_set = set()
    node_list = list()
    # find related nodes (self, ancestors, descendants)
    item_set.add(self.item_name)
    if len(self.win.graph.in_edges(self.item_name)) > 0:
      for item in nx.ancestors(self.win.graph, self.item_name):
        item_set.add(item)
    if len(self.win.graph.out_edges(self.item_name)) > 0:
      for item in nx.descendants(self.win.graph, self.item_name):
        item_set.add(item)
    dot = Digraph(strict = True, comment = f'item_flow: {self.job_name} ({self.plan_dt_fmt})', format = 'svg', node_attr = {'shape': 'record', 'fontname': 'DFKai-SB'})
    for item in item_set:
      dot.node(item, self.win.item_cfg[item, 'item_graph'])
    # find related edges
    item_list = list(set([key[0] for key in self.win.item_cfg.keys() if key[1] == 'item']))
    for item in item_list:
      if self.win.item_cfg[item, 'id'].find('edge') != -1:
        src_item = item.split('->')[0]
        dst_item = item.split('->')[1]
        if src_item in item_set and dst_item in item_set:
          dot.edge(src_item, dst_item)
      if self.win.item_cfg[item, 'id'].find('node') != -1:
        if item in item_set:
          node_list.append((item, item.split('.')[0]))
    # find groups
    all_groups = [i[1] for i in node_list]
    uniq_groups = set(all_groups)
    result = []
    for group in uniq_groups:
      this_group = []
      for i in node_list:
        if i[1] == group:
          this_group.append(i[0])
      result.append(this_group)
    for group in result:
      if len(group) > 1:
        for item in group:
          job_name = item.split('.')[0]
          with dot.subgraph(name = f'cluster_{job_name}') as c:
            c.attr(style='filled', color='#A0A0A0')
            c.node(item)
            c.attr(label = job_name)

    self.svg = dot.pipe(encoding = 'utf-8')
    renderer = QSvgRenderer()
    renderer.load(bytes(self.svg, encoding='utf-8'))
    root = et.fromstring(self.svg)
    for g in root.findall('.//{*}g'):
      id = g.get('id')
      title = g.find('.//{*}title').text
      if id != 'graph0':
        self.item = JDRRelatedItem(self, renderer, id, title)
        self.scene.addItem(self.item)

  def save_related_items(self):
    name = QFileDialog.getSaveFileName(self, 'Save File', '.', '*.svg')[0]
    if name:
      file = open(name, 'w')
      text = str(self.svg)
      file.write(text)
      file.close()
      JDRUtil.write_log(self.win, f'[Info]: JDRItemReport.save_related_items(): save file: "{name}"', 0)


class JDRRelatedItem(QGraphicsSvgItem):
  def __init__(self, sub, renderer, id, title):
    super().__init__()
    self.sub = sub
    self.renderer = renderer
    self.id = id
    self.title = title
    self.setSharedRenderer(renderer)
    self.setElementId(id)
    if self.id.find('node') != -1:
      self.change_node_color()
    bounds = renderer.boundsOnElement(id)
    self.setPos(bounds.topLeft())

  def change_node_color(self):
    if self.id.find('node') != -1:
      status = self.sub.win.item_cfg[self.title, 'item_status']
      if status in ['initial', 'waiting', 'running', 'success', 'failure']:
        act_sdt = ' ' + self.sub.win.exec_cfg[self.title, 'act_sdt']  # add prefix space to prevent parsing error (only integer)
        act_edt = ' ' + self.sub.win.exec_cfg[self.title, 'act_edt']
        dur = ' ' + self.sub.win.exec_cfg[self.title, 'dur']
        data_num = ' ' + self.sub.win.exec_cfg[self.title, 'data_num']
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

      if status in ['notjob', 'undefine', 'initial', 'waiting', 'running']:
        (self.sub.svg, num) = re.subn('(<title>' + self.title + '</title>\n<polygon fill=")([#enoA-F0-9]*)(")(.{0,2000})(status: )([a-z_]*)(</text>)', '\\1' + color + '\\3\\4\\5' + status + '\\7', self.sub.svg, 1, flags = re.DOTALL)
      if status in ['success', 'failure']:
        (self.sub.svg, num) = re.subn('(<title>' + self.title + '</title>\n<polygon fill=")([#enoA-F0-9]*)(")(.{0,2000})(status: )([a-z_]*)(</text>)(.{0,1000})(actual_start_datetime: )(.{0,30})(</text>)(.{0,150})(actual__end__datetime: )(.{0,30})(</text>)(.{0,150})(actual_duration: )(.{0,20})(</text>)(.{0,500})(data_num: )(.{0,20})(</text>)', '\\1' + color + '\\3\\4\\5' + status + '\\7\\8\\9' + act_sdt + '\\11\\12\\13' + act_edt + '\\15\\16\\17' + dur + '\\19\\20\\21' + data_num + '\\23', self.sub.svg, 1, flags = re.DOTALL)
      if num != 1:
        JDRUtil.write_log(self.win, f'[Warning]: JDRRelatedItem.change_node_color(): {self.title} change to {status} (num = {num})', 2)
      self.renderer.load(bytes(self.sub.svg, encoding='utf-8'))
      self.update()


class JDRItemReport_StatusPie(FigureCanvas):
  def __init__(self, window, item_name, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.win = window
    self.item_name = item_name
    self.job_name = item_name.split('.')[0]
    value = list()
    label = list()
    sql = f'''
      select status, count(*) from (
        select job_name, plan_dt, status, act_sdt, act_edt, data_num, extract(epoch from act_edt - act_sdt)::int dur, row_number() over (partition by job_name, plan_dt order by act_sdt desc) r from (
          select {JDRUtil.CTRL_COL_JOBNAME} as job_name, {JDRUtil.CTRL_COL_PLANDT} as plan_dt, {JDRUtil.CTRL_COL_STATUS} as status, {JDRUtil.CTRL_COL_ACTSDT} as act_sdt, {JDRUtil.CTRL_COL_ACTEDT} as act_edt, {JDRUtil.CTRL_COL_DATANUM} as data_num
          from {JDRUtil.CTRL_TABLENAME}
        ) as t0 where job_name = '{self.job_name}'
      ) as t1
      where r = 1
      group by 1
    '''
    try:
      conn = psycopg2.connect(database = f'{JDRUtil.CONN_DB}', user = f'{JDRUtil.CONN_USER}', password = f'{JDRUtil.CONN_PASSWD}', host = f'{JDRUtil.CONN_IP}', port = f'{JDRUtil.CONN_PORT}')
      cursor = conn.cursor()
      cursor.execute(sql)
      rows = cursor.fetchall()
      for row in rows:
        label.append(row[0])
        value.append(int(row[1]))
    except Exception as e:
      JDRUtil.write_log(self.win, f'[Error]: JDRItemReport_StatusPie(): {repr(e)}', 2)
    finally:
      if conn:
        cursor.close()
        conn.close()

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(value, labels=label, autopct='')
    ax.set_title(f'Status Pie Chart ({self.job_name})')
    plt.setp(autotexts, size=8, weight="bold")
    for i, a in enumerate(autotexts):
      a.set_text('{:.2f} %\n({} items)'.format(value[i]/sum(value)*100, value[i]))
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
    ax.legend(wedges, label, title='Status', loc='lower right')
    plt.tight_layout()
    ax.figure.canvas.draw()
    super(JDRItemReport_StatusPie, self).__init__(fig)
    plt.close()


class JDRItemReport_StartDTChart(FigureCanvas):
  def __init__(self, window, item_name, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.win = window
    self.item_name = item_name
    self.job_name = item_name.split('.')[0]
    plan_dt = list()
    act_sdt = list()
    sql = f'''
      select plan_dt, act_sdt from (
        select job_name, plan_dt, status, act_sdt, act_edt, data_num, extract(epoch from act_edt - act_sdt)::int dur, row_number() over (partition by job_name, plan_dt order by act_sdt desc) r from (
          select {JDRUtil.CTRL_COL_JOBNAME} as job_name, {JDRUtil.CTRL_COL_PLANDT} as plan_dt, {JDRUtil.CTRL_COL_STATUS} as status, {JDRUtil.CTRL_COL_ACTSDT} as act_sdt, {JDRUtil.CTRL_COL_ACTEDT} as act_edt, {JDRUtil.CTRL_COL_DATANUM} as data_num
          from {JDRUtil.CTRL_TABLENAME}
        ) as t0 where job_name = '{self.job_name}'
      ) as t1
      where r = 1 order by 1
    '''
    try:
      conn = psycopg2.connect(database = f'{JDRUtil.CONN_DB}', user = f'{JDRUtil.CONN_USER}', password = f'{JDRUtil.CONN_PASSWD}', host = f'{JDRUtil.CONN_IP}', port = f'{JDRUtil.CONN_PORT}')
      cursor = conn.cursor()
      cursor.execute(sql)
      rows = cursor.fetchall()
      for row in rows:
        plan_dt.append(row[0])
        act_sdt.append(row[1])
    except Exception as e:
      JDRUtil.write_log(self.win, f'[Error]: JDRItemReport_StartDTChart(): {repr(e)}', 2)
    finally:
      if conn:
        cursor.close()
        conn.close()

    fig, ax = plt.subplots()
    ax.plot_date(plan_dt, plan_dt, 'bo', markersize = 4)
    ax.plot_date(plan_dt, act_sdt, 'ro', markersize = 4)
    ax.plot((plan_dt, plan_dt), (plan_dt, act_sdt), c='#FF0000', fillstyle='bottom')
    ax.set_title(f'Plan & Start Datetime Chart ({self.job_name})')
    ax.set_xlabel('Plan Datetime')
    ax.set_ylabel('Execution Time')
    ax.legend(title=f'{self.job_name}', labels=['plan_dt', 'act_sdt'], loc='lower right')
    plt.xticks(rotation=-90, ha='right')
    plt.tight_layout()
    ax.figure.canvas.draw()
    super(JDRItemReport_StartDTChart, self).__init__(fig)
    plt.close()


class JDRItemReport_DurationChart(FigureCanvas):
  def __init__(self, window, item_name, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.win = window
    self.item_name = item_name
    self.job_name = item_name.split('.')[0]
    plan_dt = list()
    dur = list()
    sql = f'''
      select plan_dt, dur from (
        select job_name, plan_dt, status, act_sdt, act_edt, data_num, extract(epoch from act_edt - act_sdt)::int dur, row_number() over (partition by job_name, plan_dt order by act_sdt desc) r from (
          select {JDRUtil.CTRL_COL_JOBNAME} as job_name, {JDRUtil.CTRL_COL_PLANDT} as plan_dt, {JDRUtil.CTRL_COL_STATUS} as status, {JDRUtil.CTRL_COL_ACTSDT} as act_sdt, {JDRUtil.CTRL_COL_ACTEDT} as act_edt, {JDRUtil.CTRL_COL_DATANUM} as data_num
          from {JDRUtil.CTRL_TABLENAME}
        ) as t0 where job_name = '{self.job_name}'
      ) as t1
      where r = 1 order by 1
    '''
    try:
      conn = psycopg2.connect(database = f'{JDRUtil.CONN_DB}', user = f'{JDRUtil.CONN_USER}', password = f'{JDRUtil.CONN_PASSWD}', host = f'{JDRUtil.CONN_IP}', port = f'{JDRUtil.CONN_PORT}')
      cursor = conn.cursor()
      cursor.execute(sql)
      rows = cursor.fetchall()
      for row in rows:
        plan_dt.append(row[0])
        dur.append(int(row[1]))
    except Exception as e:
      JDRUtil.write_log(self.win, f'[Error]: JDRItemReport_DurationChart(): {repr(e)}', 2)
    finally:
      if conn:
        cursor.close()
        conn.close()

    fig, ax = plt.subplots()
    ax.bar(plan_dt, dur, label = plan_dt, width = 0.1)
    ax.set_title(f'Duration Chart ({self.job_name})')
    ax.set_xlabel('Plan Datetime')
    ax.set_ylabel('Duration (sec)')
    plt.xticks(rotation=-90, ha='right')
    plt.tight_layout()
    ax.figure.canvas.draw()
    super(JDRItemReport_DurationChart, self).__init__(fig)
    plt.close()


class JDRItemReport_DataNumberChart(FigureCanvas):
  def __init__(self, window, item_name, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.win = window
    self.item_name = item_name
    self.job_name = item_name.split('.')[0]
    plan_dt = list()
    data_num = list()
    sql = f'''
      select plan_dt, data_num from (
        select job_name, plan_dt, status, act_sdt, act_edt, data_num, extract(epoch from act_edt - act_sdt)::int dur, row_number() over (partition by job_name, plan_dt order by act_sdt desc) r from (
          select {JDRUtil.CTRL_COL_JOBNAME} as job_name, {JDRUtil.CTRL_COL_PLANDT} as plan_dt, {JDRUtil.CTRL_COL_STATUS} as status, {JDRUtil.CTRL_COL_ACTSDT} as act_sdt, {JDRUtil.CTRL_COL_ACTEDT} as act_edt, {JDRUtil.CTRL_COL_DATANUM} as data_num
          from {JDRUtil.CTRL_TABLENAME}
        ) as t0 where job_name = '{self.job_name}'
      ) as t1
      where r = 1 order by 1
    '''
    try:
      conn = psycopg2.connect(database = f'{JDRUtil.CONN_DB}', user = f'{JDRUtil.CONN_USER}', password = f'{JDRUtil.CONN_PASSWD}', host = f'{JDRUtil.CONN_IP}', port = f'{JDRUtil.CONN_PORT}')
      cursor = conn.cursor()
      cursor.execute(sql)
      rows = cursor.fetchall()
      for row in rows:
        plan_dt.append(row[0])
        data_num.append(int(row[1]))
    except Exception as e:
      JDRUtil.write_log(self.win, f'[Error]: JDRItemReport_DataNumberChart(): {repr(e)}', 2)
    finally:
      if conn:
        cursor.close()
        conn.close()

    fig, ax = plt.subplots()
    ax.bar(plan_dt, data_num, label = plan_dt, width = 0.1)
    ax.set_title(f'Data Number Chart ({self.job_name})')
    ax.set_xlabel('Plan Datetime')
    ax.set_ylabel('Data Number')
    plt.xticks(rotation=-90, ha='right')
    plt.tight_layout()
    ax.figure.canvas.draw()
    super(JDRItemReport_DataNumberChart, self).__init__(fig)
    plt.close()

