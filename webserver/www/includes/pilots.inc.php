<?PHP

function updatePilot($pid, $callsign) {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    
    $sql= "UPDATE tpilots SET callsign=? WHERE PID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$callsign, $pid]);
    
}

function addPilot($callsign) {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    $newid=0;
    
    $sql= "INSERT INTO tpilots SET callsign=?";
    $statement= $db->prepare($sql);
    
    $statement->execute([$callsign]);
    
    $newid=$db->lastInsertId(); 
    
    return $newid;
}


function assocCard($id, $pid) {
    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    //zuerst alle mit pid deaktivieren
     
    $sql= "UPDATE trfid SET status=0, PID=0 WHERE PID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$pid]);   
    
    
    $sql= "UPDATE trfid SET status=-1, PID=? WHERE RFIDID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$pid, $id]);   
    
}



function deletePilot($pid) {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
     
    $sql= "UPDATE trfid SET status=0, PID=0 WHERE PID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$pid]);
    
    
    $sql= "SELECT * FROM tattendance WHERE PID=".$pid.";";
    
    foreach($db->query($sql) as $row) {
    
        $sql= "DELETE FROM twaitlist WHERE AID=?";
        
        $statement= $db->prepare($sql);
        $statement->execute([$row["AID"]]);
        
        $sql= "DELETE FROM tattendance WHERE AID=?";
        
        $statement= $db->prepare($sql);
        $statement->execute([$row["AID"]]);     
        
    }
    
     $sql= "DELETE FROM tpilots WHERE PID=?";
        
     $statement= $db->prepare($sql);
     $statement->execute([$pid]); 
    
}



function ladePilot($pid) {


    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    
    $sql="SELECT * FROM tpilots WHERE PID=".$pid.";";
    $result=$db->query($sql)->fetchAll();
    
    
    if (count($result)>0) {
        $data=$result[0];
    }
    else {
    
        $pid=0;
    }
    
    $sec ="<form action=\"pilots.php?action=save&pid=".$pid."\" method=\"post\">";
 
 
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"pid\">Piloten-ID:</label>";
    $sec .="    </div>";
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <input type=\"text\" id=\"pid\" name=\"pid\" value=\"".$pid."\" readonly disabled>";
    $sec .="    </div>";
    $sec .="  </div>";
    
    
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"callsign\">Callsign:</label>";
    $sec .="    </div>";
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <input type=\"text\" id=\"callsign\" name=\"callsign\" value=\"".$data["callsign"]."\">";
    $sec .="    </div>";
    $sec .="  </div>";
    

    
    $sql="SELECT * FROM trfid WHERE (PID=".$pid." AND status=-1) OR status >-1 ORDER BY status ASC;";

    
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"uid\">Karten-ID:</label>";
    $sec .="    </div>";
    
    $sec .="    <div class=\"col-75\">";
    $sec .="      <select id=\"rfidid\" name=\"rfidid\" size=5>";
    $sec .="            <option value=\"-1\">-keine-</option>";
    
    foreach($db->query($sql) as $rowRfid) {
        $sec .="        <option value=\"".$rowRfid["RFIDID"]."\"";
        
        if ($rowRfid["PID"]==$pid && $rowRfid["status"]==-1) {
            $sec .=" selected ";
        
        }
        
        $sec .=">".$rowRfid["UID"]."</option>\n";
    }
    
    
    $sec .="      </select>";
    $sec .="    </div>";
    $sec .="  </div>";
    
    $sec .="  <div class=\"row\">";
    $sec .="    <a href=\"pilots.php?action=delete&id=".$pid."\" class=\"loeschbutton\">L&ouml;schen</a> <input type=\"submit\" value=\"Speichern\">";
    $sec .="  </div>";
    $sec .="</form>";
    
    
    return $sec;
    
}


function PilotToRace($raceid, $attendies) {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    
    
    //Erst mal alle reinpumpen - INSERT IGNORE und gut is...
    foreach ($attendies as &$pid) {
        $sql= "INSERT IGNORE INTO tattendance SET status=-1, PID=?, RID=?, WID=0";
    
        $statement= $db->prepare($sql);
        $statement->execute([$pid, $raceid]);   
    }
    
    $sql = "SELECT * FROM tattendance WHERE RID=".$raceid.";";
    foreach($db->query($sql) as $row) {
    
        $neuerStatus= (array_search($row["PID"], $attendies)!==False)*-1;
        
        if ($neuerStatus !=$row["status"]) {

            $sql = "UPDATE tattendance SET status=? WHERE PID=? AND RID=?; ";
            $statement= $db->prepare($sql);
            $statement->execute([$neuerStatus, $row["PID"], $raceid]);   
            
        }
        
    }

}

function generatePilotList($raceid, $pid) {


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

         $lst .=" value=\"".$row["PID"]."\"><a href=\"pilots.php?pid=".$row["PID"]."\" ";
         
         if ($row["PID"]==$pid) {
            $lst .=" style=\"font-weight:bold; font-style: italic; \" ";
        
         }
        
         $lst .=">".$row["callsign"];

         $sql="SELECT * FROM trfid WHERE PID=".$row["PID"]." AND status=-1";

         foreach($db->query($sql) as $rowRfid) {
            $lst .=" (".$rowRfid["UID"].")";
         }

         $lst .="</a></li>\n";
    }

    $lst .="</ul>";

    return $lst;

}

?>
