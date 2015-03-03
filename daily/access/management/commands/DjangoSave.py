#coding=utf-8
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
	
	def get_url_list(self,url):
    	while True:
			logger.info('get url list')
			req = urllib2.Request(url)
    		response_page = urllib2.urlopen(req)
    		assert isinstance(response_page, object)
    		parser = BeautifulSoup(response_page)
    		file_list = parser.find('pre').findAll('a')
			url_list = []
			if len(file_list) > 0 :
	    		del file_list[0]
	    		for file_name in file_list:
                	save_file_name = file_name.get('href')
	        		download_url = os.path.join(url[0:-1],save_file_name)
					url_list.append(download_url)
			if len(url_list) > 0 :
	    		return url_list
	    		break
	
	def restart_download(self,downlist,i=0):
    	try:
			logger.info('restart')
        	for download_url in downlist[i:]:
            	i = self.record_data(download_url)
	    		logger.info(local + '   save_compete')
            return 1 
    	except (urllib2.URLError,IOError,urllib2.HTTPError):
	    	time.sleep(1)
			restart_download(downlist,i)   
	
	def startDown(self,url,dir_name,i=0):
		while True:
		    try:
		        download_list = get_url_list(url)
				for download_url in download_list:
					i = self.record_data(download_url)
				if i == count:
					break
			except (urllib2.URLError,IOError,urllib2.HTTPError):
		        restart_download(download_list,i)      
	
	def record_data(self,download_url,i=0):
		f = urllib2.urlopen(download_url)
		save_file_name = os.path.basename(download_url)
		data = f.read()
		local = os.path.join(dir_name,save_file_name) 
		with open(local, "wb") as code:     
			code.write(data)
		i += 1 
		return i  

	def handle(self, *args, **options):
		socket.setdefaulttimeout(5)  
		serverList = DailyPath.objects.filter(saveTimes=0)
      	for server in serverList:
			if server.savePath = '':
				server.savePath = '/var/data'
				if os.path.exists(server.savePath) == False:
					os.mkdir(server.savePath)
			self.startDown(server.path,server.savePath)
			server.saveTimes = 1
			server.save()
				

