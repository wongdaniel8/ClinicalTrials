# Generated by Django 2.0.1 on 2018-02-28 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicaltrials', '0017_auto_20180126_2326'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='version',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
