# Generated by Django 4.1.5 on 2023-01-18 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recapp', '0004_alter_response_status_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='url',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
