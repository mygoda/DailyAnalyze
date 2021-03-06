#coding=utf-8
from django.contrib import admin
from django.shortcuts import render
from access.models import DailyAccess,DailyPath
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse
from django.template import Context,Template
from django.shortcuts import render_to_response 

import time,datetime
from django.views.generic import View,TemplateView
#glob模块是最简单的模块之一，内容非常少。用它可以查找符合特定规则的文件路径名
# Create your views here.
import logging 
logger = logging.getLogger(__name__)
#统计相关页面的
class dataView(View):
    
    def order_result(self,result,fields,number=10):
        #执行分组统计
        exclude_filter_result = self.exclude_filter(result)
        result = exclude_filter_result.values(fields).annotate(count=Count(fields)).order_by('-count')[:number]
        return result
    
    def exclude_filter(self,result):
        parame = result.exclude(path__startswith='/stat').exclude(path__startswith='/api').exclude(path__startswith='/settings')
        return parame  

    def get_order_result(self,result):
        order_ip = self.order_result(result,'ip')
        order_path = self.order_result(result,'path')
        order_refe = self.order_result(result,'refe')
        order_accessType = self.order_result(result,'access_type')
        order_app_name = self.order_result(result,'appName')
        order_browse = self.order_result(result,'browse')
        count = result.count()
        count_list = self.get_accessType_percent(result)
        iphone_percent = int(count_list[0]) * 100.0 / count
        android_percent = int(count_list[1]) * 100.0 / count
        pc_percent = int(count_list[2]) * 100.0 / count
        context = {
            "order_ip" :order_ip,
            "order_path" : order_path,
            "order_refe" :order_refe,
            "order_accessType" : order_accessType,
            "order_app_name" : order_app_name,
            "order_browse" : order_browse,
            "iphone_percent": iphone_percent,
            "android_percent":android_percent,
            "pc_percent" : pc_percent,
        }
        return context

    def get_accessType_percent(self,result):
        percent_list = []
        iphone_count = result.filter(access_type=2).count()
        percent_list.append(iphone_count)
        android_count = result.filter(access_type=1).count()
        percent_list.append(android_count)
        pc_count = result.filter(access_type=0).count()
        percent_list.append(pc_count)
        return percent_list

    def get(self,request,*args,**kwargs):

        result = DailyAccess.objects.all()
        filter_result = self.exclude_filter(result)
        context = self.get_order_result(filter_result)
        t = "data.html"
        return render_to_response(t,context)



class indexView(TemplateView):
    template_name='index.html'
     
class searchView(View):

    #根据年月日来格式化时间
    def time_formate_by_number(self,year,month,day):
        formateTime = datetime.date(year,month,day)
        return formateTime

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

    #格式化输出显示在查询页面的时间
    def show_formate_time(self,show_time,formate='%Y-%m-%d %H:%M:%S'):
        formateTime = show_time.strftime(formate)
        return formateTime

    #获取当前时间    
    def get_time(self):
        now = time.time()
        return now 

    def time_select(self,request,dic,singleTime=False):
        from_time = request.GET.get('from_time','')
        start = self.time_formate(dic,from_time)
        if singleTime == False :
            to_time = request.GET.get('to_time','')
            end = self.time_formate(dic,to_time)
        else:
            end = self.time_formate(dic,from_time,1)
        result = DailyAccess.objects.filter(accessTime__range=(start,end)).filter(**dic).filter(status=200).defer("access_record", "send_byte")
        time_select_exclude_result = self.exclude_filter(result)
        return time_select_exclude_result

    def exclude_filter(self,result):
        parame = result.exclude(path__startswith='/stat').exclude(path__startswith='/api').exclude(path__startswith='/settings')
        return parame  
    #检查输出的记录数，默认的是十条
    def check_output(self,dic):
        line = 10 
        if dic.has_key('output'):
            if dic['output'] != '':
                line = int(dic['output'])
                del dic['output']
        return line

    #检测输出的line参数是否正确
    def check_line(self,line,count):
        if (line == -1) | (line > count) :
            if count == 1:
                line = count 
            else :
                line = count -1 
        return line

    #得到查询参数的字典
    def get_parame_dic(self,requestDic):
        dic = {}
        for k,v in requestDic   :
            if v != '':
                dic[k] = v
        return dic 

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
                context = self.get_context(result,line,self.count,count_list)
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
            if len(dic) < 1 :
                return HttpResponseRedirect('/destails/')
            result = self.select_No_Time_query(dic)
            count = result.count()
            if count > 0 :
                count_list = self.set_parame(result,2,1,0,200,old,count)
                line = self.check_line(line,count)
                context = self.get_context(result,line,count,count_list)

                return render_to_response(t,context)
            else:
                return render_to_response('error.html')

    #在没有时间条件的时候，会默认查询表中记录最近的30天的查询
    def select_No_Time_query(self,dic):
        latest_time = DailyAccess.objects.latest('accessTime')
        latest_time_year = latest_time.accessTime.year
        latest_time_month = latest_time.accessTime.month
        latest_time_day = latest_time.accessTime.day
        first_time_month = latest_time_month - 1 
        first_time_year = latest_time_year
        if first_time_month == 0 :
            first_time_month = 12
            first_time_year = latest_time_year - 1 
        start = self.time_formate_by_number(first_time_year,first_time_month,latest_time_day)
        end = self.time_formate_by_number(latest_time_year,latest_time_month,latest_time_day)
        result = DailyAccess.objects.filter(accessTime__range=(start,end)).filter(**dic).filter(status=200).defer("access_record", "send_byte")
        exclude_result = self.exclude_filter(result)
        return exclude_result
    
    #得到统计相关的数据
    def get_order_result(self,result):
        order_ip = self.order_result(result,'ip')
        order_path = self.order_result(result,'path')
        order_refe = self.order_result(result,'refe')
        order_accessType = self.order_result(result,'access_type')
        order_app_name = self.order_result(result,'appName')
        order_browse = self.order_result(result,'browse')
        context = {
            "order_ip" :order_ip,
            "order_path" : order_path,
            "order_refe" :order_refe,
            "order_accessType" : order_accessType,
            "order_app_name" : order_app_name,
            "order_browse" : order_browse,
        }
        return context

    #得到在页面显示的参数列表
    def get_context(self,result,line,count,count_list):
        iphone_percent = int(count_list[0]) * 100 / count
        android_percent = int(count_list[1]) * 100 / count
        pc_percent = int(count_list[2]) * 100 / count
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
            "line" : line ,
            "iphone_percent": iphone_percent,
            "android_percent":android_percent,
            "pc_percent" : pc_percent
        }
        #取得统计相关的字典
        order_context = self.get_order_result(result)
        #合并相关的数据字典
        union_context = dict(context, **order_context)
        return union_context



    #获取记录中不同的用户个数
    def get_user(self,result):
        user_count = result.values('ip').distinct().count()
        return user_count

    #统计排序相关的处理
    def order_result(self,result,fields,number=10):
        #执行分组统计
        exclude_filter_result = self.exclude_filter(result)
        result = exclude_filter_result.values(fields).annotate(count=Count(fields)).order_by('-count')[:number]
        return result

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
        first_unformate_login = result[count-1].accessTime
        first_login = self.show_formate_time(first_unformate_login)
        count_list.append(first_login)       
        latest_unformate_login = result[0].accessTime
        latest_login = self.show_formate_time(latest_unformate_login) 
        count_list.append(latest_login)     
        user_count = self.get_user(result)
        count_list.append(user_count)      
        use_time = time.time() - old
        count_list.append(use_time)       
        return count_list
