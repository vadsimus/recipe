# Generated by Django 5.0.4 on 2024-05-05 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=2),
        ),
        migrations.AddField(
            model_name='recipe',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='image_url',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
