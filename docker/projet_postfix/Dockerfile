FROM debian:bullseye
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update
RUN apt-get update \
    && apt-get -y install postfix rsyslog vim host less mutt telnet net-tools procps \
    && apt-get -y install iptables build-essential zlib1g-dev libncurses5-dev libgdbm-dev\
    libnss3-dev libssl-dev libreadline-dev libffi-dev curl wget \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists

RUN cp -f /etc/services /var/spool/postfix/etc/services

ADD /scripts/script.sh /scripts/script.sh

CMD [ "/scripts/script.sh" ]