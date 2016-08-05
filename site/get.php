<html>
<body>

<?php
$versions = glob("versions/*.zip");
rsort($versions);
$newPath = $versions[0];
$newVersion = basename($newPath);
$newVersion = substr($newVersion,0,-4);
?>

<?php print_r($newPath);?>


<a href="<?php print_r($newPath);?>"><?php print_r($newPath);?></a>

</body></html>