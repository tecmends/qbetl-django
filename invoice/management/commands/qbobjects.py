# -*- coding: ascii -*-
from django.core.management.base import BaseCommand, CommandError
from invoice.invoiceoperation import InvoiceOperations


class Command(BaseCommand):
    help = 'Import Invoices from CSV for user by id'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int)

        parser.add_argument(
            '--customers',
            action='store_true',
            dest='customers',
            help='List all customer',
        )

        parser.add_argument(
            '--items',
            action='store_true',
            dest='items',
            help='List all Items',
        )

        parser.add_argument(
            '--taxcodes',
            action='store_true',
            dest='taxcodes',
            help='List all Items',
        )

        parser.add_argument(
            '--taxrates',
            action='store_true',
            dest='taxrates',
            help='List all Items',
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        print(options)
        io = InvoiceOperations(user_id=user_id)

        if options['customers']:
            print("Displaying customers")
            io.get_customer()

        if options['items']:
            print("Displaying Items")
            io.get_items()

        if options['taxrates']:
            print("Displaying taxes")
            rates = io.get_tax_rate()
            for rate in rates:
                print(rate.Name, rate)

        if options['taxcodes']:
            print("Displaying taxes")
            codes = io.get_tax_codes()
            for code in codes:
                print(code.to_ref(), code.to_ref().value)
