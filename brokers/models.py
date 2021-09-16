from django.db import models

class Broker(models.Model):
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    def __str__(self):
        return self.name