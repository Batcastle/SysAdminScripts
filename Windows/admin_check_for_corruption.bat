:: This script is used to check for corruption on a given Windows installation.
:: More advaned checks may be added later, but for now this just does the basic
:: corruption checks a person would do, just automated.
@echo off


net session >nul 2>&1
 if %errorLevel% neq 0 (
 	echo Not running as administrator. Please try again as admin.
        timeout /t -1
        exit /b 1
)


echo Checking internet connection...
FOR /F "tokens=* USEBACKQ" %%F IN (`nslookup example.com`) DO (
        SET var=%%F
)
if not x%var:SERVFAIL=%==x%var% (
        echo It appears there is no internet connection. Please connect to the internet and try again.
        timeout /t -1
        exit /b 1
)


DISM.exe /Online /Cleanup-image /RestoreHealth
TIMEOUT /T 3
sfc /scannow
echo "Scan complete!"
if %1% == "--auto" (
	timeout /t 3
	exit
)
timeout /t -1
exit /b 0