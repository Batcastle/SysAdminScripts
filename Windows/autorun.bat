:: This is an autorun batch file
:: This script allows you to just plug in the Repair Tools drive, and have a CLI come up to automate
:: handing of the scripts and other executables in this directory
@echo off

set location=%~dp0

:main_menu
	echo Welcome to Repair Tools!
	echo    1 - Run a full virus scan.
	echo    2 - Check for corrupted files.
	echo    3 - Manually run a program.
	echo    4 - Run full suite.
	echo    5 - Help
	echo    6 - Exit this script
	set /p "choice=What would you like to do? [1-6]: "


if %choice% == 0 (
	goto main_menu
)
if %choice% == 1 (
	echo Running a full virus scan. Starting with shortest AV scans...
	echo Running GetSusp...
	start /wait %location%\getsusp64.exe
	echo Running Stinger...
	start /wait %location%\Stinger64.exe
	echo Running ClamAV...
	start /wait %location%\admin_clam_scan.bat --auto
)
if %choice% == 2 (
	:: This is Windbloze. There is always corruption. But check anyways to make the user happy.
	start /wait %location%\admin_check_for_corruption.bat --auto
)
if %choice% == 4 (
	echo Checking for corrupt files...
	start /wait %location%\admin_check_for_corruption.bat --auto
	echo Running ClamAV...S
	start /wait %location%\admin_clam_scan.bat --auto
	echo Running GetSusp...
	start /wait %location%\getsusp64.exe
	echo Running Stinger...
	start /wait %location%\Stinger64.exe
)
if %choice% == 5 (
	echo Welcome to Repair Tools!
	echo This tool kit is used to perform basic, repeatable, common repairs on machines. This includes:
	echo     - Perform virus scans
	echo     - Check the file system for corruption
	echo More is planned, but has yet to be implemented.
	timeout /t -1
	goto main_menu
)
if %choice% == 3 (
	echo Not yet implemented.
	goto main_menu
)
if %choice% == 6 (
	echo Exiting...
	exit /b 0
)

goto main_menu
