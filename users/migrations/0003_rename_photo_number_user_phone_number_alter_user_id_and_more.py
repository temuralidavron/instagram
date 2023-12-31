# Generated by Django 4.2.3 on 2023-07-10 08:05

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_id_alter_user_photo_userconfirmation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='photo_number',
            new_name='phone_number',
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('b65227f0-4ec0-49bb-993a-eb40dc83a440'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='userconfirmation',
            name='id',
            field=models.UUIDField(default=uuid.UUID('b65227f0-4ec0-49bb-993a-eb40dc83a440'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
