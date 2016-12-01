@echo OFF
set /p moduleName=<moduleName.txt
python update_version.py
set /p version=<version.txt
cd ..
echo   ### UPLOADING TO PYPI ###
python setup.py sdist upload
echo   ### COMMITTING CHANGES TO GIT ###
:: using "git" from the command line may require that you add the path to git.exe to your system path:
:: C:\Users\swharden\AppData\Local\GitHub\PortableGit_d7effa1a4a322478cd29c826b52a0c118ad3db11\cmd\
git add --all
git commit -m "PyPi build %version%"
echo ### DONE! ###
echo Remember that a GitHub Sync is required.
pause
