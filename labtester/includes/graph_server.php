
<?php 

    function clean_input($data) {
        $data = preg_replace('/[^A-Za-z0-9\/\\-_]/i','',$data);
        $data = trim($data);
        $data = stripslashes($data);
        $data = htmlspecialchars($data);
        return $data;
    }
    if ( ! isset($_POST['host']) ) {
        $server = "";    
    } else {
        $server = clean_input($_POST['host']);
    }
    
    if ($server == ""){
        $server = "labtech.sfo2.twitter.com";
        $server_netdata_url = "http://${server}:19999";
    } else {
        echo '
         <script type="text/javascript" src="/js/netdata/dashboard.js">
         //Set options for TV operation
         //This has to be done, after dashboard.js is loaded
         
         //destroy charts not shown (lowers memory on the browser)
         NETDATA.options.current.destroy_on_hide = true;
         
         //set this to false, to always show all dimensions
         NETDATA.options.current.eliminate_zero_dimensions = true;
         
         //lower the pressure on this browser
         NETDATA.options.current.concurrent_refreshes = false;
         
         //if the tv browser is too slow (a pi?)
         //set this to false
         NETDATA.options.current.parallel_refresher = true;
         
         //always update the charts, even if focus is lost
         //NETDATA.options.current.stop_updates_when_focus_is_lost = false;
         
         //Since you may render charts from many servers and any of them may
         //become offline for some time, the charts will break.
         //This will reload the page every RELOAD_EVERY minutes
         
         var RELOAD_EVERY = 5;
         setTimeout(function(){
         location.reload();
         }, RELOAD_EVERY * 60 * 1000);
         </script>';
        $server_netdata_url = "http://${server}.perf.twttr.net:19999";
    }
?>
<div style="width: 100%; text-align: center; display: inline-block; padding-bottom:15px;">
    <div style="width: 100%; height: 24vh; text-align: center; display: inline-block;">
        <div style="width: 100%; height: calc(100% - 15px); text-align: center; display: inline-block;">
            <div data-netdata="system.cpu"
                    data-host="<?php echo $server_netdata_url;?>"
                    data-title="CPU usage of <?php echo $server;?>"
                    data-chart-library="dygraph"
                    data-width="90%"
                    data-height="48%"
                    data-after="-300"
                    data-dygraph-valuerange="[0, 100]"
                    ></div>
    </div>
    <div style="width: 100%; height: 24vh; text-align: center; display: inline-block;">
        <div style="width: 100%; height: calc(100% - 15px); text-align: center; display: inline-block;">
            <div data-netdata="system.io"
                    data-host="<?php echo $server_netdata_url;?>"
                    data-common-max="io"
                    data-common-min="io"
                    data-title="I/O on <?php echo $server;?>"
                    data-chart-library="dygraph"
                    data-width="90%"
                    data-height="48%"
                    data-after="-300"
                    ></div>
        </div>
    </div>
    <div style="width: 100%; height: 24vh; text-align: center; display: inline-block;">
        <div style="width: 100%; height: calc(100% - 15px); text-align: center; display: inline-block;">
            <div data-netdata="system.ram"
                    data-host="<?php echo $server_netdata_url;?>"
                    data-title="Memory Usage on <?php echo $server;?>"
                    data-chart-library="dygraph"
                    data-width="90%"
                    data-height="48%"
                    data-after="-300"
                    ></div>
    </div>
    <div style="width: 100%; height: 24vh; text-align: center; display: inline-block;">
        <div style="width: 100%; height: calc(100% - 15px); text-align: center; display: inline-block;">
            <div data-netdata="ipmi.watts"
                    data-host="<?php echo $server_netdata_url;?>"
                    data-title="IPMI Wattage on <?php echo $server;?>"
                    data-chart-library="dygraph"
                    data-width="90%"
                    data-height="48%"
                    data-after="-300"
                    ></div>
    </div>