from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Emergency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_id', models.IntegerField()),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('reported', 'Reported'), ('dispatched', 'Dispatched'), ('resolved', 'Resolved')], default='reported', max_length=20)),
                ('location', models.JSONField(default=dict)),
                ('reported_at', models.DateTimeField(auto_now_add=True)),
                ('dispatched_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
