# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.db import models
import os
import sys
import re
import time, datetime
# glob模块是最简单的模块之一，内容非常少。用它可以查找符合特定规则的文件路径名
import glob
from access.models import DailyAccess,DailyAppCount
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    login_dir_type = 0
    save_count = 0

    def file_rename(self, path):
        file_list = glob.glob(path + '*.gz')
        if len(file_list) > 0 : 
            for f in file_list:
                filename = f.split('/')[-1]
                name = filename.split('.')
                if len(name) > 4:
                    new_name = name[0] + '.' + name[1] + '.' + name[2] + '.' + name[4] + '.' + name[3]
                elif len(name) == 4:
                    new_name = name[0] + '.' + name[2] + '.' + name[1]
                os.system("gunzip %s" % f)
                file_without_gz = filename[:-3]
                os.system("mv %s %s" % (path + file_without_gz,path + new_name))
        list_log = glob.glob(path + '*.log')
        if len(list_log) > 0:
            return list_log

   


    def handle_log(self, log_file):
        ip = r"?P<ip>[\d.]*"
        date = r"?P<date>\d+"
        month = r"?P<month>\S+"
        year = r"?P<year>\d+"
        log_time = r"?P<time>\S+"
        method = r"?P<method>\S+"
        request = r"?P<request>\S+"
        status = r"?P<status>\d+"
        bodyBytesSent = r"?P<bodyBytesSent>\d+"
        refer = r"""?P<refer>
                 [^\"]*
                 """
        userAgent = r"""?P<userAgent>
                    [^\"]*
                   """
        forwardr = r"""?P<forwardr>
                    [^\"]*
                   """
        request_time = r"""?P<request_time>
                    [^\"]*
                   """
        response_time = r"""?P<response_time>
                    [^\"]*
                   """
        p = re.compile(
            r"(%s)\ -\ -\ \[(%s)/(%s)/(%s)\:(%s)\ [\S]+\]\ \"(%s)?[\s]?(%s)?.*?\"\ (%s)\ (%s)\ \"(%s)\"\ \"(%s)\"" % (
                ip, date, month, year, log_time, method, request, status, bodyBytesSent, refer, userAgent), re.VERBOSE)
        s = time.time()
        userSystems = re.compile(r'\([^\(\)]*\)')
        if os.path.isdir(log_file) == True:
            self.dir_save(log_file, p, userSystems)
        else:
            self.file_save(log_file, p, userSystems)


    def dir_save(self, dirname, p, userSystems):
        file_list = self.file_rename(dirname)
        for file_one in file_list:
            self.file_save(file_one, p, userSystems)

    #修改增加app应用的访问次数
    def file_save(self, file_name, p, userSystems):
        f = open(file_name, 'r')
        for line in f.readlines():
            self.record_data(p, line, userSystems,file_name)
        f.close()

    def check_browser(self, parame):
        browser = parame[10].split(' ')[0]
        if re.search(r'Macintosh', str(parame[10])) != None:
            browse = 'Mozilla/5.0 on Macintosh'
        elif re.search(r'Windows NT',str(parame[10])) != None:
            browse = browser + 'windows NT'
        else :
            browse = parame[10].split('(')[0]
            if browse.startswith("Mozilla") == False:
                browse = parame[10]
        return browse
        
    def check_refe(self, parame):
        refe = parame[9]
        if len(refe) > 250:
            refe = refe[:250]
        return refe

    def check_logType(self, os_list):
        login_type = 0
        if len(os_list) > 0:
            if re.search(r'Linux', str(os_list[0])) != None:
                login_type = 1
            elif re.search(r'iPhone', str(os_list[0])) != None:
                login_type = 2
            else:
                login_type = 0
        return login_type

    def check_path(self,path):
        if path == "":
            path = "empty"
        return path

    def record_data(self, p, line, userSystems,file_name):
        m = p.match(line)
        appName = file_name.split('.')[1]
        if m != None:
            parame = m.groups()
            date_time = parame[3] + '-' + parame[2] + '-' + parame[1] + ' ' + parame[4]
            date_time_formate = datetime.datetime.strptime(date_time, '%Y-%b-%d %H:%M:%S')
            method = parame[5][:3]
            browser = self.check_browser(parame)
            os_list = userSystems.findall(parame[10])
            refe = self.check_refe(parame)
            login_type = self.check_logType(os_list)
            pathCheck = self.check_path(parame[6])
            daily = DailyAccess(ip=parame[0], status=parame[7], send_byte=parame[8], method=method,
                                accessTime=date_time_formate, path=pathCheck, refe=refe, access_type=login_type,
                                access_record=line, browse=browser,appName=appName)
            daily.save()

            self.save_count += 1

    def handle(self, *args, **options):
        print 'do'
        if len(sys.argv) == 2:
            self.handle_log('/var/data/log/')
        else:
            self.handle_log(sys.argv[2])




