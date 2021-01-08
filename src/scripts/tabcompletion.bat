set powershellpath=%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
echo %powershellpath%

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
        echo         electric complete --word=^"$Local:word^" --commandline ^"$Local:ast^" --position $cursorPosition ^| ForEach-Object {
        echo             [System.Management.Automation.CompletionResult]::new^($_, $_, 'ParameterValue', $_^)
        echo         }
        echo }
    ) >> %powershellpath%
)
