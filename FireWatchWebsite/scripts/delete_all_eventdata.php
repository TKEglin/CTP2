<?php
    @session_start();

    # Checking that user is logged in
    if(empty($_SESSION["loginVerified"]) or $_SESSION["loginVerified"] === false) {
        header("Location: login.php");
        exit();
    }
    

    include 'database_connection.php';
    $conn = OpenConnection();

    $conn->query("truncate eventdata");

    CloseConnection($conn);


    header("Location: ../pages/dashboard.php");
    exit();
?>