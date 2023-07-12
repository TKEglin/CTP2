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

    $eventdata = $conn->query("SELECT * FROM eventdata ORDER BY Timestamp DESC");
    $systemdata = $conn->query("SELECT * FROM systemdata");
    $systemdata = $systemdata->fetch_assoc();
    
    CloseConnection($conn);

    # Refresh Variables
    $page = $_SERVER['PHP_SELF'];
    $updaterate = "15";

    # Timezone
    date_default_timezone_set('Europe/Copenhagen');
?>

<!DOCTYPE html>
<html lang="en">
<meta http-equiv="refresh" content="<?php echo $updaterate?>;URL='<?php echo $page?>'">


<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Firewatch Dashboard</title>

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
                        <a class="navbar-brand" href="#">
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
                                <li class="nav-item">
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
                        <div class="fw-row" >
                            <h2 class="tm-block-title">System Status:</h2>
                            <?php
                                echo "<h2 style=\"color: ", $systemdata["statuscolor"], ";text-align:center\">", $systemdata["status"], "</h2>"
                            ?>
                        </div>
                    </div>
                </div>

                <div class="col-xl-4 col-lg-12 tm-md-12 tm-sm-12 tm-col">
                    <div class="bg-white tm-block h-100">
                        <h2 class="tm-block-title">Time unwatched:</h2>
                            <?php
                                $unwatchedtimestamp = $systemdata["unwatchedtimestamp"];
                                $adjusted_timestamp = time() - $unwatchedtimestamp - 3600;
                                if($unwatchedtimestamp === "TEMP") {
                                    echo "<h2 style=\"color:", $systemdata["statuscolor"], ";text-align:center\"> </h2>";
                                }
                                else {                                                                              // subtracting an hour to counteract timezone
                                    echo "<h2 id=\"unwatched_timer\" style=\"color: ", $systemdata["statuscolor"], ";text-align:center\">";
                                        if($adjusted_timestamp > 3600) {
                                            echo date('H', $adjusted_timestamp), ":";
                                        }
                                    echo date('H:i:s', $adjusted_timestamp), "</h2>";
                                }
                                echo "<script>
                                        let timestamp = Math.floor(Date.now() - ", $unwatchedtimestamp, "*1000) - 3600000;
                                        var interval = setInterval(function() {
                                            const date = new Date(timestamp);
                                            let time_formatted =  ('0' + date.getHours()).slice(-2) + \":\" 
                                                                + ('0' + date.getMinutes()).slice(-2) + \":\" 
                                                                + ('0' + date.getSeconds()).slice(-2);

                                            document.getElementById(\"unwatched_timer\").innerHTML = time_formatted;

                                            timestamp += 1000
                                        }, 1000)
                                    </script>";
                            ?>
                            <script>
                                const date = new Date()
                                
                                //alert(date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds())
                                if()

                            </script>
                    </div>
                </div>

                <div class="tm-col tm-col-full">
                    <div class="bg-white tm-block h-100">
                        <h2 class="tm-block-title">Event History</h2>
                        <div class="table-responsive" style="max-height:500px;overflow:auto;">
                            <table class="table table-hover table-striped tm-table-striped-even mt-3 fw-table-scroll">
                                <thead>
                                    <tr class="tm-bg-gray">
                                        <th scope="col">Event Type</th>
                                        <th scope="col" class="text-center">Event ID</th>
                                        <th scope="col" class="text-center">Location</th>
                                        <th scope="col">Time</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php 
                                    if ($eventdata->num_rows > 0) {
                                        while($event = $eventdata->fetch_assoc()) {
                                            echo "<tr>";
                                            echo "<td class=\"tm-product-name\">", $event["Type"], "</td>";
                                            echo "<td class=\"text-center\">", $event["ID"], "</td>";
                                            if($event["Location"] === "None"){
                                                echo "<td class=\"text-center\"></td>";
                                            }
                                            else{
                                                echo "<td class=\"text-center\">", $event["Location"], "</td>";
                                            }
                                            echo "<td>", date('H:i:s', $event["Timestamp"]), " - ", date('d/m/Y', $event["Timestamp"]), "</td>";
                                            echo "</tr>";
                                        }
                                    } 
                                    ?>
                                </tbody>
                            </table>
                        </div>

                        <div class="tm-table-mt tm-table-actions-row">
                            <div class="tm-table-actions-col-left">
                            </div>
                            <div class="tm-table-actions-col-right">
                                <a class="nav-link d-flex" href="../scripts/delete_all_eventdata.php">
                                    <button class="btn btn-danger">Delete All Event Data</button>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>


                <div class="tm-col tm-col-half">
                <div class="bg-white tm-block">
                    <div class="row">
                        <div class="col-12">
                            <h2 class="tm-block-title">Change Login Information</h2>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <form action="../scripts/change_user_information.php" method="POST" class="tm-signup-form">
                                <div class="form-group">
                                    <label for="username">New Username</label>
                                    <input placeholder="Input new username..." id="username" name="username" type="username" class="form-control validate">
                                </div>
                                <div class="form-group">
                                    <label for="password">New Password</label>
                                    <input placeholder="Input new password..." id="password" name="password" type="password" class="form-control validate">
                                </div>
                                <div class="row">
                                    <div class="col-12 col-sm-4">
                                        <button type="submit" class="btn btn-primary">Update
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
                <div class="tm-col tm-col-half">
                    <div class="bg-white tm-block h-40">
                        <h2 class="tm-block-title">About</h2>
                        <text class="tm-list-group-item">The FireWatch Safety System is designed to prevent fires and provide peace of mind for homeowners. The FireWatch system utilizes advanced motion-sensing technology and intelligent automation to safeguard your house by deactivating unwatched applicances.</text>
                    </div>
                    <div class="bg-white tm-block h-40">
                        <h2 class="tm-block-title">Contact Info</h2>

                        <text class="tm-list-group-item">Technical Support: 201908338@post.au.dk</text>

                    </div>
                </div>
            </div>
            <footer class="row tm-mt-small">
            </footer>
        </div>
</body>
</html>



