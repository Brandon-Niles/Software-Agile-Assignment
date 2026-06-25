from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_seed_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('main', 'UserProfile')

    # Create or update admin user
    admin, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@example.com',
    })
    admin.password = make_password('adminpass')
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()
    UserProfile.objects.update_or_create(user=admin, defaults={'role': 'admin'})

    # Create or update regular user
    client, created = User.objects.get_or_create(username='user', defaults={
        'email': 'user@example.com',
    })
    client.password = make_password('userpass')
    client.is_superuser = False
    client.is_staff = False
    client.save()
    UserProfile.objects.update_or_create(user=client, defaults={'role': 'client'})


def remove_seed_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username__in=['admin', 'user']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_add_owner_field'),
    ]

    operations = [
        migrations.RunPython(create_seed_users, remove_seed_users),
    ]
