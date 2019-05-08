# -*- coding: ascii -*-
from rest_framework import serializers
from invoice.models import CsvFile, CsvFileResults, FieldMappings, BatchInvoiceResults
from qbconnect.models import *


class CsvFileSerializer(serializers.ModelSerializer):
    csv_path = serializers.SerializerMethodField()
    batch_id = serializers.SerializerMethodField()
    counts = serializers.SerializerMethodField()
    success = serializers.SerializerMethodField()
    failed = serializers.SerializerMethodField()
    warning = serializers.SerializerMethodField()

    class Meta:
        model = CsvFile
        fields = ('csv_path', 'upload_file', 'batch_id', 'csv_path', 'status', 'created_at', 'counts',
                  'success', 'failed', 'warning','batch_type')

    def get_batch_id(self, obj):
        return obj.id

    def get_csv_path(self, obj):
        if obj.upload_file:
            return obj.upload_file.url
        return ""

    def get_counts(self, obj):
        success_count = CsvFileResults.objects.filter(csv_file=obj, status=CsvFileResults.STATUS_SUCCESS).count()
        fail_count = CsvFileResults.objects.filter(csv_file=obj, status=CsvFileResults.STATUS_FAILED).count()
        result = {
            "invoice_success": success_count,
            "invoice_failed": fail_count,
            "invoice_warnings": 0
        }
        return result

    def get_success(self, obj):
        success_count = CsvFileResults.objects.filter(csv_file=obj, status=CsvFileResults.STATUS_SUCCESS).count()
        return success_count

    def get_failed(self, obj):
        fail_count = CsvFileResults.objects.filter(csv_file=obj, status=CsvFileResults.STATUS_FAILED).count()
        return fail_count

    def get_warning(self, obj):
        return 0

    def create(self, validated_data):
        # Once you are done, create the instance with the validated data
        user = self.context['request'].user
        return CsvFile.objects.create(user=user, **validated_data)


class CsvFileResultsSerializer(serializers.ModelSerializer):
    batch_id = serializers.SerializerMethodField()

    class Meta:
        model = CsvFileResults
        fields = ('batch_id', 'status', 'created_at', "invoice_id", "customer_id", "customer_name", 'total_amount')

    def get_batch_id(self, obj):
        return obj.id


class FieldMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldMappings
        exclude = ['user']


class LineItemSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    line_no = serializers.IntegerField(required=True)
    item_code = serializers.CharField(required=True)
    item_description = serializers.CharField(max_length=500)
    unit_price = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)


class InvoiceSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField(required=True)
    customer_ref_number = serializers.IntegerField(required=True)
    due_date = serializers.CharField(required=True)
    line_items = LineItemSerializer(many=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class UserConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConnection
        fields = ('consumer_key', 'consumer_secret')


class BatchInvoiceResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchInvoiceResults
        fields = ('batch_id', 'created_at', 'status', 'invoice_id', 'error_response', 'error_message')
