# Generated by Django 4.1.5 on 2023-01-13 22:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recapp', '0002_url_source'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='added',
        ),
    ]