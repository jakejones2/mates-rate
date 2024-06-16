python manage.py migrate
python manage.py collectstatic --noinput
daphne trumps.asgi:application
# python manage.py runserver 0.0.0.0:443
