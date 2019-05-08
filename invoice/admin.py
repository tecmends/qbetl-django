from django.contrib import admin
from invoice.models import CsvFile, CsvFileResults, BatchInvoiceResults


class CsvFileAdmin(admin.ModelAdmin):
    # list_display = ('category_name',)
    pass


class CsvFileResultsAdmin(admin.ModelAdmin):
    # list_display = ('category_name',)
    list_display = ('id','status')


class BatchInvoiceResultsAdmin(admin.ModelAdmin):
    # list_display = ('category_name',)
    pass


admin.site.register(CsvFile, CsvFileAdmin)
admin.site.register(CsvFileResults, CsvFileResultsAdmin)
admin.site.register(BatchInvoiceResults, BatchInvoiceResultsAdmin)
