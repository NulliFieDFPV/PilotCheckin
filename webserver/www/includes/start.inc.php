<?PHP

function setCurrentRace($raceid) {
    
    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');

    //Pruefung
    $sql ="SELECT * FROM traces WHERE RID=".$raceid." AND status=-1;";

    $result= $db->query($sql)->fetchAll();
    
    if (count($result) >0) {
        $sql ="UPDATE traces SET current=0 WHERE RID <>?; ";
        $sql .="UPDATE traces SET current=-1 WHERE RID=?; ";
        
        $statement= $db->prepare($sql);
        $statement->execute([$raceid, $raceid]);  
    }
    

}


function generateStats() {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    
    $tbl="<table width=\"100%\" >";

    $tbl .="<tr>";
    $tbl .="<th>Callsign</th>";
    $tbl .="<th>Wartend</th>";
    $tbl .="<th>Heats gesamt</th>";
    $tbl .="<th>Heats heute</th>";
    $tbl .="<tr>";
        
        
    $sql = "SELECT * FROM traces ";
    $sql .= "WHERE status=-1 AND current=-1 LIMIT 1";
    //echo $sql;

    $raceid=0;
    
    foreach ($db->query($sql) as $row) {
        $raceid=$row["RID"];
    }
    
    if ($raceid >0) {
        $sql="SELECT a.WID, callsign, w.status, a.AID FROM tattendance a ";
        $sql .="INNER JOIN tpilots p ";
        $sql .="ON a.PID=p.PID ";
        
        $sql .="LEFT JOIN twaitlist w ";
        $sql .="ON a.WID=w.WID ";
        
        $sql .="WHERE a.RID=".$raceid." AND a.status=-1";
    
        foreach ($db->query($sql) as $row) {
            $tbl .="<tr>";
            $tbl .="<td style=\"width:30%\">".$row["callsign"]."</td>";
            
            if ($row["WID"]>0 && $row["status"]<>0) {
                $tbl .="<td style=\"text-align:center\"><div class=\"online\">&nbsp;</div></td>";
            }
            else {
                $tbl .="<td style=\"text-align:center\"><div class=\"offline\">&nbsp;</div></td>";
            }
            
            
            $sql= "SELECT * FROM twaitlist WHERE AID=".$row["AID"]."; ";
            $result= $db->query($sql)->fetchAll();
    
            $tbl .="<td>".count($result)."</td>";
            
            $sql= "SELECT * FROM twaitlist WHERE AID=".$row["AID"]." AND wait_date='".date("Y-m-d")."'; ";
            $result= $db->query($sql)->fetchAll();
            
            $tbl .="<td>".count($result)."</td>";
            $tbl .="<tr>";
        }
    }
    
    $tbl .="</table>";

    return $tbl;

}


function generateCurrentRaceCombo() {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    

    $cbo ="<select id=\"race\" name=\"race\" onChange=\"this.form.submit()\" style=\"width:100%;\" >\n";
    $cbo .="<option value=\"-1\">Race w&auml;hlen...</option>";

    
    $sql = "SELECT * FROM traces ";
    $sql .= "WHERE status=-1 ";
    $sql .= "ORDER BY race_name;";
    //echo $sql;
    
    $result=$db->query($sql)->fetchAll();

    foreach ($result as $row) {
    
        $cbo .="<option ";
        if ($row["current"]==-1) {
            $cbo .="selected ";
        }
        $cbo .="value=\"".$row["RID"]."\">".$row['race_name'];
        
        $sql="SELECT * FROM tattendance WHERE RID=".$row["RID"]." AND status=-1";
        $resAnzahl=$db->query($sql)->fetchAll();
        
        $cbo .=" (".count($resAnzahl)." Teilnehmer ";      
        
        $sql="SELECT * FROM twaitlist WHERE RID=".$row["RID"]." AND status IN (-1, 1)";
        $resAnzahl=$db->query($sql)->fetchAll();

        $cbo .= count($resAnzahl)." davon eingecheckt)"; 
        
        $cbo .="</option>\n";
    }
    
    $cbo .="</select>\n";
    
    return $cbo;
}

?>
