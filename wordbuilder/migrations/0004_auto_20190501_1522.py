# Generated by Django 2.2 on 2019-05-01 12:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wordbuilder', '0003_auto_20190418_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='userword',
            name='learn_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_training', models.DateField(blank=True, null=True)),
                ('day_streak', models.IntegerField(default=1)),
                ('record_day_streak', models.IntegerField(default=1)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_statistics', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
