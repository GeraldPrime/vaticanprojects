from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("estate", "0027_add_created_by_to_property_sale"),
    ]

    operations = [
        migrations.AlterField(
            model_name="propertysale",
            name="description",
            field=models.TextField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="propertysale",
            name="marital_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("single", "Single"),
                    ("married", "Married"),
                    ("divorced", "Divorced"),
                    ("widowed", "Widowed"),
                ],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="propertysale",
            name="original_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
