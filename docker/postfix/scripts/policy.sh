#/bin/bash

. /scripts/filtre/conf.env
printenv >/tmp/mio-policy.log
/scripts/filtre/policy.py 2>>/tmp/mio-policy.log
