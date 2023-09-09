#!/bin/bash

if test -f "$DJANGO_LOG_FILE_PATH";
then
  echo "$DJANGO_LOG_FILE_PATH exists"
else
  # create log file
  touch $DJANGO_LOG_FILE_PATH
fi

# set log file owner (we are currently "root", but the app runs as "webapp")
chown root:root $DJANGO_LOG_FILE_PATH