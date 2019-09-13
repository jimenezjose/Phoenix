function mySubmit(obj){
   var host = obj.getAttribute("host");
   var test = obj.getAttribute("test");
   //console.log("my object: %o", obj);
   $.ajax
   ({
           type: "POST",
           url: "form.php",
           data: {"host" : host, "test" : test}, 
           success: function(response)
             { 
               $("#modal-content-info").html(response);
             }
   });

   $("#modal-info").modal('toggle');
}


 
 function refreshPage(){
   //$("#table_of_servers").empty();
   $("#table_of_servers").load("./build_table.php");

   
   /*$.ajax
   ({
           url: "/build_table.php", 
           success: function(response)
             { 
               $("#table_of_servers").html(response);
             }
   });*/
 }
 

 
 function serverStats(obj){
   var host = obj.getAttribute("host");
   var url = '<a target="_blank" href="http://' + host + '.perf.twttr.net:19999">' + host + '</a>';
   $("#boxheader").html("Server Metrics - More Metrics: " + url);

   $.ajax
   ({
           type: "POST",
           url: "includes/graph_server.php",
           data: {"host" : host}, 
           success: function(response)
             { 
               $("#server-graphs").html(response);
               
             }
   });
   
 }
 $(document).ready(function(){
   setInterval(function(){
     refreshPage();
   }, 30000);    
 });
 

