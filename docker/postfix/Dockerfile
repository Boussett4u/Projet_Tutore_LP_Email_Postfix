FROM debian:bullseye
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update

RUN echo "postfix postfix/main_mailer_type string No configuration" | debconf-set-selections
# FIXME Pour exemple à virer si inutile
# echo 'postfix postfix/mynetworks string "127.0.0.0/8"' | debconf-set-selections && \
# echo 'postfix postfix/mailname string temporary.example.com' | debconf-set-selections && \
# echo 'postfix postfix/destinations string temporary.example.com' | debconf-set-selections && \
# echo 'postfix postfix/myhostname string temporary.example.com' | debconf-set-selections && \
# echo 'postfix postfix/myorigin string temporary.example.com' | debconf-set-selections

# FIXME idem supra
#ENV MAILNAME mail.example.com
#ENV MY_NETWORKS 172.17.0.0/16 127.0.0.0/8
#ENV MY_DESTINATION localhost.localdomain, localhost
#ENV ROOT_ALIAS admin@example.com
#ENV HOSTNAME localhost.localdomain

RUN apt-get update \
    && apt-get --yes install \
    postfix postfix-pcre rsyslog python3 python3-pip\
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* /tmp/* /var/tmp/*

# FIXME inutile
RUN useradd -m reject ; \
    useradd -m hold ; \
    useradd -m filter ; \
    useradd -m defer ; \
    useradd -m testfilter

# FIXME trouver une meilleure place /var/spool/postfix/quarantaine ?
RUN mkdir /home/testfilter/quarantaine

COPY docker-entrypoint.sh /

RUN chmod u+x /docker-entrypoint.sh
COPY etc/postfix/ /etc/postfix/
# FIXME classes.py n'est pas synchro avec app/flask_app/db.py :(
COPY scripts/ /scripts/
COPY app/ /app/

# FIXME Beurk :(
RUN chmod 777 /scripts/classes.py

WORKDIR /app/flask_app/
RUN pip install -r /app/requirements.txt
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

ENTRYPOINT ["/docker-entrypoint.sh"]
