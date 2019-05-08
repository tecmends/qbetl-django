import json

import requests
from django.test import TestCase

# Create your tests here.
from quickbooks import Oauth2SessionManager, QuickBooks
from quickbooks.objects import Invoice, Item, SalesItemLine, SalesItemLineDetail
from quickbooks.objects.customer import Customer

MAPPING_MOCK = '''
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

MAPPING_MOCK_LEGACY = '''
[
    {
    	"QBField_dataType": "String",
		"QBField_fieldType": "Header",
		"QBField_disable": true,
		"QBField_label": "Invoice Number",
		"QBField_required": true,
		"QBField_code": "DocNumber",

		"SourceField_fieldType": "Header",
		"SourceField_type": "String",
		"SourceField_fieldXPath": "invoicenumber",
		"SourceField_fieldLabel": "Invoice Number",
		"SourceField_code": "InvoiceNumber"
    },
	{
		"QBField_dataType": "String",
		"QBField_fieldType": "Header",
		"QBField_disable": true,
		"QBField_label": "Invoice Number",
		"QBField_required": true,
		"QBField_code": "DocNumber",
		
		"SourceField_fieldType": "Header",
		"SourceField_type": "String",
		"SourceField_fieldXPath": "invoicenumber",
		"SourceField_fieldLabel": "Invoice Number",
		"SourceField_code": "InvoiceNumber"
    },
	{
		"QBField_dataType": "String",
		"QBField_fieldType": "Header",
		"QBField_disable": true,
		"QBField_label": "Customer Number",
		"QBField_required": true,
		"QBField_code": "CustomerRef",

		"SourceField_fieldType": "Header",
		"SourceField_type": "String",
		"SourceField_fieldXPath": "customerrefno",
		"SourceField_fieldLabel": "Customer Number",
		"SourceField_code": "InvoiceNumber"
	},
	{
		"QBField_dataType": "String",
		"QBField_fieldType": "Header",
		"QBField_disable": true,
		"QBField_label": "Due Date",
		"QBField_required": true,
		"QBField_code": "DueDate",

		"SourceField_fieldType": "Header",
		"SourceField_type": "String",
		"SourceField_fieldXPath": "duedate",
		"SourceField_fieldLabel": "Invoice DueDate",
		"SourceField_code": "InvoiceNumber"
	},

	{
		"QBField_dataType": "Number",
		"QBField_fieldType": "Line",
		"QBField_disable": true,
		"QBField_label": "Line No",
		"QBField_required": true,
		"QBField_code": "LineNum",

		"SourceField_fieldType": "Line",
		"SourceField_type": "Number",
		"SourceField_fieldLabel": "Line Number",
		"SourceField_fieldXPath": "lineno"
	},
	{
		"QBField_dataType": "String",
		"QBField_fieldType": "Line",
		"QBField_disable": true,
		"QBField_label": "LineItem Code",
		"QBField_required": true,
		"QBField_code": "ItemRefValue",

		"SourceField_fieldType": "Line",
		"SourceField_type": "String",
		"SourceField_fieldLabel": "Line Item Code",
		"SourceField_fieldXPath": "itemcode"
	},
	{
		"QBField_dataType": "String",
		"QBField_fieldType": "Line",
		"QBField_disable": true,
		"QBField_label": "LineItem Description",
		"QBField_required": true,
		"QBField_code": "Description",

		"SourceField_fieldType": "Line",
		"SourceField_type": "String",
		"SourceField_fieldLabel": "Line Item Description",
		"SourceField_fieldXPath": "itemdesc"
	},
	{
		"QBField_dataType": "Number",
		"QBField_fieldType": "Line",
		"QBField_disable": true,
		"QBField_label": "Rate",
		"QBField_required": true,
		"QBField_code": "UnitPrice",

		"SourceField_fieldType": "Line",
		"SourceField_type": "String",
		"SourceField_fieldLabel": "Unit Rate",
		"SourceField_fieldXPath": "unitprice"
	} ,          
	{
		"QBField_dataType": "Number",
		"QBField_fieldType": "Line",
		"QBField_disable": true,
		"QBField_label": "Quantity",
		"QBField_required": true,
		"QBField_code": "QTY",

		"SourceField_fieldType": "Line",
		"SourceField_type": "Number",
		"SourceField_fieldLabel": "Quantity",
		"SourceField_fieldXPath": "qty"
	}	
]
'''

# CLIENT_ID = 'Q0JaG7yQRQB4hdA6c3x6XdoFWiGyi1A4kJi68Od6OqXMG3Z7y7'
# CLIENT_SECRET = '0cTWZymkVMlfdrWFg9qHFp83cQlFv8759XOurT5U'
# realm_id = '193514610016949'
# REFRESH_TOKEN = 'Q011536837751d1wPipP5U4GgcuHE4dEe2BXJp4N7kw8bQMVyj'
# AUTH2_ACCESS_TOKEN = 'eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..NUeLQn9FqNfVeCucwnGkYw.M4REZPvAmAsEf2afCiA9S_TS1AVVbZShGnL3D1ijPmDX84f3L-nDVNSSuDQjrFr3bVpmvrX0xb5de0HpwJSaoZXr2SDkayu1r2nuAqXucwyHWOBOH-trJKnndmbqNCjQDtpB0s1igRsS-0vS8ebhs5Ay7WyN6s5pROF82BviZ-hUR8PchJtT8iaSyVLFRoCEIFKlYzEmKkIZHBtnQ6J2kdOyktmAcTazFFuXtJlhpK1C8sKWxdVkpPtSnDBSfmgIGUbZvqCUGnWUYMnjPQhLTmkhEnwrMdPbI9iLMQiqrK8dM-XyHPv8i-npsDINiEhL9jgMD8DbiaS6xKA8Kzg_bEr71X3EBrFsDTzFGcBdyMhB7OX0vwKp8sVFI3D63bITFvLiCSDmQRd9wKDIeGnx3f2LhRLb7x5huMl0YJfIMcKU-przcmXA2-Su5Hxkt1-O_u88ANa-LHuAGkMgmO5WK8D7Tg6dGLOcsyY2fU-fYabMfE7BhjWGftW7C_l7UHULHdpkw6yIqGAaGjmO-CYO9OkQbCErIO1HjbitnVG88_QD-Qn2c-Umyu-0UhI_UnOQLcjO4cr4MTTwNLvzwA9QKwhl3mt26JSOx5jZ_MZEqcw5-y4Qm1buVN7kAS6CBubcb5px0qL8qJuoV_hHKsgStCDZToUFH5wGv9-Q68sK43IR-TH0NsxaO7sCOHsDGQ5I.fh8QXfcVLDH37q6eXboQug'
#
#
# session_manager = Oauth2SessionManager(
#     client_id=CLIENT_ID,
#     client_secret=CLIENT_SECRET,
#     access_token=AUTH2_ACCESS_TOKEN,
# )
#
# client = QuickBooks(
#     sandbox=True,
#     session_manager=session_manager,
#     company_id=realm_id
# )
#
#
# def get_customer():
#     customers = Customer.all(qb=client)
#     for customer in customers:
#         print(customer.to_ref().name, customer.to_ref().value)
#
#
# def create_invoice(item_id):
#     invoice = Invoice()
#
#     line = SalesItemLine()
#     line.LineNum = 1
#     line.Description = "Line 1 description"
#     line.Amount = 100
#     line.SalesItemLineDetail = SalesItemLineDetail()
#
#     item = Item.all(max_results=1, qb=client)[0]
#
#     line.SalesItemLineDetail.ItemRef = item.to_ref()
#     invoice.Line.append(line)
#
#     customer = Customer.all(max_results=1, qb=client)[0]
#     invoice.CustomerRef = customer.to_ref()
#
#     invoice.save(qb=client)
#
#     # query_item = Item.get(item_id, qb=client)
#     # print(query_item.to_ref())
#     # items = Item.all(qb=client)
#     # for item in items:
#     #     print(item.to_ref().name, item.to_ref().value)
#
#
# get_customer()
# #create_invoice(14)
