 <?PHP

error_reporting(E_ALL);
session_start();

include "includes/functions.inc.php";
include "includes/races.inc.php";

$pid=0;
$raceid=0;
$action="";
$optionid=0;

if (isset($_POST["race"])) {
    $raceid=$_POST["race"];
    //$_SESSION["raceid"]=$raceid;
}

if (isset($_GET["race"])) {
    $raceid=$_GET["race"];
    //$_SESSION["raceid"]=$raceid;
}

if (isset($_SESSION["raceid"])) {
    //$raceid=$_SESSION["raceid"];
}



if (isset($_POST["option"])) {
    $optionid=$_POST["option"];
    $_SESSION["option"]=$optionid;
}

if (isset($_SESSION["option"])) {
    $optionid=$_SESSION["option"];
}

switch ($optionid) {
    case 0:
        $headline="Races";
        $headline_details="Racedetails";
        break;
        
    case 1:
        $headline="Channel";
        $headline_details="Channeldetails";
        break;
        
}

$cbo=generateOptionCbo($optionid);






if (isset($_GET["action"])) {

    $action=$_GET["action"];
    
    switch ($_GET["action"]) {
    
        case "save":
        
            switch ($optionid) {
                case 0:
                    //Races
                    //print_r($_POST);
                    $racename=$_POST["race_name"];
                    $racedate=$_POST["race_date"];
                    $racestatuse=$_POST["status"];
                    
                    //Daten in traces speichern
                    if ($raceid==0) {
                        //neu
                        $raceid=addRace($racename, $racedate, $racestatuse);
                    }
                    else {
                        //update
                        updateRace($raceid, $racename, $racedate, $racestatuse);
                    }
                    
                    //Channel-Konfig speichern
                    $arrNewChannels=array();
                    
                    foreach($_POST as $key => $val) {
                        //print $key[0];
                        if ($key[0]=="c") {
                            $arrNewChannels[substr($key,1)]=$val;
                        }
                    }
                    
                    updateRaceToChannels($raceid, $arrNewChannels);
                    //sonstige traceoptions speichern
                    break;
                    
                case 1:
                    ///Channel
                    break;
            }
            
            break;

            
        case "delete":
            $rid=$_GET["id"];
            
            deleteRace($rid);
            
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
    <title>Pilot Checkin - RACES</title>
</head>

<body>
    <?PHP include "navigation.php" ?>

   <section class="race">

    <form action="config.php" method="post">
      <?PHP echo $cbo; ?>
    </form>
    </section> 
    
    
    
<section class="main" style="display:block; overflow: hidden; ">


    <nav class="pilots" >

            <h1><?PHP echo $headline ?></h1>
            <?PHP
            if ($optionid==0) {

                $lstRaces=generateRaceList($raceid);
                echo $lstRaces;

            }
            ?>

            
            <a href="config.php?action=neu" class="neubutton">Neu</a> 

    </nav>
    <section class="pilot">
        <h1><?PHP echo $headline_details ?></h1>
        <?PHP
            if ($optionid==0) {
                if ($raceid>0) {
                    $racedetails=ladeRace($raceid);
                    echo $racedetails;
                }
                else {
                    if ($action=="neu") {
                        $racedetails=ladeRace(0);
                        echo $racedetails;
                    }
                }
            }
        ?>


    </section>
</section>
</body>
</html>
