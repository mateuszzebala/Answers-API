# Generated by Django 4.1.2 on 2022-10-27 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='number',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='task',
            name='number',
            field=models.CharField(max_length=30),
        ),
    ]