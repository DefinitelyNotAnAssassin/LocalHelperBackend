# Generated by Django 5.1.5 on 2025-01-30 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Models', '0013_account_isverified_account_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='salary_type',
            field=models.CharField(default='Monthly', max_length=100),
        ),
    ]
