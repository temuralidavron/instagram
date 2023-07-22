# Generated by Django 4.2.3 on 2023-07-13 19:34

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_id_alter_userconfirmation_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('43f5924b-ce0a-47a4-b611-38eed90ba039'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='userconfirmation',
            name='id',
            field=models.UUIDField(default=uuid.UUID('43f5924b-ce0a-47a4-b611-38eed90ba039'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
