set powershellpath=%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
echo %powershellpath%

powershell Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force 

if not EXIST %USERPROFILE%\Documents\WindowsPowerShell\ mkdir %USERPROFILE%\Documents\WindowsPowerShell\

IF not EXIST %powershellpath% type nul>%powershellpath%

>nul find "Register-ArgumentCompleter -Native -CommandName electric -ScriptBlock {" %powershellpath% && (
    echo Found
) || (
    (
        echo[
        echo # Electric Tab Completion
        echo Register-ArgumentCompleter -Native -CommandName electric -ScriptBlock {
        echo     param^($wordToComplete, $commandAst, $cursorPosition^)
        echo         [Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = [System.Text.Utf8Encoding]::new^(^)
        echo         $Local:word = $wordToComplete.Replace^('^"', '^"^"'^)
        echo         $Local:ast = $commandAst.ToString^(^).Replace^('^"', '^"^"'^)
        echo         completer complete --word=^"$Local:word^" --commandline ^"$Local:ast^" --position $cursorPosition ^| ForEach-Object {
        echo             [System.Management.Automation.CompletionResult]::new^($_, $_, 'ParameterValue', $_^)
        echo         }
        echo }
    ) >> %powershellpath%
)

>nul find "function Update-Environment() {" %powershellpath% && (
    echo Found
) || (
    (
        echo[
        echo # Refresh Environment Variables
        echo function Update-Environment() {
        echo    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        echo    Write-Host -ForegroundColor Green "Sucessfully Refreshed Environment Variables For powershell.exe"
        echo }
        echo Set-Alias refreshenv Update-Environment
    ) >> %powershellpath%
)
