# Generated by Django 5.1.4 on 2025-01-10 06:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('UserProfile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=255)),
                ('recipients', models.TextField(blank=True, null=True)),
                ('body', models.TextField(blank=True, null=True)),
                ('received_at', models.DateTimeField()),
                ('is_read', models.BooleanField(default=False)),
                ('is_replied', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('email_id', models.CharField(max_length=255)),
                ('thread_id', models.CharField(blank=True, max_length=255, null=True)),
                ('subject', models.CharField(blank=True, max_length=255, null=True)),
                ('labels', models.TextField(blank=True, null=True)),
                ('attachment_count', models.IntegerField(default=0)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserProfile.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OAuthToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.TextField(blank=True, null=True)),
                ('refresh_token', models.TextField(blank=True, null=True)),
                ('token_type', models.CharField(blank=True, max_length=50, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('scopes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oauth_tokens', to='UserProfile.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='WhatsAppMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=255)),
                ('recipients', models.TextField(blank=True, null=True)),
                ('body', models.TextField(blank=True, null=True)),
                ('received_at', models.DateTimeField()),
                ('is_read', models.BooleanField(default=False)),
                ('is_replied', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('message_id', models.CharField(max_length=255)),
                ('media_url', models.URLField(blank=True, null=True)),
                ('media_type', models.CharField(blank=True, max_length=50, null=True)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserProfile.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
