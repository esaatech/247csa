# Generated by Django 5.1.4 on 2025-05-21 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csa', '0003_alter_csa_firebase_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='csa',
            name='knowledge_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
