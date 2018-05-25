 <?PHP

error_reporting(E_ALL);
session_start();

include "includes/functions.inc.php";
include "includes/pilots.inc.php";

$pid=0;

if (isset($_POST["race"])) {
    $raceid=$_POST["race"];
    $_SESSION["raceid"]=$raceid;
}

if (isset($_SESSION["raceid"])) {
    $raceid=$_SESSION["raceid"];
}

$cbo=generateRaceCbo($raceid);



if (isset($_GET["pid"])) {
    $pid=$_GET["pid"];
}


?>

<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" type="text/css" href="css/default.css">
    <title>Pilot Checkin - PILOTEN</title>
</head>

<body>
    <?PHP include "navigation.php" ?>
    <section class="race">

    <form action="pilots.php" method="post">
      <?PHP echo $cbo; ?>
    </form>
    </section>


<br>
<section class=\"main\">

    <section style="display:block; overflow: hidden; ">
    <aside class="pilots" >
        <form action="pilots.php" method="post">

            <h1>Piloten</h1>
            <?PHP
            if ($raceid>0) {

                $lstPilots=generatePilotList($raceid);
                echo $lstPilots;

            }
            ?>

            <button type="submit">Speichern</button>

        </form>
    </aside>
    <section class="pilot">
        <h1>Pilotdetails</h1>
        <?PHP
            if ($pid>0) {
                $pilotendetails=ladePilot($pid);
                echo $pilotendetails;
             }
        ?>

    </section>
    </section>
</section>
</body>
</html>
