# Generated by Django 2.0.1 on 2018-02-19 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0003_auto_20180218_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='sample_status',
            field=models.CharField(choices=[('Consented', 'Consented'), ('Submitted', 'Submitted'), ('Received', 'Received'), ('Tested', 'Tested'), ('Insufficient', 'Insufficient')], max_length=12),
        ),
    ]