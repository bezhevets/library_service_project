# Generated by Django 5.0.1 on 2024-01-30 15:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowing", "0002_alter_borrowing_actual_return_data_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="borrow_date",
            field=models.DateField(auto_now_add=True),
        ),
    ]