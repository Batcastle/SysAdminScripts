:: Quickly and Easily Scan a system using ClamAV
@echo off


set base=%cd%
set loc=%~dp0
%loc:~0,2%
cd ClamAV

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


echo Updating AV database. Please wait...
.\freshclam.exe --config-file="conf_examples\freshclam.conf.sample" --show-progress 
    

echo Scanning. Please wait. This will likely take a while...
.\clamscan.exe --memory --kill --remove=yes --recursive=yes --bell --suppress-ok-results C:/*

timeout /t -1
cd %base%
exit /b