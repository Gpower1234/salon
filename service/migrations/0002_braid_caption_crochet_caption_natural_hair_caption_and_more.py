# Generated by Django 4.1.7 on 2023-04-18 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='braid',
            name='caption',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='crochet',
            name='caption',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='natural_hair',
            name='caption',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='other_service',
            name='caption',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='twist',
            name='caption',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='braid',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='crochet',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='natural_hair',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='other_service',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='twist',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
    ]