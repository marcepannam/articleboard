# Generated by Django 4.1.5 on 2023-01-13 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recapp', '0003_remove_article_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='response',
            name='status_code',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
