from django.db import migrations


def fix_lengths_postgres(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("ALTER TABLE stores_store ALTER COLUMN name TYPE varchar(150);")
    schema_editor.execute("ALTER TABLE stores_store ALTER COLUMN slug TYPE varchar(160);")


def reverse_lengths_postgres(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("ALTER TABLE stores_store ALTER COLUMN name TYPE varchar(100);")
    schema_editor.execute("ALTER TABLE stores_store ALTER COLUMN slug TYPE varchar(100);")


class Migration(migrations.Migration):
    dependencies = [
        ("stores", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(fix_lengths_postgres, reverse_lengths_postgres),
    ]
