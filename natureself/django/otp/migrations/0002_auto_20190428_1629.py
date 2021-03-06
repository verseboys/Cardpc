# Generated by Django 2.1.5 on 2019-04-28 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('otp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailverifycode',
            name='clone',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='otp.EmailVerifyCode'),
        ),
        migrations.AddField(
            model_name='smsverifycode',
            name='clone',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='otp.SmsVerifyCode'),
        ),
        migrations.AlterField(
            model_name='emailverifycode',
            name='usage',
            field=models.TextField(choices=[('login', '登录验证码'), ('register', '注册验证码'), ('reset-password', '重置密码')]),
        ),
        migrations.AlterField(
            model_name='smsverifycode',
            name='usage',
            field=models.TextField(choices=[('login', '登录验证码'), ('register', '注册验证码'), ('reset-password', '重置密码')]),
        ),
    ]
