from django.shortcuts import render

# Create your views here.
from quickbooks.exceptions import QuickbooksException
from quickbooks.objects import Invoice, SalesItemLine, SalesItemLineDetail, TaxCode
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

from invoice.invoiceoperation import InvoiceOperations
from invoice.restserilizers import InvoiceSerializer
from invoice.tests import MAPPING_MOCK, MAPPING_MOCK_LEGACY
from invoice.models import CsvFile
from invoice.models import CsvFileResults
from invoice.csvfileutils import create_invoice_obj_for_post
from invoice.customerrors import *


@api_view(['GET'])
def get_dashboard_kpi(request):
    user = request.user
    success_count = CsvFileResults.objects.filter(csv_file__user=user, status=CsvFileResults.STATUS_SUCCESS).count()
    fail_count = CsvFileResults.objects.filter(csv_file__user=user, status=CsvFileResults.STATUS_FAILED).count()
    result = {
        "invoice_success": success_count,
        "invoice_failed": fail_count,
        "invoice_warnings": 0
    }
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_customers(request):
    user = request.user
    print(user.id)

    io = InvoiceOperations(user_id=user.id)
    customers = io.get_customer()
    customers_dic_list = list()
    for customer in customers:
        cust_dic = {"customer_name": customer.to_ref().name, "customer_no": customer.to_ref().value}
        customers_dic_list.append(cust_dic)
    return Response(customers_dic_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_items(request):
    user = request.user
    print(user.id)
    io = InvoiceOperations(user_id=user.id)
    items = io.get_items()
    item_dic_list = list()
    for item in items:
        item_dic = {"item_name": item.to_ref().name, "item_no": item.to_ref().value}
        item_dic_list.append(item_dic)
    return Response(item_dic_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_field_mapping(request):
    return Response(json.loads(MAPPING_MOCK), status=status.HTTP_200_OK)


@api_view(['GET'])
def get_field_mapping_legacy(request):
    return Response(json.loads(MAPPING_MOCK_LEGACY), status=status.HTTP_200_OK)


@api_view(['POST'])
def post_invoice(request):
    print("post_invoice,", request.data)
    serializer = InvoiceSerializer(data=request.data)
    if serializer.is_valid():
        validated_data = serializer.data
        print(validated_data)
        user = request.user
        print(user)
        try:
            invoice = create_invoice_obj_for_post(validated_data, user)
        except InvalidItemRef:
            return Response("invalid item code, please check for valid item codes", status.HTTP_400_BAD_REQUEST)
        except QuickbooksException as e:
            print(e)
            return Response("Invalid payload:{}".format(e), status.HTTP_400_BAD_REQUEST)

        return Response("Data post success", status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def create_line_item_legacy(obj, codes):
    line = SalesItemLine()
    line.LineNum = int(obj['lineno'])
    line.Description = obj['itemdesc']
    line.SalesItemLineDetail = SalesItemLineDetail()
    line.SalesItemLineDetail.Qty = obj['qty']
    line_item_code = obj['itemcode']
    if not line_item_code in codes.keys():
        raise InvalidItemRef("No item found:{}, please check the payload".format(line_item_code))
    print("caderef", codes[line_item_code].to_ref())
    line.SalesItemLineDetail.ItemRef = codes[line_item_code].to_ref()
    return line


def create_line_item_legacy_2(obj, codes):
    unit_price = float(obj['UnitPrice'])
    qty = float(obj['Qty'])
    line = SalesItemLine()
    line.LineNum = int(obj['Line No'])
    line.Description = obj['ItemDesc']
    line.SalesItemLineDetail = SalesItemLineDetail()
    line.SalesItemLineDetail.Qty = qty
    line_item_code = obj['ItemCode']
    line.SalesItemLineDetail.ServiceDate = obj['DueDate']
    line.SalesItemLineDetail.UnitPrice = unit_price
    line.Amount = unit_price * qty
    if not line_item_code in codes.keys():
        raise InvalidItemRef("No item found:{}, please check the payload".format(line_item_code))
    print("caderef", codes[line_item_code].to_ref())
    line.SalesItemLineDetail.ItemRef = codes[line_item_code].to_ref()
    # line.SalesItemLineDetail.TaxCodeRef = 'NOTAXS'
    return line


def create_invoice_obj_legacy(list_objs, io):
    invoice = None
    item_codes = list()
    for line in list_objs:
        item_codes.append(line['itemcode'])
    codes = io.get_items_from_list(item_codes)
    print("codes", codes)
    for obj in list_objs:
        invoicenumber = obj['invoicenumber']
        duedate = obj['duedate']
        customerrefno = obj['customerrefno']
        if not invoice:
            invoice = Invoice()
            invoice.DocNumber = invoicenumber
            invoice.DueDate = duedate
            customer = io.get_customer_by_id(customerrefno)
            invoice.CustomerRef = customer.to_ref()
        line_obj = create_line_item_legacy(obj, codes)
        invoice.Line.append(line_obj)
    return invoice


def create_invoice_obj_legacy_many(list_objs, io):
    # harcode tx for now
    taxcode = io.get_tax_codes()[0]
    invoice_dic = dict()
    item_codes = list()
    for line in list_objs:
        item_code = line['ItemCode']
        if not len(item_code) < 1:
            item_codes.append(item_code)
    codes = io.get_items_from_list(item_codes)
    print("codes", codes)
    for obj in list_objs:
        invoicenumber = obj['Invoice No']
        duedate = obj['DueDate']
        customerrefno = obj['Customer Ref No']
        if len(invoicenumber) < 1:
            continue
        if invoicenumber not in invoice_dic.keys():
            invoice = Invoice()

            invoice.DocNumber = invoicenumber
            invoice.DueDate = duedate
            customer = io.get_customer_by_id(customerrefno)
            invoice.CustomerRef = customer.to_ref()
            invoice_dic[invoicenumber] = invoice
        line_obj = create_line_item_legacy_2(obj, codes)
        line_obj.SalesItemLineDetail.TaxCodeRef = taxcode.to_ref()
        invoice_dic[invoicenumber].Line.append(line_obj)
    return invoice_dic


@api_view(['POST'])
def post_invoice_legacy(request):
    print("post_invoice,", request.data)
    user = request.user
    print(user)
    io = InvoiceOperations(user_id=user.id)
    try:
        invoice = create_invoice_obj_legacy(request.data, io)
        io.save_invoice(invoice)
    except QuickbooksException as e:
        print(e)
        return Response("Invalid payload:{}".format(e), status.HTTP_400_BAD_REQUEST)
    except InvalidItemRef as e:
        print(e)
        return Response("Invalid payload:{}".format(e), status.HTTP_400_BAD_REQUEST)

    return Response("Data post success", status=status.HTTP_200_OK)


@api_view(['POST'])
def post_invoice_legacy2(request):
    import uuid
    from invoice.models import BatchInvoiceResults

    csv_file_results = list()

    csv_file = CsvFile()
    csv_file.status = 'C'
    csv_file.batch_type = 'EXCEL'
    csv_file.user = request.user
    csv_file.save()

    print("post_invoice,", request.data)
    user = request.user
    print(user)
    io = InvoiceOperations(user_id=user.id)

    try:
        invoice_dic = create_invoice_obj_legacy_many(request.data, io)
        print("invoices after parsing")
        for invoice_num in invoice_dic.keys():
            print(invoice_dic[invoice_num])

        for invoice_num in invoice_dic.keys():
            invoice = invoice_dic[invoice_num]

            csv_file_result = CsvFileResults()
            csv_file_result.csv_file = csv_file
            csv_file_result.invoice_id = invoice.DocNumber
            csv_file_result.customer_id = invoice.CustomerRef.value
            csv_file_result.customer_name = invoice.CustomerRef.name

            try:
                io.save_invoice(invoice)
                csv_file_result.status = 'S'

                query_invoice = Invoice.get(invoice.Id, qb=io.client)

                csv_file_result.total_amount = str(query_invoice.TotalAmt)
            except QuickbooksException as e:
                print("error while posting invoice", e)
                csv_file_result.status = 'E'
                csv_file_result.error_message = str(e)
            csv_file_result.save()
            csv_file_results.append(csv_file_result)

        for result in csv_file_results:
            if result.status in "F":
                csv_file.status = 'F'
                csv_file.save()
    except QuickbooksException as e:
        print(e)
        return Response("Invalid payload:{}".format(e), status.HTTP_400_BAD_REQUEST)
    except InvalidItemRef as e:
        print(e)
        return Response("Invalid payload:{}".format(e), status.HTTP_400_BAD_REQUEST)

    response_dic = dict()

    for result in csv_file_results:
        response_dic[result.invoice_id] = result.status

    return Response(response_dic, status=status.HTTP_200_OK)


def process_ar_result(results):
    final_result = dict()
    processed_results = []
    cols = results['Columns']['Column']
    rows = results['Rows']['Row']
    for col in cols:
        processed_results.append({col['ColTitle']: None})
    for row in rows:
        if "Summary" in row:
            data = row['Summary']['ColData']
            for index, val in enumerate(data):
                for key in processed_results[index].keys():
                    processed_results[index][key] = val['value']
                    break
    return processed_results


@api_view(['GET'])
def get_report(request):
    valid_report_options = ['AgedPayables',
                            'AgedReceivables',
                            'InventoryValuationSummary',
                            'CustomerSales',
                            'ItemSales',
                            'VendorExpenses'
                            ]
    user = request.user
    params = request.query_params
    for key in params.keys():
        print(key, params[key])
    report_type = request.query_params.get('report_type')
    if report_type not in valid_report_options:
        return Response("invalid report type", status=status.HTTP_400_BAD_REQUEST)
    io = InvoiceOperations(user_id=user.id)

    result = io.client.get_report(report_type, params)
    # results = io.get_report_receivables()
    # processed_results = process_ar_result(results)
    return Response(result, status=status.HTTP_200_OK)
