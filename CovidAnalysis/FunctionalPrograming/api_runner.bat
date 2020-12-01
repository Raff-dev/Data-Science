@echo off
echo.
echo Activating python virtual environment
call venv\scripts\activate.bat
python --version
echo.
echo Running Django server on localhost
echo ------------------------------------
echo.
python FunctionalProgramingAPI\manage.py runserver
pause