# Generated by Django 3.1.7 on 2021-04-01 13:55

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('scorecard', '0002_auto_20210401_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='handicap_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 1, 13, 55, 5, 380737, tzinfo=utc), verbose_name='date'),
        ),
    ]
