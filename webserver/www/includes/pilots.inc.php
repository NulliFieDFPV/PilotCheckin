<?PHP


function ladePilot($pid) {


}

function generatePilotList($raceid) {


    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');

    $sql = "SELECT * FROM tpilots ORDER BY callsign";

    $lst="<ul id=\"piloten\">";

    foreach ($db->query($sql) as $row) {

        $sql="SELECT * FROM tattendance WHERE PID=".$row["PID"]." AND RID=".$raceid." AND status=-1";
        $result=$db->query($sql)->fetchAll();
        $lst .="<li><input type=\"checkbox\" name=\"attend[]\" ";

        if (count($result)>0) {
            $lst .=" checked ";
        }


         $lst .=" value=\"".$row["PID"]."\"><a href=\"pilots.php?action=edit&pid=".$row["PID"]."\">".$row["callsign"];

         $sql="SELECT * FROM trfid WHERE PID=".$row["PID"]." AND status=-1";

         foreach($db->query($sql) as $rowRfid) {
            $lst .=" (".$rowRfid["UID"].")";
         }

         $lst .="</a></li>";
    }

    $lst .="</ul>";

    return $lst;

}


?>