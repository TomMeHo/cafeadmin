# Generated by Django 5.0 on 2024-02-14 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shift_planner', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shift',
            options={'permissions': (('can_register_others', 'Register other users'), ('does_planning', 'Sees planning relevant details')), 'verbose_name': 'Schicht', 'verbose_name_plural': 'Schichten'},
        ),
    ]
