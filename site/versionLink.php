<?php
// this file is meant to be include()'d.
$versions = glob("versions/*.zip");
rsort($versions);
print_r($versions[0]);
?>