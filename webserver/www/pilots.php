 <?PHP

error_reporting(E_ALL);
session_start();

include "includes/functions.inc.php";
include "includes/pilots.inc.php";

$pid=0;
$raceid=0;
$action="";

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



if (isset($_GET["action"])) {

    $action=$_GET["action"];
    
    switch ($_GET["action"]) {
        case "save":
        
            $callsign=$_POST["callsign"];
            $rfidid=$_POST["rfidid"];
            
            if ($callsign=="") {
                //Fehlerbehandlung
                
            }
            else {
                if ($_GET["pid"]==0) {
                    //neu
                    $pid=addPilot($callsign);
                }
                else {
                    //update
                    updatePilot($pid, $callsign);
                }
                
                
                if ($rfidid >0) {
                    assocCard($rfidid, $pid);
                }
                else if ($rfidid==-1) {
                    assocCard(0, $pid);
                }
            }
            
            break;
        case "asso":
            //Pilotenzuordnung

            $attendies=$_POST["attend"];
            PilotToRace($raceid, $attendies);
            break;
            
        case "delete":
            $pid=$_GET["id"];
            
            deletePilot($pid);
            
            break;
        default:
            $action=$_GET["action"];
    }

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

<section class="main" style="display:block; overflow: hidden; ">


    <nav class="pilots" >
        <form action="pilots.php?action=asso" method="post">

            <h1>Piloten</h1>
            <?PHP
            if ($raceid>0) {

                $lstPilots=generatePilotList($raceid, $pid);
                echo $lstPilots;

            }
            ?>
            <input type="hidden" name="race" value="<?PHP echo $raceid ?>">
            
            <a href="pilots.php?action=neu" class="neubutton">Neu</a> <input type="submit" value="Speichern">

        </form>
    </nav>
    <section class="pilot">
        <h1>Pilotdetails</h1>
        <?PHP
            if ($pid>0) {
                $pilotendetails=ladePilot($pid);
                echo $pilotendetails;
             }
             else {
                if ($action=="neu") {
                    $pilotendetails=ladePilot($pid);
                    echo $pilotendetails;
                }
             }
        ?>


    </section>
</section>
</body>
</html>
