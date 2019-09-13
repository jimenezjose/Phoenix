<!-- B: table_of_servers.php -->
<?php

if ( isset($_COOKIE['user'])) {
  $user_assigned = $_COOKIE['user'];
} else {
  $user_assigned = 'labtester';
}
?>
            <form action="/form.php" method="post" id="form1">
  
<?php
echo $user_assigned;
# Do this...
#$cmd = 'loony -D sfo2 -g role:hwlab.shared details';
#$data = shell_exec($cmd);
# Or this...
$data = file_get_contents("./loony.json", FILE_USE_INCLUDE_PATH);

include './includes/tests.php';

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

function time2string($timeline) {
    $periods = array('day' => 86400, 'hour' => 3600, 'minute' => 60);
    
    foreach($periods AS $name => $seconds){
        $num = floor($timeline / $seconds);
        $timeline -= ($num * $seconds);
        if ($num > 0) {
            $ret .= $num.' '.$name.(($num > 1) ? 's' : '').' ';
        }
    }
    
    return trim($ret);
}

foreach ($hosts as $host){
  $assignee = loony($host, "attributes", "sflab_assigned");
  if ($assignee !== $user_assigned) {
    continue;
  }
  $os_ver = loony($host, "attributes", "hoststate_release_distro");
  $exp = loony($host, "attributes", "sflab_expiration_date");
  $jira = loony($host, "attributes", "sflab_jira");
  $wilson_branch = loony($host, "attributes", "wilson_branch");
  $platform = loony($host, "groups", "platform");
  $role = loony($host, "groups", "role");
  $biosver = loony($host, "attributes", "hoststate_version_bios");
  $biosrel = loony($host, "attributes", "hoststate_version_bios_release_date");
  $bmc = loony($host, "attributes", "hoststate_version_bmcfirmware");
  $validation_status = loony($host, "attributes", "validation_status");
  $validation_stage = loony($host, "attributes", "validation");
  $TLT_TIME = loony($host, "attributes", "TLT");
  $ago = 'None';
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


    if ($validation_status === "None") {
        $val_color = "label-primary";
        $enable_test = 1;
    } elseif (stristr($validation_status,'ERROR')) {
        $val_color = "label-danger";
        $enable_test = 1;
    } elseif (stristr($validation_status,'FAIL')) {
        $val_color = "label-danger";
        $enable_test = 1;
    } elseif (stristr($validation_status,'PASS')) {
        $val_color = "label-success";
        $enable_test = 1;
    } elseif (stristr($validation_status,'COMPLETE')) {
        $val_color = "label-success";
        $enable_test = 1;
    } else {
        $val_color = "label-warning";
        $enable_test = 0;
    }
    if ($enable_test === 1) {
        $li = "";
        foreach (list_tests() as $test) {
            $test = basename($test, '.module');
            if ($test != "cancel") {
                $li .= "                    <li host=\"${short_host}\" test=\"${test}\" onclick=\"mySubmit(this);\" ><a href=\"#\">${test}</a></li>".PHP_EOL;
        
            }
        }
        $tests = '
                <div class="input-group input-group-sm">
                <div class="input-group-btn">
                  <button id="unusedbutton" type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">Run Test
                    <span class="fa fa-caret-down"></span></button>
                  <ul class="dropdown-menu" >
'.$li.'
<!-- data-toggle="modal" data-target="#modal-info" -->
                  </ul>
                </div>
              </div>
';  
    } else {
        if ($TLT_TIME !== "None") {
            $ago = time2string(time() - strtotime($TLT_TIME)).' ago';
        }
        $tests = '
                <div class="input-group input-group-sm">
                <div class="input-group-btn">
                  <button host="'.$short_host.'" test="cancel" onclick="mySubmit(this, event);" type="button" class="btn btn-danger">Stop Test</button>
                </div>
              </div>
';
    }
?>
				<tr host="<?php echo $short_host; ?>" onclick="serverStats(this);">
                  <td><?php echo "$short_host $od $bd"; ?></td>
                  <td><?php echo $platform; ?></td>
                  <td><?php echo $tests; ?></td>
                  <td><?php echo $validation_stage; ?></td>
                  <td><span class="label <?php echo $val_color; ?>"><?php echo $validation_status; ?></span></td>
                  <td><?php echo $ago; ?></td>
                </tr>
<?php 
  }
}

?>
<!-- E: table_of_servers.php -->
