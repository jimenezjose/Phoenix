    <!-- Main content -->
    <section class="content">
      <div class="row">
        <div class="col-xs-7">
          <div class="box">
            <div class="box-header">
              <h3 class="box-title">Servers</h3>

              <div class="box-tools">
                <form method="POST" action="<?= $_SERVER['PHP_SELF']; ?>">
                  <div class="input-group input-group-sm" style="width: 150px;">
                    <input type="text" name="userchange" class="form-control pull-right" placeholder="ASSIGNED">
                    <div class="input-group-btn">
                      <button type="submit" class="btn btn-default"><i class="fa fa-search"></i></button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
            <!-- /.box-header -->
            <div class="box-body table-responsive">
              
                <div id="table_of_servers">
                  <?php include 'build_table.php';?>
                </div>
              
            </div>
            <form action="/form.php" method="post" id="form1">
            <!-- /.box-body -->
          </div>
          <!-- /.box -->
        </div>
        <div class="col-md-5"><div class="box-body table-responsive no-padding">
          <div class="box">
            <div class="box-header">
              <h3 id="boxheader" class="box-title">Server Metrics - labtech.sfo2.twitter.com</h3>
            </div>
            <div id="server-graphs" class="box-body table-responsive no-padding">
              <?php include 'graph_server.php';?>
            </div>
          </div>
        </div>
      </div>
    </section>
    <!-- /.content -->
