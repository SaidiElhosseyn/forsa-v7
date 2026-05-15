web: python manage.py migrate && python manage.py create_admin && gunicorn dzfreshmarket.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
