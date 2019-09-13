<!DOCTYPE html>
<html>
<head>
  <link rel="shortcut icon" type="image/png" href="/hweng.png"/>
  <meta charset="utf-8">
  <title>Lab Tech</title>
  <link class="ui-theme" rel="stylesheet" href="css/jquery-ui.min.css">
  <link rel="stylesheet" href="css/jq.css">
  <link rel="stylesheet" href="css/jeff.css">
  <link rel="stylesheet" href="css/prettify.css">
  <link rel="stylesheet" href="css/theme.blue.css">
  <script src="js/jquery-latest.min.js"></script>
  <script src="js/jquery-ui.min.js"></script>
  <script src="js/prettify.js"></script>
  <script src="js/docs.js"></script>
  <script src="js/jquery.tablesorter.js"></script>
  <script src="js/jquery.tablesorter.widgets.js"></script>
  <script src="js/widget-saveSort.js"></script>
  <script src="js/widget-columnSelector.js"></script>
  <script src="js/widget-editable.js"></script>
  <script src="js/parser-ignore-articles.js"></script>
  <script src="js/widget-storage.js"></script>
  <script src="js/bootstrap.min.js"></script>
  <script src="js/jeff.js"></script>
</script>
<style>
  #types { width: 100%; }
</style>

</head>
<body>
<div id="Lab Tech Table"><button type="button" data-filter-column="1">^h</button> (beginning of word)<br>
<button type="button" data-filter-column="1">s$</button> (end of word)<br>
<button type="button" class="reset">Reset</button><br>
<div class="columnSelectorWrapper">
  <input id="colSelect1" type="checkbox" class="hidden">
  <label class="columnSelectorButton" for="colSelect1">Select Columns</label>
  <div id="columnSelector" class="columnSelector">
    <!-- this div is where the column selector is added -->
  </div>
</div>
<table id="filters" class="tablesorter custom-popup">
	<thead>
		<tr>
			<th data-priority="critical" id="hostname">Hostname</th>
			<th data-priority="1" id="platform">Platform</th>
			<th data-priority="1" id="wilson_branch">Wilson Branch</th>
			<th data-priority="2" id="assigned">Assigned</th>
			<th data-priority="3" id="exp">Expiration</th>
			<th data-priority="4" id="jira">JIRA</th>
      <th data-priority="5" id="debug">Debug?</th>
			<th data-priority="6" >OS Version</th>
			<th data-priority="7" >Role</th>
			<th data-priority="8" >BIOS</th>
			<th data-priority="9">BMC</th>
		</tr>
	</thead>
	<tbody>
<?php include './build_table.php'; ?>
	</tbody>
</table></div>
<div id="donkey"></div>
</body>
</html>
