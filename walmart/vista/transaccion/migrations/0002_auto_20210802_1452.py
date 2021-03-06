# Generated by Django 2.2.12 on 2021-08-02 14:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('transaccion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_error', models.IntegerField(verbose_name='Id error')),
                ('descripcion', models.CharField(max_length=200, verbose_name='Descripcion')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha transaccion')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')),
            ],
            options={
                'verbose_name': 'Error',
                'verbose_name_plural': 'Error',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Respuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_respuesta', models.IntegerField(verbose_name='Id resupesta')),
                ('descripcion', models.CharField(max_length=200, verbose_name='Descripcion')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha transaccion')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')),
            ],
            options={
                'verbose_name': 'Respuesta',
                'verbose_name_plural': 'Respuesta',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Tienda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_tienda', models.IntegerField(verbose_name='Id tienda')),
                ('ubicacion', models.CharField(max_length=200, verbose_name='Ubicacion')),
                ('activo', models.BooleanField(verbose_name='Activa')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha creacion')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')),
            ],
            options={
                'verbose_name': 'Tienda',
                'verbose_name_plural': 'Tienda',
                'ordering': ['-created'],
            },
        ),
        migrations.AddField(
            model_name='transaccion',
            name='det_estacionamiento',
            field=models.CharField(default=0, max_length=200, verbose_name='Numero estacionamiento'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaccion',
            name='no_provedor',
            field=models.CharField(default=0, max_length=200, verbose_name='Proveedor'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Terminal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_terminal', models.IntegerField(verbose_name='Id terminal')),
                ('clave', models.CharField(max_length=200, verbose_name='Clave')),
                ('activo', models.BooleanField(verbose_name='Activa')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha creacion')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')),
                ('equipo_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='get_terminal', to='transaccion.Tienda', verbose_name='Tienda')),
            ],
            options={
                'verbose_name': 'Terminal',
                'verbose_name_plural': 'Terminal',
                'ordering': ['-created'],
            },
        ),
    ]
