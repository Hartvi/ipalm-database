# Generated by Django 3.2.12 on 2022-03-10 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0007_auto_20220310_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setupelement',
            name='parameters',
            field=models.JSONField(null=True),
        ),
    ]
