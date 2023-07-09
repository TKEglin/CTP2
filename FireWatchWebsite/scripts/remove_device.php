<?php
    @session_start();

    # Checking that user is logged in
    if(empty($_SESSION["loginVerified"]) or $_SESSION["loginVerified"] === false) {
        header("Location: login.php");
        exit();
    }

    $uids = $_POST["checkboxes"];

    if(count($uids) === 0) {
        header("Location: ../pages/manage.php");
        exit();
    }

    include 'database_connection.php';
    $conn = OpenConnection();

    $uids_string = implode("','", $uids);
    $query = "DELETE FROM `devicedata` WHERE uid IN ('".$uids_string."')";

    $conn -> query(($query));

    CloseConnection($conn);


    header("Location: ../pages/manage.php");
    exit();
?>