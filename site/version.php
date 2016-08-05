<?php
// this is intended to be include()'d
$versions = glob("versions/*.zip");
rsort($versions);
$newPath = $versions[0];
$newVersion = basename($newPath);
$newVersion = substr($newVersion,0,-4);

print_r($newVersion);
?>