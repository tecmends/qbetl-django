from django.contrib import admin
from billdotcom.models import Bill, BillItem

admin.site.register(Bill)
admin.site.register(BillItem)
