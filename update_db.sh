#!/bin/bash
cd /var/www/labtech/
for i in `loony -D sfo2 -1`; do 
  php sqlite3.php -h $i &>/dev/null &
done
sleep 15
while [[ -s working.sqlite3-wal ]]; do
  sleep 1
done
chown -R apache:apache *
mv working.sqlite3 hostdata.sqlite3
