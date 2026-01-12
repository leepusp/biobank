from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_add_is_active_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="sample",
            name="is_active",
            field=models.BooleanField(
                default=True,
                help_text="Indica se a Sample está ativa para uso",
            ),
        ),
    ]
