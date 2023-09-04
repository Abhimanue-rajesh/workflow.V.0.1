# Generated by Django 4.2.4 on 2023-09-04 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow_app', '0005_selectedtask_reviewed_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=20)),
                ('interest', models.CharField(choices=[('do_not_disturb', 'Do Not Disturb'), ('call_back_later', 'Call Back Later'), ('not_interested', 'Not Interested'), ('not_reachable', 'Not Reachable')], max_length=20)),
                ('lead_source', models.CharField(max_length=255)),
                ('customer_location', models.CharField(max_length=255)),
            ],
        ),
    ]
