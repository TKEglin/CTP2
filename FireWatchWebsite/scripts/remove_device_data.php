<?php
    @session_start();

    # Checking that user is logged in
    if(empty($_SESSION["loginVerified"]) or $_SESSION["loginVerified"] === false) {
        header("Location: ../pages/login.php");
        exit();
    }

    $target = $_POST["target"];

    include 'database_connection.php';
    $conn = OpenConnection();

    if($target === "selected" && !empty($_POST["checkboxes"])) {
        $uids = $_POST["checkboxes"];

        $uids_string = implode("','", $uids);
        $query = "DELETE FROM `devicedata` WHERE uid IN ('".$uids_string."')";
    
        $conn -> query(($query));
    }
    else if($target === "all") {
        $conn -> query(("truncate `devicedata`"));
        $conn -> query(("truncate `roomdata`"));
    }

    CloseConnection($conn);

    header("Location: ../pages/manage.php");
    exit();
?>