# Generated by Django 4.1.5 on 2023-01-18 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recapp', '0005_alter_url_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crawlingtarget',
            name='url',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
