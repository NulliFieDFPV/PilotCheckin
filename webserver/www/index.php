 <?PHP

error_reporting(E_ALL);

include "includes/functions.inc.php";
include "includes/start.inc.php";

$raceid=-1;

if (isset($_POST["race"])) {
    $raceid=$_POST["race"];
}
else {
    $raceid=-1;
}


if ($raceid>0) {
    setCurrentRace($raceid);
}


$raceCombo=generateCurrentRaceCombo();

$tblstats=generateStats();


?>

<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" type="text/css" href="css/default.css">
    <title>Pilot Checkin - START</title>
</head>

<body>
    <?PHP include "navigation.php" ?>

<br>

<section class="race">
<form action="index.php" method="post">

    <?PHP echo $raceCombo; ?>
    
</form>
</section>
<section class="main">
<section class="stats">
<?PHP echo $tblstats; ?>
</section>
</section>
</body>
</html>
