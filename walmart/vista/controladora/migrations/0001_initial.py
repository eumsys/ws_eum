# Generated by Django 2.2.12 on 2020-05-08 19:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('equipo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Controladora',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_serie', models.CharField(default='-', max_length=200, verbose_name='Numero de serie')),
                ('version_tarjeta', models.DecimalField(decimal_places=5, max_digits=15, verbose_name='Version tarjeta')),
                ('version_firmware', models.DecimalField(decimal_places=5, max_digits=15, verbose_name='Version firmware')),
                ('tipo', models.CharField(choices=[('Controladora Arduino', 'Controladora Arduino'), ('Controladora Raspberry', 'Controladora Raspberry'), ('Controladora Pulso', 'Controladora Pulso')], default='Controladora Arduino', max_length=50, verbose_name='Tipo')),
                ('modo_operacion', models.CharField(choices=[('Expedidor', 'Expedidor'), ('Validador', 'Validador'), ('Cajero', 'Cajero'), ('Punto de cobro', 'Punto de cobro'), ('Servidor', 'Servidor')], default='Expedidor', max_length=50, verbose_name='Modo operacion')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de pago')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')),
                ('equipo_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='get_controladora', to='equipo.Equipo', verbose_name='Equipo')),
            ],
            options={
                'verbose_name': 'Controladora',
                'verbose_name_plural': 'Controladora',
                'ordering': ['-tipo'],
            },
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(default='-', max_length=200, verbose_name='Nombre')),
                ('version_firmware', models.DecimalField(decimal_places=5, max_digits=15, verbose_name='Version firmware')),
                ('unidad_medicion', models.CharField(choices=[('Grados', 'Grados'), ('Centimetros', 'Centimetros'), ('Otro', 'Otro')], default='grados', max_length=50, verbose_name='Unidad de medicion')),
                ('tipo', models.CharField(choices=[('Temperatura', 'Temperatura'), ('Presencia', 'Presencia'), ('Humedad', 'Humedad')], default='Controladora Arduino', max_length=50, verbose_name='Tipo')),
                ('activo', models.BooleanField(verbose_name='Activo')),
                ('valor', models.DecimalField(decimal_places=5, default=0, max_digits=15, verbose_name='Valor')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de pago')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')),
                ('controladora_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='get_sensor', to='controladora.Controladora', verbose_name='Controladora')),
            ],
            options={
                'verbose_name': 'Sensor',
                'verbose_name_plural': 'Sensor',
                'ordering': ['-tipo'],
            },
        ),
    ]