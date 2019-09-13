<?php
  if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['userchange'])) {
      $postname = strip_tags($_POST['userchange']);
      if ( $postname === "" ) {
        setcookie('user', 'labtester');
        header( "Location: index.php" );
        exit;
      } else {
        if ( $_COOKIE['user'] !== $postname ) {
          setcookie('user', $postname);
          header( "Location: index.php" );
          exit;
        }
      }
    }
  }
?>
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>Twitter Lab Tester</title>
  <!-- Tell the browser to be responsive to screen width -->
  <meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">
  <!-- Bootstrap 3.3.7 -->
  <link rel="stylesheet" href="../../bower_components/bootstrap/dist/css/bootstrap.min.css">
  <!-- Font Awesome -->
  <link rel="stylesheet" href="../../bower_components/font-awesome/css/font-awesome.min.css">
  <!-- Ionicons -->
  <link rel="stylesheet" href="../../bower_components/Ionicons/css/ionicons.min.css">
  <!-- Theme style -->
  <link rel="stylesheet" href="../../dist/css/AdminLTE.css">
  <!-- AdminLTE Skins. Choose a skin from the css/skins
       folder instead of downloading all of them to reduce the load. -->
  <link rel="stylesheet" href="../../dist/css/skins/_all-skins.min.css">

  <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
  <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
  <!--[if lt IE 9]>
  <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
  <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
  <![endif]-->

  <!-- Google Font -->
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,600,700,300italic,400italic,600italic">
<script>
  var netdataTheme = 'default'; // this is white
  // var netdataTheme = 'slate'; // this is dark
</script>

</head>
<body class="hold-transition">
<div class="wrapper">

  <?php 
  include './includes/modals.php';
      // include './includes/header.php';
      // include './includes/sidebar.php';
      
  ?>
      <!-- Content Wrapper. Contains page content -->
      <div id="content-wrapper" class="content-wrapper">
  <?php 
      include './includes/content.php';
  ?>
    </div>
    <!-- /.content-wrapper -->
  <footer class="main-footer">
    <div class="pull-right hidden-xs">
      <b>Version</b> 0.0.1
    </div>
    <strong>Copyright &copy; 2019 Twitter - HWENG</a>.</strong> All rights
    reserved.
  </footer>

</div>
<!-- ./wrapper -->

<!-- jQuery 3 -->
<script //src="../../bower_components/jquery/dist/jquery.min.js"></script>

<!-- Bootstrap 3.3.7 -->
<script src="../../bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
<!-- Slimscroll -->
<script src="../../bower_components/jquery-slimscroll/jquery.slimscroll.min.js"></script>
<!-- FastClick -->
<script src="../../bower_components/fastclick/lib/fastclick.js"></script>
<!-- AdminLTE App -->
<script src="../../dist/js/adminlte.min.js"></script>
<!-- AdminLTE for demo purposes -->
<script src="../../dist/js/demo.js"></script>
<script src="/js/jeff.js"></script>
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
</script>
</body>
</html>
