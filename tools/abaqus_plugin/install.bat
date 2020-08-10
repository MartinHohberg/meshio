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

	:: Download dependencies
	mkdir dependencies
 	for %%x in (
			https://files.pythonhosted.org/packages/ac/aa/9b065a76b9af472437a0059f77e8f962fe350438b927cb80184c32f075eb/pathlib-1.0.1.tar.gz
			https://files.pythonhosted.org/packages/16/4f/48975536bd488d3a272549eb795ac4a13a5f7fcdc8995def77fbef3532ee/configparser-4.0.2.tar.gz
			https://files.pythonhosted.org/packages/02/54/669207eb72e3d8ae8b38aa1f0703ee87a0e9f88f30d3c0a47bebdb6de242/contextlib2-0.6.0.post1.tar.gz
			https://files.pythonhosted.org/packages/94/d8/65c86584e7e97ef824a1845c72bbe95d79f5b306364fa778a3c3e401b309/pathlib2-2.3.5.tar.gz
			https://files.pythonhosted.org/packages/78/08/d52f0ea643bc1068d6dc98b412f4966a9b63255d20911a23ac3220c033c4/zipp-1.2.0.tar.gz
			https://files.pythonhosted.org/packages/dd/bf/4138e7bfb757de47d1f4b6994648ec67a51efe58fa907c1e11e350cddfca/six-1.12.0.tar.gz
			https://files.pythonhosted.org/packages/df/f5/9c052db7bd54d0cbf1bc0bb6554362bba1012d03e5888950a4f5c5dadc4e/scandir-1.10.0.tar.gz
			https://files.pythonhosted.org/packages/e2/ae/0b037584024c1557e537d25482c306cf6327b5a09b6c4b893579292c1c38/importlib_metadata-1.7.0.tar.gz) DO (
		curl %%x -o temp.tar.gz
		tar xzf temp.tar.gz -C dependencies
		:: Install dependencies
		FOR /d %%D IN (dependencies\*) DO (
			cd %%D
			!python! setup.py install
			cd ../..
			@RD /S /Q %%D
		)
		DEL temp.tar.gz
	)
	@RD /S /Q dependencies
)
