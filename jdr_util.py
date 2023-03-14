import re
import psycopg2
from PyQt6.QtCore import *

class JDRUtil():
  STYLE_CONFIG = 'QPushButton {background-color: #C0C0C0}'
  DEFAULT_COLOR_INITIAL = '#FFFFFF'
  DEFAULT_COLOR_WAITING = '#FFFFCC'
  DEFAULT_COLOR_RUNNING = '#FFFF00'
  DEFAULT_COLOR_SUCCESS = '#74C126'
  DEFAULT_COLOR_FAILURE = '#EFABCD'
  DEFAULT_COLOR_NOTJOB = '#C0C0C0'
  DEFAULT_COLOR_UNDEFINE = '#C0C0C0'
  DEFAULT_COLOR_CYCLE = '#FF0000'
  DEFAULT_CONN_IP = '127.0.0.1'
  DEFAULT_CONN_USER = ''
  DEFAULT_CONN_PASSWD = ''
  DEFAULT_CONN_PORT = '5432'
  DEFAULT_CONN_DB = ''
  DEFAULT_CTRL_TABLENAME = 'ctrl.job_exec_log'
  DEFAULT_CTRL_COL_JOBNAME = 'job_name'
  DEFAULT_CTRL_COL_PLANDT = 'plan_dt'
  DEFAULT_CTRL_COL_STATUS = 'status'
  DEFAULT_CTRL_COL_ACTSDT = 'act_sdt'
  DEFAULT_CTRL_COL_ACTEDT = 'act_edt'
  DEFAULT_CTRL_COL_DATANUM = 'data_num'
  DEFAULT_RUN_ON_TIME = True
  COLOR_INITIAL = DEFAULT_COLOR_INITIAL
  COLOR_WAITING = DEFAULT_COLOR_WAITING
  COLOR_RUNNING = DEFAULT_COLOR_RUNNING
  COLOR_SUCCESS = DEFAULT_COLOR_SUCCESS
  COLOR_FAILURE = DEFAULT_COLOR_FAILURE
  COLOR_NOTJOB = DEFAULT_COLOR_NOTJOB
  COLOR_UNDEFINE = DEFAULT_COLOR_UNDEFINE
  CONN_IP = DEFAULT_CONN_IP
  CONN_USER = DEFAULT_CONN_USER
  CONN_PASSWD = DEFAULT_CONN_PASSWD
  CONN_PORT = DEFAULT_CONN_PORT
  CONN_DB = DEFAULT_CONN_DB
  CTRL_TABLENAME = DEFAULT_CTRL_TABLENAME
  CTRL_COL_JOBNAME = DEFAULT_CTRL_COL_JOBNAME
  CTRL_COL_PLANDT = DEFAULT_CTRL_COL_PLANDT
  CTRL_COL_STATUS = DEFAULT_CTRL_COL_STATUS
  CTRL_COL_ACTSDT = DEFAULT_CTRL_COL_ACTSDT
  CTRL_COL_ACTEDT = DEFAULT_CTRL_COL_ACTEDT
  CTRL_COL_DATANUM = DEFAULT_CTRL_COL_DATANUM
  RUN_ON_TIME = DEFAULT_RUN_ON_TIME

  @classmethod
  def set_color_initial(cls, color):
    cls.COLOR_INITIAL = color

  @classmethod
  def set_color_waiting(cls, color):
    cls.COLOR_WAITING = color

  @classmethod
  def set_color_running(cls, color):
    cls.COLOR_RUNNING = color

  @classmethod
  def set_color_success(cls, color):
    cls.COLOR_SUCCESS = color

  @classmethod
  def set_color_failure(cls, color):
    cls.COLOR_FAILURE = color

  @classmethod
  def set_color_notjob(cls, color):
    cls.COLOR_NOTJOB = color

  @classmethod
  def set_color_undefine(cls, color):
    cls.COLOR_UNDEFINE = color

  @classmethod
  def set_conn_ip(cls, value):
    cls.CONN_IP = value

  @classmethod
  def set_conn_user(cls, value):
    cls.CONN_USER = value

  @classmethod
  def set_conn_passwd(cls, value):
    cls.CONN_PASSWD = value

  @classmethod
  def set_conn_port(cls, value):
    cls.CONN_PORT = value

  @classmethod
  def set_conn_db(cls, value):
    cls.CONN_DB = value

  @classmethod
  def set_ctrl_tablename(cls, value):
    cls.CTRL_TABLENAME = value

  @classmethod
  def set_ctrl_jobname(cls, value):
    cls.CTRL_COL_JOBNAME = value

  @classmethod
  def set_ctrl_plandt(cls, value):
    cls.CTRL_COL_PLANDT = value

  @classmethod
  def set_ctrl_status(cls, value):
    cls.CTRL_COL_STATUS = value

  @classmethod
  def set_ctrl_actsdt(cls, value):
    cls.CTRL_COL_ACTSDT = value

  @classmethod
  def set_ctrl_actedt(cls, value):
    cls.CTRL_COL_ACTEDT = value

  @classmethod
  def set_ctrl_datanum(cls, value):
    cls.CTRL_COL_DATANUM = value

  @classmethod
  def set_run_on_time(cls, value):
    cls.RUN_ON_TIME = value

  @staticmethod
  def get_plan_dt_list(obj, freq, job_start_dt, job_end_dt):
    try:
      if re.match('(YYYYMMDD)(\s+)([0-9]{6}$)', freq):
        return JDRUtil.get_plan_dt_YYYYMMDD_HHMMSS(obj, freq, job_start_dt, job_end_dt)
      elif re.match('(YYYYMMDD$)', freq):
        return JDRUtil.get_plan_dt_YYYYMMDD(obj, freq, job_start_dt, job_end_dt)
      elif re.match('(YYYYMM)([0-9]{2})(\s+)([0-9]{6}$)', freq):
        return JDRUtil.get_plan_dt_YYYYMMXX_HHMMSS(obj, freq, job_start_dt, job_end_dt)
      elif re.match('(YYYYMM)([0-9]{2}$)', freq):
        return JDRUtil.get_plan_dt_YYYYMMXX(obj, freq, job_start_dt, job_end_dt)
      elif re.match('(YYYYMM\$\$)(\s+)([0-9]{6}$)', freq):
        return JDRUtil.get_plan_dt_YYYYMMEE_HHMMSS(obj, freq, job_start_dt, job_end_dt)
      elif re.match('(YYYYMM\$\$$)', freq):
        return JDRUtil.get_plan_dt_YYYYMMEE(obj, freq, job_start_dt, job_end_dt)
      elif re.match('(YYYY)([0-9]{4})(\s+)([0-9]{6}$)', freq):
        return JDRUtil.get_plan_dt_YYYYXXXX_HHMMSS(obj, freq, job_start_dt, job_end_dt)
      elif re.match('(YYYY)([0-9]{4}$)', freq):
        return JDRUtil.get_plan_dt_YYYYXXXX(obj, freq, job_start_dt, job_end_dt)
      elif re.match('(YYYY)([0-9]{2})(\$\$)(\s+)([0-9]{6}$)', freq):
        return JDRUtil.get_plan_dt_YYYYXXEE_HHMMSS(obj, freq, job_start_dt, job_end_dt)
      elif re.match('(YYYY)([0-9]{2})(\$\$$)', freq):
        return JDRUtil.get_plan_dt_YYYYXXEE(obj, freq, job_start_dt, job_end_dt)
      elif re.match('([0-9]{8})(\s+)([0-9]{6}$)', freq):
        return JDRUtil.get_plan_dt_XXXXXXXX_HHMMSS(obj, freq, job_start_dt, job_end_dt)
      elif re.match('([0-9]{8}$)', freq):
        return JDRUtil.get_plan_dt_XXXXXXXX(obj, freq, job_start_dt, job_end_dt)
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_list(): freq format error: "{freq}"')
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYMMDD_HHMMSS(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYYMMDD)(\s+)([0-9]{6}$)', freq)
      result = []
      if freq_part and QTime.fromString(freq_part[3], 'hhmmss').isValid():
        start_date = QDate.fromString(job_start_dt, 'yyyyMMdd')
        end_date = QDate.fromString(job_end_dt, 'yyyyMMdd')
        for i in range(start_date.daysTo(end_date) + 1):
          result.append(QDateTime.fromString(start_date.addDays(i).toString('yyyyMMdd'), 'yyyyMMdd').toString(f'yyyyMMdd {freq_part[3]}'))
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYMMDD_HHMMSS(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYMMDD(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYYMMDD$)', freq)
      result = []
      if freq_part:
        start_date = QDate.fromString(job_start_dt, 'yyyyMMdd')
        end_date = QDate.fromString(job_end_dt, 'yyyyMMdd')
        for i in range(start_date.daysTo(end_date) + 1):
          result.append(QDateTime.fromString(start_date.addDays(i).toString('yyyyMMdd'), 'yyyyMMdd').toString('yyyyMMdd hhmmss'))
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYMMDD(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYMMXX_HHMMSS(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYYMM)([0-9]{2})(\s+)([0-9]{6}$)', freq)
      result = []
      if freq_part and QTime.fromString(freq_part[4], 'hhmmss').isValid():
        yyyymm_iter = int(job_start_dt[0:6])
        yyyymm_date = int(str(yyyymm_iter) + freq_part[2])
        while yyyymm_date <= int(job_end_dt):
          if yyyymm_date >= int(job_start_dt) and QDate.fromString(str(yyyymm_date), 'yyyyMMdd').isValid():
            result.append(QDateTime.fromString(str(yyyymm_date), 'yyyyMMdd').toString(f'yyyyMMdd {freq_part[4]}'))
          if yyyymm_iter % 100 == 12:
            yyyymm_iter += 89
          else:
            yyyymm_iter += 1
          yyyymm_date = int(str(yyyymm_iter) + freq_part[2])
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYMMXX_HHMMSS(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYMMXX(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYYMM)([0-9]{2}$)', freq)
      result = []
      if freq_part:
        yyyymm_iter = int(job_start_dt[0:6])
        yyyymm_date = int(str(yyyymm_iter) + freq_part[2])
        while yyyymm_date <= int(job_end_dt):
          if yyyymm_date >= int(job_start_dt) and QDate.fromString(str(yyyymm_date), 'yyyyMMdd').isValid():
            result.append(QDateTime.fromString(str(yyyymm_date), 'yyyyMMdd').toString('yyyyMMdd hhmmss'))
          if yyyymm_iter % 100 == 12:
            yyyymm_iter += 89
          else:
            yyyymm_iter += 1
          yyyymm_date = int(str(yyyymm_iter) + freq_part[2])
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYMMXX(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYMMEE_HHMMSS(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYYMM\$\$)(\s+)([0-9]{6}$)', freq)
      result = []
      if freq_part and QTime.fromString(freq_part[3], 'hhmmss').isValid():
        yyyymm_iter = int(job_start_dt[0:6])
        end_date = QDate.fromString(str(yyyymm_iter), 'yyyyMM').daysInMonth()
        yyyymm_date = yyyymm_iter * 100 + end_date
        while yyyymm_date <= int(job_end_dt):
          if yyyymm_date >= int(job_start_dt) and QDate.fromString(str(yyyymm_date), 'yyyyMMdd').isValid():
            result.append(QDateTime.fromString(str(yyyymm_date), 'yyyyMMdd').toString(f'yyyyMMdd {freq_part[3]}'))
          if yyyymm_iter % 100 == 12:
            yyyymm_iter += 89
          else:
            yyyymm_iter += 1
          end_date = QDate.fromString(str(yyyymm_iter), 'yyyyMM').daysInMonth()
          yyyymm_date = yyyymm_iter * 100 + end_date
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYMMEE_HHMMSS(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYMMEE(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYYMM\$\$$)', freq)
      result = []
      if freq_part:
        yyyymm_iter = int(job_start_dt[0:6])
        end_date = QDate.fromString(str(yyyymm_iter), 'yyyyMM').daysInMonth()
        yyyymm_date = yyyymm_iter * 100 + end_date
        while yyyymm_date <= int(job_end_dt):
          if yyyymm_date >= int(job_start_dt) and QDate.fromString(str(yyyymm_date), 'yyyyMMdd').isValid():
            result.append(QDateTime.fromString(str(yyyymm_date), 'yyyyMMdd').toString('yyyyMMdd hhmmss'))
          if yyyymm_iter % 100 == 12:
            yyyymm_iter += 89
          else:
            yyyymm_iter += 1
          end_date = QDate.fromString(str(yyyymm_iter), 'yyyyMM').daysInMonth()
          yyyymm_date = yyyymm_iter * 100 + end_date
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYMMEE(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYXXXX_HHMMSS(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYY)([0-9]{4})(\s+)([0-9]{6}$)', freq)
      result = []
      if freq_part and QTime.fromString(freq_part[4], 'hhmmss').isValid():
        yyyy_iter = int(job_start_dt[0:4])
        yyyy_date = int(str(yyyy_iter) + freq_part[2])
        while yyyy_date <= int(job_end_dt):
          if yyyy_date >= int(job_start_dt) and QDate.fromString(str(yyyy_date), 'yyyyMMdd').isValid():
            result.append(QDateTime.fromString(str(yyyy_date), 'yyyyMMdd').toString(f'yyyyMMdd {freq_part[4]}'))
          yyyy_iter += 1
          yyyy_date = int(str(yyyy_iter) + freq_part[2])
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYXXXX_HHMMSS(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYXXXX(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYY)([0-9]{4}$)', freq)
      result = []
      if freq_part:
        yyyy_iter = int(job_start_dt[0:4])
        yyyy_date = int(str(yyyy_iter) + freq_part[2])
        while yyyy_date <= int(job_end_dt):
          if yyyy_date >= int(job_start_dt) and QDate.fromString(str(yyyy_date), 'yyyyMMdd').isValid():
            result.append(QDateTime.fromString(str(yyyy_date), 'yyyyMMdd').toString('yyyyMMdd hhmmss'))
          yyyy_iter += 1
          yyyy_date = int(str(yyyy_iter) + freq_part[2])
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYXXXX(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYXXEE_HHMMSS(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYY)([0-9]{2})(\$\$)(\s+)([0-9]{6}$)', freq)
      result = []
      if freq_part and QTime.fromString(freq_part[5], 'hhmmss').isValid():
        yyyy_iter = int(job_start_dt[0:4])
        mm = freq_part[2]
        end_date = QDate.fromString(str(yyyy_iter) + mm, 'yyyyMM').daysInMonth()
        yyyy_date = yyyy_iter * 10000 + int(mm) * 100 + end_date
        while yyyy_date <= int(job_end_dt):
          if yyyy_date >= int(job_start_dt) and QDate.fromString(str(yyyy_date), 'yyyyMMdd').isValid():
            result.append(QDateTime.fromString(str(yyyy_date), 'yyyyMMdd').toString(f'yyyyMMdd {freq_part[5]}'))
          yyyy_iter += 1
          end_date = QDate.fromString(str(yyyy_iter) + mm, 'yyyyMM').daysInMonth()
          yyyy_date = yyyy_iter * 10000 + int(mm) * 100 + end_date
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYXXEE_HHMMSS(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_YYYYXXEE(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('(YYYY)([0-9]{2})(\$\$$)', freq)
      result = []
      if freq_part:
        yyyy_iter = int(job_start_dt[0:4])
        mm = freq_part[2]
        end_date = QDate.fromString(str(yyyy_iter) + mm, 'yyyyMM').daysInMonth()
        yyyy_date = yyyy_iter * 10000 + int(mm) * 100 + end_date
        while yyyy_date <= int(job_end_dt):
          if yyyy_date >= int(job_start_dt) and QDate.fromString(str(yyyy_date), 'yyyyMMdd').isValid():
            result.append(QDateTime.fromString(str(yyyy_date), 'yyyyMMdd').toString('yyyyMMdd hhmmss'))
          yyyy_iter += 1
          end_date = QDate.fromString(str(yyyy_iter) + mm, 'yyyyMM').daysInMonth()
          yyyy_date = yyyy_iter * 10000 + int(mm) * 100 + end_date
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_YYYYXXEE(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_XXXXXXXX_HHMMSS(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('([0-9]{8})(\s+)([0-9]{6}$)', freq)
      result = []
      if freq_part and QTime.fromString(freq_part[3], 'hhmmss').isValid():
        yyyymmdd_date = int(freq_part[1])
        if yyyymmdd_date >= int(job_start_dt) and yyyymmdd_date <= int(job_end_dt) and QDate.fromString(str(yyyymmdd_date), 'yyyyMMdd').isValid():
          result.append(QDateTime.fromString(str(yyyymmdd_date), 'yyyyMMdd').toString(f'yyyyMMdd {freq_part[3]}'))
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_XXXXXXXX_HHMMSS(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def get_plan_dt_XXXXXXXX(obj, freq, job_start_dt, job_end_dt):
    try:
      freq_part = re.match('([0-9]{8}$)', freq)
      result = []
      if freq_part:
        yyyymmdd_date = int(freq_part[1])
        if yyyymmdd_date >= int(job_start_dt) and yyyymmdd_date <= int(job_end_dt) and QDate.fromString(str(yyyymmdd_date), 'yyyyMMdd').isValid():
          result.append(QDateTime.fromString(str(yyyymmdd_date), 'yyyyMMdd').toString('yyyyMMdd hhmmss'))
      else:
        raise ValueError(f'JDRUtil.get_plan_dt_XXXXXXXX(): freq format error: "{freq}"')
      return result
    except ValueError as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return False

  @staticmethod
  def test_conn_postgresql(obj, show_sucess):
    JDRUtil.set_conn_ip(obj.setup_widget2_conn_ip_lineedit.text())
    JDRUtil.set_conn_user(obj.setup_widget2_conn_user_lineedit.text())
    JDRUtil.set_conn_passwd(obj.setup_widget2_conn_passwd_lineedit.text())
    JDRUtil.set_conn_port(obj.setup_widget2_conn_port_lineedit.text())
    JDRUtil.set_conn_db(obj.setup_widget2_conn_db_lineedit.text())
    try:
      JDRUtil.write_log(obj, f'test_conn_postgresql(): try to get DB connection...', 0)
      conn = psycopg2.connect(database=f'{JDRUtil.CONN_DB}', user=f'{JDRUtil.CONN_USER}', password=f'{JDRUtil.CONN_PASSWD}', host=f'{JDRUtil.CONN_IP}', port=f'{JDRUtil.CONN_PORT}', connect_timeout=1)
      conn.close()
      if show_sucess == True:
        JDRUtil.write_log(obj, f'DB connection success.', 1)
        JDRUtil.write_log(obj, f'CONN_USER = {JDRUtil.CONN_USER}', 1)
        JDRUtil.write_log(obj, f'CONN_IP = {JDRUtil.CONN_IP}', 1)
        JDRUtil.write_log(obj, f'CONN_PORT = {JDRUtil.CONN_PORT}', 1)
        JDRUtil.write_log(obj, f'CONN_DB = {JDRUtil.CONN_DB}', 1)
      return True
    except:
      JDRUtil.write_log(obj, f'[Error]: DB connection error. Please check your setup:', 2)
      JDRUtil.write_log(obj, f'CONN_USER = {JDRUtil.CONN_USER}', 2)
      JDRUtil.write_log(obj, f'CONN_IP = {JDRUtil.CONN_IP}', 2)
      JDRUtil.write_log(obj, f'CONN_PORT = {JDRUtil.CONN_PORT}', 2)
      JDRUtil.write_log(obj, f'CONN_DB = {JDRUtil.CONN_DB}', 2)
      return False

  @staticmethod
  def get_exec_cfg_by_key(obj, keys):
    try:
      conn = None
      if len(keys) == 0:
        return
      jobs = str([key.split('.') for key in keys]).replace('[','(').replace(']',')')[1:-1]
      sql = f'''
        select job_name || '.' || to_char(plan_dt, 'YYYYMMDD HH24MISS') as job_key, status, act_sdt, act_edt, data_num, dur from (
          select job_name, plan_dt, status, act_sdt, act_edt, data_num, extract(epoch from act_edt - act_sdt)::int dur, row_number() over (partition by job_name, plan_dt order by act_sdt desc) r from (
            select {JDRUtil.CTRL_COL_JOBNAME} as job_name, {JDRUtil.CTRL_COL_PLANDT} as plan_dt, {JDRUtil.CTRL_COL_STATUS} as status, {JDRUtil.CTRL_COL_ACTSDT} as act_sdt, {JDRUtil.CTRL_COL_ACTEDT} as act_edt, {JDRUtil.CTRL_COL_DATANUM} as data_num
            from {JDRUtil.CTRL_TABLENAME}
          ) as t0
          join (values {jobs}) as t1 (job, plan)
          on job = job_name and plan::timestamp = plan_dt
        ) as t2
        where r = 1
      '''
      conn = psycopg2.connect(database = f'{JDRUtil.CONN_DB}', user = f'{JDRUtil.CONN_USER}', password = f'{JDRUtil.CONN_PASSWD}', host = f'{JDRUtil.CONN_IP}', port = f'{JDRUtil.CONN_PORT}')
      cursor = conn.cursor()
      cursor.execute(sql)
      rows = cursor.fetchall()
      for row in rows:
        job_key = str(row[0])
        obj.exec_cfg[job_key, 'status'] = str(row[1])
        obj.exec_cfg[job_key, 'act_sdt'] = str(row[2])
        obj.exec_cfg[job_key, 'act_edt'] = str(row[3])
        obj.exec_cfg[job_key, 'data_num'] = str(row[4])
        obj.exec_cfg[job_key, 'dur'] = str(row[5])
    except Exception as e:
      JDRUtil.write_log(obj, f'{repr(e)}', 2)
      return {}
    finally:
      if conn:
        cursor.close()
        conn.close()

  @staticmethod
  def write_log(obj, msg, type):
    ## type: 0-normal  1-important  2-abnormal
    font_size = 8
    font_weight = 500
    if type == 0:
      color = '#000000'  # black
    elif type == 1:
      color = '#0000FF'  # blue
    elif type == 2:
      color = '#FF0000'  # red
    cur_time = QDateTime().currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
    obj.log_textedit.append(f'<span style="color:{color}; font-size:{font_size}pt; font-weight:{font_weight};">[{cur_time}] {msg}</span>')
