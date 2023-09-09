#!/bin/bash

source "$PYTHONPATH/activate" && {
# collect static
python manage.py collectstatic;
}
