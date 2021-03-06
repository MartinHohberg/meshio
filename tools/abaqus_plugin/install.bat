@ECHO OFF
SETLOCAL enabledelayedexpansion

ECHO ######################################
ECHO ##     Installing Meshio-Plugin     ##
ECHO ######################################

:: Set SIMULIA base directory here:
SET root=C:\SIMULIA\CAE\plugins

SET dir="%~dp0"


SET Index=1
FOR /d %%D IN (%root%\*) DO (
  SET "versions[!Index!]=%%D"
  SET /a Index+=1
)
set /a UBound=Index-1
for /l %%i in (1,1,%UBound%) do (
  ECHO "Installing Meshio for Abaqus version !versions[%%i]!"
  SET str=!versions[%%i]!
  SET version=!str:~-4!

  IF !version! GEQ 2020 (
    SET codedir=C:\SIMULIA\EstProducts\!version!\win_b64\code\bin
		SET python=C:\SIMULIA\EstProducts\!version!\win_b64\tools\SMApy\python2.7\python.exe
  ) ELSE (
    SET codedir=C:\SIMULIA\CAE\!version!\win_b64\code\bin
		SET python=C:\SIMULIA\CAE\!version!\win_b64\tools\SMApy\python2.7\python.exe
  )
	:: Copy
	XCOPY %dir%meshio_plugin %root%\!version!\MeshioPlugin\* /YQ
	XCOPY %dir%\..\..\meshio !codedir!\meshio\* /YQS
	XCOPY %dir%abq_meshio !codedir!\abq_meshio\* /YQ

	:: Download dependency
	curl --silent https://files.pythonhosted.org/packages/ac/aa/9b065a76b9af472437a0059f77e8f962fe350438b927cb80184c32f075eb/pathlib-1.0.1.tar.gz  -o pathlib-1.0.1.tar.gz
	tar xzf pathlib-1.0.1.tar.gz
	cd pathlib-1.0.1
	!python! setup.py -q install
	cd ..
	@RD /S /Q pathlib-1.0.1
	DEL pathlib-1.0.1.tar.gz
)
