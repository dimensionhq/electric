Import-Module BitsTransfer

$ErrorActionPreference = "Stop"
Start-BitsTransfer 'https://srv-store6.gofile.io/download/mwopq6/Electric%20v1.0.0%20Alpha%20Setup.exe' "${Env:\TEMP}\ElectricSetup.exe" -Description 'Downloading Electric Alpha v1.0.0 Setup from https://electric-package-manager.herokuapp.com/install/windows' -DisplayName 'Downloading Electric' -TransferType Download

Write-Host 'Installing Electric' -ForegroundColor cyan
& "${Env:\TEMP}\ElectricSetup.exe" /VERYSILENT
Write-Host 'Setting Up Tab Completion, Make Sure You Set Your Execution Policy To RemoteSigned Or Unrestricted' -ForegroundColor yellow
Write-Host 'You Can Do So Using "Set-ExecutionPolicy RemoteSigned" or "Set-ExecutionPolicy Unrestricted"' -ForegroundColor yellow
if ([System.IO.File]::Exists('C:\Program Files (x86)\Electric\bin\electric.exe')) {
    Write-Host 'Successfully Installed Electric' -ForegroundColor green
    exit
} else {
    Write-Error 'Failed To Successfully Install Electric'
}
