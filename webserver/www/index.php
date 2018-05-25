 
<?PHP
error_reporting(E_ALL);
include "includes/monitor.inc.php";

$raceid=0;
if (isset($_GET["race"])) {
    $raceid=$_GET["race"];
}


if ($raceid>0) {
    header("Refresh: 3; URL=index.php?race=".$raceid);
}


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

$cbo=generateRaceCbo($raceid);



?>

<html>
<head>

</head>

<body style="background-color:#c1eeff">

    <section style=" padding:10px; background-color:#0000cc;" width="100%">

    <form action="index.php" method="get">
      <?PHP echo $cbo; ?>
    </form>
    </section>


<br>
<section>
    <?PHP
    if ($raceid>0) {
        //Teilnehmer laden

        //Monitor laden
        echo ladeTabelle($raceid);

    }
    ?>
</section>
</body>
</html>
