use std::fs::{write, read_to_string};
use std::path::Path;
use std::env::var;
use winreg::enums::*;
use winreg::RegKey;

const SETUP: &str = r#"
# Electric Tab Completion
Register-ArgumentCompleter -Native -CommandName electric -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
        [Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = [System.Text.Utf8Encoding]::new()
        $Local:word = $wordToComplete.Replace('"', '""')
        $Local:ast = $commandAst.ToString().Replace('"', '""')
        completer --word="$Local:word" --commandline "$Local:ast" --position $cursorPosition | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
}

# Refresh Environment Variables
function Update-Environment() {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host -ForegroundColor Green "Sucessfully Refreshed Environment Variables For powershell.exe"
}

Set-Alias refreshenv Update-Environment
"#;


fn delete_web_integration() {
    let hkcr = RegKey::predef(HKEY_CLASSES_ROOT);
    hkcr.delete_subkey_all("Electric").unwrap();
}

fn main() {
    delete_web_integration();
    let userprofile = var("USERPROFILE").unwrap();

    let powershell_loc: String = format!(
        r"{}\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1",
        userprofile
    )
    .to_string();

    let powershell_path = Path::new(powershell_loc.as_str());

    if powershell_path.exists() {
        let current: String = read_to_string(&powershell_loc).unwrap();
        if current
        .contains("Register-ArgumentCompleter -Native -CommandName electric -ScriptBlock {") {
            // Delete lines from file
            let new: String = current.replace(SETUP, ""); 
            write(powershell_loc, new).unwrap();
        }
    }
}
