rm ./dist/*.zip
python "dist/newversion.py"
pause
python setup.py sdist upload
pause