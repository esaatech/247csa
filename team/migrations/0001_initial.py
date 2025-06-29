# Generated by Django 5.1.4 on 2025-06-09 18:24

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='owned_teams', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TeamInvitation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254)),
                ('role', models.CharField(choices=[('owner', 'Owner'), ('admin', 'Admin'), ('member', 'Member')], default='member', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_accepted', models.BooleanField(default=False)),
                ('invited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_sent', to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='team.team')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('owner', 'Owner'), ('admin', 'Admin'), ('member', 'Member')], default='member', max_length=20)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('invited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_invites_sent', to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='team.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['joined_at'],
                'unique_together': {('team', 'user')},
            },
        ),
    ]
