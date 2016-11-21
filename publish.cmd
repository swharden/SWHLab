python "dist/newversion.py"
python setup.py sdist upload
pause
echo "cleaning up"
del dist\*.zip
rmdir swhlab.egg-info /s /q
rmdir build