# Generated by Django 5.1.4 on 2025-01-17 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0002_knowledgebase_product"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="sender",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
