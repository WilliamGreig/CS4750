# Generated by Django 4.1.5 on 2023-02-21 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('die', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerbigpointstats',
            name='catches',
            field=models.IntegerField(default=0),
        ),
    ]
