# Generated by Django 5.1.4 on 2025-05-13 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='csa',
            name='firebase_path',
            field=models.CharField(default='', help_text="Path to this CSA's data in Firebase", max_length=255),
            preserve_default=False,
        ),
    ]
