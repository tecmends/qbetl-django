from __future__ import absolute_import, unicode_literals

from celery import Celery
import os

from celery.signals import task_failure

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qbetl.settings')

app = Celery('qbetl')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def process_invoice_batch(self, csv_file_id):
    print(csv_file_id)
    from invoice.models import CsvFile, CsvFileResults
    from invoice.csvfileutils import process_csv
    csv_file = CsvFile.objects.get(id=csv_file_id)
    print(csv_file)
    process_csv(csv_file)
    csv_file.status = 'C'
    csv_file.save()


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, traceback=None, einfo=None, **kwargs):
    print("Sender:", sender.name)
    print("Failure tasks:{}".format(task_id))
    print("Exception:", exception)
    print("args", int(args[0]))
    if sender:
        if sender.name == "qbetl.celery.process_invoice_batch":
            csv_file_id = int(args[0])
            from invoice.models import CsvFile, CsvFileResults
            csv_file = CsvFile.objects.get(id=csv_file_id)
            csv_file.status = 'F'
            csv_file.save()
