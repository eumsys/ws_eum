# Generated by Django 2.1.5 on 2021-11-11 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaccion', '0008_auto_20211019_1154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boleto',
            name='codigo',
        ),
        migrations.AddField(
            model_name='boleto',
            name='estado',
            field=models.IntegerField(default=1, verbose_name='Estado'),
        ),
    ]
