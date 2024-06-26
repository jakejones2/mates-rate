FROM python:3.11.9-bullseye

# minimum requirements for psycopg2
# RUN apt-get -qq -y update && \
#     apt-get -qq -y upgrade && \
#     apt-get -qq -y install \
#         curl \
#         make \
#         libpq-dev \
#         build-essential \
#         libsass-dev \
#         gcc && \
#     apt-get -y autoclean && \
#     apt-get -y autoremove && \
#     rm -rf /var/lib/apt-get/lists/*

RUN pip install --upgrade --no-cache-dir pip

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# if using compose, delete the below

COPY . /code
#Add the following lines to make the release.sh script executable to run your script
RUN chmod +x /code/release.sh
CMD ["/code/release.sh"]
