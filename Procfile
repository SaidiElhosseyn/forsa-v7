web: python manage.py migrate && python manage.py create_admin && python manage.py seed_categories && gunicorn dzfreshmarket.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
