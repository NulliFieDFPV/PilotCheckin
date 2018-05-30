<?PHP


function updateRaceToChannels($raceid, $channels) {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
  

    foreach($channels as $channelid => $channel) {
    

        $arrFarben=array("colorRed"=>255, "colorGreen"=>255,"colorBlue"=>255);
        
        $sql= "SELECT * FROM traceoptions WHERE RID=".$raceid." AND option_value=".$channelid." AND option_name='channel'";
        
        $result=$db->query($sql)->fetchAll();
    
        if ($channel[0]==-1) {
            if (count($result)>0) {
                //Update
                $sql= "UPDATE traceoptions SET status=-1 WHERE RID=? AND option_value=? AND option_name='channel'";
                $statement= $db->prepare($sql);
                $statement->execute([$raceid, $channelid]);            
                
            }
            else {
                //insert
                $sql= "INSERT INTO traceoptions SET status=-1, RID=?, option_value=?, option_name='channel'";
                $statement= $db->prepare($sql);
                $statement->execute([$raceid, $channelid]);   
            }
        
            
            //Farbe speichern
            foreach($channel as $i => $val) {
                switch($i) {
                    case 1:
                        //rot
                        $arrFarben["colorRed"]=$val;
                        $r=$val;
                        break;
                    case 2:
                        //Grün
                        $arrFarben["colorGreen"]=$val;
                        break;
                    case 3:
                        //blau
                        $arrFarben["colorBlue"]=$val;
                        break;
                }
                    
            }
            
            foreach($arrFarben as $farbe => $wert) {
                $sql ="SELECT * FROM traceoptions WHERE option_name='".$farbe."' AND RID=".$raceid." AND ACCID='".$channelid."';";

                $resFarbe=$db->query($sql)->fetchAll();
                
                if (count($resFarbe)>0) {
                    $sql= "UPDATE traceoptions SET status=-1, option_value=? WHERE option_name=? AND RID=? AND ACCID=?;";
                    
                    $statement= $db->prepare($sql);
                    $statement->execute([$wert, $farbe, $raceid, $channelid]);   
                
                }
                else {
                    $sql= "INSERT INTO traceoptions SET status=-1, option_value=?, option_name=?, RID=?, ACCID=?;";
                    
                    $statement= $db->prepare($sql);
                    $statement->execute([$wert, $farbe, $raceid, $channelid]);  
                
                }
                
            
            }
            
        }        
        else {
            if (count($result)>0) {
            
                //deaktivieren der Option
                $sql= "UPDATE traceoptions SET status=0 WHERE RID=? AND option_value=? AND option_name='channel'";
                $statement= $db->prepare($sql);
                $statement->execute([$raceid, $channelid]);
    
                $sql= "UPDATE traceoptions SET status=0 WHERE RID=? AND ACCID=? AND option_name IN ('colorRed','colorGreen', 'colorBlue');";
                $statement= $db->prepare($sql);
                $statement->execute([$raceid, $channelid]);
            }
            
            
        }
        
    }

}

function updateRaceOptions($raceid, $arrRaceOptions) {
    
    $neuer_parameter="";
    $neuer_parameter_name="";
    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    
    foreach($arrRaceOptions as $key => $value) {
    
        switch($key) {
            case "race_name":
            case "status":
            case "race_date":
            
                break;
                
            case "neuer_parameter_name":
                if ($value !="") {
                    $neuer_parameter_name=$value;
                }
                break;
                
            case "neuer_parameter":
                if ($value !="") {
                    $neuer_parameter=$value;
                }
                break;
                
            default:

                
                $sql= "UPDATE traceoptions SET option_value=? WHERE RID=? AND option_name=?";
                $statement= $db->prepare($sql);
                $statement->execute([$value, $raceid, $key]);
        }
    
    }
    
    if ($neuer_parameter_name !="" && $neuer_parameter !="") {
        //cheggen, ob der neue parametername nicht doch schon existiert
        foreach($arrRaceOptions as $key => $value) {
            if ($key==$neuer_parameter_name) {
                $neuer_parameter_name="";
                $neuer_parameter="";
                break;
            }
        }
    }
    
    
    
    if ($neuer_parameter_name !="" && $neuer_parameter !="") {
        $sql= "INSERT INTO traceoptions SET option_value=?, RID=?, option_name=?, status=-1;";
        $statement= $db->prepare($sql);
        $statement->execute([$neuer_parameter, $raceid, $neuer_parameter_name]);
    
    }
    
}

function updateRace($rid, $race_name, $race_date, $race_status) {



    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    
    $sql= "UPDATE traces SET race_name=?, race_date=?, status=? WHERE RID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$race_name, $race_date, $race_status, $rid]);
    
    
}

function addRace($race_name, $race_date, $race_status) {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    $newid=0;
    
    $sql= "INSERT INTO traces SET race_name=?, race_date=?, status=?";
    $statement= $db->prepare($sql);
    
    $statement->execute([$race_name, $race_date, $race_status]);
    
    $newid=$db->lastInsertId(); 
    
    return $newid;
    
}




function deleteRace($rid) {

    
    
    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
     
    $sql= "DELETE FROM traceoptions WHERE RID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$rid]);
    
    
    $sql= "DELETE FROM twaitlist WHERE RID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$rid]);
    
    $sql= "DELETE FROM tattendance WHERE RID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$rid]);     
        

     $sql= "DELETE FROM traces WHERE RID=?";
        
     $statement= $db->prepare($sql);
     $statement->execute([$rid]); 
    
    
}



function ladeRace($rid) {


    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    
    $sql="SELECT * FROM traces WHERE RID=".$rid.";";
    $result=$db->query($sql)->fetchAll();
    
    
    if (count($result)>0) {
        $data=$result[0];
    }
    else {
    
        $rid=0;
    }
    
    $sec ="<form action=\"config.php?action=save&race=".$rid."\" method=\"post\">\n";
 
 
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"rid\">Race-ID:</label>";
    $sec .="    </div>\n";
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <input type=\"text\" id=\"rid\" name=\"rid\" value=\"".$rid."\" readonly disabled>";
    $sec .="    </div>";
    $sec .="  </div>\n";
    
    
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"race_name\">Bezeichnung:</label>";
    $sec .="    </div>\n";
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <input type=\"text\" id=\"race_name\" name=\"race_name\" value=\"".$data["race_name"]."\">";
    $sec .="    </div>";
    $sec .="  </div>\n";
    

    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"race_date\">Datum:</label>";
    $sec .="    </div>\n";
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <input type=\"text\" id=\"race_date\" name=\"race_date\" value=\"".$data["race_date"]."\">";
    $sec .="    </div>";
    $sec .="  </div>\n";
    
    
    //secChannels
    $arrCh=array();
    $sql="SELECT * FROM traceoptions WHERE RID=".$rid." AND option_name='channel' AND status=-1;";
    foreach($db->query($sql) as $rowOptions) {
        $arrCh[count($arrCh)]=$rowOptions["option_value"];
    }
    
    $sql="SELECT * FROM tchannels WHERE status=-1 ORDER BY channel_name";
    
    
    $sec .="<h2>Channel:</h2>\n";
    
    $sec .="  <div class=\"rowCh\" id=\"rowCh\">";
    foreach($db->query($sql) as $rowChannel) {
    
        $r=255;
        $g=255;
        $b=255;
        
        //Farben
        $sql="SELECT * FROM traceoptions WHERE RID=".$rid." AND status=-1 ";
        $sql .=" AND option_name IN ('colorRed','colorGreen','colorBlue') ";
        $sql .=" AND ACCID=".$rowChannel["CID"].";";
        
        foreach($db->query($sql) as $rowColors) {
            switch ($rowColors["option_name"]) {
                case "colorRed":
                    $r=$rowColors["option_value"];
                    break;
                case "colorGreen":
                    $g=$rowColors["option_value"];
                    break;
                case "colorBlue":
                    $b=$rowColors["option_value"];
                    break;
            }
        }
        
        
        //Aktiviert oder nicht
        $sec .="<div style=\"background-color:rgb(".$r.", ".$g.", ".$b.")\">";
  
        
        $sec .="<input value=\"-1\" type=\"checkbox\" name=\"chan".$rowChannel["CID"]."[]\"  id=\"chan".$rowChannel["CID"]."[]\"";
 
        if (array_search($rowChannel["CID"], $arrCh)!==False) {
            $sec .=" checked ";
        }
        
        $sec .=">";
        
        $sec .="<br><span>".$rowChannel["channel_name"]."</span><br>";
        

        //Farbchooser
        $sec .="<br><input name=\"chan".$rowChannel["CID"]."[]\"  id=\"chan".$rowChannel["CID"]."[]\" type=\"number\" min=\"0\" max=\"255\" value=\"".$r."\"/>";
        $sec .="<br><input name=\"chan".$rowChannel["CID"]."[]\"  id=\"chan".$rowChannel["CID"]."[]\" type=\"number\" min=\"0\" max=\"255\" value=\"".$g."\"/>";
        $sec .="<br><input name=\"chan".$rowChannel["CID"]."[]\"  id=\"chan".$rowChannel["CID"]."[]\" type=\"number\" min=\"0\" max=\"255\" value=\"".$b."\"/>";
        $sec .="</div>";
    
    }
    
    $sec .="  </div>\n";
    
    
    
    $sec .="<h2>Sonstige Parameter:</h2>\n";
    
    //sonstige Parameter
    $sql="SELECT * FROM traceoptions WHERE RID=".$rid." AND status=-1 ";
    $sql .=" AND NOT (option_name IN ('channel','colorRed','colorGreen','colorBlue'));";
    foreach($db->query($sql) as $rowOptions) {
    
        $sec .="  <div class=\"row\">";
        $sec .="    <div class=\"col-25\">";
        $sec .="      <label for=\"".$rowOptions["option_name"]."\">".$rowOptions["option_name"].":</label>";
        $sec .="    </div>";
        
        $sqc .="    <div class=\"col-75\">";
        $sec .="      <input type=\"text\" id=\"".$rowOptions["option_name"]."\" name=\"".$rowOptions["option_name"]."\" value=\"".$rowOptions["option_value"]."\">";
        
        $sec .="    </div>";
        $sec .="  </div>\n";

    }
    

    
    
    
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <input type=\"text\" id=\"neuer_parameter_name\" name=\"neuer_parameter_name\">";
    $sec .="    </div>\n";
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <input type=\"text\" id=\"neuer_parameter\" name=\"neuer_parameter\">";
    $sec .="    </div>";
    $sec .="  </div>\n";
    
    
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"status\">Status:</label>";
    $sec .="    </div>\n";
    
    $arrstatus=array(-1 =>"aktiv", 0 => "inaktiv");
    
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <select id=\"status\" name=\"status\">";
    
    foreach ($arrstatus as $key => $status) {
        $sec .="      <option value=\"".$key."\" ";
        if ($data["status"]==$key) {
            $sec .="selected ";
        }
        $sec .=">".$status."</option>";
    }
    $sec .="      </select>";
    $sec .="    </div>";
    $sec .="  </div>\n";
    
    
    
        
    
    $sec .="  <div class=\"row\">";
    $sec .="    <a href=\"config.php?action=delete&rid=".$rid."\" class=\"loeschbutton\">L&ouml;schen</a> <input type=\"submit\" value=\"Speichern\">";
    $sec .="  </div>";
    $sec .="</form>\n";
    
    
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

function generateRaceList($raceid) {


    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');

    $sql = "SELECT * FROM traces ORDER BY race_name";

    $lst="<ul id=\"piloten\">";

    foreach ($db->query($sql) as $row) {

        $sql="SELECT * FROM tattendance WHERE RID=".$row["RID"]." AND status=-1";
        $result=$db->query($sql)->fetchAll();
        
        
        $lst .="<li><a href=\"config.php?race=".$row["RID"]."\" ";
         
         if ($row["RID"]==$raceid) {
            $lst .=" style=\"font-weight:bold; font-style: italic; \" ";
        
         }

         $lst .=">".$row["race_name"]." (".count($result)." Teilnehmer)";

         $lst .="</a></li>\n";
    }

    $lst .="</ul>";

    return $lst;

}

?>
