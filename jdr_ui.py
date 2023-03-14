from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from jdr_util import *

class MainWindowUI(object):
  def setup_ui(self):
    # main window: show svg items
    self.viewer = QGraphicsView(self)
    self.scene = QGraphicsScene(self)
    self.scene.clear()
    self.viewer.setScene(self.scene)
    self.viewer.resetTransform()
    self.setCentralWidget(self.viewer)

    # setup window: initialize setup of JDR
    self.setup_dock = QDockWidget(None, self)  # translate: Setup
    self.setup_widget = QTabWidget()
    self.setup_dock.setWidget(self.setup_widget)
    self.setup_dock.setFloating(False)
    self.setup_dock.setFeatures(self.setup_dock.features() & ~QDockWidget.DockWidgetFeature.DockWidgetClosable)
    self.setup_dock.setFixedHeight(520)
    self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.setup_dock)
    self.setup_widget1 = QWidget()
    self.setup_widget2 = QWidget()
    self.setup_widget3 = QWidget()
    self.setup_widget4 = QWidget()
    self.setup_widget.addTab(self.setup_widget1, None)  # translate: Basic
    self.setup_widget.addTab(self.setup_widget2, None)  # translate: DB
    self.setup_widget.addTab(self.setup_widget3, None)  # translate: Function
    self.setup_widget.addTab(self.setup_widget4, None)  # translate: Information
    self.setup_layout1 = QVBoxLayout()
    self.setup_layout2 = QVBoxLayout()
    self.setup_layout3 = QVBoxLayout()
    self.setup_layout4 = QVBoxLayout()
    self.setup_widget1.setLayout(self.setup_layout1)
    self.setup_widget2.setLayout(self.setup_layout2)
    self.setup_widget3.setLayout(self.setup_layout3)
    self.setup_widget4.setLayout(self.setup_layout4)

    # item navigator button window: help searching the specific item
    self.job_dock = QDockWidget(None, self)  # translate: Item Navigator Button
    self.job_dock.setFeatures(self.job_dock.features() & ~QDockWidget.DockWidgetFeature.DockWidgetClosable)
    self.job_scrollarea = QScrollArea()
    self.job_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    self.job_scrollarea.setWidgetResizable(True)
    self.job_widget = QWidget()
    self.job_layout = QFormLayout()
    self.job_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.job_widget.setLayout(self.job_layout)
    self.job_scrollarea.setWidget(self.job_widget)
    self.job_dock.setWidget(self.job_scrollarea)
    self.job_dock.setFloating(False)
    self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.job_dock)

    # log window: show log messages of every activities
    self.log_dock = QDockWidget(None, self)  # translate: Log
    self.log_dock.setFeatures(self.log_dock.features() & ~QDockWidget.DockWidgetFeature.DockWidgetClosable)
    self.log_textedit = QTextEdit()
    self.log_dock.setWidget(self.log_textedit)
    self.log_dock.setFloating(False)
    self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock)

    # initialize all objects in the setup window
    self.init_setup_input()
    self.init_setup_db()
    self.init_setup_function()
    self.init_setup_information()

    self.retranslate_ui()


  def init_setup_input(self):
    self.setup_widget1_lang_layout = QVBoxLayout()
    self.setup_widget1_lang_group = QGroupBox()  # translate: Language
    self.setup_widget1_lang_group.setLayout(self.setup_widget1_lang_layout)
    self.setup_widget1_lang_combo = QComboBox()
    self.setup_widget1_lang_layout.addWidget(self.setup_widget1_lang_combo)
    lang_options = ([('English', ''), ('繁體中文', 'jdr_zh_tw'), ('ㄅㄆㄇ', 'jdr_bpm_tw'), ])
    for i, (text, lang) in enumerate(lang_options):
      self.setup_widget1_lang_combo.addItem(text)
      self.setup_widget1_lang_combo.setItemData(i, lang)

    self.setup_widget1_input_layout = QGridLayout()
    self.setup_widget1_input_group = QGroupBox()  # translate: Input
    self.setup_widget1_input_group.setLayout(self.setup_widget1_input_layout)
    self.setup_widget1_input_start_label = QLabel()  # translate: Start
    self.setup_widget1_input_start_dateedit = QDateEdit()
    self.setup_widget1_input_start_dateedit.setCalendarPopup(True)
    self.setup_widget1_input_start_dateedit.setDate(QDate.currentDate())
    self.setup_widget1_input_start_dateedit.setDisplayFormat('yyyy-MM-dd')
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_start_label, 0, 0)
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_start_dateedit, 0, 1, 1, 2)

    self.setup_widget1_input_end_label = QLabel()  # translate: End
    self.setup_widget1_input_end_dateedit = QDateEdit()
    self.setup_widget1_input_end_dateedit.setCalendarPopup(True)
    self.setup_widget1_input_end_dateedit.setDate(QDate.currentDate())
    self.setup_widget1_input_end_dateedit.setDisplayFormat('yyyy-MM-dd')
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_end_label, 1, 0)
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_end_dateedit, 1, 1, 1, 2)

    self.setup_widget1_input_file_label = QLabel()  # translate: File
    self.setup_widget1_input_file_lineedit = QLineEdit()
    self.setup_widget1_input_browse_button = QPushButton() # translate: Browse
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_file_label, 2, 0)
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_file_lineedit, 2, 1)
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_browse_button, 2, 2)

    self.setup_widget1_input_sheet_label = QLabel()  # translate: Sheet
    self.setup_widget1_input_sheet_combobox = QComboBox()
    self.setup_widget1_input_generate_button = QPushButton()  # translate: Generate
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_sheet_label, 3, 0)
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_sheet_combobox, 3, 1)
    self.setup_widget1_input_layout.addWidget(self.setup_widget1_input_generate_button, 3, 2)

    self.setup_widget1_color_layout = QGridLayout()
    self.setup_widget1_color_group = QGroupBox()  # translate: Color
    self.setup_widget1_color_group.setLayout(self.setup_widget1_color_layout)
    self.setup_widget1_color_initial_label = QLabel()  # translate: Status (initial)
    self.setup_widget1_color_initial_lineedit = QLineEdit(JDRUtil.DEFAULT_COLOR_INITIAL)
    self.setup_widget1_color_initial_rect = QLabel()
    self.setup_widget1_color_initial_rect.setFixedSize(20, 20)
    self.setup_widget1_color_initial_rect.setFrameShape(QFrame.Shape.WinPanel)
    self.setup_widget1_color_initial_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_INITIAL}')
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_initial_label, 0, 0)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_initial_lineedit, 0, 1)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_initial_rect, 0, 2)

    self.setup_widget1_color_waiting_label = QLabel()  # translate: Status (waiting)
    self.setup_widget1_color_waiting_lineedit = QLineEdit(JDRUtil.DEFAULT_COLOR_WAITING)
    self.setup_widget1_color_waiting_rect = QLabel()
    self.setup_widget1_color_waiting_rect.setFixedSize(20, 20)
    self.setup_widget1_color_waiting_rect.setFrameShape(QFrame.Shape.WinPanel)
    self.setup_widget1_color_waiting_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_WAITING}')
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_waiting_label, 1, 0)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_waiting_lineedit, 1, 1)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_waiting_rect, 1, 2)

    self.setup_widget1_color_running_label = QLabel()  # translate: Status (running)
    self.setup_widget1_color_running_lineedit = QLineEdit(JDRUtil.DEFAULT_COLOR_RUNNING)
    self.setup_widget1_color_running_rect = QLabel()
    self.setup_widget1_color_running_rect.setFixedSize(20, 20)
    self.setup_widget1_color_running_rect.setFrameShape(QFrame.Shape.WinPanel)
    self.setup_widget1_color_running_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_RUNNING}')
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_running_label, 2, 0)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_running_lineedit, 2, 1)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_running_rect, 2, 2)

    self.setup_widget1_color_success_label = QLabel()  # translate: Status (success)
    self.setup_widget1_color_success_lineedit = QLineEdit(JDRUtil.DEFAULT_COLOR_SUCCESS)
    self.setup_widget1_color_success_rect = QLabel()
    self.setup_widget1_color_success_rect.setFixedSize(20, 20)
    self.setup_widget1_color_success_rect.setFrameShape(QFrame.Shape.WinPanel)
    self.setup_widget1_color_success_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_SUCCESS}')
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_success_label, 3, 0)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_success_lineedit, 3, 1)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_success_rect, 3, 2)

    self.setup_widget1_color_failure_label = QLabel()  # translate: Status (failure)
    self.setup_widget1_color_failure_lineedit = QLineEdit(JDRUtil.DEFAULT_COLOR_FAILURE)
    self.setup_widget1_color_failure_rect = QLabel()
    self.setup_widget1_color_failure_rect.setFixedSize(20, 20)
    self.setup_widget1_color_failure_rect.setFrameShape(QFrame.Shape.WinPanel)
    self.setup_widget1_color_failure_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_FAILURE}')
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_failure_label, 4, 0)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_failure_lineedit, 4, 1)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_failure_rect, 4, 2)

    self.setup_widget1_color_notjob_label = QLabel()  # translate: Status (notjob)
    self.setup_widget1_color_notjob_lineedit = QLineEdit(JDRUtil.DEFAULT_COLOR_NOTJOB)
    self.setup_widget1_color_notjob_rect = QLabel()
    self.setup_widget1_color_notjob_rect.setFixedSize(20, 20)
    self.setup_widget1_color_notjob_rect.setFrameShape(QFrame.Shape.WinPanel)
    self.setup_widget1_color_notjob_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_NOTJOB}')
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_notjob_label, 5, 0)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_notjob_lineedit, 5, 1)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_notjob_rect, 5, 2)

    self.setup_widget1_color_undefine_label = QLabel()  # translate: Status (undefine)
    self.setup_widget1_color_undefine_lineedit = QLineEdit(JDRUtil.DEFAULT_COLOR_UNDEFINE)
    self.setup_widget1_color_undefine_rect = QLabel()
    self.setup_widget1_color_undefine_rect.setFixedSize(20, 20)
    self.setup_widget1_color_undefine_rect.setFrameShape(QFrame.Shape.WinPanel)
    self.setup_widget1_color_undefine_rect.setStyleSheet(f'background-color: {JDRUtil.DEFAULT_COLOR_UNDEFINE}')
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_undefine_label, 6, 0)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_undefine_lineedit, 6, 1)
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_undefine_rect, 6, 2)

    self.setup_widget1_color_default_button = QPushButton()  # translate: Default Color
    self.setup_widget1_color_layout.addWidget(self.setup_widget1_color_default_button, 7, 1)

    self.setup_layout1.addWidget(self.setup_widget1_lang_group)
    self.setup_layout1.addWidget(self.setup_widget1_input_group)
    self.setup_layout1.addWidget(self.setup_widget1_color_group)

    spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    self.setup_layout1.addItem(spacer)

  def init_setup_db(self):
    self.setup_widget2_conn_layout = QFormLayout()
    self.setup_widget2_conn_group = QGroupBox()  # translate: DB Connection (PostgreSQL)
    self.setup_widget2_conn_group.setLayout(self.setup_widget2_conn_layout)
    self.setup_widget2_conn_ip_label = QLabel()  # translate: IP
    self.setup_widget2_conn_ip_lineedit = QLineEdit(JDRUtil.DEFAULT_CONN_IP)
    self.setup_widget2_conn_user_label = QLabel()  # translate: User
    self.setup_widget2_conn_user_lineedit = QLineEdit(JDRUtil.DEFAULT_CONN_USER)
    self.setup_widget2_conn_passwd_label = QLabel()  # translate: Password
    self.setup_widget2_conn_passwd_lineedit = QLineEdit(JDRUtil.DEFAULT_CONN_PASSWD)
    self.setup_widget2_conn_passwd_lineedit.setEchoMode(QLineEdit.EchoMode.Password)
    self.setup_widget2_conn_port_label = QLabel()  # translate: Port
    self.setup_widget2_conn_port_lineedit = QLineEdit(JDRUtil.DEFAULT_CONN_PORT)
    self.setup_widget2_conn_db_label = QLabel()  # translate: DB Name
    self.setup_widget2_conn_db_lineedit = QLineEdit(JDRUtil.DEFAULT_CONN_DB)
    self.setup_widget2_conn_test_button = QPushButton()  # translate: Test Connection...
    self.setup_widget2_conn_layout.addRow(self.setup_widget2_conn_ip_label, self.setup_widget2_conn_ip_lineedit)
    self.setup_widget2_conn_layout.addRow(self.setup_widget2_conn_user_label, self.setup_widget2_conn_user_lineedit)
    self.setup_widget2_conn_layout.addRow(self.setup_widget2_conn_passwd_label, self.setup_widget2_conn_passwd_lineedit)
    self.setup_widget2_conn_layout.addRow(self.setup_widget2_conn_port_label, self.setup_widget2_conn_port_lineedit)
    self.setup_widget2_conn_layout.addRow(self.setup_widget2_conn_db_label, self.setup_widget2_conn_db_lineedit)
    self.setup_widget2_conn_layout.addRow(None, self.setup_widget2_conn_test_button)

    self.setup_widget2_ctrl_layout = QFormLayout()
    self.setup_widget2_ctrl_group = QGroupBox()  # translate: Control Table
    self.setup_widget2_ctrl_group.setLayout(self.setup_widget2_ctrl_layout)
    self.setup_widget2_ctrl_tablename_label = QLabel()  # translate: Control Table Name
    self.setup_widget2_ctrl_tablename_lineedit = QLineEdit(JDRUtil.DEFAULT_CTRL_TABLENAME)
    self.setup_widget2_ctrl_jobname_label = QLabel()  # translate: Column Name (Job Name)
    self.setup_widget2_ctrl_jobname_lineedit = QLineEdit(JDRUtil.DEFAULT_CTRL_COL_JOBNAME)
    self.setup_widget2_ctrl_plandt_label = QLabel()  # translate: Column Name (Plan Datetime)
    self.setup_widget2_ctrl_plandt_lineedit = QLineEdit(JDRUtil.DEFAULT_CTRL_COL_PLANDT)
    self.setup_widget2_ctrl_status_label = QLabel()  # translate: Column Name (Job Status)
    self.setup_widget2_ctrl_status_lineedit = QLineEdit(JDRUtil.DEFAULT_CTRL_COL_STATUS)
    self.setup_widget2_ctrl_actsdt_label = QLabel()  # translate: Column Name (Actual Start Datetime)
    self.setup_widget2_ctrl_actsdt_lineedit = QLineEdit(JDRUtil.DEFAULT_CTRL_COL_ACTSDT)
    self.setup_widget2_ctrl_actedt_label = QLabel()  # translate: Column Name (Actual End Datetime)
    self.setup_widget2_ctrl_actedt_lineedit = QLineEdit(JDRUtil.DEFAULT_CTRL_COL_ACTEDT)
    self.setup_widget2_ctrl_datanum_label = QLabel()  # translate: Column Name (Data Number)
    self.setup_widget2_ctrl_datanum_lineedit = QLineEdit(JDRUtil.DEFAULT_CTRL_COL_DATANUM)
    self.setup_widget2_ctrl_layout.addRow(self.setup_widget2_ctrl_tablename_label, self.setup_widget2_ctrl_tablename_lineedit)
    self.setup_widget2_ctrl_layout.addRow(self.setup_widget2_ctrl_jobname_label, self.setup_widget2_ctrl_jobname_lineedit)
    self.setup_widget2_ctrl_layout.addRow(self.setup_widget2_ctrl_plandt_label, self.setup_widget2_ctrl_plandt_lineedit)
    self.setup_widget2_ctrl_layout.addRow(self.setup_widget2_ctrl_status_label, self.setup_widget2_ctrl_status_lineedit)
    self.setup_widget2_ctrl_layout.addRow(self.setup_widget2_ctrl_actsdt_label, self.setup_widget2_ctrl_actsdt_lineedit)
    self.setup_widget2_ctrl_layout.addRow(self.setup_widget2_ctrl_actedt_label, self.setup_widget2_ctrl_actedt_lineedit)
    self.setup_widget2_ctrl_layout.addRow(self.setup_widget2_ctrl_datanum_label, self.setup_widget2_ctrl_datanum_lineedit)

    self.setup_layout2.addWidget(self.setup_widget2_conn_group)
    self.setup_layout2.addWidget(self.setup_widget2_ctrl_group)

    spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    self.setup_layout2.addItem(spacer)

  def init_setup_function(self):
    self.setup_widget3_execute_layout = QGridLayout()
    self.setup_widget3_execute_group = QGroupBox()  # translate: Execute Items
    self.setup_widget3_execute_group.setLayout(self.setup_widget3_execute_layout)
    self.setup_widget3_execute_runontime_check = QCheckBox()  # translate: Run On Time
    self.setup_widget3_execute_runontime_check.setChecked(JDRUtil.DEFAULT_RUN_ON_TIME)
    self.setup_widget3_execute_layout.addWidget(self.setup_widget3_execute_runontime_check, 0, 0)
    self.setup_widget3_execute_runalljob_button = QPushButton()  # translate: Run All Items
    self.setup_widget3_execute_runalljob_button.setStyleSheet('text-align:left')
    self.setup_widget3_execute_runalljob_label = QLabel()  # translate: Only allowed to be used when\nthere are no running/waiting items
    self.setup_widget3_execute_layout.addWidget(self.setup_widget3_execute_runalljob_button, 1, 0)
    self.setup_widget3_execute_layout.addWidget(self.setup_widget3_execute_runalljob_label, 1, 1)
    self.setup_widget3_execute_contalljob_button = QPushButton()  # translate: Continue All Items
    self.setup_widget3_execute_contalljob_button.setStyleSheet('text-align:left')
    self.setup_widget3_execute_contalljob_label = QLabel()  # translate: Start from the job which is not success
    self.setup_widget3_execute_layout.addWidget(self.setup_widget3_execute_contalljob_button, 2, 0)
    self.setup_widget3_execute_layout.addWidget(self.setup_widget3_execute_contalljob_label, 2, 1)
    self.setup_widget3_execute_stopdepjob_button = QPushButton()  # translate: Stop All Items
    self.setup_widget3_execute_stopdepjob_button.setStyleSheet('text-align:left')
    self.setup_widget3_execute_stopdepjob_label = QLabel()  # translate: Stop all dependency items (except running items)
    self.setup_widget3_execute_layout.addWidget(self.setup_widget3_execute_stopdepjob_button, 3, 0)
    self.setup_widget3_execute_layout.addWidget(self.setup_widget3_execute_stopdepjob_label, 3, 1)

    self.setup_widget3_other_layout = QGridLayout()
    self.setup_widget3_other_group = QGroupBox()  # translate: Other
    self.setup_widget3_other_group.setLayout(self.setup_widget3_other_layout)

    self.setup_widget3_other_showrep_button = QPushButton()  # translate: Show report
    self.setup_widget3_other_showrep_label = QLabel()  # translate: Open the main report of all items
    self.setup_widget3_other_layout.addWidget(self.setup_widget3_other_showrep_button, 0, 0)
    self.setup_widget3_other_layout.addWidget(self.setup_widget3_other_showrep_label, 0, 1)

    self.setup_widget3_other_reloaddb_button = QPushButton()  # translate: Reload From DB
    self.setup_widget3_other_reloaddb_label = QLabel()  # translate: Reload job information and status\nfrom control table
    self.setup_widget3_other_layout.addWidget(self.setup_widget3_other_reloaddb_button, 1, 0)
    self.setup_widget3_other_layout.addWidget(self.setup_widget3_other_reloaddb_label, 1, 1)
    self.setup_widget3_other_savesvg_button = QPushButton()  # translate: Save SVG
    self.setup_widget3_other_savesvg_label = QLabel()  # translate: Save the current view as SVG file
    self.setup_widget3_other_layout.addWidget(self.setup_widget3_other_savesvg_button, 2, 0)
    self.setup_widget3_other_layout.addWidget(self.setup_widget3_other_savesvg_label, 2, 1)

    self.setup_layout3.addWidget(self.setup_widget3_execute_group)
    self.setup_layout3.addWidget(self.setup_widget3_other_group)

    spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    self.setup_layout3.addItem(spacer)

  def init_setup_information(self):
    self.setup_widget4_info_jobs_layout = QGridLayout()
    self.setup_widget4_info_jobs_group = QGroupBox()  # translate: About Jobs
    self.setup_widget4_info_jobs_group.setLayout(self.setup_widget4_info_jobs_layout)
    self.setup_widget4_info_jobs_document1_label = QLabel()  # translate: Document jobs:
    self.setup_widget4_info_jobs_document2_label = QLabel('0')
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_document1_label, 0, 0)
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_document2_label, 0, 1)

    self.setup_widget4_info_jobs_available1_label = QLabel()  # translate: Available jobs:
    self.setup_widget4_info_jobs_available2_label = QLabel('0')
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_available1_label, 1, 0)
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_available2_label, 1, 1)

    self.setup_widget4_info_jobs_unavailable1_label = QLabel()  # translate: Unavailable jobs:
    self.setup_widget4_info_jobs_unavailable2_label = QLabel('0')
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_unavailable1_label, 2, 0)
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_unavailable2_label, 2, 1)

    self.setup_widget4_info_jobs_not1_label = QLabel()  # translate: Not jobs:
    self.setup_widget4_info_jobs_not2_label = QLabel('0')
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_not1_label, 3, 0)
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_not2_label, 3, 1)

    self.setup_widget4_info_jobs_undefine1_label = QLabel()  # translate: Undefine jobs:
    self.setup_widget4_info_jobs_undefine2_label = QLabel('0')
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_undefine1_label, 4, 0)
    self.setup_widget4_info_jobs_layout.addWidget(self.setup_widget4_info_jobs_undefine2_label, 4, 1)


    self.setup_widget4_info_items_layout = QGridLayout()
    self.setup_widget4_info_items_group = QGroupBox()  # translate: About Items
    self.setup_widget4_info_items_group.setLayout(self.setup_widget4_info_items_layout)
    self.setup_widget4_info_items_all1_label = QLabel()  # translate: All items:
    self.setup_widget4_info_items_all2_label = QLabel('0')
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_all1_label, 0, 0)
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_all2_label, 0, 1)

    self.setup_widget4_info_items_available1_label = QLabel()  # translate: Available items:
    self.setup_widget4_info_items_available2_label = QLabel('0')
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_available1_label, 1, 0)
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_available2_label, 1, 1)

    self.setup_widget4_info_items_initial1_label = QLabel()  # translate: Initial items:
    self.setup_widget4_info_items_initial2_label = QLabel('0')
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_initial1_label, 2, 0)
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_initial2_label, 2, 1)

    self.setup_widget4_info_items_waiting1_label = QLabel()  # translate: Waiting items:
    self.setup_widget4_info_items_waiting2_label = QLabel('0')
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_waiting1_label, 3, 0)
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_waiting2_label, 3, 1)

    self.setup_widget4_info_items_running1_label = QLabel()  # translate: Running items:
    self.setup_widget4_info_items_running2_label = QLabel('0')
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_running1_label, 4, 0)
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_running2_label, 4, 1)

    self.setup_widget4_info_items_success1_label = QLabel()  # translate: Success items:
    self.setup_widget4_info_items_success2_label = QLabel('0')
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_success1_label, 5, 0)
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_success2_label, 5, 1)

    self.setup_widget4_info_items_failure1_label = QLabel()  # translate: Failure items:
    self.setup_widget4_info_items_failure2_label = QLabel('0')
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_failure1_label, 6, 0)
    self.setup_widget4_info_items_layout.addWidget(self.setup_widget4_info_items_failure2_label, 6, 1)


    self.setup_widget4_info_note_layout = QVBoxLayout()
    self.setup_widget4_info_note_group = QGroupBox()  # translate: Note
    self.setup_widget4_info_note_group.setLayout(self.setup_widget4_info_note_layout)
    self.setup_widget4_info_note_list1_label = QLabel()  # translate: 1. (A1) = (A2) + (A3) + (A4)
    self.setup_widget4_info_note_list2_label = QLabel()  # translate: 2. (B2) = (B3) + (B4) + (B5) + (B6) + (B7)
    self.setup_widget4_info_note_list3_label = QLabel()  # translate: 3. (B1) = (B2) + (A4) + (A5)
    self.setup_widget4_info_note_layout.addWidget(self.setup_widget4_info_note_list1_label)
    self.setup_widget4_info_note_layout.addWidget(self.setup_widget4_info_note_list2_label)
    self.setup_widget4_info_note_layout.addWidget(self.setup_widget4_info_note_list3_label)


    self.setup_layout4.addWidget(self.setup_widget4_info_jobs_group)
    self.setup_layout4.addWidget(self.setup_widget4_info_items_group)
    self.setup_layout4.addWidget(self.setup_widget4_info_note_group)

    spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    self.setup_layout4.addItem(spacer)


  def retranslate_ui(self):
    self.setWindowTitle(QCoreApplication.translate('MainWindowUI', u'Job Dependency Runner'))
    self.setup_dock.setWindowTitle(QCoreApplication.translate('MainWindowUI', u'Setup'))
    self.job_dock.setWindowTitle(QCoreApplication.translate('MainWindowUI', u'Item Navigator Button'))
    self.log_dock.setWindowTitle(QCoreApplication.translate('MainWindowUI', u'Log'))
    self.setup_widget.setTabText(0, QCoreApplication.translate('MainWindowUI', u'Basic'))
    self.setup_widget.setTabText(1, QCoreApplication.translate('MainWindowUI', u'DB'))
    self.setup_widget.setTabText(2, QCoreApplication.translate('MainWindowUI', u'Function'))
    self.setup_widget.setTabText(3, QCoreApplication.translate('MainWindowUI', u'Information'))
    self.setup_widget1_lang_group.setTitle(QCoreApplication.translate('MainWindowUI', u'Language'))
    self.setup_widget1_input_group.setTitle(QCoreApplication.translate('MainWindowUI', u'Input'))
    self.setup_widget1_input_start_label.setText(QCoreApplication.translate('MainWindowUI', u'Start'))
    self.setup_widget1_input_end_label.setText(QCoreApplication.translate('MainWindowUI', u'End'))
    self.setup_widget1_input_file_label.setText(QCoreApplication.translate('MainWindowUI', u'File'))
    self.setup_widget1_input_browse_button.setText(QCoreApplication.translate('MainWindowUI', u'Browse'))
    self.setup_widget1_input_sheet_label.setText(QCoreApplication.translate('MainWindowUI', u'Sheet'))
    self.setup_widget1_input_generate_button.setText(QCoreApplication.translate('MainWindowUI', u'Generate'))
    self.setup_widget1_color_group.setTitle(QCoreApplication.translate('MainWindowUI', u'Color'))
    self.setup_widget1_color_initial_label.setText(QCoreApplication.translate('MainWindowUI', u'Status (initial)'))
    self.setup_widget1_color_waiting_label.setText(QCoreApplication.translate('MainWindowUI', u'Status (waiting)'))
    self.setup_widget1_color_running_label.setText(QCoreApplication.translate('MainWindowUI', u'Status (running)'))
    self.setup_widget1_color_success_label.setText(QCoreApplication.translate('MainWindowUI', u'Status (success)'))
    self.setup_widget1_color_failure_label.setText(QCoreApplication.translate('MainWindowUI', u'Status (failure)'))
    self.setup_widget1_color_notjob_label.setText(QCoreApplication.translate('MainWindowUI', u'Status (notjob)'))
    self.setup_widget1_color_undefine_label.setText(QCoreApplication.translate('MainWindowUI', u'Status (undefine)'))
    self.setup_widget1_color_default_button.setText(QCoreApplication.translate('MainWindowUI', u'Default Color'))
    self.setup_widget2_conn_group.setTitle(QCoreApplication.translate('MainWindowUI', u'DB Connection (PostgreSQL)'))
    self.setup_widget2_conn_ip_label.setText(QCoreApplication.translate('MainWindowUI', u'IP'))
    self.setup_widget2_conn_user_label.setText(QCoreApplication.translate('MainWindowUI', u'User'))
    self.setup_widget2_conn_passwd_label.setText(QCoreApplication.translate('MainWindowUI', u'Password'))
    self.setup_widget2_conn_port_label.setText(QCoreApplication.translate('MainWindowUI', u'Port'))
    self.setup_widget2_conn_db_label.setText(QCoreApplication.translate('MainWindowUI', u'DB Name'))
    self.setup_widget2_conn_test_button.setText(QCoreApplication.translate('MainWindowUI', u'Test Connection...'))
    self.setup_widget2_ctrl_group.setTitle(QCoreApplication.translate('MainWindowUI', u'Control Table'))
    self.setup_widget2_ctrl_tablename_label.setText(QCoreApplication.translate('MainWindowUI', u'Control Table Name'))
    self.setup_widget2_ctrl_jobname_label.setText(QCoreApplication.translate('MainWindowUI', u'Column Name (Job Name)'))
    self.setup_widget2_ctrl_plandt_label.setText(QCoreApplication.translate('MainWindowUI', u'Column Name (Plan Datetime)'))
    self.setup_widget2_ctrl_status_label.setText(QCoreApplication.translate('MainWindowUI', u'Column Name (Job Status)'))
    self.setup_widget2_ctrl_actsdt_label.setText(QCoreApplication.translate('MainWindowUI', u'Column Name (Actual Start Datetime)'))
    self.setup_widget2_ctrl_actedt_label.setText(QCoreApplication.translate('MainWindowUI', u'Column Name (Actual End Datetime)'))
    self.setup_widget2_ctrl_datanum_label.setText(QCoreApplication.translate('MainWindowUI', u'Column Name (Data Number)'))
    self.setup_widget3_execute_group.setTitle(QCoreApplication.translate('MainWindowUI', u'Execute Items'))
    self.setup_widget3_execute_runontime_check.setText(QCoreApplication.translate('MainWindowUI', u'Run On Time'))
    self.setup_widget3_execute_runalljob_button.setText(QCoreApplication.translate('MainWindowUI', u'► 　Run All Items'))
    self.setup_widget3_execute_runalljob_label.setText(QCoreApplication.translate('MainWindowUI', u'Only allowed to be used when\nthere are no running/waiting items'))
    self.setup_widget3_execute_contalljob_button.setText(QCoreApplication.translate('MainWindowUI', u'►► Continue All Items'))
    self.setup_widget3_execute_contalljob_label.setText(QCoreApplication.translate('MainWindowUI', u'Run all items except success'))
    self.setup_widget3_execute_stopdepjob_button.setText(QCoreApplication.translate('MainWindowUI', u'◼ 　Stop All Items'))
    self.setup_widget3_execute_stopdepjob_label.setText(QCoreApplication.translate('MainWindowUI', u'Stop all dependency items (except running items)'))
    self.setup_widget3_other_group.setTitle(QCoreApplication.translate('MainWindowUI', u'Other'))
    self.setup_widget3_other_showrep_button.setText(QCoreApplication.translate('MainWindowUI', u'🖺 　Show report'))
    self.setup_widget3_other_showrep_label.setText(QCoreApplication.translate('MainWindowUI', u'Open the main report of all items'))
    self.setup_widget3_other_reloaddb_button.setText(QCoreApplication.translate('MainWindowUI', u'🗘 　Reload From DB'))
    self.setup_widget3_other_reloaddb_label.setText(QCoreApplication.translate('MainWindowUI', u'Reload item information and status\nfrom control table'))
    self.setup_widget3_other_savesvg_button.setText(QCoreApplication.translate('MainWindowUI', u'🖫 　Save SVG'))
    self.setup_widget3_other_savesvg_label.setText(QCoreApplication.translate('MainWindowUI', u'Save the current view as SVG file'))
    self.setup_widget4_info_jobs_group.setTitle(QCoreApplication.translate('MainWindowUI', u'About Jobs'))
    self.setup_widget4_info_jobs_document1_label.setText(QCoreApplication.translate('MainWindowUI', u'(A1).Document jobs:'))
    self.setup_widget4_info_jobs_available1_label.setText(QCoreApplication.translate('MainWindowUI', u'(A2).Available jobs:'))
    self.setup_widget4_info_jobs_unavailable1_label.setText(QCoreApplication.translate('MainWindowUI', u'(A3).Unavailable jobs:'))
    self.setup_widget4_info_jobs_not1_label.setText(QCoreApplication.translate('MainWindowUI', u'(A4).Not jobs:'))
    self.setup_widget4_info_jobs_undefine1_label.setText(QCoreApplication.translate('MainWindowUI', u'(A5).Undefine jobs:'))
    self.setup_widget4_info_items_group.setTitle(QCoreApplication.translate('MainWindowUI', u'About Items'))
    self.setup_widget4_info_items_all1_label.setText(QCoreApplication.translate('MainWindowUI', u'(B1).All items:'))
    self.setup_widget4_info_items_available1_label.setText(QCoreApplication.translate('MainWindowUI', u'(B2).Available items:'))
    self.setup_widget4_info_items_initial1_label.setText(QCoreApplication.translate('MainWindowUI', u'(B3).Initial items:'))
    self.setup_widget4_info_items_waiting1_label.setText(QCoreApplication.translate('MainWindowUI', u'(B4).Waiting items:'))
    self.setup_widget4_info_items_running1_label.setText(QCoreApplication.translate('MainWindowUI', u'(B5).Running items:'))
    self.setup_widget4_info_items_success1_label.setText(QCoreApplication.translate('MainWindowUI', u'(B6).Success items:'))
    self.setup_widget4_info_items_failure1_label.setText(QCoreApplication.translate('MainWindowUI', u'(B7).Failure items:'))
    self.setup_widget4_info_note_group.setTitle(QCoreApplication.translate('MainWindowUI', u'Note'))
    self.setup_widget4_info_note_list1_label.setText(QCoreApplication.translate('MainWindowUI', u'1. (A1) = (A2) + (A3) + (A4)'))
    self.setup_widget4_info_note_list2_label.setText(QCoreApplication.translate('MainWindowUI', u'2. (B2) = (B3) + (B4) + (B5) + (B6) + (B7)'))
    self.setup_widget4_info_note_list3_label.setText(QCoreApplication.translate('MainWindowUI', u'3. (B1) = (B2) + (A4) + (A5)'))
