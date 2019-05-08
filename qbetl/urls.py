"""qbetl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views
from invoice.restviewsets import CsvFileViewSet, CsvFileResultViewSet, FieldMappingViewSet, UserConnectionViewSet, \
    BatchInvoiceResultsViewSet
from invoice.views import get_dashboard_kpi, get_field_mapping, get_items, get_customers, post_invoice, \
    post_invoice_legacy, get_field_mapping_legacy, post_invoice_legacy2, get_report
from qbconnect.views import connect_with_qb, connect_with_qb_success_handler
from billdotcom.views import fetch_data, fetch_bill_from_db, fetch_bill_approvers, approve_bill, send_auth_token, \
    verify_authentication_token, pay_bills

router = routers.DefaultRouter()
router.register(r'csv', CsvFileViewSet, 'csvfile')
router.register(r'csvresult', CsvFileResultViewSet, 'csvfileresult')
router.register(r'fieldmapping', FieldMappingViewSet, 'fieldmapping')
router.register(r'userconnection', UserConnectionViewSet, 'userconnection')
router.register(r'batchInvoiceresults', BatchInvoiceResultsViewSet, 'batchInvoiceresults')

urlpatterns = [
    path('qbetl/admin/', admin.site.urls),
    url(r'^qbetl/api-token-auth/', views.obtain_auth_token),
    url(r'^qbetl/api/', include(router.urls)),
    url(r'^qbetl/api/filedmappinglegacy', get_field_mapping_legacy),
    url(r'^qbetl/api/invoice', post_invoice),
    url(r'^qbetl/api/post/invoicelegacy', post_invoice_legacy),
    url(r'^qbetl/api/post/excel/invoicelegacy', post_invoice_legacy2),
    url(r'qbetl/api/dashboard', get_dashboard_kpi),
    url(r'qbetl/api/customers', get_customers),
    url(r'qbetl/api/reports', get_report),
    url(r'qbetl/api/items', get_items),
    url(r'^qbetl/api-auth/', include('rest_framework.urls')),
    url(r'^qbetl/connect/', connect_with_qb),
    url(r'^qbetl/connectsuccess/', connect_with_qb_success_handler),
    url(r'^qbetl/fetch_data/', fetch_data, ),
    url(r'^qbetl/fetch_db_bills/', fetch_bill_from_db, ),
    url(r'^qbetl/fetch_bill_approvers/', fetch_bill_approvers, ),
    url(r'^qbetl/approve_bill/', approve_bill, ),
    url(r'^qbetl/send_auth_token/', send_auth_token, ),
    url(r'^qbetl/verify_auth_token/', verify_authentication_token, ),
    url(r'^qbetl/pay_bill/', pay_bills, ),

]
