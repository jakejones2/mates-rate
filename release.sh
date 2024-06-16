python manage.py migrate
python manage.py collectstatic --noinput
daphne -b 0.0.0.0 -p 8001 trumps.asgi:application
# python manage.py runserver 0.0.0.0:443
