<?php

# Do this...
$cmd = 'loony -D sfo2 details';
$data = shell_exec($cmd);
# Or this...
#$data = file_get_contents("./loony.json", FILE_USE_INCLUDE_PATH);


#var_dump($data);
$hosts = array_keys(json_decode($data, true));
$alldata= array(json_decode($data, true));

# This function runs loony getting the data for a single attribute
# Example:
# loony($hostname, $type, $name)
# loony("sfo2-aar-17-sr1", "attributes", "sku_signature")
function loony($host, $type, $name){
  global $alldata;
  if ($type === "groups") {
    $from_data = $alldata[0][$host]['groups'];
  } else if ($type === "attributes") {
    $from_data = $alldata[0][$host]['attributes'];
  }
    if (array_key_exists($name, $from_data) && $from_data[$name] !== null ) {
      if ($type === "groups") {
        $returnstr = $from_data[$name];
      } else {
        $returnstr = end($from_data[$name]);	
      }
    } else {
      $returnstr = "None";
    }
  return $returnstr;
}

function dropdown($host) {

$data = '
<div class="dropdown">
  <button class="dropbtn">'.$host.'</button>
  <div class="dropdown-content">
    <a href="#">IPMI Power Reset</a>
    <a href="#">IPMI Power Cycle</a>
    <a href="#">AC Power Cycle</a>
    <a href="#">Firmware Update</a>
    <a href="#">Reinstall</a>
  </div>
</div>';
return $data;
}

$file_db = new PDO('sqlite:'.__DIR__.'/hostdata.sqlite3');
$file_db->setAttribute(PDO::ATTR_ERRMODE,
                          PDO::ERRMODE_EXCEPTION);
// $file_db->exec("PRAGMA journal_mode=WAL;");

// Prepared sqlite statement to get the data we need for the host:
$stmt = $file_db->prepare('SELECT hostname, os_ip_online, bmc_ip_online FROM hostdata');
$stmt->execute();
$db_data = [];
while ($row = $stmt->fetch()) {
  $db_data[$row['hostname']]['os'] = $row['os_ip_online'];
  $db_data[$row['hostname']]['bmc'] = $row['bmc_ip_online'];
}

$greendot='<font color="green">&#9641;</font>';
$reddot='<font color="red">&#9641;</font>';


foreach ($hosts as $host){
  $os_ver = loony($host, "attributes", "hoststate_release_distro");
  $assignee = loony($host, "attributes", "sflab_assigned");
  $exp = loony($host, "attributes", "sflab_expiration_date");
  $jira = loony($host, "attributes", "sflab_jira");
  $wilson_branch = loony($host, "attributes", "wilson_branch");
  $platform = loony($host, "groups", "platform");
  $role = loony($host, "groups", "role");
  $biosver = loony($host, "attributes", "hoststate_version_bios");
  $biosrel = loony($host, "attributes", "hoststate_version_bios_release_date");
  $bmc = loony($host, "attributes", "hoststate_version_bmcfirmware");
  $debug = loony($host, "attributes", "debug");
  $short_host=strstr($host, '.', true);
  #$sku_sig = loony($host, "attributes", "sku_signature");
  #$sku_sig = loony($host, "attributes", "sku_signature");
  if ($platform !== "None") {
    if ($db_data[$short_host]['os'] === 'online') {
      $od = $greendot;
    } else {
      $od = $reddot;
    }
    if ($db_data[$short_host]['bmc'] === 'online') {
      $bd = $greendot;
    } else {
      $bd = $reddot;
    }

?>
        <tr>
            <td><?php echo "$short_host $od $bd"; ?></td>
            <td id="platform" data-name="<?php echo $short_host; ?>"><?php echo $platform; ?></td>
	          <td id="w_b" data-name="<?php echo $short_host; ?>"><?php echo $wilson_branch; ?></td>
            <td id="assignee" data-name="<?php echo $short_host; ?>"><?php echo $assignee; ?></td>  
            <td id="exp" data-name="<?php echo $short_host; ?>"><?php echo $exp; ?></td>  
            <td id="jira" data-name="<?php echo $short_host; ?>"><?php echo $jira; ?></td>
            <td id="debug" data-name="<?php echo $short_host; ?>"><?php echo $debug; ?></td>  
            <td><?php echo $os_ver; ?></td>  
            <td><?php echo $role; ?></td>  
            <td><?php echo $biosver . " / " . $biosrel; ?></td>  
            <td><?php echo $bmc; ?></td>
        </tr>
<?php 
  }
} 

?>
