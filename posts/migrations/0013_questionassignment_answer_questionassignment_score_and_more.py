# Generated by Django 5.0.3 on 2024-10-24 13:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_alter_questioncategory_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='questionassignment',
            name='answer',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='questionassignment',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='questionassignment',
            name='status',
            field=models.CharField(choices=[('pending', '待提交'), ('submitted', '已提交'), ('graded', '已評分')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='questionassignment',
            name='submitted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='questionassignment',
            name='question_data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.questiondata'),
        ),
        migrations.AlterField(
            model_name='questionassignment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='questioncategory',
            name='type',
            field=models.CharField(choices=[('----請選擇類別----', '----請選擇類別----'), ('if-else', 'if-else'), ('for-loop', 'for-loop'), ('while-loop', 'while-loop'), ('function', 'function'), ('list', 'list'), ('dictionary', 'dictionary'), ('string', 'string'), ('file', 'file'), ('exception', 'exception')], max_length=20),
        ),
    ]