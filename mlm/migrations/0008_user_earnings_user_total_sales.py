# Generated by Django 5.0.6 on 2024-05-29 22:33

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlm', '0007_referredusers'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='earnings',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='user',
            name='total_sales',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
    ]