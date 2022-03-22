#!/bin/bash
while true
do
valide=$(psql -d postfix -c "select count("actionFiltre") from statistiques where "actionFiltre" = '1'" | tail -n 3 | head -n 1 | sed 's/ //g')

echo "mailvalide $valide" | curl --data-binary @- http://127.0.0.1:9091/metrics/job/pushgateway/instance/db/provider/db

bloque=$(psql -d postfix -c "select count("actionFiltre") from statistiques where "actionFiltre" = '2'" | tail -n 3 | head -n 1 | sed 's/ //g')

echo "mailbloque $bloque" | curl --data-binary @- http://127.0.0.1:9091/metrics/job/pushgateway/instance/db/provider/db

attente=$(psql -d postfix -c "select count("actionFiltre") from statistiques where "actionFiltre" = '3'" | tail -n 3 | head -n 1 | sed 's/ //g')

echo "mailattente $attente" | curl --data-binary @- http://127.0.0.1:9091/metrics/job/pushgateway/instance/db/provider/db

sleep 15

done

