# Generated by Django 2.2 on 2019-05-09 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wordbuilder', '0006_auto_20190501_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wordset',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='media/'),
        ),
    ]