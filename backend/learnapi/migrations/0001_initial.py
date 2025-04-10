# Generated by Django 5.2 on 2025-04-11 11:24

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shared', '0002_video_youtube_title'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SnippetPractice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('perceived_difficulty', models.IntegerField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('snippet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snippet_practices', to='shared.snippet')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snippet_practices', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'snippet')},
            },
        ),
        migrations.CreateModel(
            name='VideoProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_watched', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_progress', to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progresses', to='shared.video')),
            ],
            options={
                'unique_together': {('user', 'video')},
            },
        ),
        migrations.CreateModel(
            name='VocabPractice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_id', models.BigIntegerField(blank=True, null=True)),
                ('state', models.CharField(default='Learning', max_length=20)),
                ('step', models.IntegerField(blank=True, null=True)),
                ('stability', models.FloatField(blank=True, null=True)),
                ('difficulty', models.FloatField(blank=True, null=True)),
                ('due', models.DateTimeField(blank=True, null=True)),
                ('last_review', models.DateTimeField(blank=True, null=True)),
                ('is_blacklisted', models.BooleanField(default=False)),
                ('is_favorite', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocab_practices', to=settings.AUTH_USER_MODEL)),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocab_practices', to='shared.word')),
            ],
            options={
                'unique_together': {('user', 'word')},
            },
        ),
    ]
