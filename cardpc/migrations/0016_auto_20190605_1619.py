# Generated by Django 2.2.1 on 2019-06-05 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardpc', '0015_projectpage_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectnews',
            name='excerpt',
            field=models.TextField(default='', verbose_name='摘要'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='status',
            field=models.TextField(choices=[('published', '已发布'), ('draft', '草稿')], default='draft', verbose_name='状态'),
        ),
    ]
