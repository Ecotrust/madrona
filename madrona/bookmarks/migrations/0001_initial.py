# Generated by Django 2.1.7 on 2019-04-30 16:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0009_alter_user_last_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Date Modified')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('altitude', models.FloatField()),
                ('heading', models.FloatField(default=0)),
                ('tilt', models.FloatField(default=0)),
                ('roll', models.FloatField(default=0)),
                ('altitudeMode', models.FloatField(default=1)),
                ('ip', models.GenericIPAddressField(blank=True, default='0.0.0.0', null=True)),
                ('publicstate', models.TextField(default='{}')),
                ('content_type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='bookmarks_bookmark_related', to='contenttypes.ContentType')),
                ('sharing_groups', models.ManyToManyField(blank=True, editable=False, null=True, related_name='bookmarks_bookmark_related', to='auth.Group', verbose_name='Share with the following groups')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks_bookmark_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
