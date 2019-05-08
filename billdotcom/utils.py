import json

import requests
from django.conf import settings
from .models import Bill, BillItem, BillSession

api_url = settings.BILL_DOT_COM_API_URL
DEVICE_ID = '916E333F-1BBC-4471-946D-8059DB9488B6'


def make_request(url, data, session_id):
    url = "{}{}".format(api_url, url)
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    request_data = dict(
        devKey=settings.DEV_KEY,
        sessionId=session_id,
        data=json.dumps(data)
    )
    response = requests.post(url, data=request_data, headers=headers)
    response_json = response.json()
    return response_json


def get_bill_list(session_id):
    api_url = settings.BILL_DOT_COM_API_URL
    list_url = "{}{}".format(api_url, "List/Bill.json")
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    request_data = dict(
        devKey=settings.DEV_KEY,
        sessionId=session_id,
        data=json.dumps({"start": 0, "max": 999})
    )
    response = requests.post(list_url, data=request_data, headers=headers)
    response_json = response.json()
    if response_json.get('response_data'):
        for data in response_json.get('response_data'):
            bill_id = data.get('id')
            is_active = data.get('isActive')
            vendor_id = data.get('vendorId')
            invoice_number = data.get('invoiceNumber')
            approval_status = data.get('approvalStatus')
            amount = data.get('amount')
            bill, _ = Bill.objects.get_or_create(bill_id=bill_id, vendor_id=vendor_id, invoice_number=invoice_number)
            if bill:
                bill.is_active = is_active
                bill.approval_status = approval_status
                bill.amount = amount
                bill.json_data = data
                bill.save()
                for bill_item in data.get('billLineItems'):
                    id = bill_item.get('id')
                    amount = bill_item.get('amount')
                    bill_item_object, _ = BillItem.objects.get_or_create(bill_item_id=id, bill=bill)
                    if bill_item:
                        bill_item_object.json_data = bill_item
                        bill_item_object.amount = amount
                        bill_item_object.save()


def get_bills():
    api_url = settings.BILL_DOT_COM_API_URL
    login_url = "{}{}".format(api_url, "Login.json")
    json_data = dict(orgId=settings.ORG_ID, devKey=settings.DEV_KEY, userName=settings.USER_NAME,
                     password=settings.PASSWORD)  # {'OrgId': settings.ORG_ID, 'devKey': settings.DEV_KEY, 'userName': settings.USER_NAME,'password': settings.PASSWORD}
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    response = requests.post(login_url, data=json_data, headers=headers)
    response_json = response.json()
    session_id = ''
    if response_json.get('response_data') and response_json.get('response_data').get('sessionId'):
        session_id = response_json.get('response_data').get('sessionId')
        get_bill_list(session_id)
    pass


def get_session_id():
    api_url = settings.BILL_DOT_COM_API_URL
    login_url = "{}{}".format(api_url, "Login.json")
    json_data = dict(orgId=settings.ORG_ID, devKey=settings.DEV_KEY, userName=settings.USER_NAME,
                     password=settings.PASSWORD)  # {'OrgId': settings.ORG_ID, 'devKey': settings.DEV_KEY, 'userName': settings.USER_NAME,'password': settings.PASSWORD}
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    response = requests.post(login_url, data=json_data, headers=headers)
    response_json = response.json()
    if response_json.get('response_data') and response_json.get('response_data').get('sessionId'):
        return response_json.get('response_data').get('sessionId')


def get_bill_approvers(bill_id):
    data = {"objectId": bill_id, "entity": "Bill"}
    session_id = get_session_id()
    response = make_request('ListApprovers.json', data, session_id)
    users = []
    if response.get('response_data'):
        for approver in response.get('response_data'):
            user_id = approver.get('usersId')
            user_response = make_request('Crud/Read/User.json', {"id": user_id}, session_id)
            if user_response.get('response_data'):
                users.append('{} {}'.format(user_response.get('response_data').get('firstName'),
                                            user_response.get('response_data').get('lastName')))

    return users


def approve_bills(bill_id):
    session_id = get_session_id()
    data = {"objectId": bill_id, "entity": "Bill", "comment": "Looks good to me."}
    response = make_request('Approve.json', data, session_id)
    if response.get('response_message') == 'Success':
        return "Successfully Approved bill"
    elif response.get('response_data').get('error_message'):
        return '{} {}'.format(response.get('response_data').get('error_message'),
                              "You are not Authorized to approve this bill. Please check bill Approvers.")

    return 'Something Went wrong'


def send_token():
    session_id = get_session_id()
    BillSession.objects.all().delete()

    data = {"useBackup": False}
    response = make_request('MFAChallenge.json', data, session_id)
    if response.get('response_message') == 'Success':
        challenge_id = response.get('response_data', {}).get('challengeId')
        BillSession.objects.create(session_id=session_id, challenge_id=challenge_id, device_id=DEVICE_ID)
        return "Please verify access token."
    elif response.get('response_data').get('error_message'):
        return '{}'.format(response.get('response_data').get('error_message'))
    return 'Something Went wrong'


def verify_auth_token(token):
    bill_session = BillSession.objects.all().first()
    session_id = bill_session.session_id
    data = {"challengeId": bill_session.challenge_id, "token": token,
            "deviceId": bill_session.device_id, "machineName": "Test Phone", "rememberMe": True
            }
    response = make_request('MFAAuthenticate.json', data, session_id)

    if response.get('response_message') == 'Success':
        mfa_id = response.get('response_data', {}).get('mfaId')
        bill_session.mfa_id = mfa_id
        bill_session.save()
        return "Access Token Has been verified"
    elif response.get('response_data').get('error_message'):
        return '{}'.format(response.get('response_data').get('error_message'))

    return 'Something Went wrong'


def pay_bill(vendor_id, bill_id, amount):
    bill_session = BillSession.objects.all().first()

    data = {"vendorId": vendor_id, "billPays": [{"billId": bill_id, "amount": float(amount)}]}

    url = "{}{}".format(api_url, 'PayBills.json')
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    request_data = dict(
        devKey=settings.DEV_KEY,
        sessionId=bill_session.session_id,
        data=json.dumps(data),
        mfaId=bill_session.mfa_id,
        deviceId=bill_session.device_id,
    )
    response = requests.post(url, data=request_data, headers=headers)
    response = response.json()
    return response
    # PayBills
