from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("stores", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE stores_store ALTER COLUMN name TYPE varchar(150);",
                "ALTER TABLE stores_store ALTER COLUMN slug TYPE varchar(160);",
            ],
            reverse_sql=[
                "ALTER TABLE stores_store ALTER COLUMN name TYPE varchar(100);",
                "ALTER TABLE stores_store ALTER COLUMN slug TYPE varchar(100);",
            ],
            hints={"target_db": "default"},
        ),
    ]
