#-*- coding: utf-8 -*-
###############################################################################
# This script is for Logmanager

###############################################################################
import LogManager

class Funtions(object):
    # #所有可以修改的DB属性，config中为默认值
    # config={'host':'localhost','port':3306,'user':'root','passwd':'password','db':'data_log','table':'log_2'}
    # #插入数据
     #lm = auto_report.Logmanager(config)
    # config={'log_file':'/Users/huangkaiping/Downloads/production.log','passwd':'123456'}#插入数据，DB密码为123456，更改DB的参数和表名时在config中添加要更改的属性。
    # lm.Insertlog(config)
    # #通过邮件发送某一天或几天的报告
    # #只发送当天的报告不需要写period字段,单独某天写20170408，某几天的情况写20170408-20170410
    #
    # config={'email':'18910931590@163.com','period':'20170321'}
    # lm=auto_report.Logmanager(config)
    # lm.Createsummary(config)
    # #将log数据更新写入数据库，并且通过邮件发送产生的错误的报告。
    # config = {'log_file': 'D:/netro/test.log','level': '1', 'email': '18910931590@163.com'}
    # lm = LogManager.Logmanager(config)
    # lm.Email(config)

    # #将log数据更新写入数据库
    # config={'log_file':'/Users/huangkaiping/Downloads/test.txt'}
    # lm.Processlog(config)
    # #创建数据库
    # config={'db':'data_log_new'}
    # lm.Initdb()
    # #创建表或清空表
    # config={'table':'log_new'}
    # lm.Createtable(config)
    # lm.Deletedata(config)
    #config={'log_file':'/Users/huangkaiping/Downloads/production.log','table':'log_2'}
    #lm = LogManager.Logmanager(config)
    #lm.Processlog(config)
    # config={'max_allowed_packet':8}#设置mysql的max_allowed_packet,单位是M
    # lm=LogManager.Logmanager(config)
    # lm.Set_max_allowed_packet(config)
    config={'log_file':'D:/netro/production.log','table':'log','num_transactions':2200}
    lm=LogManager.Logmanager(config)
    lm.Processlog(config)