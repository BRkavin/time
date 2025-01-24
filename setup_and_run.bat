@echo off
setlocal

:: Set paths
set "python_path=%cd%\PortablePython\Python312"
set "launcher_py=%cd%\launcher.py"

:: Print current directory and paths for debugging
echo Current directory: %cd%
echo Python path: %python_path%
echo Launcher script: %launcher_py%

:: Function to download and install full Python 3.12
:InstallFullPython
echo Downloading full Python installer...
powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe -OutFile python-3.12.0-amd64.exe"
if %errorlevel% neq 0 (
    echo Failed to download Python installer.
    exit /b %errorlevel%
)

echo Installing Python...
start /wait python-3.12.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
if %errorlevel% neq 0 (
    echo Failed to install Python.
    exit /b %errorlevel%
)

del python-3.12.0-amd64.exe

:: Ensure using the correct python executable
echo Searching for Python executable...
for /f "tokens=* delims=" %%P in ('where python') do (
    set "global_python=%%P"
    goto :FoundPython
)

:FoundPython
if not defined global_python (
    echo Python installation verification failed.
    exit /b 1
)

echo Global Python executable: %global_python%

:: Run the launcher.py script
echo Running launcher.py...
"%global_python%" "%launcher_py%"
if %errorlevel% neq 0 (
    echo Failed to run launcher.py.
    exit /b %errorlevel%
)

echo Setup and run completed successfully.
endlocal
pause
goto :EOF
