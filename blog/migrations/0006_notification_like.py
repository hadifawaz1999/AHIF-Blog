# Generated by Django 3.0.6 on 2020-10-19 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_notification_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='like',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.Like'),
        ),
    ]
