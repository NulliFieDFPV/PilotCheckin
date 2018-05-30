<?PHP

function generateRaceCbo($raceid) {

    $db = new PDO('mysql:host=localhost;dbname=dbpilotcheckin', 'udbpilot', 'pdbpilot');

    $sql = "SELECT * FROM traces WHERE status=-1 ORDER BY race_name";


    $cbo="<select id=\"race\" name=\"race\" style=\"width:100%;\" onChange=\"this.form.submit()\">";
    $cbo .="<option value=\"0\">Race w&auml;hlen</option>";
    foreach ($db->query($sql) as $row) {

        $cbo .="<option ";
        if ($raceid==$row["RID"]) {
            $cbo .="selected ";
        }
        $cbo .="value=\"".$row["RID"]."\">".$row['race_name']."</option>";
    }

    $cbo .="</select>";

    return $cbo;
}




function generateOptionCbo($oid) {


    $arrOptions=["Races","Channel"];
    
    $cbo="<select id=\"option\" name=\"option\" style=\"width:100%;\" onChange=\"this.form.submit()\">";
    $cbo .="<option value=\"-1\">Option w&auml;hlen</option>";
    foreach ($arrOptions as $key => $option) {

        $cbo .="<option ";
        if ($oid==$key) {
            $cbo .="selected ";
        }
        $cbo .="value=\"".$key."\">".$option."</option>";
    }

    $cbo .="</select>";

    return $cbo;
}



?>

