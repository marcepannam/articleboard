# Generated by Django 4.1.5 on 2023-01-13 22:33

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
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1000)),
                ('article_text', models.TextField(max_length=1000000)),
                ('short_description', models.TextField(max_length=10000)),
                ('added', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CrawlingTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=200)),
                ('last_successful_crawl', models.DateTimeField()),
                ('last_crawl', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('keywords', models.TextField(default='', max_length=10000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0))),
                ('status_code', models.IntegerField(default=None)),
                ('was_successful', models.BooleanField(default=False)),
                ('error_type', models.CharField(blank=True, choices=[('HttpError', 'HttpError'), ('GeneralError', 'GeneralError'), ('none', 'none')], default='none', max_length=200, null=True)),
                ('error_message', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('url', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='recapp.url')),
            ],
        ),
        migrations.CreateModel(
            name='DashboardArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like_or_dislike', models.CharField(choices=[('like', 'like'), ('dislike', 'dislike'), ('none', 'none')], default='none', max_length=200)),
                ('added', models.DateTimeField()),
                ('is_no_longer_recommended', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recapp.article')),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recapp.dashboard')),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='url',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='article', to='recapp.url'),
        ),
    ]