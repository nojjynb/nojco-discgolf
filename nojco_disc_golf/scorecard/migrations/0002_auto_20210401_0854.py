# Generated by Django 3.1.7 on 2021-04-01 13:54

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('scorecard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='handicap_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 1, 13, 54, 42, 470593, tzinfo=utc), verbose_name='date'),
        ),
    ]