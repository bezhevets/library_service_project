# Generated by Django 4.2.9 on 2024-02-01 14:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="payment",
            old_name="borrowing_id",
            new_name="borrowing",
        ),
    ]
