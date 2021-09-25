from django.db import models
from datetime import datetime
from brokers.models import Broker

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('BUY', 'BUY'),
        ('SELL', 'SELL'),
    ]

    exchange = models.CharField(max_length=50,null=True)
    coin = models.CharField(max_length=20)
    transType = models.CharField(max_length=5, verbose_name='Type', choices=TYPE_CHOICES, default='BUY')
    priceAtBought = models.DecimalField(decimal_places=2, max_digits=18, verbose_name='Bought Price')
    purchasedDate = models.DateTimeField(default=datetime.now, verbose_name='Purchased Date')
    qty = models.DecimalField(decimal_places=4, max_digits=18)
    fees = models.DecimalField(decimal_places=2, max_digits=18)
    notes = models.TextField(blank=True)
    def __str__(self):
        return self.coin + ' (' + self.exchange + ')'