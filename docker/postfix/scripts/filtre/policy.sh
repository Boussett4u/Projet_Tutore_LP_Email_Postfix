#/bin/bash

LOG=/tmp/mio-policy.log
. /scripts/filtre/conf.env
printenv >>$LOG
/scripts/filtre/policy.py 2>>$LOG
