from django.db import models
from datetime import datetime
from brokers.models import Broker

class Transaction(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.DO_NOTHING)
    coin = models.CharField(max_length=10)
    priceAtBought = models.DecimalField(decimal_places=2, max_digits=18)
    purchasedDate = models.DateTimeField(default=datetime.now)
    qty = models.DecimalField(decimal_places=4, max_digits=18)
    fees = models.DecimalField(decimal_places=2, max_digits=18)
    notes = models.TextField(blank=True)
    def __str__(self):
        return self.coin + ' ' + self.broker.name