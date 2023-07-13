<?php 
    @session_start();

    # Checking that user is logged in
    if(empty($_SESSION["loginVerified"]) or $_SESSION["loginVerified"] === false) {
        header("Location: login.php");
        exit();
    }

    # Getting event data
    include '../scripts/database_connection.php';
    $conn = OpenConnection();

    $supporteddevices = $conn->query("SELECT * FROM supporteddevices");
    $roomdata         = $conn->query("SELECT * FROM roomdata"        );
    $devicedata       = $conn->query("SELECT * FROM devicedata"      );
    
    CloseConnection($conn);

    # Timezone
    date_default_timezone_set('Europe/Copenhagen');
?>

<!DOCTYPE html>
<html lang="en">


<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Firewatch Manager</title>

    <link rel="stylesheet" href="../css/opensans.css">
    <link rel="stylesheet" href="../css/fontawesome.min.css">
    <link rel="stylesheet" href="../css/bootstrap.min.css">
    <link rel="stylesheet" href="../css/tooplate.css">
</head>

<body id="reportsPage">
    <div class="" id="home">
        <div class="container">
            <div class="row">
                <div class="col-12">
                    <nav class="navbar navbar-expand-xl navbar-light bg-light">
                        <a class="navbar-brand" href="dashboard.php">
                            <img src="../img/firewatch_logo.png" alt="Firewatch" style="width:54px;height:65px;">
                            <h1 class="tm-site-title mb-0">Firewatch Dashboard</h1>
                        </a>
                        <button class="navbar-toggler ml-auto mr-0" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent"
                            aria-expanded="false" aria-label="Toggle navigation">
                            <span class="navbar-toggler-icon"></span>
                        </button>

                        <div class="collapse navbar-collapse" id="navbarSupportedContent">
                            <ul class="navbar-nav mx-auto">
                            </ul>
                            <ul class="navbar-nav">
                                <li class="nav-item active">
                                    <a class="nav-link d-flex" href="manage.php">
                                        <i class="fas fa-3x fa-tachometer-alt mr-2 tm-logout-icon"></i>
                                        <span>Manage System</span>
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link d-flex" href="login.php">
                                        <i class="far fa-user mr-2 tm-logout-icon"></i>
                                        <span>Logout</span>
                                    </a>
                                </li>
                            </ul>
                        </div>  
                    </nav>
                </div>
            </div>
            <!-- row -->
            <div class="row tm-content-row tm-mt-big">

                <div class="col-xl-8 col-lg-12 tm-md-12 tm-sm-12 tm-col">
                    <div class="bg-white tm-block h-100">
                        <div class="row">
                            <div class="col-md-8 col-sm-12">
                                <h2 class="tm-block-title d-inline-block">Devices</h2>
                            </div>
                        </div>
                        <form action = "../scripts/remove_device_data.php" method ="POST">
                        <div class="table-responsive" style="max-height:1000px;overflow:auto;">
                            <table class="table table-hover table-striped tm-table-striped-even mt-3">
                                <thead>
                                    <tr class="tm-bg-gray">
                                        <th scope="col">&nbsp;</th>
                                        <th scope="col">Device Name</th>
                                        <th scope="col">Room</th>
                                        <th scope="col">Type</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php 
                                    if ($devicedata->num_rows > 0) {
                                        while($device = $devicedata->fetch_assoc()) {
                                            echo 
                                           "<tr>
                                                <th scope=\"row\">
                                                    <input value=\"", $device["uid"], "\" 
                                                        type=\"checkbox\"
                                                        name=\"checkboxes[]\"
                                                        aria-label=\"Checkbox\">
                                                </th>
                                                <td class=\"tm-product-name\">", $device["name"], "</td>
                                                <td>", $device["room"], "</td>
                                                <td>", $device["type"], "</td>
                                            </tr>";
                                        }
                                    }
                                    ?>
                                </tbody>
                            </table>
                        </div>
                        <div class="tm-table-mt tm-table-actions-row">
                            <div class="tm-table-actions-col-left">
                                <a class="nav-link d-flex">
                                    <button type="submit" name="target" value="selected" class="btn">Delete Selected</button>
                                </a>
                            </div>
                            <div class="tm-table-actions-col-right" >
                                <a class="nav-link d-flex">
                                    <button type="submit" name="target" value="all" class="btn btn-danger">Delete All Data</button>
                                </a>
                            </div>
                        </div>
                        </form>
                    </div>
                </div>
                 
                <div class="col-xl-4 col-lg-12 tm-md-12 tm-sm-12 tm-col">
                    <div class="bg-white tm-block">
                        <div>
                            <div>
                                <h2 class="tm-block-title d-inline-block">Add Device</h2>
                                <form action="../scripts/add_device.php" class="tm-edit-product-form" method="POST">
                                    <div>
                                        <label for="name">Device Name </label>
                                        <input id="name" name="name" type="text" class="form-control validate" required>
                                    </div>
                                    <div>
                                        <label for="room" >Device Room </label>
                                        <select name="room" class="custom-select" id="room" required>              
                                            <option value="" disabled selected hidden>Choose a room</option>
                                            <?php 
                                                if ($roomdata->num_rows > 0) {
                                                    while($room = $roomdata->fetch_assoc()) {
                                                        echo "<option value=\"", $room["name"], "\">", $room["name"], "</option>";
                                                    }
                                                } 
                                            ?>
                                        </select>
                                        <p style = "margin-top:25px"></p>
                                    </div>
                                    <div >
                                        <label for="uid">Device Brand</label>
                                        <select name="uid" class="custom-select " id="uid" required>              
                                        <option value="" disabled selected hidden>Choose a device</option>
                                            <?php 
                                                if ($supporteddevices->num_rows > 0) {
                                                    while($device = $supporteddevices->fetch_assoc()) {
                                                        echo "<option value=\"", $device["uid"], "\">", $device["name"], " (", $device["function"], ")</option>";
                                                    }
                                                } 
                                            ?>
                                        </select>
                                    </div>

                                    <div class="input-group mb-3" style="margin-top:30px; margin-buttom:10px;">
                                        <div class="ml-auto col-xl-8 pl-0">
                                            <button type="submit" class="btn btn-primary">Add</button>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                        <div>
                            <div>
                                <h2 class="tm-block-title d-inline-block">Add Room</h2>
                                <form action="../scripts/add_room.php" class="tm-edit-product-form" method="POST">
                                    <div>
                                        <label for="name">Room Name </label>
                                        <input id="name" name="name" type="text" class="form-control validate" required>
                                    </div>

                                    <div class="input-group mb-3" style="margin-top:30px; margin-buttom:10px;">
                                        <div class="ml-auto col-xl-8 pl-0">
                                            <button type="submit" class="btn btn-primary">Add</button>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <footer class="row tm-mt-small">
            </footer>
        </div>
</body>
</html>