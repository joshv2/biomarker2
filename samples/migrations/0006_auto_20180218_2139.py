# Generated by Django 2.0.1 on 2018-02-19 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0005_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_PI',
            field=models.BooleanField(default=False, verbose_name='Are you the Primary Investigator?'),
        ),
    ]
