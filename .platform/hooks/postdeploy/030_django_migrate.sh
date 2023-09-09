#!/bin/bash

source "$PYTHONPATH/activate" && {
# migrate
python manage.py migrate;
}