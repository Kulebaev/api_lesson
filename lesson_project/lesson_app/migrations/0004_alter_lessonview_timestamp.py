# Generated by Django 4.2.5 on 2023-09-20 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_app', '0003_alter_lessonview_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessonview',
            name='timestamp',
            field=models.DateTimeField(default=None),
        ),
    ]
