<?php 
    function OpenConnection() 
    { 
        $dbhost = "localhost"; 
        $dbuser = "root"; 
        $dbpass = "grp4";
        $db = "firewatchdata";  

        $conn = new mysqli($dbhost, $dbuser, $dbpass,$db)
                or die("Connect failed: %s\n". $conn -> error); 

        return $conn; 
    } 

    function CloseConnection($conn) 
    {
        $conn -> close(); 
    }
?>
