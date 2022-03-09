FROM debian:bullseye
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update
RUN apt-get update \
    && apt-get -y install postfix rsyslog vim host less mutt telnet net-tools procps \
    && apt-get -y install iptables build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
    && apt-get -y install libnss3-dev libssl-dev libreadline-dev libffi-dev curl wget \
    && apt-get -y install iproute2 python python3-flask \
    && apt-get -y install python3-flask-sqlalchemy python3-psycopg2 postgresql-client \
    && apt-get -y install python3-pip python-dev python3-venv apache2\
    && apt-get clean \
    ; rm -rf /var/cache/apt/archives /var/lib/apt/lists \
    ; useradd -m reject ; useradd -m hold ; useradd -m filter ; useradd -m defer ; useradd -m testfilter \
    ; mkdir /home/testfilter/quarantaine

RUN cp -f /etc/services /var/spool/postfix/etc/services

COPY docker-entrypoint.sh /usr/local/bin/

RUN chmod 777 /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]
COPY /etc/postfix/ /etc/postfix/
COPY /scripts/ /scripts/
COPY /app/ /app/
RUN pip install -r /app/requirements.txt
RUN chmod 777 /scripts/classes.py
#RUN /scripts/classes.py
EXPOSE 5000
CMD ["flask", "run"]