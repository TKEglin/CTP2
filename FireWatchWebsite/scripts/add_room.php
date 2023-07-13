<?php
    @session_start();

    # Checking that user is logged in
    if(empty($_SESSION["loginVerified"]) or $_SESSION["loginVerified"] === false) {
        header("Location: ../pages/login.php");
        exit();
    }
    
    $name = $_POST["name"];

    include 'database_connection.php';
    $conn = OpenConnection();

    $query = "INSERT IGNORE INTO `roomdata` (`name`)
              VALUES ('$name')";

    echo $query;

    $conn -> query(($query));

    CloseConnection($conn);


    header("Location: ../pages/manage.php");
    exit();
?>