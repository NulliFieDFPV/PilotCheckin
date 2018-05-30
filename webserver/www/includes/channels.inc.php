<?PHP


function updateChannel($cid, $ch_name, $ch_band, $ch_channel, $ch_address, $ch_status) {



    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    
    $sql= "UPDATE tchannels SET channel_name=?, band=?, channel=?, address=?, status=? WHERE CID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$ch_name, $ch_band, $ch_channel, $ch_address, $ch_status, $cid]);
    
    
}

function addChannel($ch_name, $ch_band, $ch_channel, $ch_address, $ch_status) {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    $newid=0;
    
    $sql= "INSERT INTO tchannels SET channel_name=?, band=?, channel=?, address=?, status=?";
    $statement= $db->prepare($sql);
    
    $statement->execute([$ch_name, $ch_band, $ch_channel, $ch_address, $ch_status]);
    
    $newid=$db->lastInsertId(); 
    
    return $newid;
    
}
                     


function deleteChannel($cid) {

    
    
    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
     
    $sql= "DELETE FROM traceoptions WHERE option_value=? AND option_name=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$cid]);
    
    $sql= "DELETE FROM traceoptions WHERE ACCID=? AND option_name IN('colorRed', 'colorGreen', 'colorBlue')";
    
    $statement= $db->prepare($sql);
    $statement->execute([$cid]);    
    
    
    $sql= "DELETE FROM tchannels WHERE CID=?";
    
    $statement= $db->prepare($sql);
    $statement->execute([$cid]);
    
}



function ladeChannel($cid) {


    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');
    $arrstatus=array(-1 =>"aktiv", 0 => "inaktiv");
    
    
    $sql="SELECT * FROM tchannels WHERE CID=".$cid.";";
    $result=$db->query($sql)->fetchAll();
    
    
    if (count($result)>0) {
        $data=$result[0];
    }
    else {
    
        $cid=0;
    }
    
    $sec ="<form action=\"config.php?action=save&cid=".$cid."\" method=\"post\">\n";
 
 
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"cid\">Channel-ID:</label>";
    $sec .="    </div>\n";
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <input type=\"text\" id=\"cid\" name=\"cid\" value=\"".$cid."\" readonly disabled>";
    $sec .="    </div>";
    $sec .="  </div>\n";
    
    
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"channel_name\">Bezeichnung:</label>";
    $sec .="    </div>\n";
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <input type=\"text\" id=\"channel_name\" name=\"channel_name\" value=\"".$data["channel_name"]."\">";
    $sec .="    </div>";
    $sec .="  </div>\n";
    

    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"channel_band\">Band:</label>";
    $sec .="    </div>\n";
    
    $sec .="    <div class=\"col-75\">";
    $sec .="    <select id=\"channel_band\" name=\"channel_band\">";
    
    $band=0;
    for ($band=0;$band<=10;$band++) {
        $sec .="      <option value=\"".$band."\" ";
    
        if ($band==$data["band"]) {
            $sec .=" selected";
        }
    
    
        $sec .=" >".$band."</option>";
    }
    
    $sec .="    </select>";
    $sec .="    </div>";
    $sec .="  </div>\n";
    
    
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"channel_channel\">Channel:</label>";
    $sec .="    </div>\n";
    
    $sec .="    <div class=\"col-75\">";
    $sec .="    <select id=\"channel_channel\" name=\"channel_channel\">";
    
    $channel=0;
    for ($channel=0;$channel<=8;$channel++) {
        $sec .="      <option value=\"".$channel."\" ";

        if ($channel==$data["channel"]) {
            $sec .=" selected";
        }
    
    
        $sec .=" >".$channel."</option>";
    }
    
    $sec .="    </select>";
    $sec .="    </div>";
    $sec .="  </div>\n";
    
   
   $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"channel_name\">I2C-Adresse (Dezimal):</label>";
    $sec .="    </div>\n";
    
    $sqc .="    <div class=\"col-75\">";
    $sec .="      <input type=\"text\" id=\"channel_address\" name=\"channel_address\" value=\"".$data["address"]."\">";
    $sec .="    </div>";
    $sec .="  </div>\n";
    

    
    $sec .="  <div class=\"row\">";
    $sec .="    <div class=\"col-25\">";
    $sec .="      <label for=\"status\">Status:</label>";
    $sec .="    </div>\n";
    
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
    $sec .="    <a href=\"config.php?action=delete&cid=".$cid."\" class=\"loeschbutton\">L&ouml;schen</a> <input type=\"submit\" value=\"Speichern\">";
    $sec .="  </div>";
    $sec .="</form>\n";
    
    
    return $sec;
    
}




function generateChannelList($channelid) {


    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');

    $sql = "SELECT * FROM tchannels ORDER BY channel_name";

    $lst="<ul id=\"piloten\">";

    foreach ($db->query($sql) as $row) {

        $sql="SELECT * FROM traceoptions WHERE option_value=".$row["CID"]." AND status=-1 AND option_name='channel'";
        $result=$db->query($sql)->fetchAll();
        
        
        $lst .="<li><a href=\"config.php?cid=".$row["CID"]."\" ";
         
         if ($row["CID"]==$channelid) {
            $lst .=" style=\"font-weight:bold; font-style: italic; \" ";
        
         }

         $lst .=">".$row["channel_name"]." (".count($result)." Races zugeordnet)";

         $lst .="</a></li>\n";
    }

    $lst .="</ul>";

    return $lst;

}

?>
