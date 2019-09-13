<?php
date_default_timezone_set('UTC');
function list_tests()
{
    $files = glob($_SERVER["DOCUMENT_ROOT"].'/test_modules/*.module');
    return $files;
}

function setloony($host, $attr, $value)
{
    $cmd = "loony -H ${host} set attribute ${attr}:${value}";
    return $cmd;
}

function settime($host)
{
    $datetime=date(DATE_RFC3339);
    $cmd = "loony -H ${host} set attribute TLT:${datetime}";
    return $cmd;
}

function clearloony($host, $attr)
{
    $cmd = "loony -H ${host} clear attribute ${attr}";
    return $cmd;
}

function ipmi($host, $command)
{
    $cmd = "ipmitool -H ${host} -U root -P root ${command}";
    return $cmd;
}

function decipher_test($text, $hostname)
{
    //echo $text;
    $ret = "";
    $separator = "\n";
    $line = strtok($text, $separator);
    
    while ($line !== false) {
        //var_dump($line);
        $work = explode(":", $line);
        //var_dump($work);
        if ($work[0] === "loony") {
            if (count($work) === 2) {
                $ret .= clearloony($hostname, $work[1]) . PHP_EOL;
            } elseif (count($work) === 3) {
                $ret .= setloony($hostname, $work[1], $work[2]) . PHP_EOL;
            }
        } elseif ($work[0] === "ipmi") {
            $ret .= ipmi($hostname.".ipmi.twttr.net", $work[1]) . PHP_EOL;
        }
        $line = strtok( $separator );
    }
    //echo $ret;
    return $ret;
}

function get_test($want_test, $hostname){
    foreach (list_tests() as $thistest) {
        if (basename($thistest, '.module') === $want_test) {
            return decipher_test(file_get_contents($thistest), $hostname);
        }
    }
    echo $thistest;
    return "Invalid test";
}

function run_test($want_test, $hostname){
    foreach (list_tests() as $thistest) {
        if (basename($thistest, '.module') === $want_test) {
            $testcmds = decipher_test(file_get_contents($thistest), $hostname);
            $ret = "";
            $separator = "\n";
            $line2 = strtok($testcmds, $separator);
            
            while ($line2 !== false) {
                shell_exec($line2 . " > /dev/null 2>/dev/null &");
                //echo $line;
                $line2 = strtok( $separator );
            }
            if ($want_test != "cancel") {
                $var = settime($hostname);
                echo $var;
                shell_exec($var . " > /dev/null 2>/dev/null &");
            }
            //echo $ret;
            shell_exec('/home/jeffryw/labtech/labtester/crontab_makejson.sh > /dev/null 2>/dev/null &');
            return "\nCommands submitted";
        }
    }
    return "Invalid test";
}