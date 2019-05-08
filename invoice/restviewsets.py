# -*- coding: ascii -*-
from rest_framework import viewsets

from invoice.models import CsvFile, CsvFileResults, FieldMappings, BatchInvoiceResults
from invoice.restserilizers import CsvFileSerializer, CsvFileResultsSerializer, FieldMappingSerializer, \
    UserConnectionSerializer, BatchInvoiceResultsSerializer
from rest_framework import mixins

from qbconnect.models import UserConnection


class CsvFileViewSet(viewsets.ModelViewSet):
    serializer_class = CsvFileSerializer

    def get_queryset(self):
        queryset = CsvFile.objects.filter(user=self.request.user)
        return queryset


class CsvFileResultViewSet(viewsets.ModelViewSet):
    serializer_class = CsvFileResultsSerializer

    def get_queryset(self):

        queryset = CsvFileResults.objects.filter(csv_file__user=self.request.user)
        if "batchid" in self.request.query_params:
            batch_id = self.request.query_params['batchid']
            queryset = CsvFileResults.objects.filter(csv_file__id=batch_id)
        return queryset


class FieldMappingViewSet(viewsets.ModelViewSet):
    serializer_class = FieldMappingSerializer

    def get_queryset(self):
        queryset = FieldMappings.objects.filter(user=self.request.user)
        return queryset


class UserConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = UserConnectionSerializer

    def get_queryset(self):
        queryset = UserConnection.objects.filter(user=self.request.user)
        return queryset


class BatchInvoiceResultsViewSet(viewsets.ModelViewSet):
    serializer_class = BatchInvoiceResultsSerializer

    def get_queryset(self):
        queryset = BatchInvoiceResults.objects.filter(user=self.request.user)
        return queryset

