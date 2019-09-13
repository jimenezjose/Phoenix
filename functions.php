<?php
function loony($host, $type, $name, $alldata){
  if (strpos($host, 'perf') === false) {
    $host = $host.".perf.twttr.net";
  }
  if ($type === "groups") {
    $from_data = $alldata[0][$host]['groups'];
  } else if ($type === "attributes") {
    $from_data = $alldata[0][$host]['attributes'];
  } else if ($type === "facts") {
    $from_data = $alldata[0][$host]['facts'];
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

function clean_input($data) {
        $data = preg_replace('/[^A-Za-z0-9-]/i','',$data);
  $data = trim($data);
        $data = stripslashes($data);
        $data = htmlspecialchars($data);
        return $data;
}

function online($ip){
  $str = exec("ping -W 1 -c 1 ".$ip, $output, $retval);
  if ($retval === 0){
    return "online";
  }else{
    return "offline";
  }
}

function vex_data($ip){
  if (online($ip) === "online") {
    $url="http://$ip:4680/?text";
    $ch=curl_init();
    $timeout=1;

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, $timeout);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $timeout);

    $result=curl_exec($ch);
    curl_close($ch);
    if ($result !== false) {
      return $result;
    } else {
      return "vex not retrievable";
    }
  }
}

function get_vex($ip){
  $vex = '
    <button class="collapsible">Vex</button>
    <div class="content">
      <pre>'.vex_data($ip).'</pre>
    </div>
';
    return $vex;
}



?>
