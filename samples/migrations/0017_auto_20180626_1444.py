# Generated by Django 2.0.1 on 2018-06-26 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0016_auto_20180626_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='ns_antibody',
            field=models.CharField(max_length=100),
        ),
    ]
