# Generated by Django 4.1.7 on 2023-04-14 23:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0007_remove_braid_description_remove_crochet_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='braid',
            name='caption',
        ),
        migrations.RemoveField(
            model_name='braid',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='crochet',
            name='caption',
        ),
        migrations.RemoveField(
            model_name='crochet',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='natural_hair',
            name='caption',
        ),
        migrations.RemoveField(
            model_name='natural_hair',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='other_service',
            name='caption',
        ),
        migrations.RemoveField(
            model_name='other_service',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='twist',
            name='caption',
        ),
        migrations.RemoveField(
            model_name='twist',
            name='duration',
        ),
    ]
