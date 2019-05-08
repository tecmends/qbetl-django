# -*- coding: ascii -*-
import json

import requests
from django.contrib.auth.models import User
from quickbooks import Oauth2SessionManager, QuickBooks
from quickbooks.objects import Customer, Item, TaxCode, TaxRate

from qbconnect.models import UserConnection

from django.conf import settings


class InvoiceOperations:
    session_manager = ''
    refresh_token = ''
    client_id = ''
    client_secret = ''
    company_id = ''

    def __init__(self, **kwargs):
        if 'user_id' in kwargs:
            self.user_id = kwargs['user_id']
        user_connection = self.__get_user_client_credential()
        self.client_id = user_connection.consumer_key
        self.client_secret = user_connection.consumer_secret
        self.company_id = user_connection.company_id
        self.refresh_token = user_connection.refresh_token
        self.access_token = user_connection.access_token

        self.session_manager = Oauth2SessionManager(
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token=self.access_token
        )
        self.get_new_auth_token()
        # self.session_manager.access_token = self.access_token

        self.client = QuickBooks(
            sandbox=settings.QB_SANDBOX,
            session_manager=self.session_manager,
            company_id=self.company_id
        )

    def __get_user_client_credential(self):
        user = User.objects.get(id=self.user_id)
        user_connection = UserConnection.objects.filter(user=user).first()
        return user_connection

    def get_new_auth_token(self):
        session_manager = self.session_manager

        headers = {
            'Accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': session_manager.get_auth_header()
        }

        payload = {
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }

        r = requests.post(session_manager.access_token_url, data=payload, headers=headers)
        print(r.status_code)
        print(r.text)
        print(session_manager.get_auth_header())
        if r.status_code != 200:
            return r.text

        bearer_raw = json.loads(r.text)

        session_manager.x_refresh_token_expires_in = bearer_raw['x_refresh_token_expires_in']
        session_manager.access_token = bearer_raw['access_token']
        session_manager.token_type = bearer_raw['token_type']
        session_manager.refresh_token = bearer_raw['refresh_token']
        session_manager.expires_in = bearer_raw['expires_in']
        refresh_token = session_manager.refresh_token
        return refresh_token

    def get_customer(self):
        customers = Customer.all(qb=self.client)
        for customer in customers:
            print(customer.to_ref().name, customer.to_ref().value)
        return customers

    def get_items(self):
        items = Item.all(qb=self.client)
        for item in items:
            print(item.to_ref().name, item.to_ref().value)
        return items

    def do_customer_exists(self, customer_ref_no):
        # customer = Customer.get(customer_ref_no, qb=self.client)
        customers = Customer.filter(Active=True, id=customer_ref_no, qb=self.client)
        if len(customers) > 0:
            return True
        return False

    def are_line_item_codes_valid(self, codes):
        code_unique = list(set(codes))
        print("unique codes", code_unique)
        items = Item.choose(code_unique, qb=self.client)
        if len(items) not in [len(code_unique)]:
            return False
        return True

    def get_customer_by_id(self, customer_ref_no):
        customer = Customer.get(customer_ref_no, qb=self.client)
        return customer

    def get_items_from_list(self, codes):
        code_unique = list(set(codes))
        print("unique codes", code_unique)
        items = Item.choose(code_unique, qb=self.client)
        items_result = dict()
        for item in items:
            items_result[item.Id] = item
        return items_result

    def get_tax_codes(self):
        tax_codes = TaxCode.all(qb=self.client)
        return tax_codes

    def get_tax_rate(self):
        tax_codes = TaxRate.all(qb=self.client)
        return tax_codes

    def save_invoice(self, invoice):
        invoice.save(qb=self.client)

    def get_report_receivables(self):
        result = self.client.get_report(report_type="AgedReceivables")
        return result

