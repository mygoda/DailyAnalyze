# coding=utf-8
import os
import sys
import re
import glob
import socket
import time
import logging
import urllib2
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.db import models
from access.models import DailyPath
# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def get_url_list(self, url):
        while True:
            logger.debug('get url list')
            req = urllib2.Request(url)
            response_page = urllib2.urlopen(req)
            assert isinstance(response_page, object)
            parser = BeautifulSoup(response_page)
            file_list = parser.find('pre').findAll('a')
            url_list = []
            if len(file_list) > 0:
                del file_list[0]
            for file_name in file_list:
                save_file_name = file_name.get('href')
                download_url = os.path.join(url[0:-1], save_file_name)
                url_list.append(download_url)
            if len(url_list) > 0:
                return url_list
                break

    def restart_download(self, downlist, dir_name, i=0):
        try:
            logger.debug('restart')
            restart_list = downlist
            for download_url in downlist[i:]:
                i = self.record_data(download_url, dir_name, i)
        except (urllib2.URLError, IOError, urllib2.HTTPError):
            logger.error("抓取出现问题！")
            time.sleep(1)
            self.restart_download(restart_list,dir_name, i)
            

    def startDown(self, url, dir_name, i=0):
        while True:
            try:
                logger.debug("开始抓取！")
                start_download_list = self.get_url_list(url)
                count = len(start_download_list)
                for download_url in start_download_list:
                    i = self.record_data(download_url, dir_name, i)
                if i == count:
                    break
            except (urllib2.URLError, IOError, urllib2.HTTPError):
                logger.error("抓取出现问题")
                self.restart_download(start_download_list, dir_name, i)


    def record_data(self, download_url, dir_name, i=0):
        f = urllib2.urlopen(download_url)
        save_file_name = os.path.basename(download_url)
        data = f.read()
        local = os.path.join(dir_name, save_file_name)
        with open(local, "wb") as code:
            code.write(data)
            i += 1
        logger.debug("第 %s 个完成抓取" % i )
        return i


    def handle(self, *args, **options):
        socket.setdefaulttimeout(5)
        serverList = DailyPath.objects.all()
        for server in serverList:
            savePath = '/var/data/log/'
            if os.path.exists(savePath) == False:
                os.mkdir(savePath)
            self.startDown(server.path, savePath)



