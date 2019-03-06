# Generated by Django 2.1.7 on 2019-03-06 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Screencast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='screencasts/')),
                ('image', models.ImageField(upload_to='screencasts/images')),
                ('title', models.CharField(max_length=100)),
                ('urlname', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=350)),
                ('selected_for_help', models.BooleanField(default=False, help_text='Display this screencast on the main help page?')),
                ('importance', models.IntegerField(blank=True, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')], null=True)),
            ],
            options={
                'db_table': 'mm_screencast',
            },
        ),
        migrations.CreateModel(
            name='YoutubeScreencast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('youtube_id', models.CharField(help_text='Youtube video id (hint: http://www.youtube.com/watch?v=<YOUTUBE_VIDEO_ID>)', max_length=24, unique=True)),
                ('image', models.ImageField(upload_to='screencasts/images')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=350)),
                ('selected_for_help', models.BooleanField(default=False, help_text='Display this screencast on the main help page?')),
                ('importance', models.IntegerField(blank=True, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')], null=True)),
                ('video_width', models.IntegerField(default=853)),
                ('video_height', models.IntegerField(default=505)),
                ('play_hd', models.BooleanField(default=True)),
            ],
        ),
    ]
