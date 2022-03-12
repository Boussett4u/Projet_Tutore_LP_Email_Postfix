FROM debian:bullseye
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update
RUN apt-get update \
    && apt-get -y install \
    postfix rsyslog vim host less mutt procps \
    curl wget \
    iproute2 python python3-flask \
    python3-flask-sqlalchemy python3-psycopg2 postgresql-client \
    python3-pip python-dev python3-venv apache2\
    && apt-get clean \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists \
    && useradd -m reject ; useradd -m hold ; useradd -m filter ; useradd -m defer ; useradd -m testfilter \
    &&  mkdir /home/testfilter/quarantaine

RUN cp -f /etc/services /var/spool/postfix/etc/services

COPY docker-entrypoint.sh /

RUN chmod 777 /docker-entrypoint.sh
COPY etc/postfix/ /etc/postfix/
COPY scripts/ /scripts/
COPY app/ /app/
RUN chmod 777 /scripts/classes.py
#RUN /scripts/classes.py
WORKDIR /app/flask_app/
RUN pip install -r /app/requirements.txt
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

ENTRYPOINT ["/docker-entrypoint.sh"]
