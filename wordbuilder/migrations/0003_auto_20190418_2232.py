# Generated by Django 2.2 on 2019-04-18 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wordbuilder', '0002_auto_20190418_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wordset',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]