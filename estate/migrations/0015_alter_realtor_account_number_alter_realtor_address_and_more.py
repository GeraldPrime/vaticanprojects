# Generated by Django 5.1.4 on 2025-05-31 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate', '0014_gallery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realtor',
            name='account_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='realtor',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='realtor',
            name='bank_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='realtor',
            name='country',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='realtor',
            name='first_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='realtor',
            name='last_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='realtor',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
