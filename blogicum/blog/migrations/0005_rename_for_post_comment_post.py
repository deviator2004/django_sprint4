# Generated by Django 3.2.16 on 2023-05-27 10:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_rename_post_comment_for_post'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='for_post',
            new_name='post',
        ),
    ]
