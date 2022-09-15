echo off

:: Get current dir
SET thispath=%~dp0
echo %thispath%

:: Set python runtime path
set PyRunTime=%thispath%\..\python3x64
::
set PATH=%PyRunTime%\python-current;%PyRunTime%\python-current\Scripts;%PyRunTime%\python-current\Lib\;%PATH%
set PYTHONPATH=%PyRunTime%\python-current;%PyRunTime%\python-current\lib;%PyRunTime%\python-current\libs;%PyRunTime%\python-current\DLLs;%PyRunTime%\python-current\

set QT_SCALE_FACTOR=1.5
python --version
start python src/jas_is_view.py --ip 192.168.0.130

if errorlevel 1 (
   echo Failure Reason Given is %errorlevel%
   pause
   exit /b %errorlevel%
)
