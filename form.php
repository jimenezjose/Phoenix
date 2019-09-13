<?php
function clean_input($data) {
	$data = preg_replace('/[^A-Za-z0-9\/\\-_]/i','',$data);
  $data = trim($data);
	$data = stripslashes($data);
	$data = htmlspecialchars($data);
	return $data;
}

$hostname = clean_input($_POST["host"]);
$id = clean_input($_POST["id"]);
$data = clean_input($_POST["data"]);
$field = "None";

if ($id === "assignee") {
        $field = 'sflab_assigned';
} elseif ($id === "exp") {
        $field = 'sflab_expiration_date';
} elseif ($id === "jira") {
        $field = 'sflab_jira';
} elseif ($id === "w_b") {
        $field = 'wilson_branch';
} elseif ($id === "debug") {
        $field = 'debug';
}

if ($field !== "None") {
	if ($data === "") {
    		$cmd = "loony -H $hostname clear attribute $field";
	} else {
  		$cmd = "loony -H $hostname set attribute $field:$data";
	}
	$data = shell_exec($cmd);
	echo $data;
} else {
	echo "Failed";
}
?>
