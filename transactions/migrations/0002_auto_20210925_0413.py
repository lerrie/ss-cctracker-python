# Generated by Django 3.2.6 on 2021-09-25 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='broker',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='coin',
            field=models.CharField(max_length=20),
        ),
    ]
