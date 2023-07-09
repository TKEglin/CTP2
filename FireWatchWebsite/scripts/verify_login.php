<?php
    @session_start();

    include 'database_connection.php';
    $conn = OpenConnection();

    $sql = "SELECT * FROM userdata";
    $result = $conn->query($sql);
    
    CloseConnection($conn); 

    $username = $_POST["username"];
    $password = $_POST["password"];


    $row = $result->fetch_assoc();

    if (strcmp($username, $row["username"]) != 0 or strcmp($password, $row["password"]) != 0) {
        // Not equal -> return to login
        $_SESSION["loginVerified"] = false;
        $_SESSION["loginFailed"] = true;
        header("Location: ../pages/login.php");
        exit();
    } else { 
        // Equal -> go to main page
        $_SESSION["loginVerified"] = true;
        $_SESSION["loginFailed"] = false;
        header("Location: ../pages/dashboard.php");
        exit();
    }



?>