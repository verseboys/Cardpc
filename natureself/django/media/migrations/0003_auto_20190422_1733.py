# Generated by Django 2.1.5 on 2019-04-22 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0002_auto_20190311_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='key',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='key',
            field=models.TextField(unique=True),
        ),
    ]
