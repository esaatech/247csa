from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

def forwards_func(apps, schema_editor):
    # Get the historical version of the models
    Customer = apps.get_model("mycrm", "Customer")
    User = apps.get_model("auth", "User")
    
    # Get the first user (or create one if none exists)
    default_user = User.objects.first()
    if not default_user:
        default_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin'
        )
    
    # Update all existing customers
    Customer.objects.filter(created_by__isnull=True).update(created_by=default_user)

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mycrm', '0004_populate_activity_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='customers',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.RunPython(forwards_func),
        migrations.AlterField(
            model_name='customer',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='customers',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ] 