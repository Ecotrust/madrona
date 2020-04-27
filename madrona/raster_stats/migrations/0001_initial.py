# Generated by Django 2.1.7 on 2019-03-06 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RasterDataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('full_name', models.CharField(default='', max_length=255)),
                ('filepath', models.FilePathField(max_length=255, path='/usr/local/apps/forestplanner/apps/madrona/madrona/raster_stats/test_data', recursive=True)),
                ('type', models.CharField(choices=[('continuous', 'continuous'), ('categorical', 'catgorical')], max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='ZonalCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.IntegerField()),
                ('count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ZonalStatsCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geom_hash', models.CharField(max_length=255)),
                ('sum', models.FloatField(blank=True, null=True)),
                ('avg', models.FloatField(blank=True, null=True)),
                ('min', models.FloatField(blank=True, null=True)),
                ('max', models.FloatField(blank=True, null=True)),
                ('mode', models.FloatField(blank=True, null=True)),
                ('median', models.FloatField(blank=True, null=True)),
                ('stdev', models.FloatField(blank=True, null=True)),
                ('nulls', models.FloatField(blank=True, null=True)),
                ('pixels', models.FloatField(blank=True, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('categories', models.ManyToManyField(to='raster_stats.ZonalCategory')),
                ('raster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raster_stats.RasterDataset')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='zonalstatscache',
            unique_together={('geom_hash', 'raster')},
        ),
    ]
