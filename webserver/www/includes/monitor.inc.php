<?PHP

error_reporting(E_ALL);
function ladeTabelle($raceid) {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');

    //Channel ziehen, das sind die Spalten
    $sql = "SELECT * FROM traceoptions o ";
    $sql .="INNER JOIN tchannels c ";
    $sql .="ON o.option_value=c.CID ";

    $sql .= "WHERE o.RID=".$raceid." AND o.option_name='channel'";
    $sql .= "AND o.status=-1 ";
    $sql .= "ORDER BY channel_name;";
    //echo $sql;



    $tablehead="<tr>";
    $tablerow="<tr>";


    $result=$db->query($sql)->fetchAll();

    foreach ($result as $row) {

        $r=255;
        $g=255;
        $b=255;

        //jeder Channel hat auch ne Farbe in diesem Race
        $sql = "SELECT * FROM traceoptions WHERE ACCID=".$row["CID"]." AND RID=".$raceid." ";
        $sql .="AND option_name IN ('colorRed','colorGreen', 'colorBlue') ";
        $sql .="AND status=-1;";
        //echo $sql;

        foreach ($db->query($sql) as $rowColor) {
            switch($rowColor["option_name"]) {
                case "colorRed":
                    $r=$rowColor["option_value"];
                    break;
                case "colorGreen":
                    $g=$rowColor["option_value"];
                    break;

                 case "colorBlue":
                    $b=$rowColor["option_value"];
                    break;

            }
        }



        $sql = "SELECT p.callsign, w.status, r.UID FROM twaitlist w ";
        $sql .="INNER JOIN tattendance a ";
        $sql .="ON a.WID=w.WID ";
        $sql .="INNER JOIN tpilots p ";
        $sql .="ON a.PID=p.PID ";

        $sql .= "LEFT JOIN trfid r ";
        $sql .="ON r.PID=p.PID ";

        $sql .= "WHERE w.CID=".$row["CID"]." AND w.rid=".$raceid." ";
        $sql .= "AND w.status IN (-1,1) ";

        $sql .="ORDER BY w.status DESC, w.wait_date, w.wait_time";

        $resultWaiting=$db->query($sql)->fetchAll();

        $tablerow .="<td style=\"vertical-align: top\"><div style=\"vertical-align: top\">";

        foreach ($resultWaiting as $rowWaitlist) {
            if ($rowWaitlist["status"]==1) {
                //Inflight
                $tablerow .="<div style=\"background-color:#ccccff; font-weight: bold; padding:0.5em; margin:0.1em;  text-align:center; \">".$rowWaitlist["callsign"]."</div>\n";
            }
            else {
                $tablerow .="<div style=\"background-color:white; padding:0.5em; margin:0.1em; text-align:center\" >".$rowWaitlist["callsign"]."</div>\n";
            }
        }

        $tablerow .="</div></td>\n";


        $tablehead .="<th style=\"background-color:rgb(".$r.", ".$g.", ".$b."); color:white; padding:1em; margin:1em\" ><div style=\"background-color:black; padding:0.2em\">".$row["channel_name"]."</div></th>\n";

    }
    $tablehead .="</tr>";
    $tablerow .="</tr>";


    $table="<table width=\"100%\">";
    $table .=$tablehead;
    $table .=$tablerow;


    $table .="</table>";


    return $table;

}



?>
