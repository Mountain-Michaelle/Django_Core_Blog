# Generated by Django 4.2.13 on 2024-07-01 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='body',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
