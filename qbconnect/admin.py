from django.contrib import admin

from invoice.models import FieldMappings
from qbconnect.models import UserConnection


# Register your models here.

class UserConnectionAdmin(admin.ModelAdmin):
    # list_display = ('category_name',)
    pass


class FieldMappingsAdmin(admin.ModelAdmin):
    # list_display = ('category_name',)
    pass


admin.site.register(UserConnection, UserConnectionAdmin)
admin.site.register(FieldMappings, FieldMappingsAdmin)
