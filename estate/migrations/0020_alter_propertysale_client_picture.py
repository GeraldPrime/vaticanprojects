# Generated by Django 5.1.4 on 2025-06-26 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate', '0019_propertysale_client_picture_propertysale_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertysale',
            name='client_picture',
            field=models.ImageField(blank=True, default='static/user/images/pph.jpeg', null=True, upload_to='client_pictures/'),
        ),
    ]
