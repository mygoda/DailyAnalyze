#coding=utf-8
from django.contrib import admin
from django.shortcuts import render
from access.models import DailyAccess,DailyPath
from django.http import HttpResponseRedirect, HttpResponse
from django.template import Context,Template
from django.shortcuts import render_to_response 
import linecache
import re
import time,datetime
from django.views.generic import View,TemplateView
#glob模块是最简单的模块之一，内容非常少。用它可以查找符合特定规则的文件路径名
import glob
import os
# Create your views here.
import logging 
logger = logging.getLogger(__name__)

class indexView(TemplateView):

    template_name='index.html'
    #def get(self, request, *args, **kwargs):
     #   return render_to_response(self.template_name)
     
class searchView(View):


    #格式化时间
    def time_formate(self,dic,time,tag=0):
        if dic.has_key('from_time'):
            del dic['from_time']
        if dic.has_key('to_time'):
            del dic['to_time']
        from_date = time.split(' ')[0]
        from_year = int(from_date.split('/')[2])
        from_month = int(from_date.split('/')[0])
        from_day = int(from_date.split('/')[1])
        if tag == 1:
            from_day = from_day + 1
        start = datetime.date(from_year, from_month, from_day)
        return start
    #检查输出的记录数，默认的是十条
    def check_output(self,dic):
        line = 10 
        if dic.has_key('output'):
            if dic['output'] != '':
                line = int(dic['output'])
                del dic['output']
        return line
    #得到查询参数的字典
    def get_parame_dic(self,requestDic):
        dic = {}
        for k,v in dic:
            if v != '':
                dic[k] = v
        return dic 
    #获取当前时间    
    def get_time(self):
        now = time.time()
        return now 

    def time_select(self,request,dic,singleTime=False):
        if singleTime == False :
            end = self.time_formate(dic,to_time)
        else:
            end = self.time_formate(dic,to_time,1)
        from_time = request.GET.get('from_time','')
        start = self.time_formate(dic,from_time)
        to_time = request.GET.get('to_time','')
        result = DailyAccess.objects.filter(accessTime__range=(start,end)).filter(**dic)
        return result
    #检测输出的line参数是否正确
    def check_line(self,line,count):

        if (line == -1) | (line > count) :
            line = count - 1 
        return line

    def get(self,request,*args,**kwargs):
        t = 'type_select_destails.html'
        old = self.get_time()
        #得到查询参数的字典
        dic = self.get_parame_dic(request.GET.items())
        #取得输出的记录数
        
        line = self.check_output(dic)   
        #执行区间查询的情况
        if (request.GET.get('from_time','') != '') & (request.GET.get('to_time','') != ''):
            result = self.time_select(request,dic)
            count = result.count()
            if count > 0 :
                count_list = self.set_parame(result,2,1,0,200,old,count)
                line = self.check_line(line,count) 
                context = self.get_context(result,line,count,count_list)
                return render_to_response(t,context)
            else:
                return render_to_response('error.html')
        #执行指定日期查询的情况
        elif (request.GET.get('from_time','') != '') & (request.GET.get('to_time','') == ''):
            result = self.time_select(request,dic,True)
            count = result.count()
            if count > 0 :
                count_list = self.set_parame(result,2,1,0,200,old,count)
                line = self.check_line(line,count) 
                context = self.get_context(result,line,count,count_list)
                return render_to_response(t,context)
            else:
                return render_to_response('error.html')
        #其他没有时间的查询
        else:
            result = DailyAccess.objects.filter(**dic)
    	    count = result.count()
            if count > 0 :
                count_list = self.set_parame(result,2,1,0,200,old,count)
                line = self.check_line(line,count)
                context = self.get_context(result,line,count,count_list)
                return render_to_response(t,context)
            else:
                return render_to_response('error.html')
    #得到在页面显示的参数列表
    def get_context(self,result,line,count,count_list):
        line = line - 1
        context = {
            "searchlist" : result[:line],
            "count" : count,
            "use_time" : count_list[7],
            "user_count" : count_list[6],
            "iphone_count" : count_list[0],
            "android_count" : count_list[1],
            "pc_count" : count_list[2],
            "ok_count" : count_list[3],
            "first_login" : count_list[4],
            "latest_login" : count_list[5],
            "line" : line 
        }
        return context

    #获取记录中不同的用户个数
    def get_user(self,result):
        user_count = result.values('ip').distinct().count()
        return user_count
    
    #设置相关参数
    def set_parame(self,result,iphone,android,pc,ok,old,count):
        count_list = []
        iphone_count = result.filter(access_type=iphone).count()
        count_list.append(iphone_count)            
        android_count = result.filter(access_type=android).count()
        count_list.append(android_count)           
        pc_count = result.filter(access_type=pc).count()
        count_list.append(pc_count)                
        ok_count = result.filter(status=200).count()
        count_list.append(ok_count)           
        first_login = result[count-1].accessTime
        count_list.append(first_login)       
        latest_login = result[0].accessTime 
        count_list.append(latest_login)     
        user_count = self.get_user(result)
        count_list.append(user_count)      
        use_time = time.time() - old
        count_list.append(use_time)        
        return count_list
