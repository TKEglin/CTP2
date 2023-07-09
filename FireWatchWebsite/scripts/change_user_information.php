<?php
    @session_start();
    
    $username = $_POST["username"];
    $password = $_POST["password"];

    include 'database_connection.php';
    $conn = OpenConnection();

    $conn -> query("truncate userdata");

    $conn -> query((
        "INSERT INTO userdata (username, password)
         VALUES ('$username', '$password')"       ));

    
    CloseConnection($conn);


    header("Location: ../pages/dashboard.php");
    exit();
?>