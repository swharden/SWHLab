@echo off
python "./cleantests.py"
python "../doc/gendocs.py"
pause
python "../core/version.py" distribute
pause