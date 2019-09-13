<?php
  $file_db = new PDO('sqlite:'.__DIR__.'/hostdata.sqlite3');
  $file_db->setAttribute(PDO::ATTR_ERRMODE,
                          PDO::ERRMODE_EXCEPTION);
  $file_db->exec("PRAGMA journal_mode=WAL;");

  // Prepared sqlite statement to get the data we need for the host:
  $stmt = $file_db->prepare('SELECT hostname, os_ip_online, bmc_ip_online FROM hostdata');
  $stmt->execute();
  $db_data = [];
  while ($row = $stmt->fetch()) {
    $db_data[$row['hostname']]['os'] = $row['os_ip_online'];
    $db_data[$row['hostname']]['bmc'] = $row['bmc_ip_online'];
  }

$greendot='<font color="green">&#9679;</font>';
$reddot='<font color="red">&#9679;</font>';

echo "
sfo2-aar-17-sr1 $greendot $reddot



";
