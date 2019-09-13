$<?php

function clean_input($data) {
    $data = preg_replace('/[^A-Za-z0-9\/\\-_]/i','',$data);
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

include __DIR__ . '/includes/tests.php';
echo "<pre>";

$hostname = clean_input($_POST['host']);

if (preg_match("/sfo2-[a-z]{3}-[0-9]{2}-sr[0-4]/", $hostname)) {
    $test = clean_input($_POST['test']);
    $var = get_test($test, $hostname);
    echo $var;
    $var2 = run_test($test, $hostname);
    echo $var2;
    echo "</pre>";
} else {
    echo "Make sure hostname is in the format sfo2-aad-24-sr1\n";
}


