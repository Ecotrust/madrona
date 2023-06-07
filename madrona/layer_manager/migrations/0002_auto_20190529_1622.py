# Generated by Django 2.2.1 on 2019-05-29 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layer_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataneed',
            name='themes',
            field=models.ManyToManyField(blank=True, to='layer_manager.Theme'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='attribute_fields',
            field=models.ManyToManyField(blank=True, to='layer_manager.AttributeInfo'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='lookup_table',
            field=models.ManyToManyField(blank=True, to='layer_manager.LookupInfo'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='sublayers',
            field=models.ManyToManyField(blank=True, help_text='Select the PARENT layer (which should be checkbox or radio type). Be sure to also check is_sublayer.', related_name='_layer_sublayers_+', to='layer_manager.Layer'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='themes',
            field=models.ManyToManyField(to='layer_manager.Theme'),
        ),
    ]