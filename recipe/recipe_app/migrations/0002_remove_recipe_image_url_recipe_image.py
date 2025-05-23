# Generated by Django 5.0.4 on 2025-01-21 17:50

import recipe_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='image_url',
        ),
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(
                blank=True, null=True, upload_to='recipes/', validators=[recipe_app.models.validate_image]
            ),
        ),
    ]
