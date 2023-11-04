# Generated by Django 4.2.4 on 2023-10-31 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_alter_employee_email_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='email_address',
            field=models.EmailField(editable=False, max_length=254, unique=True, verbose_name='email_address'),
        ),
    ]
