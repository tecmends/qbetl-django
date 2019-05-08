# from rest_framework.response import Response
import json

from rest_framework.decorators import api_view

from .utils import get_bills, get_bill_approvers, approve_bills, send_token, verify_auth_token, pay_bill
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from .models import Bill


@api_view(['GET'])
def fetch_data(request):
    get_bills()
    data = "Database Successfully Updated."
    # for bill in Bill.objects.all():
    #     data.append(bill.json_data)
    return Response({'data': data}, status=HTTP_200_OK)


@api_view(['GET'])
def fetch_bill_from_db(request):
    data = []
    for bill in Bill.objects.all():
        data.append(bill.json_data)
    return Response({'data': data}, status=HTTP_200_OK)


@api_view(['POST'])
def fetch_bill_approvers(request):
    if request.POST.get('bill_id'):
        data = get_bill_approvers(request.POST.get('bill_id'))
    else:
        data = 'Please provide bill_id'
    return Response({'data': data}, status=HTTP_200_OK)


@api_view(['POST'])
def approve_bill(request):
    if request.POST.get('bill_id'):
        data = approve_bills(request.POST.get('bill_id'))
    else:
        data = 'Please provide bill_id'
    return Response({'data': data}, status=HTTP_200_OK)


@api_view(['POST'])
def send_auth_token(request):
    data = send_token()
    return Response({'data': data}, status=HTTP_200_OK)


@api_view(['POST'])
def verify_authentication_token(request):
    if request.POST.get('token'):
        data = verify_auth_token(request.POST.get('token'))
    else:
        data = 'Please provide token'
    return Response({'data': data}, status=HTTP_200_OK)


@api_view(['POST'])
def pay_bills(request):
    vendor_id = request.POST.get('vendor_id')
    bill_id = request.POST.get('bill_id')
    amount = request.POST.get('amount')
    if vendor_id and bill_id and amount:
        data = pay_bill(vendor_id, bill_id, amount)
    else:
        data = 'Following parameters are required, vendor_id, bill_id and amount'
    return Response({'data': data}, status=HTTP_200_OK)
