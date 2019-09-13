<?php

require(__DIR__ . "/functions.php");

$options = getopt("h:");
if (array_key_exists("h", $options)) {
  $h = $options["h"];
} else {
  echo "Please use -h<hostname>\n";
  exit();
}

if (! preg_match("/sfo2-[a-z]{3}-[0-9]{2}-sr[0-4].perf.twttr.net/", $h)) {
  echo "Make sure hostname is in the format sfo2-aad-24-sr1.perf.twttr.net\n";
}

# Do this...
$cmd = 'loony -D sfo2 -H '.$h." details";
$data = shell_exec($cmd);
# Or this...
#$data = file_get_contents("./loony.json", FILE_USE_INCLUDE_PATH);
$hosts = array_keys(json_decode($data, true));
$alldata= array(json_decode($data, true));

# This function runs loony getting the data for a single attribute
# Example:
# loony($hostname, $type, $name)
# loony("sfo2-aar-17-sr1", "attributes", "sku_signature")

try {
  $file_db = new PDO('sqlite:'.__DIR__.'/working.sqlite3');
  $file_db->setAttribute(PDO::ATTR_ERRMODE, 
                          PDO::ERRMODE_EXCEPTION);

  $file_db->exec("CREATE TABLE IF NOT EXISTS hostdata (
                  hostname TEXT PRIMARY KEY,
                  os_ip TEXT,
                  bmc_ip TEXT,
                  vex TEXT,
                  os_ip_online TEXT,
                  bmc_ip_online TEXT)");
  $file_db->exec("PRAGMA journal_mode=WAL;");
  $file_db->exec("PRAGMA read_uncommitted=true;");

  $insert = "INSERT OR REPLACE INTO hostdata (hostname, os_ip, bmc_ip, vex, os_ip_online, bmc_ip_online) VALUES (:hn, :oi, :bi, :vex, :oio, :bio)";
  $stmt = $file_db->prepare($insert);
  # $file_db->beginTransation();
  foreach ($hosts as $host){
    $os_ver = loony($host, "attributes", "hoststate_release_distro", $alldata);
    $assignee = loony($host, "attributes", "sflab_assigned", $alldata);
    $exp = loony($host, "attributes", "sflab_expiration_date", $alldata);
    $jira = loony($host, "attributes", "sflab_jira", $alldata);
    $wilson_branch = loony($host, "attributes", "wilson_branch", $alldata);
    $platform = loony($host, "groups", "platform", $alldata);
    $role = loony($host, "groups", "role", $alldata);
    $biosver = loony($host, "attributes", "hoststate_version_bios", $alldata);
    $biosrel = loony($host, "attributes", "hoststate_version_bios_release_date", $alldata);
    $bmc = loony($host, "attributes", "hoststate_version_bmcfirmware", $alldata);
    $os_ip = loony($host, "facts", "ipaddress_prod", $alldata);
    $bmc_ip = loony($host, "facts", "bmc_address", $alldata);
    $short_host=strstr($host, '.', true);
    $vex=vex_data($os_ip);
    $online_os=online($os_ip);
    $online_bmc=online($bmc_ip);
    echo "$host - $assignee";

    $stmt->bindValue(':hn', $short_host, PDO::PARAM_STR);
    $stmt->bindValue(':oi', $os_ip, PDO::PARAM_STR);
    $stmt->bindValue(':bi', $bmc_ip, PDO::PARAM_STR);
    $stmt->bindValue(':vex', $vex, PDO::PARAM_STR);
    $stmt->bindValue(':oio', $online_os, PDO::PARAM_STR);
    $stmt->bindValue(':bio', $online_bmc, PDO::PARAM_STR);
    $stmt->execute();
  }
} catch(Exception $e) {
  echo $e;
}
/*} catch(PDOException $e) {
  if(stripos($e->getMessage(), 'DATABASE IS LOCKED') !== false) {
    // This should be specific to SQLite, sleep for 0.25 seconds
    // and try again.  We do have to commit the open transaction first though
    $file_db->commit();
    usleep(250000);
  } else {
    $file_db->rollBack();
    throw $e;
  }
}
  $file_db->commit();*/
  
$file_db = null;

?> 
