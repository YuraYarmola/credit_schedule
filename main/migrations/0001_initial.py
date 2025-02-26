# Generated by Django 5.1.1 on 2024-09-04 20:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_start_date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('number_of_payments', models.IntegerField()),
                ('periodicity', models.CharField(max_length=2)),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('principal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('interest', models.DecimalField(decimal_places=2, max_digits=10)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='main.paymentschedule')),
            ],
        ),
    ]
