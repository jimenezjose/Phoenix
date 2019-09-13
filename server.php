<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
.collapsible {
    background-color: #777;
    color: white;
    cursor: pointer;
    padding: 18px;
    width: 100%;
    border: none;
    text-align: left;
    outline: none;
    font-size: 15px;
}

.active, .collapsible:hover {
    background-color: #555;
}

.content {
    padding: 0 18px;
    display: none;
    overflow: hidden;
    background-color: #f1f1f1;
}
</style>
</head>
<body>

<?php

require(__DIR__ . "/functions.php");

# Do this...
$cmd = 'loony -D sfo2 -H '.$h.' details';
$data = shell_exec($cmd);
# Or this...
#$data = file_get_contents("./loony.json", FILE_USE_INCLUDE_PATH);
$hosts = array_keys(json_decode($data, true));
$alldata= array(json_decode($data, true));

# This function runs loony getting the data for a single attribute
# Example:
# loony($hostname, $type, $name)
# loony("sfo2-aar-17-sr1", "attributes", "sku_signature")

  $file_db = new PDO('sqlite:'.__DIR__.'/hostdata.sqlite3');
  $file_db->setAttribute(PDO::ATTR_ERRMODE,
                          PDO::ERRMODE_EXCEPTION);
  $file_db->exec("PRAGMA journal_mode=WAL;");

$hostname = clean_input($_GET["host"]);

if (preg_match("/sfo2-[a-z]{3}-[0-9]{2}-sr[0-4]/", $hostname)) {
  if (strpos($hostname, '.perf.twtter.net') === false) {
    $hostname = $hostname.".perf.twttr.net";
  }
	$cmd = 'loony -D sfo2 -H '.$hostname.' details';
	$data = array(json_decode(shell_exec($cmd), true));
	#header('Content-Type: application/json');
	$os_ver = loony($hostname, "attributes", "hoststate_release_distro", $data);
	$wanted_os_ver = loony($hostname, "attributes", "os_version", $data);
	$assignee = loony($hostname, "attributes", "sflab_assigned", $data);
	$exp = loony($hostname, "attributes", "sflab_expiration_date", $data);
	$jira = loony($hostname, "attributes", "sflab_jira", $data);
	$platform = loony($hostname, "groups", "platform", $data);
	$role = loony($hostname, "groups", "role", $data);
	$biosver = loony($hostname, "attributes", "hoststate_version_bios", $data);
	$biosrel = loony($hostname, "attributes", "hoststate_version_bios_release_date", $data);
	$bmc = loony($hostname, "attributes", "hoststate_version_bmcfirmware", $data);
	$sku = loony($hostname, "attributes", "sku_signature", $data);
  $short_host=strstr($hostname, '.', true);
  
  // Prepared sqlite statement to get the data we need for the host:
  $stmt = $file_db->prepare('SELECT hostname, os_ip_online, bmc_ip_online, vex FROM hostdata WHERE hostname=:hostie');
  $stmt->bindParam(':hostie', $short_host);
  $stmt->execute();
  $db_data=$stmt->fetch();
  
  $os_ip = loony($hostname, "facts", "ipaddress_prod", $data);
  $online_os = $db_data["os_ip_online"];
  $online_bmc = $db_data["bmc_ip_online"];
  $vex = $db_data["vex"];
	$bmc_ip = loony($hostname, "facts", "bmc_address", $data);
	echo "<pre>
Host: $hostname
Platform: $platform
Assigned: $assignee
Installed OS: $os_ver / $wanted_os_ver
BIOS Version: $biosver, $biosrel
BMC Version: $bmc
SKU Signature: $sku
OS IP: $os_ip [".$online_os."]
BMC IP: $bmc_ip [".$online_bmc."]
</pre>
<button class='collapsible'>Vex</button>
  <div class='content'>
    <pre>$vex</pre>
  </div>";
} else { 
	echo $hostname." is invalid.";
}
?>

<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
</script>
</body>
</html>


<?php
exit();
?>













