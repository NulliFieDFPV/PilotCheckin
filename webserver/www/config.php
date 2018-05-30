 <?PHP

error_reporting(E_ALL);
session_start();

include "includes/functions.inc.php";
include "includes/races.inc.php";
include "includes/channels.inc.php";
$pid=0;
$raceid=0;
$action="";
$optionid=0;
$cid=0;

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


if (isset($_POST["cid"])) {
    $cid=$_POST["cid"];
    //$_SESSION["raceid"]=$raceid;
}

if (isset($_GET["cid"])) {
    $cid=$_GET["cid"];
    //$_SESSION["raceid"]=$raceid;
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
    
    switch ($action) {
    
        case "save":
        
            switch ($optionid) {
                case 0:
                    //Races
                    //print_r($_POST);
                    $racename=$_POST["race_name"];
                    $racedate=$_POST["race_date"];
                    $racestatus=$_POST["status"];
                    
                    //Daten in traces speichern
                    if ($raceid==0) {
                        //neu
                        $raceid=addRace($racename, $racedate, $racestatus);
                    }
                    else {
                        //update
                        updateRace($raceid, $racename, $racedate, $racestatus);
                    }
                    
                    //Channel-Konfig speichern
                    $arrNewChannels=array();
                    $arrRaceOptions=array();
                    foreach($_POST as $key => $val) {
                        //print $key[0];
                        if (substr($key,0,4)=="chan") {
                            $arrNewChannels[substr($key,4)]=$val;
                        }
                        else {
                            $arrRaceOptions[$key]=$val;
                        }
                    }
                    
                    updateRaceToChannels($raceid, $arrNewChannels);
                    //sonstige traceoptions speichern
                    
                    updateRaceOptions($raceid, $arrRaceOptions);
                    break;
                    
                case 1:
                    ///Channel
                    
                    $ch_name=$_POST["channel_name"];
                    $ch_status=$_POST["status"];
                    $ch_band=$_POST["channel_band"];
                    $ch_channel=$_POST["channel_channel"];
                    $ch_address=$_POST["channel_address"];
                    if ($cid==0) {
                        //neu
                        $cid=addchannel($ch_name, $ch_band, $ch_channel, $ch_address, $ch_status);
                    }
                    else {
                        //update
                        updateChannel($cid, $ch_name, $ch_band, $ch_channel, $ch_address, $ch_status);
                    }
                    
                    break;
            }
            
            break;

            
        case "delete":
        
            switch ($optionid) {
                case 0:
                    //Races
                    deleteRace($rid);
                    break;
                    
                case 1:
                    deleteChannel($cid);
                    break;
                    
                default:
                
            }
            
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
            else if ($optionid==1) {

                $lstChannel=generateChannelList($cid);
                echo $lstChannel;

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
            else if ($optionid==1) {
                if ($cid>0) {
                    $channeldetails=ladeChannel($cid);
                    echo $channeldetails;
                }
                else {
                    if ($action=="neu") {
                        $channeldetails=ladeChannel(0);
                        echo $channeldetails;
                    }
                }
            }
        ?>


    </section>
</section>
</body>
</html>
