# Generated by Django 2.2 on 2019-05-01 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wordbuilder', '0004_auto_20190501_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistics',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_statistics', to=settings.AUTH_USER_MODEL),
        ),
    ]
