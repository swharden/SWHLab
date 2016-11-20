python "_ newversion.py"
python setup.py clean
python setup.py sdist
python setup.py register
python setup.py sdist upload
pause