# -*- coding: utf-8 -*-

import os
import sys
import string
import MySQLdb
import re
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from enum import Enum
import smtplib
import datetime

class Reportlevel(Enum):
    Warning = 0
    Error = 1
    Fatal = 2


class Logmanager(object):
    def __init__(self, config):
        self.host = 'localhost'
        self.port = 3306
        self.user = 'root'
        self.passwd = 'password'
        self.db = 'data_log'
        self.table = 'log'
        if 'port' in config:
            self.port = config['port']
        elif 'user' in config:
            self.user = config['user']
        elif 'passwd' in config:
            self.passwd = config['passwd']
        elif 'db' in config:
            self.db = config['db']
        elif 'table' in config:
            self.table = config['table']

    def Conn(self, sql, v):
        conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        cur = conn.cursor()
        if v:
            cur.execute(sql, v)
        else:
            cur.execute(sql)
        conn.commit()
        alldata = cur.fetchall()
        if alldata:
            for row in alldata:
                print("".join(row))
        conn.close()
        return alldata

    def Connnoprint(self, sql, v):
        conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        cur = conn.cursor()
        if v:
            cur.execute(sql, v)
        else:
            cur.execute(sql)
        conn.commit()
        alldata = cur.fetchall()
        conn.close()
        return alldata

    def Initdb(self):
        sql = "create database if not exists " + self.db
        v = []
        self.Conn(sql, v)
        print("Successfully create DB")

    def Createsummary(self, config):
        if 'period' in config:#有period字段表示某天或某几天，没有表示当天
            date = re.compile(r'^[0-9]{8}$')
            result = date.search(config['period'])
            if result:
                time_start = config['period'] + '000000000000'
                time_end = config['period'] + '235959000000'
            else:
                time_start = config['period'][:8] + '000000000000'
                time_end = config['period'][-8:] + '235959000000'
            current_date = config['period']
        else:
            time_end = (datetime.date.today()).strftime("%Y%m%d") + '235959000000'
            time_start = (datetime.date.today()).strftime("%Y%m%d") + '000000000000'
            current_date = (datetime.date.today()).strftime("%Y%m%d")
        v = []
        Errormessage = "Summary for " + current_date + " log:\nIndividual device:\n"
        str_who = ''

        sql_device = "select distinct Who from " + self.table + " where Date< " + time_end + " and Date >" + time_start + " and Device_or_user =1"
        devices = self.Connnoprint(sql_device, v)
        for row in devices:
            str_who = row.__str__().replace('\'', '').replace('(', '').replace(')', '').replace(',', '').replace(' ',
                                                                                                                 '')
            Errormessage = Errormessage + "device:" + str_who + "\n"
            sql_select_who = "select Date,Requestmethod,Accessmode,Who from " + self.table + " where Who= \'" + str_who + "\' and Date<" + time_end + " and Date>" + time_start + ""
            devices_separate = self.Connnoprint(sql_select_who, v)
            for line in devices_separate:
                Errormessage = Errormessage + str(line) + "\n"
            sql_who_error = "select Detail from " + self.table + " where Date< " + time_end + " and Date> " + time_start + " and Detail like '%Error%' and Who= \'" + str_who + "\'"
            devices_error = self.Connnoprint(sql_who_error, v)
            if devices_error:
                Errormessage = Errormessage + "Error message:\n"
                for line in devices_error:
                    Errormessage = Errormessage + line[0]

        sql_user = "select distinct who from " + self.table + " where Date<" + time_end + " and Date>" + time_start + " and Device_or_user =0"
        users = self.Connnoprint(sql_user, v)
        Errormessage = Errormessage + "Individual user:\n"
        for row in users:
            str_who = row.__str__().replace('\'', '').replace('(', '').replace(')', '').replace(',', '').replace(' ',
                                                                                                                 '')
            if str_who != 'None':
                Errormessage = Errormessage + "user:" + str_who + "\n"
                sql_select_who = "select Date,Requestmethod,Accessmode,Who from " + self.table + " where Who= \'" + str_who + "\' and Date<" + time_end + " and Date>" + time_start + ""
                users_separate = self.Connnoprint(sql_select_who, v)
                for line in users_separate:
                    Errormessage = Errormessage + str(line) + "\n"
                sql_who_error = "select Detail from " + self.table + " where Date<" + time_end + " and Date> " + time_start + " and Detail like '%Error%' and Who= \'" + str_who + "\'"
                users_error = self.Connnoprint(sql_who_error, v)
                if users_error:
                    Errormessage = Errormessage + "Error message:\n"
                    for line in users_error:
                        Errormessage = Errormessage + line[0]
        Errormessage = Errormessage
        header = "Summary for " + current_date + "'s log"
        self.Sendmail(Errormessage, header, config)

    def Createtable(self):
        sql = "create table if not exists " + self.table + "(Sign varchar(2),Detail mediumblob,Date varchar(20),IPaddress varchar(20),Accessmode varchar(255),Requestmethod varchar(20),Device_or_user boolean,Who varchar(20))"
        v = []
        self.Conn(sql, v)
        print("Successfully create table")
    def Set_max_allowed_packet(self,config):
        sql="set global max_allowed_packet=%s"
        v=config['max_allowed_packet']*1024*1024
        self.Conn(sql,v)
        print v
        print ("Successfully set")
    def Deletedata(self):
        sql = "truncate table " + self.table + ";"
        v = []
        self.Conn(sql, v)
        print("Successfully delete")

    def Email(self, config):
        LatestDate = self.Latestdate()
        if config['level'] == Reportlevel.Warning.value:
            sql = "select Detail from " + self.table + " where (Date > " + LatestDate + " and Detail like '%W, [%') or (Date > " + LatestDate + " and Detail like '%FATAL%') or (Detail like '%E, [%' and Date > " + LatestDate + ")"
            self.Fetch_Error(config, sql)
        elif config['level'] == Reportlevel.Error.value:
            sql = "select Detail from " + self.table + " where (Date > " + LatestDate + " and Detail like '%FATAL%') or (Detail like '%E, [%' and Date > " + LatestDate + ")"
            self.Fetch_Error(config, sql)
        else:
            sql = "select Detail from " + self.table + " where Date > " + LatestDate + " and Detail like '%FATAL%'"
            self.Fetch_Error(config, sql)

    def Fetch_Error(self, config, sql):
        self.Processlog(config)
        v = []
        Errormsg = ''
        header = 'Error in log'
        result = self.Connnoprint(sql, v)
        for row in result:
            Errormsg = Errormsg + row[0]
        if result:
            self.Sendmail(Errormsg, header,config)
        else:
            print('no new Error')

    def Sendmail(self, Errormsg, header, config):
        def _format_addr(s):
            name, addr = parseaddr(s)
            return formataddr(( \
                Header(name, 'utf-8').encode(), \
                addr.encode('utf-8') if isinstance(addr, unicode)else addr))

        from_addr = 'ruixinli@netrohome.com'
        password = '15035040929Lrx'
        to_addr = config['email']
        smtp_server = 'smtp.exmail.qq.com'
        msg = MIMEText(Errormsg, 'plain', 'utf-8')
        msg['From'] = _format_addr('LOG program')
        msg['To'] = _format_addr('%s' % to_addr)
        msg['Subject'] = Header(header, 'utf-8').encode()

        server = smtplib.SMTP(smtp_server, 25)
        server.starttls()
        # server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()

    def Latestdate(self):
        sql = "select max(Date) from " + self.table
        v = []
        result = self.Connnoprint(sql, v)
        text = result.__str__()
        MaxDate = text.replace(',', '').replace('(', '').replace(')', '').replace('\'', '')
        if MaxDate == 'None':
            MaxDate = '10000000000000000000'
        return MaxDate

    def Processlog(self, config):
        LatestDate = self.Latestdate()
        input = open(config['log_file'], 'r')
        my_str = ''
        i = 0
        last_date = ''
        sql_insert_user_device = 'insert into ' + self.table + '(Requestmethod,Accessmode,IPaddress,Date)values'# true是device false是user
        sql_update_detail = "update " + self.table + " set Detail=case Date"
        sql_update_who="Who=case Date"
        sql_update_deviceoruser="device_or_user=case Date"
        IPaddr = re.compile(r'^(\d{1,3}\.){3}(\d{1,3})$')
        IP_dict = {}
        IP = ''
        flag_user_device=0
        device_name=''
        v_insert_user_device = []
        v_update_detail = []
        v_update_deviceoruser=[]
        v_update_who = []
        v_detail_date = ''
        v_who_date = ''
        v_deviceoruser_date=''
        user_name=''
        time_str=''
        for line in input:
            f = line.split()
            if 'Started' in line:
                time_str = f[1].replace('[', '').replace('-', '').replace(':', '').replace('.', '').replace('T', '')
                if time_str > LatestDate or LatestDate == 'None':
                    i = i + 1
                    if f[6] == "Started":
                        sql_insert_user_device = sql_insert_user_device + '(%s,%s,%s,%s),'
                        v_insert_user_device.extend([f[7], f[8], f[10], time_str])
                    else:
                        sql_insert_user_device = sql_insert_user_device + '(%s,%s,%s,%s),'
                        v_insert_user_device.extend([f[8], f[9], f[11], time_str])
                    if i > 1:
                        sql_update_detail = sql_update_detail + ' when %s then %s '
                        v_update_detail.extend([last_date, my_str])#lastdate与mystr一一对应
                        v_detail_date = v_detail_date + last_date + ','

                        sql_update_deviceoruser=sql_update_deviceoruser+' when %s then %s '
                        v_update_deviceoruser.extend([last_date,flag_user_device])
                        v_deviceoruser_date=v_deviceoruser_date+last_date+','

                        if IP_dict.get(IP) and not flag_user_device:#判断是user还是device，也可以不用flag：用字典存放device_name和last_date
                            sql_update_who = sql_update_who + ' when %s then %s '
                            v_update_who.extend([last_date, IP_dict[IP]])
                            v_who_date = v_who_date + last_date + ','
                        if flag_user_device:
                            sql_update_who=sql_update_who+' when %s then %s '
                            v_update_who.extend([last_date,device_name])
                            v_who_date=v_who_date+last_date+','

                        flag_new=flag_user_device#每900个执行一次的时候赋值
                        flag_user_device=0#一个transaction用过以后就重新赋值，不能在started对应的else中赋值（每个line都会进入started对应的else)
                        if not i % config['num_transactions']:#每900个语句执行一次
                            sql_update_3=''
                            v_update_3=[]
                            v_date_3=''

                            sql_insert_user_device = sql_insert_user_device[:-1] + ';'
                            self.Conn(sql_insert_user_device, v_insert_user_device)
                            sql_insert_user_device = 'insert into ' + self.table + '(Requestmethod,Accessmode,IPaddress,Date)values'
                            v_insert_user_device = []

                            sql_update_detail = sql_update_detail + 'end,'
                            sql_update_3 = sql_update_detail
                            v_update_3 = v_update_detail
                            v_date_3=v_detail_date[:-1]
                            sql_update_detail = "update "+self.table+" set detail=case Date when %s then %s"
                            v_update_detail = []
                            v_update_detail.extend([last_date, my_str])  # 前899个（0-898）写进库，补上本次（899）的transaction
                            v_detail_date = ''
                            v_detail_date = v_detail_date + last_date + ','

                            sql_update_who=sql_update_who+'end,'
                            sql_update_3 = sql_update_3 + sql_update_who
                            v_update_3.extend(v_update_who)
                            sql_update_who = "Who=case Date"
                            v_update_who = []
                            v_who_date = ''

                            sql_update_deviceoruser=sql_update_deviceoruser+' end where Date in ('+v_date_3+'); '
                            sql_update_3 = sql_update_3 + sql_update_deviceoruser
                            v_update_3.extend(v_update_deviceoruser)
                            sql_update_deviceoruser="device_or_user=case Date when %s then %s "
                            v_update_deviceoruser=[]
                            v_update_deviceoruser.extend([last_date,flag_new])
                            v_deviceoruser_date=''
                            v_deviceoruser_date=v_deviceoruser_date+last_date+','

                            self.Conn(sql_update_3,v_update_3)
                        my_str = ''
                    search_IP = IPaddr.search(f[10])
                    if search_IP:
                        IP = f[10]
                    else:
                        IP = f[11]
                    last_date = time_str
                    my_str = my_str + line
                else:
                    my_str = ''
            else:
                if time_str > LatestDate or LatestDate == 'None':#对比新的transaction的时间与库中最大date值，除首句（started）外其他句子也要删去
                    my_str = my_str + line
                    if "Parameters:" in line:
                        for j in f:
                            if "\"serial\"=>" in j:
                                device_name=j.split("\"")[3]
                                flag_user_device=1
                                break#有些transaction的parameter有name和serial number
                            if "\"name\"=>" in j:
                                user_name = j.split("\"")[3]
                                IP_dict[IP] = user_name#IP地址与user对应放在字典中
                                break#有些transaction的

        if i>0:
            sql_update_3 = ''
            v_update_3 = []
            v_date_3 = ''

            sql_insert_user_device = sql_insert_user_device[:-1] + ';'
            self.Conn(sql_insert_user_device, v_insert_user_device)

            v_detail_date = v_detail_date + last_date
            v_update_detail.extend([last_date, my_str])
            sql_update_3=sql_update_detail+'when %s then %s end,'
            v_update_3=v_update_detail
            v_date_3=v_detail_date

            if not flag_user_device:
                sql_update_who = sql_update_who + ' when %s then %s '
                v_update_who.extend([last_date, user_name])#一个transaction无法向前追溯user_name
                v_who_date = v_who_date + last_date + ','
            if flag_user_device:
                sql_update_who = sql_update_who + ' when %s then %s '
                v_update_who.extend([last_date, device_name])
                v_who_date = v_who_date + last_date + ','

            v_who_date=v_who_date+last_date
            sql_update_3=sql_update_3+sql_update_who+'end,'
            v_update_3.extend(v_update_who)

            v_deviceoruser_date=v_deviceoruser_date+last_date
            sql_update_3=sql_update_3+sql_update_deviceoruser+'when %s then %s end where Date in ('+v_date_3+'); '
            v_update_deviceoruser.extend([last_date,flag_new])
            v_update_3.extend(v_update_deviceoruser)
            self.Conn(sql_update_3,v_update_3)








