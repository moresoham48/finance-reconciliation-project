from django.db import models
from django.contrib import admin
from .models import *

class BankStatement(models.Model):
    date = models.DateField()
    narration = models.TextField()
    amount = models.FloatField()
    type = models.CharField(max_length=10)

class InternalLedger(models.Model):
    date = models.DateField()
    description = models.TextField()
    amount = models.FloatField()
    category = models.CharField(max_length=50)

class FinalLedger(models.Model):
    date = models.DateField()
    amount = models.FloatField()
    category = models.CharField(max_length=50)
    source = models.CharField(max_length=20)
    reconciliation_status = models.CharField(max_length=20)


admin.site.register(BankStatement)
admin.site.register(InternalLedger)
admin.site.register(FinalLedger)


class FinalLedger(models.Model):
    date = models.DateField()
    amount = models.FloatField()
    category = models.CharField(max_length=50)
    source = models.CharField(max_length=20)
    reconciliation_status = models.CharField(max_length=20)