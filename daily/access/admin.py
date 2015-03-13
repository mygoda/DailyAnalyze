from django.contrib import admin
from access.models import DailyAccess,DailyPath,DailyAppCount
# Register your models here.


class DailyAccessAdmin(admin.ModelAdmin):
	list_display = ['ip', 'appName', 'path', 'status', 'access_type', 'accessTime',
                    'browse','refe',]
    
	search_fields = ['method', 'access_type','ip']
	list_filter = ['appName','path','accessTime','access_type','browse','refe']
#admin.site.register(DailyAccess, DailyAccessAdmin)
class DailyPathAdmin(admin.ModelAdmin):
	list_display = ['path','dailyType']
	readonly_fields = ['SaveYesNo']

admin.site.register(DailyAccess,DailyAccessAdmin)
admin.site.register(DailyPath,DailyPathAdmin)


