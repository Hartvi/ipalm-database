# Generated by Django 3.2.12 on 2022-02-27 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='organization')),
            ],
        ),
        migrations.AlterField(
            model_name='customuser',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.organization'),
        ),
    ]
