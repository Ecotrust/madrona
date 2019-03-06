# Generated by Django 2.1.7 on 2019-03-06 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MapConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mapname', models.CharField(max_length=50, unique=True)),
                ('mapfile', models.FileField(help_text='\n        Mapnik xml configuration file that defines data sources and styles. \n        All paths within xml must be relative to media/staticmap/\n    ', max_length=510, upload_to='staticmap/')),
                ('default_x1', models.FloatField(help_text='Lower-left X coordinate of default map extent. Units and spatial reference system are defined in the mapnik xml.')),
                ('default_y1', models.FloatField(help_text='Lower-left Y coordinate of default map extent. Units and spatial reference system are defined in the mapnik xml.')),
                ('default_x2', models.FloatField(help_text='Upper-right X coordinate of default map extent. Units and spatial reference system are defined in the mapnik xml.')),
                ('default_y2', models.FloatField(help_text='Upper-right Y coordinate of default map extent. Units and spatial reference system are defined in the mapnik xml.')),
                ('default_width', models.IntegerField(help_text='Default map image width in pixels')),
                ('default_height', models.IntegerField(help_text='Default map image height in pixels')),
                ('default_srid', models.IntegerField(default=4326, help_text='Spatial Reference ID of the output map')),
            ],
        ),
    ]
