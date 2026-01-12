from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='biobank',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Indica se o Biobank está ativo para uso'
            ),
        ),
        migrations.AddField(
            model_name='collection',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Indica se a Collection está ativa para uso'
            ),
        ),
    ]
