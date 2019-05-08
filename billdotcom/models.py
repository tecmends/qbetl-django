from django.db import models
from jsonfield import JSONField


class BillSession(models.Model):
    session_id = models.CharField(max_length=500)
    device_id = models.CharField(max_length=500, default='', blank=True)
    challenge_id = models.CharField(max_length=500, default='', blank=True)
    mfa_id = models.CharField(max_length=500, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class Bill(models.Model):
    bill_id = models.CharField(max_length=50)
    is_active = models.CharField(max_length=20, default='1')
    vendor_id = models.CharField(max_length=50)
    invoice_number = models.CharField(max_length=50)
    approval_status = models.CharField(max_length=50, default='1')
    amount = models.FloatField(default=0.0)
    paid_amount = models.FloatField(default=0.0)
    due_amount = models.FloatField(default=0.0)
    json_data = JSONField()

    def __str__(self):
        return str(self.id)


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    bill_item_id = models.CharField(max_length=50)
    amount = models.FloatField(default=0.0)
    json_data = JSONField()

    def __str__(self):
        return str(self.id)
