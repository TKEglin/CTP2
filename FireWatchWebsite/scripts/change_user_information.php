<?php
    @session_start();
    
    # Checking that user is logged in
    if(empty($_SESSION["loginVerified"]) or $_SESSION["loginVerified"] === false) {
        header("Location: ../pages/login.php");
        exit();
    }
    
    
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