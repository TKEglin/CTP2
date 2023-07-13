<?php
    @session_start();

    # Checking that user is logged in
    if(empty($_SESSION["loginVerified"]) or $_SESSION["loginVerified"] === false) {
        header("Location: ../pages/login.php");
        exit();
    }
    
    $name = $_POST["name"];
    $room = $_POST["room"];
    $uid = $_POST["uid"];

    include 'database_connection.php';
    $conn = OpenConnection();

    $result = $conn->query("SELECT * FROM supporteddevices WHERE uid = " . $uid);
    $supporteddevice = $result->fetch_assoc();
    
    $function    = $supporteddevice["name"] . " (" . $supporteddevice["function"] . ")";
    $device_JSON = $supporteddevice["device_JSON"];

    // $query = "INSERT INTO devicedata(name, function, room, device_JSON) 
    //           VALUES ( '" . $name . 
    //                "', '" . $function . 
    //                "', '" . $room .
    //                "', 'test')";


    $query = "INSERT INTO `devicedata` (`name`, `type`, `room`, `device_JSON`)
              VALUES ('$name', '$function', '$room', '$device_JSON')";

    echo $query;

    $conn -> query(($query));

    CloseConnection($conn);


    header("Location: ../pages/manage.php");
    exit();
?>