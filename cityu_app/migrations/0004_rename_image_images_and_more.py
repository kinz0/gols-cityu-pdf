# Generated by Django 4.1.2 on 2022-10-28 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityu_app', '0003_image_delete_folder'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Image',
            new_name='Images',
        ),
        migrations.RenameField(
            model_name='images',
            old_name='imagefile',
            new_name='imagesfile',
        ),
    ]
