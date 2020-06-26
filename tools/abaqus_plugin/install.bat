@ECHO OFF
SETLOCAL enabledelayedexpansion


ECHO "Installing Meshio-Plugin"

:: Set SIMULIA base directory here:
SET root=C:\SIMULIA\CAE\plugins

SET dir="%~dp0"
SET version=2020
SET codedir=C:\SIMULIA\EstProducts\!version!\win_b64\code\bin

:: Copy
XCOPY %dir%meshio_plugin %root%\!version!\MeshioPlugin\* /YQ
XCOPY %dir%\..\..\meshio !codedir!\meshio\* /YQS
XCOPY %dir%abq_meshio !codedir!\abq_meshio\* /YQ

:: Install dependencies for new Python 3 version ...
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
C:\SIMULIA\EstProducts\2020\win_b64\tools\SMApy\python2.7\python.exe get-pip.py
DEL get-pip.py
C:\SIMULIA\EstProducts\2020\win_b64\tools\SMApy\python2.7\Scripts\pip.exe install pathlib importlib_metadata
