@ECHO OFF
python "dist/newversion.py"
python setup.py --quiet sdist upload

@ECHO OFF
echo "cleaning up"
del dist\*.zip
rmdir swhlab.egg-info /s /q
pause