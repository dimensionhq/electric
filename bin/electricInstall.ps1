Import-Module BitsTransfer

$ErrorActionPreference = "Stop"
Start-BitsTransfer 'http://s000.tinyupload.com/download.php?file_id=02437613971367945650&t=0243761397136794565077933' "${Env:\TEMP}\ElectricSetup.exe" -Description 'Downloading Electric Alpha v1.0.0 Setup from https://srv-store6.gofile.io/download' -DisplayName 'Downloading Electric' -TransferType Download

Write-Host 'Installing Electric' -ForegroundColor cyan
& "${Env:\TEMP}\ElectricSetup.exe" /VERYSILENT | Out-Null
Write-Host 'Setting Up Tab Completion, Make Sure You Set Your Execution Policy To RemoteSigned Or Unrestricted' -ForegroundColor yellow
Write-Host 'You Can Do So Using "Set-ExecutionPolicy RemoteSigned" or "Set-ExecutionPolicy Unrestricted"' -ForegroundColor yellow
if ([System.IO.File]::Exists('C:\Program Files (x86)\Electric\bin\electric.exe')) {
    Write-Host 'Successfully Installed Electric' -ForegroundColor green
    exit
} else {
    Write-Error 'Failed To Successfully Install Electric'
}
