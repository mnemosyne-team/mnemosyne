# Generated by Django 2.2 on 2019-04-13 14:24

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Definition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'dictionary',
                'verbose_name_plural': 'dictionaries',
            },
        ),
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='LexicalCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
            ],
            options={
                'verbose_name': 'lexical category',
                'verbose_name_plural': 'lexical categories',
            },
        ),
        migrations.CreateModel(
            name='LexicalEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'lexical entry',
                'verbose_name_plural': 'lexical entries',
            },
        ),
        migrations.CreateModel(
            name='Pronunciation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phonetic_spelling', models.CharField(max_length=30)),
                ('audio', models.URLField(blank=True, null=True, verbose_name='audio file url')),
            ],
            options={
                'verbose_name': 'pronunciation',
                'verbose_name_plural': 'pronunciations',
            },
        ),
        migrations.CreateModel(
            name='Sense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='UserWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_progress', models.IntegerField(default=0)),
                ('added', models.DateTimeField(default=datetime.datetime.utcnow)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True)),
            ],
            options={
                'verbose_name': 'word',
                'verbose_name_plural': 'words',
            },
        ),
        migrations.AddIndex(
            model_name='word',
            index=models.Index(fields=['name'], name='wordbuilder_name_935413_idx'),
        ),
        migrations.AddField(
            model_name='userword',
            name='dictionary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='words', to='wordbuilder.Dictionary'),
        ),
        migrations.AddField(
            model_name='userword',
            name='lexical_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_words', to='wordbuilder.LexicalCategory'),
        ),
        migrations.AddField(
            model_name='userword',
            name='pronunciation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_words', to='wordbuilder.Pronunciation'),
        ),
        migrations.AddField(
            model_name='userword',
            name='sense',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_words', to='wordbuilder.Sense'),
        ),
        migrations.AddField(
            model_name='userword',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_words', to='wordbuilder.Word'),
        ),
        migrations.AddField(
            model_name='sense',
            name='lexical_entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='senses', to='wordbuilder.LexicalEntry'),
        ),
        migrations.AddField(
            model_name='lexicalentry',
            name='lexical_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lexical_entries', to='wordbuilder.LexicalCategory'),
        ),
        migrations.AddField(
            model_name='lexicalentry',
            name='pronunciation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lexical_entries', to='wordbuilder.Pronunciation'),
        ),
        migrations.AddField(
            model_name='lexicalentry',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lexical_entries', to='wordbuilder.Word'),
        ),
        migrations.AddIndex(
            model_name='lexicalcategory',
            index=models.Index(fields=['name'], name='wordbuilder_name_c5ed86_idx'),
        ),
        migrations.AddField(
            model_name='example',
            name='sense',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examples', to='wordbuilder.Sense'),
        ),
        migrations.AddField(
            model_name='dictionary',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dictionary', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='definition',
            name='sense',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='definitions', to='wordbuilder.Sense'),
        ),
    ]
