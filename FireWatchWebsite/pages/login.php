<?php
    @session_start();
    $_SESSION["loginVerified"] = false;
    if(empty($_SESSION["loginFailed"])) {
        $_SESSION["loginFailed"] = false;
    }
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Login Page</title>

    <link rel="stylesheet" href="../css/opensans.css">
    <link rel="stylesheet" href="../css/fontawesome.min.css">
    <link rel="stylesheet" href="../css/bootstrap.min.css">
    <link rel="stylesheet" href="../css/tooplate.css">
    <link rel="stylesheet" href="../css/firewatch.custom.css">
</head>

<body class="bg03">
    <div class="container">
        <div class="row tm-mt-big">
            <div class="col-12 mx-auto tm-login-col">
                <div class="bg-white tm-block">
                    <div class="row">
                        <div class="col-12 text-center">
                            <img src="../img/firewatch_logo.png" alt="Firewatch" style="width:183px;height:220px;">
                            <h2 class="tm-block-title mt-3">Firewatch Login</h2>
                        </div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-12">
                            <form action="../scripts/verify_login.php" method="POST" class="tm-login-form">
                                <div class="input-group">
                                    <label for="username" class="col-xl-4 col-lg-4 col-md-4 col-sm-5 col-form-label">Username</label>
                                    <input name="username" type="text" class="form-control validate col-xl-9 col-lg-8 col-md-8 col-sm-7" id="username">
                                </div>
                                <div class="input-group mt-3">
                                    <label for="password" class="col-xl-4 col-lg-4 col-md-4 col-sm-5 col-form-label">Password</label>
                                    <input name="password" type="password" class="form-control validate" id="password">
                                </div>
                                <div class="input-group mt-3">
                                    <button type="submit" class="btn btn-primary d-inline-block mx-auto">Login</button>
                                </div>
                                <?php 
                                    if($_SESSION["loginFailed"] === true)
                                    echo("
                                    <div class=\"input-group mt-3 fw-error-text\">
                                        <p><em>Login failed. Please verify login information and try again.</em></p>
                                        <p><em>If the issue persists, please contact FireWatch technical support.</em></p>
                                    </div>")
                                ?>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <footer class="row tm-mt-big">
        </footer>
    </div>
</body>

</html>