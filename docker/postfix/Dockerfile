FROM debian:bullseye
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update

RUN echo "postfix postfix/main_mailer_type string No configuration" | debconf-set-selections

RUN apt-get update \
    && apt-get --yes install \
    postfix postfix-pcre rsyslog python3 python3-pip\
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* /tmp/* /var/tmp/*

# FIXME trouver une meilleure place /var/spool/postfix/quarantaine ?
RUN mkdir -p /home/testfilter/quarantaine

COPY docker-entrypoint.sh /

RUN chmod u+x /docker-entrypoint.sh
COPY etc/postfix/main.cf etc/postfix/master.cf etc/postfix/master.policy.cf /etc/postfix/
# FIXME classes.py n'est pas synchro avec app/flask_app/db.py :(
COPY scripts/ /scripts/
COPY app/ /app/

# FIXME Beurk :(
RUN chmod 555 /scripts/classes.py

WORKDIR /app/flask_app/
RUN pip install -r /app/requirements.txt
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

ENTRYPOINT ["/docker-entrypoint.sh"]
