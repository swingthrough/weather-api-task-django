# Generated by Django 3.2.4 on 2021-06-22 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_weather_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='weatherforecastday',
            name='average_temp_c',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
            preserve_default=False,
        ),
    ]