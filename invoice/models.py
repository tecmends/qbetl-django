import json
import os
import uuid
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models

# Create your models here.

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_results.utils import now
from django_mysql.models import JSONField
from rest_framework.authtoken.models import Token

from qbetl import celery as celery


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class CsvFile(models.Model):

    def uid_upload_to(instance, filename):
        uid = str(uuid.uuid4())
        return os.path.join("csvuploads", uid, filename)

    STATUS_CHOICES = [
        ("R", "Received"),
        ("Q", "InProgress"),
        ("C", "Completed"),
        ("F", "Failed"),

    ]
    upload_file = models.FileField(upload_to=uid_upload_to, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='R')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    batch_type = models.CharField(max_length=50, default='CSV')


@receiver(post_save, sender=CsvFile)
def create_celery_task(sender, instance=None, created=False, **kwargs):
    if created:
        print("Created")
        print(instance.upload_file)
        if instance.upload_file:
            celery.process_invoice_batch.apply_async((instance.id,), countdown=10)


class CsvFileResults(models.Model):
    STATUS_SUCCESS = "S"
    STATUS_FAILED = "F"
    STATUS_CHOICES = [
        ("S", "Success"),
        ("F", "Failed"),
        ("W", "Warning")
    ]
    csv_file = models.ForeignKey(CsvFile, on_delete=models.CASCADE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='S')
    invoice_id = models.CharField(max_length=500, null=True)
    customer_id = models.CharField(max_length=500, null=True)
    customer_name = models.CharField(max_length=500, null=True)
    total_amount = models.CharField(max_length=500,blank=True,null=True)
    error_message = models.TextField(null=True)
    error_response = models.TextField(null=True)


class BatchInvoiceResults(models.Model):
    STATUS_SUCCESS = "S"
    STATUS_FAILED = "F"
    STATUS_CHOICES = [
        ("S", "Success"),
        ("F", "Failed"),
        ("W", "Warning")
    ]
    batch_id = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='S')
    invoice_id = models.CharField(max_length=500, null=True)
    customer_id = models.CharField(max_length=500, null=True)
    error_message = models.TextField(null=True)
    error_response = models.TextField(null=True)


def default_mapping():
    mapping_moc = '''
    {
      "docType": "Invoice",
      "mapping": [
        {
          "SourceField": {
            "fieldLabel": "Invoice Number",
            "fieldType": "Header",
            "fieldXPath": "invoicenumber",
            "type": "String",
            "code": "InvoiceNumber"
          },
          "QBField": {
            "code": "DocNumber",
            "label": "Invoice Number",
            "dataType": "String",
            "fieldType": "Header",
            "disable": true,
            "required": true
          },
          "requireField": true,
          "defaultValue": ""
        },
        {
          "SourceField": {
            "fieldLabel": "Customer Number",
            "fieldType": "Header",
            "fieldXPath": "customerrefno",
            "type": "String",
            "code": "InvoiceNumber"
          },
          "QBField": {
            "code": "CustomerRef",
            "label": "Customer Number",
            "dataType": "String",
            "fieldType": "Header",
            "disable": true,
            "required": true
          },
          "requireField": true,
          "defaultValue": ""
        },
        {
          "SourceField": {
            "fieldLabel": "Invoice DueDate",
            "fieldType": "Header",
            "fieldXPath": "duedate",
            "type": "String",
            "code": "InvoiceNumber"
          },
          "QBField": {
            "code": "DueDate",
            "label": "Due Date",
            "dataType": "String",
            "fieldType": "Header",
            "disable": true,
            "required": true
          },
          "requireField": true,
          "defaultValue": ""
        },
        {
          "SourceField": {
            "fieldLabel": "Line Number",
            "fieldType": "Line",
            "fieldXPath": "lineno",
            "type": "Number"
          },
          "QBField": {
            "code": "LineNum",
            "label": "Line No",
            "dataType": "Number",
            "fieldType": "Line",
            "disable": true,
            "required": true
          },
          "requireField": true,
          "defaultValue": ""
        },
        {
          "SourceField": {
            "fieldLabel": "Line Item Code",
            "fieldType": "Line",
            "fieldXPath": "itemcode",
            "type": "String"
          },
          "QBField": {
            "code": "ItemRefValue",
            "label": "LineItem Code",
            "dataType": "String",
            "fieldType": "Line",
            "disable": true,
            "required": true
          },
          "requireField": true,
          "defaultValue": ""
        },
        {
          "SourceField": {
            "fieldLabel": "Line Item Description",
            "fieldType": "Line",
            "fieldXPath": "itemdesc",
            "type": "String"
          },
          "QBField": {
            "code": "Description",
            "label": "LineItem Description",
            "dataType": "String",
            "fieldType": "Line",
            "disable": true,
            "required": true
          },
          "requireField": true,
          "defaultValue": ""
        },
        {
          "SourceField": {
            "fieldLabel": "Unit Rate",
            "fieldType": "Line",
            "fieldXPath": "unitprice",
            "type": "String"
          },
          "QBField": {
            "code": "UnitPrice",
            "label": "Rate",
            "dataType": "Number",
            "fieldType": "Line",
            "disable": true,
            "required": true
          },
          "requireField": true,
          "defaultValue": ""
        },
        {
          "SourceField": {
            "fieldLabel": "Quantity",
            "fieldType": "Line",
            "fieldXPath": "qty",
            "type": "Number"
          },
          "QBField": {
            "code": "QTY",
            "label": "Quantity",
            "dataType": "Number",
            "fieldType": "Line",
            "disable": true,
            "required": true
          },
          "requireField": true,
          "defaultValue": ""
        }
      ]
    }
    '''
    return json.loads(mapping_moc)


class FieldMappings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    mapping = JSONField(default=default_mapping)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):  # __unicode__ on Python 2
        return self.user.username
