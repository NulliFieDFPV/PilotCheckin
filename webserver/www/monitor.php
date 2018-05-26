 <?PHP

error_reporting(E_ALL);
session_start();

include "includes/functions.inc.php";
include "includes/monitor.inc.php";

$raceid=0;
if (isset($_GET["race"])) {
    $raceid=$_GET["race"];
}


if (isset($_GET["race"])) {
    $raceid=$_GET["race"];
    $_SESSION["raceid"]=$raceid;
}

if (isset($_SESSION["raceid"])) {
    $raceid=$_SESSION["raceid"];
}



if ($raceid>0) {
    header("Refresh: 3; URL=monitor.php?race=".$raceid);
}


$cbo=generateRaceCbo($raceid);


?>

<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" type="text/css" href="css/default.css">
    <title>Pilot Checkin - MONITOR</title>
</head>

<body>
    <?PHP include "navigation.php" ?>
    <section class="race">

    <form action="monitor.php" method="get">
      <?PHP echo $cbo; ?>
    </form>
    </section>

    <section class="racetable">
    <?PHP
    if ($raceid>0) {
        //Teilnehmer laden

        //Monitor laden
        echo ladeTabelle($raceid);

    }
    ?>
    </section>
</body>
</html>
