import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solicitud_id', models.IntegerField(unique=True)),
                ('riesgo_score', models.FloatField(default=0.0)),
                ('recomendaciones', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Matching',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('centro_asignado', models.CharField(max_length=255)),
                ('recursos', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('evaluacion', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='matching', to='evaluacion_app.evaluacion')),
            ],
        ),
    ]
