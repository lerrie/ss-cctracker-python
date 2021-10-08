from django.db import models
from datetime import datetime
from django.utils import timezone
from brokers.models import Broker
from .choices import type_choices

class Transaction(models.Model):
    exchange = models.CharField(max_length=50,null=True)
    coin = models.CharField(max_length=20)
    transType = models.CharField(max_length=5, verbose_name='Type', default='BUY')
    priceAtBought = models.DecimalField(decimal_places=2, max_digits=18, verbose_name='Price', default=0.00)
    purchasedDate = models.DateTimeField(default=timezone.now(), verbose_name='Purchased Date')
    qty = models.DecimalField(decimal_places=4, max_digits=18, verbose_name="Qty", default=0.0000)
    fees = models.DecimalField(decimal_places=2, max_digits=18, verbose_name="Fees", default=0.00)
    notes = models.TextField(blank=True, verbose_name="Notes")
    userId = models.IntegerField(default=1) #default 1=admin
    soldQty = models.DecimalField(decimal_places=4, max_digits=18, default=0.0000)
    latestPrice = models.DecimalField(decimal_places=2, max_digits=18, verbose_name='Latest Price', default=0.00)
    def __str__(self):
        return self.coin + ' (' + self.exchange + ')'

    def total(self):
        total_amt = round((self.priceAtBought * self.qty) + self.fees, 2) 
        return total_amt