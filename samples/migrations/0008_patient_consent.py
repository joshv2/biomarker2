# Generated by Django 2.0.1 on 2018-05-24 00:20

from django.db import migrations, models
import samples.models


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0007_auto_20180516_2107'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='consent',
            field=models.FileField(default='', upload_to=samples.models.user_directory_path),
        ),
    ]
