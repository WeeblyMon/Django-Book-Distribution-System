# Generated by Django 4.2.20 on 2025-03-17 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='publishing_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
