#coding=utf-8
from django.db import models
import time,datetime
from django.contrib import admin
# Create your models here.
#from admin import DailyPathAdmin

class DailyAccess(models.Model):
	class Meta:
		db_table = "dailyAccess"
		verbose_name_plural = verbose_name = "访问日志"
	PC = 0 
	ANDROID = 1 
	IPHONE = 2
	
	MOBILE_CHOICES =(
	
		(PC , '电脑登录' ),
		(ANDROID,'安卓手机登录'),
		(IPHONE,'苹果手机登录')
	)
	
	ip = models.CharField(u"ip地址",max_length = 15)
	method = models.CharField(u"请求方法",max_length=10)
	accessTime = models.DateTimeField(u"访问时间",null = True , blank=True)
	path = models.TextField(u"访问的路径",null=True)
	status = models.IntegerField(u"返回的状态码")
	send_byte = models.IntegerField(u"返回给客户端的字节数" )
	access_type = models.SmallIntegerField(u"访问方式", choices=MOBILE_CHOICES, default=PC)
	browse = models.CharField(u"浏览器",max_length=20)
	refe = models.CharField(u"from",max_length=252)
	access_record = models.TextField(u'完整记录信息')

	@property
	def show_formate_time(self,formate='%Y-%m-%d %H:%M:%S'):
		self.accessTime = self.accessTime.strftime(formate)
		return self.accessTime

class DailyPath(models.Model):
	
	NGINX_ACCESS = 0 
	NGINX_ERROR = 1
	ELSE_DAILY = 2
	DAILY_CHOICES=(
	   (NGINX_ACCESS,'nginx访问日志'),
	   (NGINX_ERROR,'nginx错误日志'),
	   (ELSE_DAILY,'其他日志')
	    	
	)
	SAVE_NO = 0
	SAVE_YES = 1
	SAVE_CHOICES = (
	   (SAVE_NO,'未抓取'),
	   (SAVE_YES,'已抓取')
	)
	path = models.CharField(u'日志地址',max_length=255)
	dailyType = models.SmallIntegerField(u"日志种类", choices=DAILY_CHOICES, default=NGINX_ACCESS)
	SaveYesNo = models.SmallIntegerField(u'是否抓取',choices=SAVE_CHOICES,default=SAVE_NO)
	
	

