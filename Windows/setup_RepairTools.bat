:: Setup Repair Tools on a new USB drive
@echo off


:: Make sure we are not running as root. That makes this much more difficult and we don't need it.
net session >nul 2>&1
if %errorLevel% eq 0 (
    echo Running as administrator. Please run normally.
    timeout /t -1
    exit /b 1
)


:: Download files
echo Downloading necessary files...

:: AVs
curl.exe --output ClamAV.zip https://www.clamav.net/downloads/production/clamav-1.3.0.win.x64.zip
curl.exe --output GetSusp64.exe https://downloadcenter.trellix.com/products/mcafee-avert/getsusp/getsusp64.exe
curl.exe --output Stinger64.exe https://downloadcenter.trellix.com/products/mcafee-avert/Stinger/stinger64.exe

:: Batch Scripts
curl.exe --output admin_check_for_corruption.bat https://raw.githubusercontent.com/Batcastle/SysAdminScripts/master/Windows/check_for_corruption.bat
curl.exe --output admin_clam_scan.bat https://raw.githubusercontent.com/Batcastle/SysAdminScripts/master/Windows/clam_scan.bat
curl.exe --output autorun.bat https://raw.githubusercontent.com/Batcastle/SysAdminScripts/master/Windows/autorun.bat

:: Config files
curl.exe --output freshclam.conf https://raw.githubusercontent.com/Batcastle/SysAdminScripts/master/Windows/freshclam.conf

:: Other Assets
curl.exe --output 7z.exe https://www.7-zip.org/a/7zr.exe

:: Extract ClamAV.zip
echo Extracting archives...
7z.exe e ClamAV.zip -y -o ClamAV

:: Configure ClamAV
echo Configuring tools...
move freshclam.conf ClamAV\freshclam.conf

:: Clean up
echo Cleaning up...
@echo on
del ClamAV.zip
del 7z.exe
